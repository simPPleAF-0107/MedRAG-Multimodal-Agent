"""
Wave 3: Dedicated Symptom Extraction Service
==============================================
Medical NER using regex patterns + a curated medical dictionary.
Maps extracted symptoms → canonical terms (e.g., "chest hurts" → "chest pain").
Returns structured symptom list with body region mapping.

No ML model needed — fast, deterministic, and accurate for prototype scope.
"""
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ── Canonical symptom dictionary ──────────────────────────────────────────────
# Maps variations → canonical medical term
SYMPTOM_SYNONYMS = {
    # Pain variants
    "chest hurts": "chest pain", "chest tightness": "chest pain",
    "heart hurts": "chest pain", "chest ache": "chest pain",
    "tummy ache": "abdominal pain", "stomach ache": "abdominal pain",
    "stomach hurts": "abdominal pain", "belly pain": "abdominal pain",
    "head hurts": "headache", "head pounding": "headache",
    "migraine": "headache", "head ache": "headache",
    "back hurts": "back pain", "lower back pain": "back pain",
    "backache": "back pain", "lumbago": "back pain",
    "sore throat": "sore throat", "throat hurts": "sore throat",
    "throat pain": "sore throat",
    "joint ache": "joint pain", "joints hurt": "joint pain",
    "achy joints": "joint pain",
    "muscle ache": "muscle pain", "muscles hurt": "muscle pain",
    "body ache": "muscle pain", "body aches": "muscle pain",

    # Breathing
    "can't breathe": "shortness of breath", "hard to breathe": "shortness of breath",
    "breathing difficulty": "shortness of breath", "breathless": "shortness of breath",
    "out of breath": "shortness of breath", "trouble breathing": "shortness of breath",
    "gasping": "shortness of breath", "dyspnea": "shortness of breath",
    "wheezy": "wheezing",

    # GI symptoms
    "throwing up": "vomiting", "puking": "vomiting", "emesis": "vomiting",
    "feel sick": "nausea", "queasy": "nausea", "feeling nauseous": "nausea",
    "loose stools": "diarrhea", "watery stool": "diarrhea",
    "can't poop": "constipation", "difficulty swallowing": "dysphagia",

    # General
    "feel tired": "fatigue", "exhausted": "fatigue", "no energy": "fatigue",
    "lethargic": "fatigue", "malaise": "fatigue",
    "feel dizzy": "dizziness", "lightheaded": "dizziness",
    "room spinning": "vertigo",
    "can't sleep": "insomnia", "trouble sleeping": "insomnia",
    "feel anxious": "anxiety", "feel depressed": "depression",
    "feel sad": "depression", "low mood": "depression",
    "weight loss": "weight loss", "losing weight": "weight loss",
    "weight gain": "weight gain", "gaining weight": "weight gain",
    "heart racing": "palpitations", "heart pounding": "palpitations",
    "fast heartbeat": "palpitations", "tachycardia": "palpitations",
    "passed out": "syncope", "fainted": "syncope", "blacked out": "syncope",
    "seizure": "seizure", "convulsion": "seizure", "fits": "seizure",
    "shaking": "tremor", "trembling": "tremor",
    "blurry vision": "blurred vision", "vision blurry": "blurred vision",
    "double vision": "diplopia",
    "blood in urine": "hematuria", "peeing blood": "hematuria",
    "blood in stool": "rectal bleeding", "bloody stool": "rectal bleeding",
    "coughing blood": "hemoptysis", "blood in sputum": "hemoptysis",
    "swollen": "swelling", "puffy": "swelling",
    "skin rash": "rash", "itchy skin": "itching", "itching": "itching",
    "pins and needles": "tingling", "numbness": "numbness",
    "nose bleed": "epistaxis", "nosebleed": "epistaxis",
    "ear pain": "otalgia", "earache": "otalgia",
    "night sweats": "night sweats", "sweating at night": "night sweats",
    "excessive thirst": "polydipsia", "very thirsty": "polydipsia",
    "frequent urination": "polyuria", "peeing a lot": "polyuria",
    "excessive hunger": "polyphagia", "always hungry": "polyphagia",
    "yellow skin": "jaundice", "yellowing": "jaundice",
    "memory loss": "memory loss", "forgetful": "memory loss",
    "confusion": "confusion", "confused": "confusion", "disoriented": "confusion",
    "high temperature": "fever", "temperature": "fever",
}

# ── Canonical symptom list (the targets) ──────────────────────────────────────
CANONICAL_SYMPTOMS = sorted(set(SYMPTOM_SYNONYMS.values()) | {
    "chest pain", "abdominal pain", "back pain", "headache", "fever",
    "cough", "shortness of breath", "dyspnea", "nausea", "vomiting",
    "diarrhea", "constipation", "fatigue", "weakness", "dizziness",
    "swelling", "edema", "rash", "itching", "numbness", "tingling",
    "bleeding", "bruising", "weight loss", "weight gain", "night sweats",
    "palpitations", "syncope", "seizure", "tremor", "blurred vision",
    "joint pain", "muscle pain", "sore throat", "dysphagia",
    "urinary frequency", "hematuria", "jaundice", "confusion",
    "memory loss", "insomnia", "anxiety", "depression",
    "wheezing", "stridor", "hemoptysis", "tinnitus", "vertigo",
    "polyuria", "polydipsia", "polyphagia", "pallor", "cyanosis",
    "epistaxis", "otalgia", "rectal bleeding", "diplopia",
})

# ── Body region mapping ───────────────────────────────────────────────────────
SYMPTOM_BODY_REGION = {
    "chest pain": "Chest", "shortness of breath": "Chest", "palpitations": "Chest",
    "wheezing": "Chest", "hemoptysis": "Chest", "cough": "Chest",
    "headache": "Head", "dizziness": "Head", "vertigo": "Head",
    "blurred vision": "Head", "diplopia": "Head", "tinnitus": "Head",
    "confusion": "Head", "memory loss": "Head", "seizure": "Head",
    "sore throat": "Head/Neck", "dysphagia": "Head/Neck",
    "epistaxis": "Head/Neck", "otalgia": "Head/Neck",
    "abdominal pain": "Abdomen", "nausea": "Abdomen", "vomiting": "Abdomen",
    "diarrhea": "Abdomen", "constipation": "Abdomen", "jaundice": "Abdomen",
    "rectal bleeding": "Abdomen",
    "back pain": "Back/Spine", "joint pain": "Musculoskeletal",
    "muscle pain": "Musculoskeletal", "swelling": "Musculoskeletal",
    "numbness": "Neurological", "tingling": "Neurological",
    "tremor": "Neurological", "weakness": "Neurological",
    "hematuria": "Urogenital", "polyuria": "Urogenital",
    "rash": "Skin", "itching": "Skin", "bruising": "Skin",
    "fever": "Systemic", "fatigue": "Systemic", "weight loss": "Systemic",
    "weight gain": "Systemic", "night sweats": "Systemic",
    "pallor": "Systemic", "cyanosis": "Systemic", "edema": "Systemic",
    "anxiety": "Psychiatric", "depression": "Psychiatric",
    "insomnia": "Psychiatric", "syncope": "Cardiovascular",
    "polydipsia": "Endocrine", "polyphagia": "Endocrine",
}


class SymptomExtractor:
    """
    Extracts symptoms from free-text patient queries.
    Returns structured symptom list with canonical terms and body region mapping.
    """

    def extract(self, text: str) -> dict:
        """
        Extract symptoms from patient text.

        Returns:
            {
                "symptoms": ["chest pain", "shortness of breath", ...],
                "body_regions": {"Chest": ["chest pain", ...], ...},
                "canonical_count": 5,
                "raw_text": "original input"
            }
        """
        if not text:
            return {"symptoms": [], "body_regions": {}, "canonical_count": 0, "raw_text": ""}

        text_lower = text.lower()
        found_symptoms = set()

        # Step 1: Check synonym dictionary (catches colloquial language)
        for synonym, canonical in SYMPTOM_SYNONYMS.items():
            if synonym in text_lower:
                found_symptoms.add(canonical)

        # Step 2: Direct canonical symptom matching
        for symptom in CANONICAL_SYMPTOMS:
            if symptom in text_lower:
                found_symptoms.add(symptom)

        # Step 3: Categorize by body region
        body_regions: dict[str, list[str]] = {}
        for symptom in found_symptoms:
            region = SYMPTOM_BODY_REGION.get(symptom, "Other")
            if region not in body_regions:
                body_regions[region] = []
            body_regions[region].append(symptom)

        result = {
            "symptoms": sorted(found_symptoms),
            "body_regions": body_regions,
            "canonical_count": len(found_symptoms),
            "raw_text": text,
        }

        logger.info(
            f"Symptom extraction: {len(found_symptoms)} symptoms across "
            f"{len(body_regions)} body regions from query"
        )

        return result

    def get_specialty_hint(self, extraction_result: dict) -> Optional[str]:
        """
        Suggest a medical specialty based on the dominant body region
        of extracted symptoms.
        """
        regions = extraction_result.get("body_regions", {})
        if not regions:
            return None

        # Find the region with the most symptoms
        dominant_region = max(regions, key=lambda r: len(regions[r]))

        region_to_specialty = {
            "Chest": "Cardiology",
            "Head": "Neurology",
            "Head/Neck": "ENT / Otolaryngology",
            "Abdomen": "Gastroenterology",
            "Back/Spine": "Orthopedics",
            "Musculoskeletal": "Rheumatology",
            "Neurological": "Neurology",
            "Urogenital": "Urology",
            "Skin": "Dermatology",
            "Systemic": None,  # Too general
            "Psychiatric": "Psychiatry",
            "Cardiovascular": "Cardiology",
            "Endocrine": "Endocrinology",
        }

        return region_to_specialty.get(dominant_region)


# Singleton
symptom_extractor = SymptomExtractor()
