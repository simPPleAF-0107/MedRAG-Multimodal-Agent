"""
Wave 2: Build Structured Diagnostic Cases
==========================================
Reads already-processed JSONL files (from Wave 1) and builds highly structured
symptom→disease diagnostic entries that power the primary retrieval layer.

Sources (priority order):
1. MedQA + MedMCQA → extract symptom-disease patterns from MCQ format
2. Clinical Guidelines → structured case extraction
3. PubMedQA → research-backed diagnostic patterns
4. ICD-10 / SNOMED → disease-code-symptom linking

Output: data/processed/diagnostic_cases.jsonl
"""
import os
import json
import uuid
import logging
import re

from .base_processor import (
    PROCESSED_DATA_DIR, load_processed, save_processed,
    detect_specialty, extract_symptoms, detect_severity,
    deduplicate_entries, is_medical
)

logger = logging.getLogger(__name__)


# ── Disease extraction patterns ───────────────────────────────────────────────
DISEASE_PATTERNS = [
    # "diagnosis of X", "diagnosed with X"
    r"(?:diagnosis|diagnosed)\s+(?:of|with)\s+([A-Z][a-z]+(?:\s+[a-z]+){0,4})",
    # "consistent with X"
    r"consistent\s+with\s+([A-Z][a-z]+(?:\s+[a-z]+){0,4})",
    # "The answer is X" (from MCQ datasets)
    r"(?:answer|correct)\s+(?:is|:)\s*([A-Z][a-z]+(?:\s+[a-z]+){0,4})",
    # "most likely X"
    r"most\s+likely\s+(?:diagnosis\s+is\s+)?([A-Z][a-z]+(?:\s+[a-z]+){0,4})",
    # Common disease name patterns (capitalized medical terms)
    r"\b((?:Acute|Chronic|Type\s+[12])\s+[A-Z][a-z]+(?:\s+[a-z]+){0,3})",
]

# Known disease names for direct matching
KNOWN_DISEASES = {
    "myocardial infarction", "heart failure", "atrial fibrillation",
    "pulmonary embolism", "deep vein thrombosis", "aortic dissection",
    "pneumonia", "asthma", "copd", "tuberculosis", "lung cancer",
    "stroke", "transient ischemic attack", "epilepsy", "meningitis",
    "diabetes mellitus", "diabetic ketoacidosis", "hypothyroidism", "hyperthyroidism",
    "acute kidney injury", "chronic kidney disease", "nephrotic syndrome",
    "cirrhosis", "hepatitis", "pancreatitis", "appendicitis", "cholecystitis",
    "rheumatoid arthritis", "systemic lupus erythematosus", "gout",
    "anemia", "leukemia", "lymphoma", "multiple myeloma",
    "melanoma", "breast cancer", "colon cancer", "prostate cancer",
    "urinary tract infection", "pyelonephritis", "benign prostatic hyperplasia",
    "preeclampsia", "gestational diabetes", "ectopic pregnancy",
    "major depressive disorder", "bipolar disorder", "schizophrenia",
    "celiac disease", "crohn disease", "ulcerative colitis",
    "osteoporosis", "osteoarthritis", "herniated disc",
    "glaucoma", "macular degeneration", "retinal detachment",
    "hypertension", "hyperlipidemia", "metabolic syndrome",
    "sepsis", "endocarditis", "osteomyelitis",
    "guillain barre syndrome", "multiple sclerosis", "parkinson disease",
    "addison disease", "cushing syndrome", "pheochromocytoma",
    "sarcoidosis", "amyloidosis", "hemochromatosis",
}


def _extract_disease(text: str) -> str | None:
    """Try to extract a primary disease name from text."""
    text_lower = text.lower()

    # Direct match against known diseases
    for disease in KNOWN_DISEASES:
        if disease in text_lower:
            return disease.title()

    # Regex pattern matching
    for pattern in DISEASE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(1).strip()
            # Filter out garbage matches
            if len(candidate) > 3 and len(candidate.split()) <= 6:
                return candidate

    return None


def _extract_differentials(text: str, primary_disease: str) -> list[str]:
    """Extract differential diagnosis candidates from text."""
    differentials = []
    text_lower = text.lower()
    primary_lower = primary_disease.lower() if primary_disease else ""

    for disease in KNOWN_DISEASES:
        if disease in text_lower and disease != primary_lower:
            differentials.append(disease.title())
            if len(differentials) >= 4:
                break

    return differentials


def build_from_medqa() -> list[dict]:
    """Build diagnostic cases from MedQA processed data."""
    entries = load_processed("medqa_cleaned.jsonl")
    if not entries:
        logger.warning("medqa_cleaned.jsonl not found or empty")
        return []

    cases = []
    for entry in entries:
        text = entry.get("text", "")
        if not text or len(text) < 50:
            continue

        disease = _extract_disease(text)
        symptoms = extract_symptoms(text)

        if disease or symptoms:
            case = {
                "id": str(uuid.uuid4()),
                "text": text,
                "disease": disease or "Unknown",
                "symptoms": symptoms,
                "differentials": _extract_differentials(text, disease) if disease else [],
                "severity": detect_severity(text),
                "specialty": entry.get("specialty", detect_specialty(text)),
                "evidence_text": text[:500],
                "source": "MedQA",
                "type": "diagnostic_case",
                "confidence_weight": 0.95,
            }
            cases.append(case)

    logger.info(f"MedQA: built {len(cases)} diagnostic cases")
    return cases


def build_from_medmcqa() -> list[dict]:
    """Build diagnostic cases from MedMCQA processed data."""
    entries = load_processed("medmcqa_cleaned.jsonl")
    if not entries:
        logger.warning("medmcqa_cleaned.jsonl not found or empty")
        return []

    cases = []
    for entry in entries:
        text = entry.get("text", "")
        if not text or len(text) < 50:
            continue

        disease = _extract_disease(text)
        symptoms = extract_symptoms(text)

        if disease or symptoms:
            case = {
                "id": str(uuid.uuid4()),
                "text": text,
                "disease": disease or "Unknown",
                "symptoms": symptoms,
                "differentials": _extract_differentials(text, disease) if disease else [],
                "severity": detect_severity(text),
                "specialty": entry.get("specialty", detect_specialty(text)),
                "evidence_text": text[:500],
                "source": "MedMCQA",
                "type": "diagnostic_case",
                "confidence_weight": 0.90,
            }
            cases.append(case)

    logger.info(f"MedMCQA: built {len(cases)} diagnostic cases")
    return cases


def build_from_pubmedqa() -> list[dict]:
    """Build research-backed diagnostic patterns from PubMedQA."""
    entries = load_processed("pubmedqa_cleaned.jsonl")
    if not entries:
        logger.warning("pubmedqa_cleaned.jsonl not found or empty")
        return []

    cases = []
    for entry in entries:
        text = entry.get("text", "")
        if not text or len(text) < 100:
            continue

        disease = _extract_disease(text)
        symptoms = extract_symptoms(text)

        # PubMedQA is research-focused, so only include entries with clear disease patterns
        if disease and len(symptoms) >= 1:
            case = {
                "id": str(uuid.uuid4()),
                "text": text,
                "disease": disease,
                "symptoms": symptoms,
                "differentials": _extract_differentials(text, disease),
                "severity": detect_severity(text),
                "specialty": entry.get("specialty", detect_specialty(text)),
                "evidence_text": text[:500],
                "source": "PubMedQA",
                "type": "diagnostic_case",
                "confidence_weight": 0.85,
            }
            cases.append(case)

    logger.info(f"PubMedQA: built {len(cases)} diagnostic cases")
    return cases


def build_from_guidelines() -> list[dict]:
    """Build structured cases from clinical guidelines."""
    entries = load_processed("clinical_guidelines_cleaned.jsonl")
    if not entries:
        logger.warning("clinical_guidelines_cleaned.jsonl not found or empty")
        return []

    cases = []
    for entry in entries:
        text = entry.get("text", "")
        if not text or len(text) < 100:
            continue

        disease = _extract_disease(text)
        symptoms = extract_symptoms(text)

        if disease:
            case = {
                "id": str(uuid.uuid4()),
                "text": text[:1000],  # Guidelines can be very long
                "disease": disease,
                "symptoms": symptoms,
                "differentials": _extract_differentials(text, disease),
                "severity": detect_severity(text),
                "specialty": entry.get("specialty", detect_specialty(text)),
                "evidence_text": text[:500],
                "source": "ClinicalGuidelines",
                "type": "diagnostic_case",
                "confidence_weight": 0.92,
            }
            cases.append(case)

    logger.info(f"Guidelines: built {len(cases)} diagnostic cases")
    return cases


def build_from_ontologies() -> list[dict]:
    """Build disease-code-symptom linking from ICD-10 / SNOMED."""
    cases = []

    for ontology_file in ["icd10_cleaned.jsonl", "snomed_cleaned.jsonl"]:
        entries = load_processed(ontology_file)
        if not entries:
            continue

        source = ontology_file.replace("_cleaned.jsonl", "").upper()
        for entry in entries:
            text = entry.get("text", "")
            disease = entry.get("disease") or _extract_disease(text)
            if not disease:
                continue

            symptoms = extract_symptoms(text)
            case = {
                "id": str(uuid.uuid4()),
                "text": text,
                "disease": disease,
                "symptoms": symptoms,
                "differentials": [],
                "severity": detect_severity(text),
                "specialty": entry.get("specialty", detect_specialty(text)),
                "evidence_text": text[:500],
                "source": source,
                "type": "diagnostic_case",
                "confidence_weight": 0.80,
                "metadata": entry.get("metadata", {}),
            }
            cases.append(case)

        logger.info(f"{source}: built {len(cases)} diagnostic cases")

    return cases


def build_all_diagnostic_cases():
    """Master function: build from all sources, deduplicate, and save."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")

    logger.info("=" * 60)
    logger.info(" BUILDING STRUCTURED DIAGNOSTIC CASES")
    logger.info("=" * 60)

    all_cases = []

    # Priority order: MedQA > MedMCQA > Guidelines > PubMedQA > Ontologies
    all_cases.extend(build_from_medqa())
    all_cases.extend(build_from_medmcqa())
    all_cases.extend(build_from_guidelines())
    all_cases.extend(build_from_pubmedqa())
    all_cases.extend(build_from_ontologies())

    logger.info(f"\nTotal raw cases: {len(all_cases)}")

    # Deduplicate
    all_cases = deduplicate_entries(all_cases)
    logger.info(f"After deduplication: {len(all_cases)}")

    # Save
    save_processed(all_cases, "diagnostic_cases.jsonl")

    # Print stats
    specialties = {}
    diseases_found = 0
    for case in all_cases:
        spec = case.get("specialty", "General")
        specialties[spec] = specialties.get(spec, 0) + 1
        if case.get("disease") and case["disease"] != "Unknown":
            diseases_found += 1

    logger.info(f"\n📊 Diagnostic Cases Summary:")
    logger.info(f"  Total cases: {len(all_cases)}")
    logger.info(f"  With known disease: {diseases_found}")
    logger.info(f"  Specialties: {len(specialties)}")
    for spec, count in sorted(specialties.items(), key=lambda x: x[1], reverse=True)[:10]:
        logger.info(f"    {spec}: {count}")

    return all_cases


if __name__ == "__main__":
    build_all_diagnostic_cases()
