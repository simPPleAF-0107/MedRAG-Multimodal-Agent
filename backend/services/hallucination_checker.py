import logging

logger = logging.getLogger(__name__)

class HallucinationChecker:
    @staticmethod
    def detect_hallucination(response: str, retrieved_context: str) -> tuple:
        """
        Calculates hallucination score and flags by comparing response to retrieved context.
        Returns: hallucination_score (float), hallucination_flags (list)
        """
        logger.info("Running hallucination checker...")
        try:
            # Placeholder for actual LLM/NLI based hallucination check
            if not retrieved_context or len(retrieved_context.strip()) == 0:
                return 1.0, ["No context provided, high risk of hallucination."]
            
            # Simulated logic
            score = 0.1
            flags = []
            if "unknown" in response.lower() and "unknown" not in retrieved_context.lower():
                score += 0.3
                flags.append("Warning: 'unknown' mentioned in response but not in context.")
            
            return min(score, 1.0), flags
        except Exception as e:
            logger.error(f"Hallucination checker failed: {e}")
            return 0.0, [f"Error during check: {str(e)}"]

# Alias for external calling if function is imported directly
def detect_hallucination(response, retrieved_context):
    return HallucinationChecker.detect_hallucination(response, retrieved_context)
