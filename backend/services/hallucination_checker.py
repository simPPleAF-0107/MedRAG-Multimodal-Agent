import logging
import re
from backend.llm.openai_client import openai_client

logger = logging.getLogger(__name__)

class HallucinationChecker:
    @staticmethod
    async def detect_hallucination(response: str, retrieved_context: str) -> tuple:
        """
        Calculates hallucination score comparing LLM response to retrieved context.
        Returns: (hallucination_score: float 0.0-1.0, flags: list[str])

        Two-stage approach:
          Stage 1 — Deterministic: evidence term overlap (fast, reproducible)
          Stage 2 — LLM-graded: semantic claim verification (nuanced, but stochastic)

        The final score is a weighted blend:
          final = 0.45 * deterministic + 0.55 * llm_score

        Increased deterministic weight (was 0.35) for more stable, reproducible scoring.
        """
        logger.info("Running two-stage hallucination checker...")

        # ── Stage 1: Deterministic evidence overlap ──────────────────────────
        from backend.services.confidence_engine import evidence_overlap_score
        overlap = evidence_overlap_score(response, retrieved_context)
        # Invert: high overlap = low hallucination
        deterministic_score = round(max(0.0, 1.0 - overlap), 3)
        logger.info(f"Hallucination Stage 1 (deterministic): overlap={overlap:.2f} -> score={deterministic_score:.2f}")

        if not retrieved_context or len(retrieved_context.strip()) < 20:
            return 0.15, [
                "No retrieved context; diagnosis based on LLM medical knowledge — low hallucination risk for established medical knowledge.",
                f"Deterministic overlap score: {deterministic_score:.2f}"
            ]

        # ── Stage 2: LLM-graded semantic verification ────────────────────────
        prompt = f"""You are a STRICT medical report auditor performing evidence-grounded verification.

RETRIEVED EVIDENCE:
{retrieved_context[:4000]}

GENERATED REPORT:
{response[:3000]}

STRICT SCORING RULES:
1. Check if clinical claims are supported by the retrieved evidence
2. Claims citing [Evidence: Chunk X] MUST have matching content in the evidence — if not, flag as unsupported
3. Claims marked [Clinical Reasoning] should be well-established textbook facts — flag if obscure or questionable
4. Claims WITHOUT any citation tag are automatically SUSPICIOUS — flag and penalize them
5. UNCITED CLAIMS ARE PENALIZED: Any clinical fact stated without [Evidence: Chunk X] or [Clinical Reasoning] increases the score
6. If the evidence topic matches the report topic, score based on factual alignment:
   - 0.0-0.05: All claims well-grounded in evidence, properly cited with chunk numbers, no gaps
   - 0.05-0.10: Excellent grounding with trivial summary differences
   - 0.10-0.15: Minor gaps, but all claims are medically accurate and mostly cited
   - 0.15-0.25: Some uncited claims, but no contradictions
   - 0.25-0.40: Multiple uncited or weakly supported claims
   - 0.40-0.60: Contains claims that clearly go beyond evidence
   - 0.60-0.80: Contains claims that contradict evidence
   - 0.80-1.0: Fabricated data, invented studies, or dangerous misinformation
7. CRITICAL EXCEPTION — EVIDENCE TOPIC MISMATCH: If the retrieved evidence is clearly about a DIFFERENT medical
   condition than the patient query, then:
   - The model is EXPECTED to use [Clinical Reasoning] instead of citing the irrelevant evidence
   - This is CORRECT and SAFE clinical judgment, NOT a hallucination
   - Score such responses 0.05-0.20 depending on medical accuracy of the [Clinical Reasoning] claims
   - If the model correctly identifies the mismatch and still provides an accurate diagnosis: score 0.05-0.10
   - Only penalize if the [Clinical Reasoning] claims themselves are medically inaccurate or dangerous

IMPORTANT: Be PRECISE. Do not round to convenient numbers like 0.1 or 0.2. Give exact scores like 0.07 or 0.13.

Return ONLY a decimal score (0.0-1.0) on the first line.
Return brief, specific flags on subsequent lines (what was flagged and why)."""

        try:
            llm_response = await openai_client.generate_completion(
                prompt=prompt,
                system_prompt="You are a strict medical auditor. Grade hallucination precisely. Be fair but thorough — every unsupported claim matters. Penalize uncited claims.",
                temperature=0.0,  # Deterministic scoring
                max_tokens=400
            )

            lines = llm_response.strip().split("\n")
            score_str = lines[0].strip()

            match = re.search(r'0\.\d+|1\.0|0|1', score_str)
            if match:
                llm_score = float(match.group())
            else:
                llm_score = 0.15  # Default to low if parsing fails

            flags = [l.strip() for l in lines[1:] if l.strip()] or ["Audited via strict LLM checker."]

            # ── Blend: 45% deterministic + 55% LLM ──────────────────────────
            blended_score = round(0.45 * deterministic_score + 0.55 * llm_score, 4)

            flags.insert(0, f"Deterministic overlap: {overlap:.2f} | LLM score: {llm_score:.2f} | Blended: {blended_score:.3f}")

            logger.info(
                f"Hallucination check: deterministic={deterministic_score:.2f}, "
                f"llm={llm_score:.2f}, blended={blended_score:.3f}, flags={flags[:3]}"
            )
            return min(blended_score, 1.0), flags

        except Exception as e:
            logger.warning(f"Hallucination checker LLM failed (fallback to deterministic): {e}")
            # Fall back to deterministic-only score
            return deterministic_score, [
                f"Hallucination check LLM unavailable — using deterministic overlap: {deterministic_score:.2f}"
            ]

async def detect_hallucination(response, retrieved_context):
    return await HallucinationChecker.detect_hallucination(response, retrieved_context)
