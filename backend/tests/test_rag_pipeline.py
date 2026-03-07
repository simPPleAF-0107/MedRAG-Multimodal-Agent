import pytest
import asyncio
from backend.core.pipeline import core_pipeline

@pytest.mark.asyncio
async def test_pipeline_execution_success():
    """
    Ensures the 10-step intelligence pipeline orchestrator runs end-to-end without crashing
    and returns the expected evaluation keys.
    """
    query = "Patient has severe chest pain and left arm numbness."
    
    # Run the pipeline purely with text to verify fallbacks work
    result = await core_pipeline.run_multimodal_rag_pipeline(text_query=query, image=None)
    
    assert isinstance(result, dict)
    assert "diagnosis" in result
    assert "confidence_score" in result
    assert "risk_score" in result
    assert "emergency_flag" in result
    
    # Specific verification of the triage route
    assert result["emergency_flag"] == True  # "chest pain" / "numbness" should trigger the emergency detector
