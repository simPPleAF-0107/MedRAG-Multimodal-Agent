import logging
import asyncio
from backend.agents.retriever_agent import retriever_agent
from backend.agents.reasoning_agent import reasoning_agent
from backend.agents.memory_agent import memory_agent

# Dynamic Intelligence Plugin Services
from backend.services.hallucination_checker import detect_hallucination
from backend.services.risk_engine import calculate_risk
from backend.services.temporal_analyzer import analyze_trends
from backend.services.emergency_detector import detect_emergency
from backend.services.differential_diagnosis import generate_differential
from backend.services.confidence_engine import calculate_confidence
from backend.services.bias_checker import check_bias
from backend.services.recommendation_engine import generate_recommendations

# Multimodal processing
from backend.rag.image.heatmap import generate_heatmap

# Final Report generation
from backend.llm.report_generator import report_generator

# Performance Profiling
from backend.utils.performance_logger import performance_logger

logger = logging.getLogger(__name__)

class CorePipeline:
    """
    Modular Orchestrator Pipeline implementing the strict Research-Grade requirements.
    All components are executed sequentially with try/except fallbacks ensuring pipeline stability.
    """

    async def run_multimodal_rag_pipeline(self, text_query: str, image=None, patient_graph=None) -> dict:
        logger.info(f"== MEDRAG LANGGRAPH PIPELINE INITIATED == Query: {text_query[:50]}...")
        from backend.core.agent_workflow import medrag_agent

        initial_state = {
            "text_query": text_query,
            "image": image,
            "evidence_text": "",
            "evidence_image": "",
            "retrieval_scores": [],
            "diagnosis": "",
            "hallucination_score": 0.0,
            "risk_score": 0,
            "risk_level": "Unknown",
            "emergency_flag": False,
            "differential": [],
            "confidence": 0.0,
            "recommendations": {},
            "heatmap_path": "",
            "recommended_specialty": "General",
            "final_payload": {}
        }

        # Run the compiled LangGraph workflow asynchronously
        final_state = await medrag_agent.ainvoke(initial_state)

        logger.info("== MEDRAG LANGGRAPH PIPELINE COMPLETE ==")
        return final_state["final_payload"]

core_pipeline = CorePipeline()
