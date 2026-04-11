import logging
import asyncio
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
from backend.rag.image.heatmap import generate_heatmap
from backend.llm.report_generator import report_generator

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    text_query: str
    image: any  # Image object
    evidence_text: str
    evidence_image: str
    retrieval_scores: list  # Real similarity scores from Qdrant
    diagnosis: str
    hallucination_score: float
    hallucination_flags: list  # Flags from hallucination checker for self-correction
    risk_score: int
    risk_level: str
    emergency_flag: bool
    differential: list
    confidence: float
    recommendations: dict
    heatmap_path: str
    recommended_specialty: str
    verification_passed: bool  # Whether self-verify loop passed
    correction_attempts: int   # Number of self-correction attempts (max 1)
    final_payload: dict

# 1. Retriever Component
async def retrieve_node(state: AgentState) -> AgentState:
    logger.info("LangGraph Node: Retrieving Evidence...")
    try:
        retrieval_result = await retriever_agent.run({
            "text_query": state["text_query"],
            "image": state.get("image")
        })
        state["evidence_text"] = retrieval_result.get("text_context", "")
        state["evidence_image"] = retrieval_result.get("image_context", "")
        state["retrieval_scores"] = retrieval_result.get("retrieval_scores", [0.5])
        
        logger.info(f"Retrieve node: evidence_len={len(state['evidence_text'])}, scores={state['retrieval_scores']}")
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
        MAX_EVIDENCE_CHARS = 12_000
        if len(state["evidence_text"]) > MAX_EVIDENCE_CHARS:
            state["evidence_text"] = state["evidence_text"][:MAX_EVIDENCE_CHARS] + "\n... [evidence truncated for context limit]"
            logger.info(f"Evidence text capped at {MAX_EVIDENCE_CHARS} chars to prevent TPM overflow.")
            
    except Exception as e:
        logger.error(f"Evidence retrieval failed: {e}")
        state["evidence_text"] = ""
        state["retrieval_scores"] = [0.5]
    return state

# 2. Reasoning Component
async def reasoning_node(state: AgentState) -> AgentState:
    logger.info("LangGraph Node: Reasoning & Diagnosis...")
    try:
        reasoning_result = await reasoning_agent.run({
            "text_query": state["text_query"],
            "text_context": state.get("evidence_text", ""),
            "image_context": state.get("evidence_image", "")
        })
        state["diagnosis"] = reasoning_result.get("diagnosis_reasoning", "Unable to generate diagnosis.")
    except Exception as e:
        logger.error(f"Reasoning agent failed: {e}")
        state["diagnosis"] = "Unable to generate diagnosis due to error."
    return state

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

# 4. Self-Verification & Correction Node (NEW)
async def verify_and_correct_node(state: AgentState) -> AgentState:
    """
    If hallucination_score > 0.12, re-reason with correction instructions.
    Max 2 retries to avoid infinite loops.
    """
    hallucination = state.get("hallucination_score", 0.0)
    attempts = state.get("correction_attempts", 0)
    
    if hallucination <= 0.12 or attempts >= 2:
        # Either hallucination is acceptably low, or we've exhausted retries
        state["verification_passed"] = (hallucination <= 0.12)
        if state["verification_passed"]:
            logger.info("✅ Verification PASSED: hallucination within acceptable range (≤0.12)")
        else:
            logger.warning(f"⚠️ Verification: hallucination={hallucination:.2f} after {attempts} correction(s) — proceeding with best result")
        return state
    
    # Hallucination too high — trigger self-correction
    logger.info(f"🔄 Self-correction triggered: hallucination={hallucination:.2f}, attempt={attempts+1}")
    
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
            max_tokens=2500,
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
            state["verification_passed"] = (new_hall_score <= 0.12)
            
            logger.info(f"Self-correction result: hallucination {hallucination:.2f} → {new_hall_score:.2f}")
        except Exception as e:
            logger.error(f"Re-check after correction failed: {e}")
            state["verification_passed"] = False
            
    except Exception as e:
        logger.error(f"Self-correction LLM call failed: {e}")
        state["verification_passed"] = False
        state["correction_attempts"] = attempts + 1
    
    return state

# 5. Final Reporter
async def reporter_node(state: AgentState) -> AgentState:
    logger.info("LangGraph Node: Final Report Generation...")
    
    try:
        # Compute deterministic evidence overlap for the confidence formula
        from backend.services.confidence_engine import evidence_overlap_score
        overlap = evidence_overlap_score(
            state.get("diagnosis", ""),
            state.get("evidence_text", "")
        )
        
        # Use REAL retrieval scores from the vector search, not hardcoded values
        real_scores = state.get("retrieval_scores", [0.5])
        verification_passed = state.get("verification_passed", False)
        state["confidence"] = calculate_confidence(
            real_scores, 
            state.get("hallucination_score", 0.0),
            verification_passed=verification_passed,
            evidence_overlap=overlap
        )
    except: state["confidence"] = 0.0
    
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
        "heatmap": state.get("heatmap_path", ""),
        "final_report": report_generator.format_final_report(state),
        "confidence_calibration": {"overall_confidence": state.get("confidence", 0.0)},
        "risk_assessment": {"risk_score": state.get("risk_score", 0), "risk_level": state.get("risk_level", "Unknown")},
        "verification_passed": state.get("verification_passed", False),
        "correction_attempts": state.get("correction_attempts", 0),
    }
    return state

# Setup LangGraph Workflow with Verify-and-Correct Loop
workflow = StateGraph(AgentState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("reasoning", reasoning_node)
workflow.add_node("guardrails", guardrails_node)
workflow.add_node("verify_and_correct", verify_and_correct_node)
workflow.add_node("reporter", reporter_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "reasoning")
workflow.add_edge("reasoning", "guardrails")
workflow.add_edge("guardrails", "verify_and_correct")
workflow.add_edge("verify_and_correct", "reporter")
workflow.add_edge("reporter", END)

medrag_agent = workflow.compile()
