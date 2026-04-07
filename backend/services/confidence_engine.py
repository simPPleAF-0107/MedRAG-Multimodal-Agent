import logging

logger = logging.getLogger(__name__)

class ConfidenceEngine:
    @staticmethod
    def calculate_confidence(retrieval_scores: list, hallucination_score: float) -> float:
        """
        Calculates a calibrated confidence score (0.0 - 95.0) based on:
        1. Evidence quality (retrieval relevance scores)
        2. Evidence coverage (number of sources)
        3. Hallucination assessment
        4. LLM reasoning baseline (LLMs have inherent medical knowledge)
        
        Key insight: Even with low retrieval relevance, the LLM uses its own
        medical training to produce accurate diagnoses. The confidence should
        reflect BOTH evidence quality AND the LLM's reasoning capability.
        
        Max capped at 95% — no AI system should claim 100% medical confidence.
        """
        logger.info(f"Confidence engine: scores={retrieval_scores}, hallucination={hallucination_score:.2f}")
        try:
            if not retrieval_scores or all(s == 0 for s in retrieval_scores):
                retrieval_scores = [0.5]
            
            # 1. Average retrieval relevance (0-1 from LLM reranker)
            avg_retrieval = sum(retrieval_scores) / len(retrieval_scores)
            
            # 2. Evidence coverage (more sources = better)
            num_sources = len([s for s in retrieval_scores if s > 0.01])
            
            # 3. LLM Reasoning Baseline
            # Even with zero retrieval, the LLM has medical knowledge (GPT-4 level).
            # This baseline represents the inherent reliability of LLM medical reasoning.
            llm_baseline = 55  # Base confidence from LLM's own training
            
            # 4. Evidence boost: Good retrieval adds confidence ON TOP of baseline
            if avg_retrieval > 0.6:
                evidence_boost = 25  # Highly relevant evidence found
            elif avg_retrieval > 0.3:
                evidence_boost = 15  # Moderately relevant evidence
            elif avg_retrieval > 0.1:
                evidence_boost = 8   # Some relevant evidence
            else:
                evidence_boost = 3   # Minimal/no relevant evidence
            
            # 5. Coverage bonus
            coverage_bonus = min(num_sources * 1.0, 5)  # Up to +5
            
            # 6. Hallucination adjustment
            if hallucination_score <= 0.3:
                hall_adj = 5    # Low hallucination = bonus
            elif hallucination_score <= 0.5:
                hall_adj = 0    # Moderate = neutral
            elif hallucination_score <= 0.7:
                hall_adj = -5   # Moderate-high = small penalty
            else:
                hall_adj = -12  # High = larger penalty
            
            final_score = llm_baseline + evidence_boost + coverage_bonus + hall_adj
            
            # Clamp: minimum 30% (LLM always provides some value), maximum 95%
            final_score = max(30.0, min(95.0, final_score))
            
            logger.info(
                f"Confidence: baseline={llm_baseline} + evidence_boost={evidence_boost} "
                f"(avg_ret={avg_retrieval:.2f}) + coverage={coverage_bonus:.1f} "
                f"+ hall_adj={hall_adj} = {final_score:.1f}%"
            )
            return round(final_score, 2)
        except Exception as e:
            logger.error(f"Confidence engine failed: {e}")
            return 50.0

def calculate_confidence(retrieval_scores, hallucination_score):
    return ConfidenceEngine.calculate_confidence(retrieval_scores, hallucination_score)
