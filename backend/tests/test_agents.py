import pytest
from backend.services.hallucination_checker import detect_hallucination
from backend.services.emergency_detector import detect_emergency
from backend.services.confidence_engine import calculate_confidence, evidence_overlap_score

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
    assert level == "URGENT"
    
    is_emergency_false, level_false = detect_emergency("Patient has a mild rash on left arm", "Contact Dermatitis")
    assert is_emergency_false is False

def test_confidence_calibration():
    """ Verify math execution for confidence score combining retrieves and hallucinations """
    high_conf = calculate_confidence([0.9, 0.95], 0.0, evidence_overlap=0.8)
    assert high_conf >= 85.0  # Adjusted for lower baseline (58)
    
    low_conf = calculate_confidence([0.4, 0.5], 1.0, evidence_overlap=0.1)  # High hallucination drastically lowers confidence
    assert low_conf < 50.0

def test_evidence_overlap_score():
    """ Verify the deterministic evidence overlap computation """
    # High overlap: diagnosis terms appear in evidence
    diagnosis = "Patient shows signs of rheumatoid arthritis with elevated CRP and joint inflammation."
    evidence = "Rheumatoid arthritis is characterized by joint inflammation, elevated CRP levels, and synovial hypertrophy."
    score = evidence_overlap_score(diagnosis, evidence)
    assert score >= 0.4, f"Expected high overlap, got {score}"
    
    # Low overlap: diagnosis terms NOT in evidence
    diagnosis_unrelated = "Patient has severe cardiac arrhythmia with ventricular tachycardia."
    evidence_unrelated = "Dermatitis treatment involves topical corticosteroids and moisturizers."
    score_low = evidence_overlap_score(diagnosis_unrelated, evidence_unrelated)
    assert score_low < 0.3, f"Expected low overlap, got {score_low}"
    
    # Edge case: empty evidence
    score_empty = evidence_overlap_score("Some diagnosis text", "")
    assert score_empty == 0.0

def test_confidence_with_overlap():
    """ Verify that evidence_overlap parameter affects confidence score """
    # Same retrieval + hallucination, different overlap
    conf_high_overlap = calculate_confidence([0.7, 0.8], 0.1, evidence_overlap=0.7)
    conf_low_overlap  = calculate_confidence([0.7, 0.8], 0.1, evidence_overlap=0.1)
    assert conf_high_overlap > conf_low_overlap, "Higher evidence overlap should yield higher confidence"
