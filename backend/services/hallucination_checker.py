import logging
import re
from backend.llm.openai_client import openai_client
from backend.llm.prompt_templates import HALLUCINATION_CHECK_PROMPT

logger = logging.getLogger(__name__)

class HallucinationChecker:
    @staticmethod
    async def detect_hallucination(response: str, retrieved_context: str) -> tuple:
        """
        Calculates hallucination score and flags by comparing response to retrieved context.
        Returns: hallucination_score (float), hallucination_flags (list)
        """
        logger.info("Running hallucination checker via OpenAI...")
        if not retrieved_context or len(retrieved_context.strip()) == 0:
            return 1.0, ["No context provided, high risk of hallucination."]
                
        prompt = HALLUCINATION_CHECK_PROMPT.format(
            evidence=retrieved_context,
            report=response
        )
        
        try:
            llm_response = await openai_client.generate_completion(
                prompt=prompt,
                system_prompt="You are a clinical hallucination auditor.",
                max_tokens=300
            )
            
            lines = llm_response.strip().split("\n")
            score_str = lines[0].strip()
            
            # Extract float
            match = re.search(r'0\.\d+|1\.0|0|1', score_str)
            if match:
                score = float(match.group())
            else:
                score = 0.1
                
            flags = lines[1:] if len(lines) > 1 else ["Audited via LLM."]
            return min(score, 1.0), flags
            
        except Exception as e:
            logger.warning(f"Hallucination checker LLM failed (fallback to rule-based): {e}")
            score = 0.1
            flags = []
            if "unknown" in response.lower() and "unknown" not in retrieved_context.lower():
                score += 0.3
                flags.append("Warning: 'unknown' mentioned in response but not in context.")
            
            return min(score, 1.0), flags

# Alias for external calling if function is imported directly
async def detect_hallucination(response, retrieved_context):
    return await HallucinationChecker.detect_hallucination(response, retrieved_context)
