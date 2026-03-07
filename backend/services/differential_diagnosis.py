import logging
import json
import re
from backend.llm.openai_client import openai_client
from backend.llm.prompt_templates import DIFFERENTIAL_DIAGNOSIS_PROMPT

logger = logging.getLogger(__name__)

class DifferentialDiagnosis:
    @staticmethod
    async def generate_differential(context: str) -> list:
        """
        Returns: top_possible_diagnoses (list of dicts)
        """
        logger.info("Running differential diagnosis engine via OpenAI...")
        
        prompt = DIFFERENTIAL_DIAGNOSIS_PROMPT.format(
            symptoms="Extracted from context", 
            history=context
        )
        
        try:
            # Use LLM for actual diagnosis processing
            response = await openai_client.generate_completion(
                prompt=prompt,
                system_prompt="You are an expert diagnostician. Output only JSON array where each object has 'condition' and 'probability' (float between 0 and 1). No other text.",
                max_tokens=300
            )
            
            # Use regex to find block of json
            json_match = re.search(r'\[.*\]', response.replace('\n', ''), re.DOTALL)
            if json_match:
                differentials = json.loads(json_match.group(0))
                return differentials
            else:
                # Attempt to parse directly
                differentials = json.loads(response)
                return differentials
                
        except Exception as e:
            logger.warning(f"Differential diagnosis LLM failed (fallback to mock): {e}")
            differentials = [
                {"condition": "Condition A (Based on context)", "probability": 0.65},
                {"condition": "Condition B (Secondary match)", "probability": 0.25},
                {"condition": "Condition C (Unlikely)", "probability": 0.10}
            ]
            return differentials

async def generate_differential(context):
    return await DifferentialDiagnosis.generate_differential(context)

