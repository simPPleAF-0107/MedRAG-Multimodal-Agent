import logging
import asyncio
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from backend.agents.retriever_agent import retriever_agent
from backend.agents.reasoning_agent import reasoning_agent

# Plugins
from backend.services.hallucination_checker import detect_hallucination
from backend.services.risk_engine import calculate_risk
from backend.services.temporal_analyzer import analyze_trends
from backend.services.emergency_detector import detect_emergency
from backend.services.differential_diagnosis import generate_differential
from backend.services.confidence_engine import calculate_confidence
from backend.services.bias_checker import check_bias
from backend.services.recommendation_engine import generate_recommendations
from backend.services.symptom_extractor import symptom_extractor
from backend.rag.image.heatmap import generate_heatmap
from backend.llm.report_generator import report_generator

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
ENABLE_MULTI_PASS = os.environ.get("ENABLE_MULTI_PASS", "true").lower() == "true"
HALLUCINATION_ACCEPT_THRESHOLD = 0.20    # Below this = acceptable (was 0.25)
HALLUCINATION_HARD_REJECT = 0.35         # Above this after retries = hard reject (was 0.50)
LOW_CONFIDENCE_THRESHOLD = 75.0          # Below this = "I don't know" path (was 40.0)
MAX_CORRECTION_ATTEMPTS = 2


class AgentState(TypedDict):
    text_query: str
    image: any  # Image object
    evidence_text: str
    evidence_image: str
    evidence_quality: str  # HIGH / MODERATE / LOW / INSUFFICIENT
    retrieval_scores: list  # Real similarity scores from Qdrant
    extracted_symptoms: list  # Structured symptoms from symptom extractor
    symptom_specialty_hint: str  # Specialty suggested by symptom body regions
    diagnosis: str
    hallucination_score: float
    hallucination_flags: list  # Flags from hallucination checker for self-correction
    risk_score: int
    risk_level: str
    emergency_flag: bool
    differential: list
    confidence: float
    consistency_score: float  # Multi-pass agreement score (P7)
    diagnostic_match_score: float  # Symptom→disease pattern match score
    recommendations: dict
    heatmap_path: str
    recommended_specialty: str
    verification_passed: bool  # Whether self-verify loop passed
    correction_attempts: int   # Number of self-correction attempts (max 2)
    final_payload: dict

# 0. Symptom Extraction Node (NEW — Wave 3)
async def symptom_extraction_node(state: AgentState) -> AgentState:
    """Extract structured symptoms from the patient query using the dedicated extractor."""
    logger.info("LangGraph Node: Extracting Symptoms...")
    try:
        extraction = symptom_extractor.extract(state["text_query"])
        state["extracted_symptoms"] = extraction.get("symptoms", [])
        
        # Get specialty hint from body region analysis
        specialty_hint = symptom_extractor.get_specialty_hint(extraction)
        state["symptom_specialty_hint"] = specialty_hint or ""
        
        logger.info(
            f"Symptom extraction: {len(state['extracted_symptoms'])} symptoms found, "
            f"specialty_hint={state['symptom_specialty_hint']}, "
            f"body_regions={list(extraction.get('body_regions', {}).keys())}"
        )
    except Exception as e:
        logger.error(f"Symptom extraction failed (non-critical): {e}")
        state["extracted_symptoms"] = []
        state["symptom_specialty_hint"] = ""
    return state

# 1. Retriever Component
async def retrieve_node(state: AgentState) -> AgentState:
    logger.info("LangGraph Node: Retrieving Evidence...")
    try:
        retrieval_result = await retriever_agent.run({
            "text_query": state["text_query"],
            "image": state.get("image"),
            "extracted_symptoms": state.get("extracted_symptoms", []),
            "specialty_hint": state.get("symptom_specialty_hint", ""),
        })
        state["evidence_text"] = retrieval_result.get("text_context", "")
        state["evidence_image"] = retrieval_result.get("image_context", "")
        state["retrieval_scores"] = retrieval_result.get("retrieval_scores", [0.5])
        state["evidence_quality"] = retrieval_result.get("evidence_quality", "LOW")
        
        logger.info(
            f"Retrieve node: evidence_len={len(state['evidence_text'])}, "
            f"scores={state['retrieval_scores']}, quality={state['evidence_quality']}"
        )
        if state.get("image"):
            state["heatmap_path"] = generate_heatmap(state["image"])
            
        # -- GraphRAG Enhancement --
        from backend.rag.graph_store import graph_store
        
        # Extract keywords for graph query (simple implementation for prototype)
        keywords = [word for word in state["text_query"].lower().replace('?', '').replace('.', '').split() if len(word) > 4]
        graph_context = graph_store.query_subgraph(starting_nodes=keywords)
        
        if graph_context:
            context_str = "\n[Knowledge Graph Context]:\n"
            for node, relations in graph_context.items():
                for rel in relations:
                    context_str += f"- {node} -> {rel['relation']} -> {rel['target']}\n"
            # Cap GraphRAG context to ~1K tokens to prevent LLM TPM overflow
            MAX_GRAPH_CHARS = 5_000
            if len(context_str) > MAX_GRAPH_CHARS:
                context_str = context_str[:MAX_GRAPH_CHARS] + "\n... [graph context truncated]\n"
            state["evidence_text"] += context_str
            logger.info("GraphRAG contextual fusion successful.")
        
        # Final safety cap: total evidence must not exceed ~3K tokens for the reasoning LLM
        MAX_EVIDENCE_CHARS = 16_000
        if len(state["evidence_text"]) > MAX_EVIDENCE_CHARS:
            state["evidence_text"] = state["evidence_text"][:MAX_EVIDENCE_CHARS] + "\n... [evidence truncated for context limit]"
            logger.info(f"Evidence text capped at {MAX_EVIDENCE_CHARS} chars to prevent TPM overflow.")
            
    except Exception as e:
        logger.error(f"Evidence retrieval failed: {e}")
        state["evidence_text"] = ""
        state["retrieval_scores"] = [0.5]
        state["evidence_quality"] = "INSUFFICIENT"
    return state

# 2. Reasoning Component with Multi-Pass Consistency (P7)
async def reasoning_node(state: AgentState) -> AgentState:
    logger.info("LangGraph Node: Reasoning & Diagnosis...")
    try:
        # Primary reasoning pass
        reasoning_result = await reasoning_agent.run({
            "text_query": state["text_query"],
            "text_context": state.get("evidence_text", ""),
            "image_context": state.get("evidence_image", "")
        })
        primary_diagnosis = reasoning_result.get("diagnosis_reasoning", "Unable to generate diagnosis.")
        state["diagnosis"] = primary_diagnosis

        # ── P7: Multi-pass consistency check ──────────────────────────────────
        if ENABLE_MULTI_PASS:
            try:
                consistency = await _check_consistency(state, primary_diagnosis)
                state["consistency_score"] = consistency
                logger.info(f"Multi-pass consistency score: {consistency:.2f}")
            except Exception as e:
                logger.warning(f"Multi-pass consistency check failed (non-critical): {e}")
                state["consistency_score"] = 0.7  # Neutral fallback
        else:
            state["consistency_score"] = 0.7  # Disabled — neutral

    except Exception as e:
        logger.error(f"Reasoning agent failed: {e}")
        state["diagnosis"] = "Unable to generate diagnosis due to error."
        state["consistency_score"] = 0.3
    return state


async def _check_consistency(state: AgentState, primary_diagnosis: str) -> float:
    """
    Run a second reasoning pass with slightly different temperature
    and compare the top diagnoses for agreement.
    Returns a consistency score 0.0 - 1.0.
    """
    from backend.llm.openai_client import openai_client
    from backend.llm.prompt_templates import MEDICAL_ASSISTANT_SYSTEM_PROMPT, DIAGNOSIS_PROMPT_TEMPLATE

    diagnosis_prompt = DIAGNOSIS_PROMPT_TEMPLATE.format(
        query=state["text_query"],
        text_context=state.get("evidence_text", "")[:8000],  # Truncate for second pass
        image_context=state.get("evidence_image", "")
    )

    second_diagnosis = await openai_client.generate_completion(
        prompt=diagnosis_prompt,
        system_prompt=MEDICAL_ASSISTANT_SYSTEM_PROMPT,
        temperature=0.15,  # Slightly higher than primary (0.05)
        max_tokens=1500,   # Shorter — we only need the key findings
        use_cache=False     # Must be a fresh generation
    )

    # Compare: extract top condition names from both and check overlap
    from backend.services.confidence_engine import extract_medical_terms
    terms_1 = extract_medical_terms(primary_diagnosis)
    terms_2 = extract_medical_terms(second_diagnosis)

    if not terms_1 or not terms_2:
        return 0.5

    overlap = terms_1 & terms_2
    union = terms_1 | terms_2
    jaccard = len(overlap) / len(union) if union else 0.5

    # Scale: Jaccard > 0.6 = high consistency, < 0.3 = concerning
    if jaccard >= 0.6:
        return 1.0
    elif jaccard >= 0.4:
        return 0.7
    elif jaccard >= 0.25:
        return 0.4
    else:
        return 0.2


# 3. Guardrails / Plugin Parallel Execution
async def guardrails_node(state: AgentState) -> AgentState:
    logger.info("LangGraph Node: Running Guardrails...")
    
    async def run_hallucination():
        try: return await detect_hallucination(state.get("diagnosis", ""), state.get("evidence_text", ""))
        except Exception as e:
            logger.error(f"Hallucination check failed: {e}")
            return 0.15, ["Hallucination check unavailable."]
        
    async def run_risk():
        try:
            patient_context = {"history": state.get("text_query", ""), "evidence": state.get("evidence_text", "")[:500]}
            return await calculate_risk(patient_context, state.get("diagnosis", ""))
        except Exception as e:
            logger.error(f"Risk engine failed: {e}")
            return 20, "Low"
        
    async def run_emergency():
        try: return detect_emergency(state["text_query"], state.get("diagnosis", ""))
        except Exception: return False, "None"
        
    async def run_differential():
        try:
            # Pass both diagnosis and query for accurate differential generation
            context = f"Patient Query: {state.get('text_query', '')}\n\nDiagnosis: {state.get('diagnosis', '')}\n\nEvidence: {state.get('evidence_text', '')[:1000]}"
            return await generate_differential(context)
        except Exception as e:
            logger.error(f"Differential diagnosis failed: {e}")
            return []

    hallucination_res, risk_res, emergency_res, diff_res = await asyncio.gather(
        run_hallucination(), run_risk(), run_emergency(), run_differential()
    )
    
    # Unpack hallucination result
    if hallucination_res and isinstance(hallucination_res, tuple):
        state["hallucination_score"] = hallucination_res[0]
        state["hallucination_flags"] = hallucination_res[1] if len(hallucination_res) > 1 else []
    else:
        state["hallucination_score"] = 0.15
        state["hallucination_flags"] = []
    
    # Unpack risk result
    if risk_res and isinstance(risk_res, tuple):
        state["risk_score"], state["risk_level"] = risk_res
    else:
        state["risk_score"], state["risk_level"] = 20, "Low"
        
    # Unpack emergency result
    if emergency_res and isinstance(emergency_res, tuple):
        state["emergency_flag"] = emergency_res[0]
    else:
        state["emergency_flag"] = False
        
    # Unpack differential
    if diff_res and isinstance(diff_res, list):
        state["differential"] = diff_res
    else:
        state["differential"] = []
    
    logger.info(f"Guardrails complete: hallucination={state['hallucination_score']:.2f}, risk={state['risk_score']}, emergency={state['emergency_flag']}")

    return state

# 4. Self-Verification & Correction Node (P3: Hard Rejection)
async def verify_and_correct_node(state: AgentState) -> AgentState:
    """
    Verification loop with hard rejection:
    - hallucination <= 0.25: PASS (acceptable)
    - hallucination 0.25-0.50: Re-reason with stricter constraints (max 2 retries)
    - hallucination > 0.50 after retries: HARD REJECT → replace with safe fallback
    """
    hallucination = state.get("hallucination_score", 0.0)
    attempts = state.get("correction_attempts", 0)
    
    # ── Case 1: Acceptable hallucination ─────────────────────────────────────
    if hallucination <= HALLUCINATION_ACCEPT_THRESHOLD:
        state["verification_passed"] = True
        logger.info(f"[PASS] Verification PASSED: hallucination={hallucination:.2f} <= {HALLUCINATION_ACCEPT_THRESHOLD}")
        return state

    # ── Case 2: Exhausted retries ────────────────────────────────────────────
    if attempts >= MAX_CORRECTION_ATTEMPTS:
        if hallucination > HALLUCINATION_HARD_REJECT:
            # ── P3+P9: HARD REJECT — replace with safe fallback ──────────────
            from backend.llm.prompt_templates import INSUFFICIENT_EVIDENCE_RESPONSE
            logger.warning(
                f"[HARD REJECT] Hallucination={hallucination:.2f} > {HALLUCINATION_HARD_REJECT} "
                f"after {attempts} corrections. Replacing with safe fallback."
            )
            state["diagnosis"] = INSUFFICIENT_EVIDENCE_RESPONSE
            state["verification_passed"] = False
        else:
            # Moderate hallucination but retries exhausted — proceed with warning
            state["verification_passed"] = False
            logger.warning(
                f"[WARN] Verification: hallucination={hallucination:.2f} after {attempts} "
                f"correction(s) — proceeding with best result"
            )
        return state
    
    # ── Case 3: Hallucination too high — trigger self-correction ─────────────
    logger.info(f"[RETRY] Self-correction triggered: hallucination={hallucination:.2f}, attempt={attempts+1}")
    
    from backend.llm.openai_client import openai_client
    from backend.llm.prompt_templates import SELF_VERIFICATION_PROMPT, MEDICAL_ASSISTANT_SYSTEM_PROMPT
    
    flags_text = "\n".join(state.get("hallucination_flags", ["Unsupported claims detected"]))
    
    correction_prompt = SELF_VERIFICATION_PROMPT.format(
        diagnosis=state.get("diagnosis", ""),
        evidence=state.get("evidence_text", "")[:4000],
        flags=flags_text
    )
    
    try:
        corrected_diagnosis = await openai_client.generate_completion(
            prompt=correction_prompt,
            system_prompt=MEDICAL_ASSISTANT_SYSTEM_PROMPT,
            temperature=0.0,   # Fully deterministic for corrections — zero creativity
            max_tokens=2000,
            use_cache=False  # Never use cached results for corrections
        )
        
        state["diagnosis"] = corrected_diagnosis
        state["correction_attempts"] = attempts + 1
        
        # Re-check hallucination on the corrected diagnosis
        try:
            new_hall_score, new_flags = await detect_hallucination(
                corrected_diagnosis, state.get("evidence_text", "")
            )
            state["hallucination_score"] = new_hall_score
            state["hallucination_flags"] = new_flags
            state["verification_passed"] = (new_hall_score <= HALLUCINATION_ACCEPT_THRESHOLD)
            
            logger.info(f"Self-correction result: hallucination {hallucination:.2f} -> {new_hall_score:.2f}")

            # If still too high after this correction, the next invocation will handle it
            # (via the conditional edge that loops back to this node)
        except Exception as e:
            logger.error(f"Re-check after correction failed: {e}")
            state["verification_passed"] = False
            
    except Exception as e:
        logger.error(f"Self-correction LLM call failed: {e}")
        state["verification_passed"] = False
        state["correction_attempts"] = attempts + 1
    
    return state


def _should_retry_verification(state: AgentState) -> str:
    """
    Conditional edge: after verify_and_correct, decide whether to retry or proceed.
    Returns the name of the next node.
    """
    hallucination = state.get("hallucination_score", 0.0)
    attempts = state.get("correction_attempts", 0)

    if hallucination > HALLUCINATION_ACCEPT_THRESHOLD and attempts < MAX_CORRECTION_ATTEMPTS:
        logger.info(f"[LOOP] Re-entering verify_and_correct: hall={hallucination:.2f}, attempts={attempts}")
        return "verify_and_correct"
    else:
        return "reporter"


# 5. Final Reporter
async def reporter_node(state: AgentState) -> AgentState:
    logger.info("LangGraph Node: Final Report Generation...")
    
    try:
        # Compute deterministic evidence overlap for the confidence formula
        from backend.services.confidence_engine import evidence_overlap_score, symptom_coverage_score
        overlap = evidence_overlap_score(
            state.get("diagnosis", ""),
            state.get("evidence_text", "")
        )
        
        # Compute strict symptom coverage score
        cov_score, _, _ = symptom_coverage_score(
            state.get("text_query", ""),
            state.get("diagnosis", "")
        )
        
        # Use REAL retrieval scores from the vector search, not hardcoded values
        real_scores = state.get("retrieval_scores", [0.5])
        verification_passed = state.get("verification_passed", False)
        evidence_quality = state.get("evidence_quality", "LOW")
        consistency = state.get("consistency_score", 0.7)

        # Compute diagnostic match score from extracted symptoms
        from backend.services.confidence_engine import compute_diagnostic_match_score
        diag_match = compute_diagnostic_match_score(
            state.get("extracted_symptoms", []),
            state.get("evidence_text", "")
        )
        state["diagnostic_match_score"] = diag_match

        state["confidence"] = calculate_confidence(
            real_scores, 
            state.get("hallucination_score", 0.0),
            verification_passed=verification_passed,
            evidence_overlap=overlap,
            evidence_quality=evidence_quality,
            consistency_score=consistency,
            coverage_score=cov_score,
            diagnostic_match_score=diag_match,
        )
    except: state["confidence"] = 0.0
    
    # ── P9: "I Don't Know" Path (Strict Answer Abstention) ────────────────────
    low_confidence_flag = False
    if state["confidence"] < LOW_CONFIDENCE_THRESHOLD:
        # Only replace if not already replaced by hard rejection
        if "Unable to Provide Reliable Diagnosis" not in state.get("diagnosis", ""):
            logger.warning(
                f"[LOW CONFIDENCE] confidence={state['confidence']:.1f}% < {LOW_CONFIDENCE_THRESHOLD}%. "
                f"Abstaining from diagnosis."
            )
            state["diagnosis"] = (
                f"⚠️ **Low confidence — consult specialist** (Confidence: {state['confidence']:.1f}%)\n\n"
                f"The system has low confidence in this assessment due to insufficient or conflicting "
                f"retrieved evidence. Rather than hallucinate an answer, the AI has abstained from providing a "
                f"diagnostic evaluation. Please seek professional medical advice."
            )
        low_confidence_flag = True

    try:
        meal, act = generate_recommendations(state.get("diagnosis", ""), {})
        state["recommendations"] = {"meal_plan": meal, "activity_plan": act}
    except: state["recommendations"] = {}
    
    # Expanded Specialty Router — matches all 30 seeded specialties
    specialty = "General"
    t_low = state["text_query"].lower()
    d_low = state.get("diagnosis", "").lower()
    combined = t_low + " " + d_low
    
    SPECIALTY_KEYWORDS = [
        (["heart", "cardio", "chest pain", "ecg", "cardiac", "arrhythmia", "murmur"], "Cardiology"),
        (["brain", "neuro", "seizure", "stroke", "migraine", "headache", "neuropathy"], "Neurology"),
        (["bone", "joint", "fracture", "ortho", "spine", "disc", "acl", "arthritis"], "Orthopaedics"),
        (["gyn", "period", "menstrual", "pregnancy", "ovarian", "uterus"], "Gynaecology"),
        (["cancer", "tumor", "oncol", "chemotherapy", "carcinoma", "neoplasm", "malignant"], "Oncology"),
        (["blood", "anemia", "leukemia", "lymphoma", "platelet", "coagulation", "hemoglobin"], "Hematology"),
        (["kidney", "renal", "nephro", "dialysis", "creatinine", "glomerulo"], "Nephrology"),
        (["lung", "pulmon", "asthma", "copd", "pneumonia", "bronch", "respiratory"], "Pulmonology"),
        (["diabetes", "thyroid", "endocrine", "insulin", "cortisol", "hormone", "pituitary"], "Endocrinology"),
        (["rheumat", "lupus", "autoimmune", "gout", "fibromyalgia"], "Rheumatology"),
        (["stomach", "gastro", "liver", "hepat", "bowel", "colon", "ibd", "gerd", "pancreat"], "Gastroenterology"),
        (["hiv", "infection", "sepsis", "tuberculosis", "malaria", "meningitis", "antibiotic"], "Infectious Disease"),
        (["skin", "rash", "dermat", "eczema", "psoriasis", "melanoma", "acne"], "Dermatology"),
        (["eye", "vision", "retina", "glaucoma", "cataract", "ophthal", "ocular", "optic"], "Ophthalmology"),
        (["ear", "nose", "throat", "tonsil", "sinus", "hearing", "ent", "laryn"], "ENT / Otolaryngology"),
        (["urin", "bladder", "prostate", "kidney stone", "urol"], "Urology"),
        (["obstetric", "prenatal", "fetal", "labour", "labor", "preeclamp", "gestation"], "Obstetrics"),
        (["child", "pediatr", "neonatal", "infant", "vaccination", "newborn"], "Pediatrics"),
        (["anxiety", "depression", "psychiatr", "bipolar", "schizo", "mental", "suicid", "ptsd", "ocd"], "Psychiatry"),
        (["emergency", "trauma", "cpr", "resuscit", "anaphylax", "shock"], "Emergency Medicine"),
        (["tooth", "dental", "molar", "wisdom", "gum", "oral", "jaw", "tmj", "periodon", "cavity", "impacted"], "Dental / Oral Surgery"),
        (["x-ray", "xray", "mri", "ct scan", "ultrasound", "radiol", "imaging"], "Radiology"),
        (["anesthes", "sedation", "intubat", "ventilat"], "Anesthesiology"),
        (["biopsy", "histol", "patholog", "cytol"], "Pathology"),
        (["neurosurg", "craniot", "hydrocephalus", "spinal surgery"], "Neurosurgery"),
        (["plastic", "reconstruct", "cosmetic", "burn"], "Plastic Surgery"),
        (["vascular", "aorta", "aneurysm", "varicose", "dvt", "thrombosis"], "Vascular Surgery"),
        (["elderly", "geriatr", "dementia", "alzheimer", "frail"], "Geriatrics"),
        (["palliat", "hospice", "end of life", "terminal"], "Palliative Care"),
    ]
    
    for keywords, spec in SPECIALTY_KEYWORDS:
        if any(kw in combined for kw in keywords):
            specialty = spec
            break
    
    state["recommended_specialty"] = specialty

    # --- KNOWLEDGE GAP DETECTION ---
    from backend.services.knowledge_gap_tracker import log_knowledge_gap
    gap_logged = log_knowledge_gap(
        query=state["text_query"],
        hallucination_score=state.get("hallucination_score", 0.0),
        retrieval_scores=state.get("retrieval_scores", []),
        hallucination_flags=state.get("hallucination_flags", []),
        specialty=specialty
    )

    state["final_payload"] = {
        "diagnosis": state.get("diagnosis", ""),
        "differential_diagnosis": state.get("differential", []),
        "confidence_score": state.get("confidence", 0.0),
        "risk_score": state.get("risk_score", 0),
        "hallucination_score": state.get("hallucination_score", 0.0),
        "emergency_flag": state.get("emergency_flag", False),
        "recommended_specialty": state.get("recommended_specialty", "General"),
        "recommendations": state.get("recommendations", {}),
        "evidence": state.get("evidence_text", ""),
        "evidence_quality": state.get("evidence_quality", "LOW"),
        "heatmap": state.get("heatmap_path", ""),
        "final_report": report_generator.format_final_report(state),
        "confidence_calibration": {"overall_confidence": state.get("confidence", 0.0)},
        "risk_assessment": {"risk_score": state.get("risk_score", 0), "risk_level": state.get("risk_level", "Unknown")},
        "verification_passed": state.get("verification_passed", False),
        "correction_attempts": state.get("correction_attempts", 0),
        "consistency_score": state.get("consistency_score", 0.7),
        "knowledge_gap_detected": gap_logged,
        "low_confidence_flag": low_confidence_flag,
    }
    return state

# Setup LangGraph Workflow with Verify-and-Correct Loop + Conditional Retry
workflow = StateGraph(AgentState)

workflow.add_node("symptom_extraction", symptom_extraction_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("reasoning", reasoning_node)
workflow.add_node("guardrails", guardrails_node)
workflow.add_node("verify_and_correct", verify_and_correct_node)
workflow.add_node("reporter", reporter_node)

workflow.set_entry_point("symptom_extraction")
workflow.add_edge("symptom_extraction", "retrieve")
workflow.add_edge("retrieve", "reasoning")
workflow.add_edge("reasoning", "guardrails")
workflow.add_edge("guardrails", "verify_and_correct")

# Conditional edge: retry verification or proceed to reporter
workflow.add_conditional_edges(
    "verify_and_correct",
    _should_retry_verification,
    {
        "verify_and_correct": "verify_and_correct",
        "reporter": "reporter",
    }
)

workflow.add_edge("reporter", END)

medrag_agent = workflow.compile()

class CorePipeline:
    async def run_multimodal_rag_pipeline(self, text_query: str, image=None, patient_graph=None) -> dict:
        initial_state = {
            "text_query": text_query,
            "image": image,
            "evidence_text": "",
            "evidence_image": "",
            "evidence_quality": "LOW",
            "retrieval_scores": [],
            "extracted_symptoms": [],
            "symptom_specialty_hint": "",
            "diagnosis": "",
            "hallucination_score": 0.0,
            "hallucination_flags": [],
            "risk_score": 0,
            "risk_level": "Unknown",
            "emergency_flag": False,
            "differential": [],
            "confidence": 0.0,
            "consistency_score": 0.7,
            "diagnostic_match_score": 0.5,
            "recommendations": {},
            "heatmap_path": "",
            "recommended_specialty": "General",
            "verification_passed": False,
            "correction_attempts": 0,
            "final_payload": {}
        }
        final_state = await medrag_agent.ainvoke(initial_state)
        return final_state["final_payload"]

core_pipeline = CorePipeline()
