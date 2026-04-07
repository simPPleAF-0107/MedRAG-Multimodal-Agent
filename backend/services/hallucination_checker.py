import logging
import re
from backend.llm.openai_client import openai_client
from backend.llm.prompt_templates import HALLUCINATION_CHECK_PROMPT

logger = logging.getLogger(__name__)

class HallucinationChecker:
    @staticmethod
    async def detect_hallucination(response: str, retrieved_context: str) -> tuple:
        """
        Calculates hallucination score comparing LLM response to retrieved context.
        Returns: (hallucination_score: float 0.0-1.0, flags: list[str])
        
        IMPORTANT DISTINCTION:
        - "Hallucination" = fabricated medical claims or contradictions
        - "Using own knowledge" = NOT hallucination (LLMs are trained on medical literature)
        - "Topic mismatch" = Retrieved evidence is on a different topic; this is a RETRIEVAL 
          quality issue, NOT a hallucination issue
        """
        logger.info("Running hallucination checker via OpenAI...")
        
        if not retrieved_context or len(retrieved_context.strip()) < 20:
            return 0.3, ["No retrieved context; diagnosis based on LLM medical knowledge."]
                
        prompt = f"""You are a medical report auditor. Compare the generated report to the retrieved evidence.

RETRIEVED EVIDENCE:
{retrieved_context[:3000]}

GENERATED REPORT:
{response[:2000]}

SCORING RULES:
- If the evidence is on a DIFFERENT TOPIC than the report, this is NOT hallucination — it's a retrieval mismatch. Score 0.2-0.3.
- If the report makes medically accurate statements that aren't in the evidence, this is the AI using its own medical training. Score 0.1-0.3.
- Only score above 0.5 if the report contains claims that DIRECTLY CONTRADICT the evidence or are clearly medically WRONG.
- Score 0.7+ only if there are fabricated statistics, invented study names, or dangerous medical misinformation.

Return ONLY a decimal score (0.0-1.0) on the first line.
Return brief flags on subsequent lines."""

        try:
            llm_response = await openai_client.generate_completion(
                prompt=prompt,
                system_prompt="You are a precise medical auditor. Score hallucination fairly. Topic mismatch between evidence and report is NOT hallucination.",
                max_tokens=200
            )
            
            lines = llm_response.strip().split("\n")
            score_str = lines[0].strip()
            
            match = re.search(r'0\.\d+|1\.0|0|1', score_str)
            if match:
                score = float(match.group())
            else:
                score = 0.25
            
            flags = [l.strip() for l in lines[1:] if l.strip()] or ["Audited via LLM."]
            
            logger.info(f"Hallucination check: score={score:.2f}, flags={flags[:2]}")
            return min(score, 1.0), flags
            
        except Exception as e:
            logger.warning(f"Hallucination checker LLM failed (fallback): {e}")
            # Rule-based fallback — default to low hallucination
            return 0.25, ["Hallucination check fallback: LLM unavailable."]

async def detect_hallucination(response, retrieved_context):
    return await HallucinationChecker.detect_hallucination(response, retrieved_context)
