import logging

logger = logging.getLogger(__name__)

class RiskEngine:
    @staticmethod
    def calculate_risk(patient_data: dict, diagnosis: str) -> tuple:
        """
        Calculates risk based on patient data and diagnosis.
        Returns: risk_score (int 0-100), risk_level (str)
        """
        logger.info("Running risk engine...")
        try:
            score = 20 # base risk
            
            if diagnosis:
                diagnosis_lower = diagnosis.lower()
                if "cancer" in diagnosis_lower or "infarction" in diagnosis_lower or "failure" in diagnosis_lower:
                    score += 50
                if "acute" in diagnosis_lower or "severe" in diagnosis_lower:
                    score += 20
                    
            if score < 40:
                level = "Low"
            elif score < 70:
                level = "Medium"
            else:
                level = "High"
                
            return min(score, 100), level
        except Exception as e:
            logger.error(f"Risk engine failed: {e}")
            return 0, "Unknown"

def calculate_risk(patient_data, diagnosis):
    return RiskEngine.calculate_risk(patient_data, diagnosis)
