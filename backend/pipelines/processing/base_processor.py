"""
Shared utilities for all data processing pipelines.
Provides standardized schema, medical filtering, specialty detection, and deduplication.
"""
import json
import hashlib
import re
import os
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger(__name__)

# ── Project root paths ────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


# ── Standardized entry schema ────────────────────────────────────────────────
@dataclass
class StandardizedEntry:
    """
    Universal schema all processed data must follow.
    This is the common format that seeding scripts consume.
    """
    text: str
    source: str                      # e.g. "pubmedqa", "medqa", "snomed", "mtsamples"
    type: str                        # "diagnostic", "evidence", "clinical_note", "drug", "ontology", "fact_verification"
    specialty: str = "General"       # e.g. "Cardiology", "Neurology"
    metadata: dict = field(default_factory=dict)
    # Optional structured fields (for diagnostic cases)
    disease: Optional[str] = None
    symptoms: Optional[list] = None
    severity: Optional[str] = None
    confidence_weight: float = 0.8

    def to_dict(self) -> dict:
        d = asdict(self)
        # Remove None values to keep JSONL lean
        return {k: v for k, v in d.items() if v is not None}


# ── Medical keyword filter ────────────────────────────────────────────────────
MEDICAL_KEYWORDS = {
    # Symptoms
    "pain", "fever", "cough", "swelling", "rash", "nausea", "vomiting",
    "headache", "bleeding", "fatigue", "weakness", "dizziness", "dyspnea",
    "chest", "abdominal", "shortness of breath", "palpitations", "edema",
    "inflammation", "seizure", "tremor", "numbness", "tingling",
    # Conditions
    "disease", "infection", "syndrome", "disorder", "cancer", "tumor",
    "fracture", "stroke", "infarction", "thrombosis", "embolism",
    "diabetes", "hypertension", "pneumonia", "anemia", "arthritis",
    "asthma", "hepatitis", "cirrhosis", "nephritis", "meningitis",
    # Clinical terms
    "diagnosis", "treatment", "therapy", "prognosis", "pathology",
    "etiology", "clinical", "patient", "symptom", "chronic", "acute",
    "malignant", "benign", "metastasis", "congenital", "hereditary",
    # Anatomy
    "heart", "lung", "liver", "kidney", "brain", "bone", "blood",
    "artery", "vein", "nerve", "muscle", "skin", "stomach", "colon",
    # Procedures
    "surgery", "biopsy", "transplant", "chemotherapy", "radiation",
    "imaging", "ultrasound", "mri", "ct scan", "x-ray", "ecg",
    # Pharmacology
    "drug", "medication", "dose", "adverse", "contraindication",
    "pharmacology", "antibiotic", "insulin", "vaccine",
}

def is_medical(text: str, min_keywords: int = 2) -> bool:
    """Check if text contains enough medical keywords to be relevant."""
    if not text or len(text.split()) < 10:
        return False
    text_lower = text.lower()
    matches = sum(1 for kw in MEDICAL_KEYWORDS if kw in text_lower)
    return matches >= min_keywords


# ── Specialty detection ───────────────────────────────────────────────────────
SPECIALTY_RULES = {
    "Cardiology": ["heart", "cardiac", "cardiovascular", "coronary", "arrhythmia",
                    "hypertension", "atrial", "ventricular", "ecg", "myocardial"],
    "Neurology": ["brain", "neurological", "seizure", "stroke", "migraine",
                   "neuropathy", "cerebral", "dementia", "parkinson", "epilepsy"],
    "Pulmonology": ["lung", "pulmonary", "respiratory", "asthma", "copd",
                     "pneumonia", "bronchial", "pleural", "ventilation"],
    "Gastroenterology": ["stomach", "gastric", "liver", "hepatic", "bowel",
                          "colon", "pancreas", "esophageal", "gi tract", "gerd"],
    "Endocrinology": ["diabetes", "thyroid", "insulin", "hormone", "endocrine",
                       "pituitary", "adrenal", "cortisol", "glucose"],
    "Nephrology": ["kidney", "renal", "dialysis", "nephro", "glomerular",
                    "creatinine", "urinary"],
    "Oncology": ["cancer", "tumor", "neoplasm", "chemotherapy", "carcinoma",
                  "malignant", "metastasis", "oncology", "lymphoma", "leukemia"],
    "Rheumatology": ["arthritis", "rheumatoid", "lupus", "autoimmune", "gout",
                      "fibromyalgia", "inflammation joint"],
    "Dermatology": ["skin", "rash", "dermatitis", "eczema", "psoriasis",
                     "melanoma", "lesion cutaneous", "acne"],
    "Ophthalmology": ["eye", "vision", "retina", "glaucoma", "cataract",
                       "optic", "ocular", "macular"],
    "Orthopedics": ["bone", "fracture", "joint", "spine", "orthopedic",
                     "osteoporosis", "disc", "ligament", "tendon"],
    "Psychiatry": ["depression", "anxiety", "psychiatric", "bipolar",
                    "schizophrenia", "mental health", "psychosis", "ptsd"],
    "Infectious Disease": ["infection", "bacterial", "viral", "antibiotic",
                            "sepsis", "tuberculosis", "hiv", "malaria"],
    "Pediatrics": ["child", "pediatric", "infant", "neonatal", "newborn",
                    "vaccination", "congenital"],
    "Obstetrics": ["pregnancy", "prenatal", "fetal", "labor", "delivery",
                    "gestational", "obstetric", "maternal"],
    "Emergency Medicine": ["emergency", "trauma", "resuscitation", "shock",
                            "anaphylaxis", "acute care", "triage"],
    "Urology": ["urinary", "bladder", "prostate", "kidney stone", "urological"],
    "Hematology": ["blood", "anemia", "platelet", "coagulation", "hemoglobin",
                    "transfusion", "thrombocytopenia"],
}

def detect_specialty(text: str) -> str:
    """Map text content to a medical specialty using keyword matching."""
    if not text:
        return "General"
    text_lower = text.lower()
    best_spec = "General"
    best_score = 0
    for spec, keywords in SPECIALTY_RULES.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > best_score:
            best_score = score
            best_spec = spec
    return best_spec if best_score >= 2 else "General"


# ── Symptom extraction ────────────────────────────────────────────────────────
SYMPTOM_PATTERNS = [
    "chest pain", "abdominal pain", "back pain", "headache", "fever",
    "cough", "shortness of breath", "dyspnea", "nausea", "vomiting",
    "diarrhea", "constipation", "fatigue", "weakness", "dizziness",
    "swelling", "edema", "rash", "itching", "numbness", "tingling",
    "bleeding", "bruising", "weight loss", "weight gain", "night sweats",
    "palpitations", "syncope", "seizure", "tremor", "blurred vision",
    "joint pain", "muscle pain", "sore throat", "difficulty swallowing",
    "urinary frequency", "hematuria", "jaundice", "confusion",
    "memory loss", "insomnia", "anxiety", "depression",
    "wheezing", "stridor", "hemoptysis", "tinnitus", "vertigo",
    "polyuria", "polydipsia", "polyphagia", "pallor", "cyanosis",
]

def extract_symptoms(text: str) -> list:
    """Extract symptom mentions from text using pattern matching."""
    if not text:
        return []
    text_lower = text.lower()
    found = []
    for symptom in SYMPTOM_PATTERNS:
        if symptom in text_lower:
            found.append(symptom)
    return found


# ── Severity detection ────────────────────────────────────────────────────────
def detect_severity(text: str) -> str:
    """Estimate severity level from text content."""
    if not text:
        return "moderate"
    text_lower = text.lower()
    high_markers = ["emergency", "critical", "severe", "life-threatening",
                     "acute", "fatal", "lethal", "malignant", "unstable"]
    low_markers = ["mild", "benign", "self-limiting", "minor", "routine",
                    "chronic stable", "subclinical"]
    high = sum(1 for m in high_markers if m in text_lower)
    low = sum(1 for m in low_markers if m in text_lower)
    if high >= 2:
        return "high"
    elif low >= 2:
        return "low"
    return "moderate"


# ── Deduplication ─────────────────────────────────────────────────────────────
def deduplicate_entries(entries: list[dict]) -> list[dict]:
    """Remove exact and near-duplicate entries based on text hash."""
    seen_hashes = set()
    unique = []
    for entry in entries:
        text = entry.get("text", "").strip()
        if not text:
            continue
        # Normalize whitespace for hash
        normalized = re.sub(r'\s+', ' ', text.lower())
        text_hash = hashlib.md5(normalized.encode()).hexdigest()
        if text_hash not in seen_hashes:
            seen_hashes.add(text_hash)
            unique.append(entry)
    removed = len(entries) - len(unique)
    if removed:
        logger.info(f"Deduplication: {len(entries)} → {len(unique)} ({removed} duplicates removed)")
    return unique


# ── I/O helpers ───────────────────────────────────────────────────────────────
def save_processed(entries: list[dict], output_filename: str, append: bool = False) -> str:
    """Save processed entries as JSONL to data/processed/."""
    output_path = os.path.join(PROCESSED_DATA_DIR, output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    mode = 'a' if append else 'w'
    with open(output_path, mode, encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    logger.info(f"Saved {len(entries)} entries to {output_path}")
    print(f"  💾 Saved {len(entries)} entries → {output_filename}")
    return output_path


def load_processed(filename: str) -> list[dict]:
    """Load processed JSONL from data/processed/."""
    filepath = os.path.join(PROCESSED_DATA_DIR, filename)
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return []
    entries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def count_entries_in_file(filepath: str) -> int:
    """Count lines in a JSONL file without loading it all."""
    count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        for _ in f:
            count += 1
    return count
