import pytest
from backend.services.hallucination_checker import detect_hallucination
from backend.services.emergency_detector import detect_emergency
from backend.services.confidence_engine import calculate_confidence

@pytest.mark.asyncio
async def test_hallucination_checker():
    """ Verify the logical bounds and functionality of hallucination checks. """
    score, flags = await detect_hallucination("Response unknown", "Context specifies clear conditions.")
    assert score > 0
    assert len(flags) > 0

def test_emergency_detector():
    """ Verify the triage keyword extraction """
    is_emergency, level = detect_emergency("Patient unresponsive with severe myocardial ischemia", "Myocardial Infarction")
    assert is_emergency is True
    assert level == "Critical"
    
    is_emergency_false, level_false = detect_emergency("Patient has a mild rash on left arm", "Contact Dermatitis")
    assert is_emergency_false is False

def test_confidence_calibration():
    """ Verify math execution for confidence score combining retrieves and hallucinations """
    high_conf = calculate_confidence([0.9, 0.95], 0.0)
    assert high_conf >= 90.0
    
    low_conf = calculate_confidence([0.4, 0.5], 1.0) # High hallucination drastically lowers confidence
    assert low_conf < 50.0
