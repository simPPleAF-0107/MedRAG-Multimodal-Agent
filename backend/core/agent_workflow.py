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
        except Exception: return 0.0, ""
        
    async def run_risk():
        try: return await calculate_risk({"history": ""}, state.get("diagnosis", ""))
        except Exception: return 0, "Unknown"
        
    async def run_emergency():
        try: return detect_emergency(state["text_query"], state.get("diagnosis", ""))
        except Exception: return False, ""
        
    async def run_differential():
        try: return await generate_differential(state.get("evidence_text", ""))
        except Exception: return []

    hallucination_res, risk_res, emergency_res, diff_res = await asyncio.gather(
        run_hallucination(), run_risk(), run_emergency(), run_differential()
    )
    
    if hallucination_res: state["hallucination_score"], _ = hallucination_res
    else: state["hallucination_score"] = 0.0
    
    if risk_res: state["risk_score"], state["risk_level"] = risk_res
    else: state["risk_score"], state["risk_level"] = 0, "Unknown"
        
    if emergency_res: state["emergency_flag"], _ = emergency_res
    else: state["emergency_flag"] = False
        
    if diff_res: state["differential"] = diff_res
    else: state["differential"] = []
    
    return state

# 4. Final Reporter
async def reporter_node(state: AgentState) -> AgentState:
    logger.info("LangGraph Node: Final Report Generation...")
    
    try:
        # Confidence processing
        state["confidence"] = calculate_confidence([0.85], state.get("hallucination_score", 0.0))
    except: state["confidence"] = 0.0
    
    try:
        meal, act = generate_recommendations(state.get("diagnosis", ""), {})
        state["recommendations"] = {"meal_plan": meal, "activity_plan": act}
    except: state["recommendations"] = {}
    
    # Specialty router
    specialty = "General"
    t_low = state["text_query"].lower()
    d_low = state.get("diagnosis", "").lower()
    if any(w in t_low or w in d_low for w in ["heart", "cardio", "chest"]): specialty = "Cardiology"
    elif any(w in t_low or w in d_low for w in ["brain", "neuro"]): specialty = "Neurology"
    elif any(w in t_low or w in d_low for w in ["bone", "joint", "ortho"]): specialty = "Orthopaedic"
    elif any(w in t_low or w in d_low for w in ["cycle", "gyn", "period"]): specialty = "Gynaecology"
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
