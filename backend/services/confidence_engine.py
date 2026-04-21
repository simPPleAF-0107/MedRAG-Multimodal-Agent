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


def symptom_coverage_score(query: str, diagnosis: str) -> tuple[float, int, int]:
    """
    Strict evidence coverage scoring.
    coverage_score = matched_symptoms / total_symptoms

    Extracts medical terms from the query (representing symptoms/patient context)
    and checks if they are addressed/covered in the final diagnosis.
    Returns (coverage_score, matched_count, total_count).
    """
    query_terms = extract_medical_terms(query)
    if not query_terms:
        return 1.0, 0, 0  # No terms to cover

    diag_terms = extract_medical_terms(diagnosis)
    matched = query_terms & diag_terms
    score = len(matched) / len(query_terms)
    
    logger.debug(f"Symptom Coverage: {len(matched)}/{len(query_terms)} ({score:.2%})")
    return round(score, 4), len(matched), len(query_terms)


class ConfidenceEngine:
    @staticmethod
    def calculate_confidence(
        retrieval_scores: list,
        hallucination_score: float,
        verification_passed: bool = False,
        evidence_overlap: float = None,
        evidence_quality: str = None,
        consistency_score: float = None,
        coverage_score: float = None,
        diagnostic_match_score: float = None,
    ) -> float:
        """
        Calculates a CALIBRATED confidence score (0.0 – 95.0) using a
        weighted multiplicative formula instead of arbitrary additive buckets.

        Formula:
            confidence = (
                0.35 × retrieval_score       # avg relevance from reranker
              + 0.30 × verifier_score        # inverse hallucination
              + 0.20 × overlap_score         # deterministic grounding
              + 0.15 × consistency_score     # multi-pass agreement
            ) × 100

        Adjustments:
            - Verification bonus (+5 if self-verify passed)
            - Evidence quality cap (INSUFFICIENT → max 40%)
            - Hard floor at 15%, hard ceiling at 95%

        Philosophy:
            Confidence is EARNED from evidence, not gifted from a baseline.
            No evidence = low confidence. Period.
        """
        logger.info(
            f"Confidence engine: scores={retrieval_scores}, "
            f"hallucination={hallucination_score:.2f}, "
            f"verified={verification_passed}, "
            f"evidence_overlap={evidence_overlap}, "
            f"evidence_quality={evidence_quality}, "
            f"consistency={consistency_score}"
        )
        try:
            if not retrieval_scores or all(s == 0 for s in retrieval_scores):
                retrieval_scores = [0.1]

            # ── Component scores (all normalized to 0.0 - 1.0) ───────────────

            # 1. Retrieval relevance: average score from reranker
            avg_retrieval = sum(retrieval_scores) / len(retrieval_scores)
            avg_retrieval = max(0.0, min(1.0, avg_retrieval))

            # 2. Verifier score: inverse of hallucination (low hallucination = high confidence)
            verifier_score = max(0.0, min(1.0, 1.0 - hallucination_score))

            # 3. Evidence overlap: deterministic term-matching score
            overlap_score = evidence_overlap if evidence_overlap is not None else 0.3

            # 4. Consistency score: multi-pass agreement (defaults to 0.7 if not available)
            consist_score = consistency_score if consistency_score is not None else 0.7

            # 5. Diagnostic match score: symptom→disease pattern match boost
            diag_match = diagnostic_match_score if diagnostic_match_score is not None else 0.5

            # ── Weighted combination ─────────────────────────────────────────
            raw_confidence = (
                0.30 * avg_retrieval
                + 0.25 * verifier_score
                + 0.15 * overlap_score
                + 0.15 * consist_score
                + 0.15 * diag_match
            ) * 100

            # ── Verification bonus ───────────────────────────────────────────
            if verification_passed:
                raw_confidence += 5.0

            # ── Evidence quality cap ─────────────────────────────────────────
            if evidence_quality == "INSUFFICIENT":
                raw_confidence = min(raw_confidence, 40.0)
            elif evidence_quality == "LOW":
                raw_confidence = min(raw_confidence, 65.0)

            # ── Strict Evidence Coverage Penalty ─────────────────────────────
            if coverage_score is not None and coverage_score < 0.70:
                logger.warning(f"Coverage penalty applied: coverage={coverage_score:.2f} < 0.70")
                # Force the confidence below the 75% abstention threshold
                raw_confidence = min(raw_confidence, 68.0)

            # ── Clamp: floor 15%, ceiling 95% ────────────────────────────────
            final_score = max(15.0, min(95.0, raw_confidence))

            logger.info(
                f"Confidence: retrieval={avg_retrieval:.2f}×0.35 + "
                f"verifier={verifier_score:.2f}×0.30 + "
                f"overlap={overlap_score:.2f}×0.20 + "
                f"consistency={consist_score:.2f}×0.15 = "
                f"raw={raw_confidence:.1f} -> final={final_score:.1f}% "
                f"(quality_cap={evidence_quality}, coverage={coverage_score}, verified={verification_passed})"
            )
            return round(final_score, 2)
        except Exception as e:
            logger.error(f"Confidence engine failed: {e}")
            return 30.0  # Conservative fallback instead of 50


def calculate_confidence(
    retrieval_scores,
    hallucination_score,
    verification_passed=False,
    evidence_overlap=None,
    evidence_quality=None,
    consistency_score=None,
    coverage_score=None,
    diagnostic_match_score=None,
):
    return ConfidenceEngine.calculate_confidence(
        retrieval_scores, hallucination_score, verification_passed,
        evidence_overlap, evidence_quality, consistency_score, coverage_score,
        diagnostic_match_score,
    )


def compute_diagnostic_match_score(extracted_symptoms: list[str], evidence_text: str) -> float:
    """
    Compute how well the extracted symptoms match patterns found in the retrieved evidence.
    Returns a float in [0.0, 1.0].
    """
    if not extracted_symptoms:
        return 0.5  # Neutral if no symptoms extracted

    evidence_lower = evidence_text.lower()
    matched = sum(1 for s in extracted_symptoms if s.lower() in evidence_lower)
    score = matched / len(extracted_symptoms)

    logger.debug(f"Diagnostic match: {matched}/{len(extracted_symptoms)} symptoms found in evidence ({score:.2%})")
    return round(score, 4)
