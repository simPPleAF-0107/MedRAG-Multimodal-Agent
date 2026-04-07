import logging

logger = logging.getLogger(__name__)

class EmergencyDetector:
    """
    Rule-based emergency detector that evaluates symptom severity.
    IMPORTANT: Only scans the PATIENT'S original query, NOT the AI-generated diagnosis
    (which often contains hypothetical red flags like "seek help if difficulty breathing").
    """
    
    CRITICAL_PATTERNS = [
        (["myocardial infarction", "heart attack", "cardiac arrest", "ventricular fibrillation"], "Cardiac Emergency"),
        (["acute stroke", "hemorrhagic stroke", "ischemic stroke", "intracranial hemorrhage"], "Neurological Emergency"),
        (["septic shock", "anaphylactic shock", "anaphylaxis"], "Systemic Emergency"),
        (["suicidal ideation", "suicide attempt", "self-harm", "actively suicidal"], "Psychiatric Emergency"),
        (["respiratory failure", "respiratory arrest", "airway obstruction"], "Respiratory Emergency"),
    ]
    
    URGENT_PATTERNS = [
        (["severe chest pain", "crushing chest pain", "chest tightness"], "Possible Cardiac Event"),
        (["cannot breathe", "can't breathe", "choking"], "Respiratory Distress"),
        (["uncontrolled bleeding", "heavy bleeding", "won't stop bleeding"], "Hemorrhage"),
        (["loss of consciousness", "unconscious", "unresponsive", "passed out", "fainted"], "Altered Consciousness"),
        (["severe allergic reaction", "swelling of throat", "throat closing"], "Allergic Reaction"),
        (["seizure", "convulsion", "status epilepticus"], "Seizure"),
        (["overdose", "poisoning", "ingested"], "Toxic Exposure"),
    ]
    
    @staticmethod
    def detect_emergency(symptoms: str, diagnosis: str) -> tuple:
        """
        Returns: (emergency_flag: bool, emergency_level: str)
        
        ONLY checks the patient's symptoms/query text — NOT the AI diagnosis,
        which often contains hypothetical warnings that would cause false positives.
        """
        logger.info("Running emergency detector...")
        try:
            # Only check patient's own words, NOT the AI-generated diagnosis
            text_to_check = symptoms.lower()
            
            for keywords, label in EmergencyDetector.CRITICAL_PATTERNS:
                for keyword in keywords:
                    if keyword in text_to_check:
                        logger.warning(f"CRITICAL emergency detected: {label} (matched: '{keyword}' in patient query)")
                        return True, "CRITICAL"
            
            for keywords, label in EmergencyDetector.URGENT_PATTERNS:
                for keyword in keywords:
                    if keyword in text_to_check:
                        logger.warning(f"URGENT emergency detected: {label} (matched: '{keyword}' in patient query)")
                        return True, "URGENT"
            
            return False, "NONE"
        except Exception as e:
            logger.error(f"Emergency detector failed: {e}")
            return False, "UNKNOWN"

def detect_emergency(symptoms, diagnosis):
    return EmergencyDetector.detect_emergency(symptoms, diagnosis)
