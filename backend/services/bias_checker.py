import logging

logger = logging.getLogger(__name__)

class BiasChecker:
    @staticmethod
    def check_bias(patient_data: dict, diagnosis: str) -> float:
        """
        Returns: bias_score (float 0.0 - 1.0)
        """
        logger.info("Running bias checker...")
        try:
            # Simulated demographic check over diagnostic output
            bias_score = 0.05
            if "gender" in patient_data or "race" in patient_data:
                # Mock evaluation finding mild correlation
                bias_score = 0.12
            return bias_score
        except Exception as e:
            logger.error(f"Bias checker failed: {e}")
            return 1.0

def check_bias(patient_data, diagnosis):
    return BiasChecker.check_bias(patient_data, diagnosis)
