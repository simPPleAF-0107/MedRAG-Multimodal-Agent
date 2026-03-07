import logging

logger = logging.getLogger(__name__)

class ConfidenceEngine:
    @staticmethod
    def calculate_confidence(retrieval_scores: list, hallucination_score: float) -> float:
        """
        Returns: confidence_score (float 0.0 - 100.0)
        """
        logger.info("Running confidence engine...")
        try:
            avg_retrieval = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0.5
            
            # Simulated confidence math
            # Higher hallucination = lower confidence
            base_score = avg_retrieval * 100
            penalty = hallucination_score * 50
            
            final_score = max(0.0, min(100.0, base_score - penalty))
            return round(final_score, 2)
        except Exception as e:
            logger.error(f"Confidence engine failed: {e}")
            return 0.0

def calculate_confidence(retrieval_scores, hallucination_score):
    return ConfidenceEngine.calculate_confidence(retrieval_scores, hallucination_score)
