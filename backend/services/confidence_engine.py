import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)

# ── Medical stopwords that should not count as "medical terms" ──────────────
_MEDICAL_STOPWORDS = frozenset([
    "patient", "present", "history", "report", "study", "treatment",
    "diagnosis", "clinical", "medical", "condition", "disease", "findings",
    "symptoms", "recommend", "evidence", "assessment", "analysis",
    "management", "evaluation", "examination", "results", "normal",
    "review", "noted", "suggest", "include", "associated", "common",
    "often", "typically", "usually", "known", "cases", "significant",
    "increased", "decreased", "chronic", "acute", "severe", "mild",
])

# General English stopwords
_ENGLISH_STOPS = frozenset([
    "the", "a", "an", "is", "are", "was", "were", "with", "and", "or",
    "of", "in", "to", "for", "at", "by", "from", "on", "it", "this",
    "that", "be", "as", "may", "can", "has", "have", "had", "not", "but",
    "will", "been", "its", "also", "more", "than", "such", "other",
    "should", "would", "could", "into", "most", "some", "there", "these",
    "those", "which", "about", "between", "through", "after", "before",
    "each", "when", "where", "very", "just", "over", "only", "both",
])


def extract_medical_terms(text: str, min_length: int = 4) -> set:
    """
    Extract candidate medical terms from text.
    Filters out common English words and generic medical stopwords,
    keeping domain-specific clinical vocabulary.
    """
    if not text:
        return set()
    words = re.findall(r'[a-z]+', text.lower())
    return {
        w for w in words
        if len(w) >= min_length
        and w not in _ENGLISH_STOPS
        and w not in _MEDICAL_STOPWORDS
    }


def evidence_overlap_score(diagnosis: str, evidence: str) -> float:
    """
    Deterministic evidence-grounding score.

    Computes the fraction of medical terms in the *diagnosis* that also
    appear anywhere in the *retrieved evidence*.

    Returns a float in [0.0, 1.0]:
        1.0 = every medical term in the diagnosis appears in the evidence
        0.0 = no overlap at all

    This supplements the LLM-based hallucination checker with a
    fast, reproducible, noise-free baseline.
    """
    diag_terms = extract_medical_terms(diagnosis)
    if not diag_terms:
        return 0.5  # No meaningful terms → neutral score

    evidence_terms = extract_medical_terms(evidence)
    if not evidence_terms:
        return 0.0  # No evidence at all → no grounding possible

    overlap = diag_terms & evidence_terms
    score = len(overlap) / len(diag_terms)

    logger.debug(
        f"Evidence overlap: {len(overlap)}/{len(diag_terms)} terms matched "
        f"({score:.2%}) — matched: {list(overlap)[:10]}"
    )
    return round(score, 4)


class ConfidenceEngine:
    @staticmethod
    def calculate_confidence(
        retrieval_scores: list,
        hallucination_score: float,
        verification_passed: bool = False,
        evidence_overlap: float = None,
    ) -> float:
        """
        Calculates a calibrated confidence score (0.0 – 95.0) based on:
        1. Evidence quality (retrieval relevance scores from LLM reranker)
        2. Evidence coverage (number of unique sources)
        3. Hallucination assessment (LLM-graded)
        4. Evidence overlap (deterministic term-matching — NEW)
        5. LLM reasoning baseline
        6. Verification bonus (self-verify loop)

        Tuning philosophy:
        - Lower baseline (58) makes evidence quality matter more
        - Steeper hallucination penalties to discourage unsupported claims
        - Evidence overlap provides a deterministic grounding signal
        - Max capped at 95 — no AI system should claim 100% confidence
        """
        logger.info(
            f"Confidence engine: scores={retrieval_scores}, "
            f"hallucination={hallucination_score:.2f}, "
            f"verified={verification_passed}, "
            f"evidence_overlap={evidence_overlap}"
        )
        try:
            if not retrieval_scores or all(s == 0 for s in retrieval_scores):
                retrieval_scores = [0.5]

            # 1. Average retrieval relevance (0-1 from LLM reranker)
            avg_retrieval = sum(retrieval_scores) / len(retrieval_scores)

            # 2. Evidence coverage (more sources = better)
            num_sources = len([s for s in retrieval_scores if s > 0.01])

            # 3. LLM Reasoning Baseline — lowered to make evidence matter more
            llm_baseline = 58

            # 4. Evidence boost: Good retrieval adds confidence ON TOP of baseline
            if avg_retrieval > 0.7:
                evidence_boost = 25   # Excellent evidence match
            elif avg_retrieval > 0.5:
                evidence_boost = 20   # Strong evidence match
            elif avg_retrieval > 0.3:
                evidence_boost = 14   # Moderate evidence
            elif avg_retrieval > 0.1:
                evidence_boost = 7    # Some relevant evidence
            else:
                evidence_boost = 2    # Minimal/no relevant evidence

            # 5. Coverage bonus (more sources → higher confidence, up to +10)
            coverage_bonus = min(num_sources * 0.85, 10)

            # 6. Hallucination adjustment — steeper penalties
            if hallucination_score <= 0.08:
                hall_adj = 10    # Near-zero hallucination = strong bonus
            elif hallucination_score <= 0.15:
                hall_adj = 7     # Very low hallucination
            elif hallucination_score <= 0.25:
                hall_adj = 3     # Low hallucination
            elif hallucination_score <= 0.35:
                hall_adj = 0     # Moderate = neutral
            elif hallucination_score <= 0.5:
                hall_adj = -10   # Moderate-high = meaningful penalty
            else:
                hall_adj = -25   # High hallucination = severe penalty

            # 7. Evidence overlap bonus (deterministic grounding signal — NEW)
            overlap_bonus = 0
            if evidence_overlap is not None:
                if evidence_overlap >= 0.6:
                    overlap_bonus = 6    # Strong term overlap with evidence
                elif evidence_overlap >= 0.4:
                    overlap_bonus = 3    # Moderate overlap
                elif evidence_overlap >= 0.2:
                    overlap_bonus = 1    # Some overlap
                else:
                    overlap_bonus = -3   # Diagnosis terms barely appear in evidence

            # 8. Verification bonus — self-verify loop passed
            verify_bonus = 8 if verification_passed else 0

            final_score = (
                llm_baseline
                + evidence_boost
                + coverage_bonus
                + hall_adj
                + overlap_bonus
                + verify_bonus
            )

            # Clamp: minimum 25% (LLM always provides some value), maximum 95%
            final_score = max(25.0, min(95.0, final_score))

            logger.info(
                f"Confidence: baseline={llm_baseline} + evidence_boost={evidence_boost} "
                f"(avg_ret={avg_retrieval:.2f}) + coverage={coverage_bonus:.1f} "
                f"+ hall_adj={hall_adj} + overlap={overlap_bonus} "
                f"+ verify={verify_bonus} = {final_score:.1f}%"
            )
            return round(final_score, 2)
        except Exception as e:
            logger.error(f"Confidence engine failed: {e}")
            return 50.0


def calculate_confidence(
    retrieval_scores,
    hallucination_score,
    verification_passed=False,
    evidence_overlap=None,
):
    return ConfidenceEngine.calculate_confidence(
        retrieval_scores, hallucination_score, verification_passed, evidence_overlap
    )
