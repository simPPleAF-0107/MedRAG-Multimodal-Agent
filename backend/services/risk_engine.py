import logging
from backend.llm.openai_client import openai_client
from backend.llm.prompt_templates import RISK_ANALYSIS_PROMPT
import re

logger = logging.getLogger(__name__)

class RiskEngine:
    @staticmethod
    async def calculate_risk(patient_data: dict, diagnosis: str) -> tuple:
        """
        Calculates risk based on patient data and diagnosis using LLM.
        Returns: risk_score (int 0-100), risk_level (str)
        """
        logger.info("Running risk engine via OpenAI...")
        
        prompt = RISK_ANALYSIS_PROMPT.format(
            patient_data=str(patient_data),
            diagnosis=diagnosis
        )
        
        try:
            # Attempt to use the OpenAI LLM client
            response = await openai_client.generate_completion(
                prompt=prompt,
                system_prompt="You are a clinical risk analysis expert.",
                max_tokens=200
            )
            
            # The prompt asks for a risk score on the first line
            lines = response.strip().split("\n")
            score_str = lines[0].strip()
            # Extract number from the first line
            match = re.search(r'\d+', score_str)
            if match:
                score = int(match.group())
                score = min(max(score, 0), 100)
            else:
                score = 20
        except Exception as e:
            logger.warning(f"Risk engine LLM failed (fallback to rule-based): {e}")
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

async def calculate_risk(patient_data, diagnosis):
    return await RiskEngine.calculate_risk(patient_data, diagnosis)

