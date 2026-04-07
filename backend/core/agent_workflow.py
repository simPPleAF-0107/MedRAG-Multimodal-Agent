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
    risk_score: int
    risk_level: str
    emergency_flag: bool
    differential: list
    confidence: float
    recommendations: dict
    heatmap_path: str
    recommended_specialty: str
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
            state["evidence_text"] += context_str
            logger.info("GraphRAG contextual fusion successful.")
            
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
            return 0.3, ["Hallucination check unavailable."]
        
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
    else:
        state["hallucination_score"] = 0.3
    
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

# 4. Final Reporter
async def reporter_node(state: AgentState) -> AgentState:
    logger.info("LangGraph Node: Final Report Generation...")
    
    try:
        # Use REAL retrieval scores from the vector search, not hardcoded values
        real_scores = state.get("retrieval_scores", [0.5])
        state["confidence"] = calculate_confidence(real_scores, state.get("hallucination_score", 0.0))
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
    }
    return state

# Setup LangGraph Workflow
workflow = StateGraph(AgentState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("reasoning", reasoning_node)
workflow.add_node("guardrails", guardrails_node)
workflow.add_node("reporter", reporter_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "reasoning")
workflow.add_edge("reasoning", "guardrails")
workflow.add_edge("guardrails", "reporter")
workflow.add_edge("reporter", END)

medrag_agent = workflow.compile()
