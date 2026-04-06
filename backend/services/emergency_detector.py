import logging

logger = logging.getLogger(__name__)

class EmergencyDetector:
    @staticmethod
    def detect_emergency(symptoms: str, diagnosis: str) -> tuple:
        """
        Returns: emergency_flag (bool), emergency_level (str)
        """
        logger.info("Running emergency detector...")
        try:
            text_to_check = f"{symptoms} {diagnosis}".lower()
            critical_keywords = ['myocardial', 'stroke', 'hemorrhage', 'sepsis', 'anaphylaxis', 'suicidal', 'chest pain', 'numbness']
            urgent_keywords = ['severe pain', 'fever > 103', 'shortness of breath', 'chest pain']
            
            for word in critical_keywords:
                if word in text_to_check:
                    return True, "Critical"
                    
            for word in urgent_keywords:
                if word in text_to_check:
                    return True, "Urgent"
                    
            return False, "None"
        except Exception as e:
            logger.error(f"Emergency detector failed: {e}")
            return False, "Unknown"

def detect_emergency(symptoms, diagnosis):
    return EmergencyDetector.detect_emergency(symptoms, diagnosis)
