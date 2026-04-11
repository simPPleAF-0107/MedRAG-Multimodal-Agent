import logging
import json
import re
from backend.llm.openai_client import openai_client
from backend.llm.prompt_templates import DIFFERENTIAL_DIAGNOSIS_PROMPT

logger = logging.getLogger(__name__)

class DifferentialDiagnosis:
    @staticmethod
    def _extract_json_array(text: str) -> list | None:
        """
        Robustly extract a JSON array from LLM output that may contain:
        - Markdown fences: ```json ... ```
        - Plain JSON arrays: [...]
        - JSON wrapped in prose text
        """
        # Strip markdown fences first
        text = re.sub(r'```(?:json)?\s*', '', text).strip()
        text = re.sub(r'```', '', text).strip()

        # Try direct parse first (cleanest case)
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                # Sometimes LLM wraps array in {"diagnoses": [...]} or similar
                for v in parsed.values():
                    if isinstance(v, list):
                        return v
        except json.JSONDecodeError:
            pass

        # Regex: find the first [...] block (DOTALL for multiline)
        match = re.search(r'\[[\s\S]*?\]', text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    @staticmethod
    async def generate_differential(context: str) -> list:
        """
        Returns: top_possible_diagnoses (list of dicts with 'condition' and 'probability')
        """
        logger.info("Running differential diagnosis engine via OpenAI...")

        # Limit context sent to differential engine to avoid token blowout
        prompt = DIFFERENTIAL_DIAGNOSIS_PROMPT.format(
            symptoms="Extracted from context",
            history=context[:2000]  # Cap context for this lightweight call
        )

        try:
            response = await openai_client.generate_completion(
                prompt=prompt,
                system_prompt=(
                    "You are an expert diagnostician. "
                    "Output ONLY a valid JSON array. Each element must be an object with exactly two keys: "
                    "'condition' (string) and 'probability' (float 0.0–1.0). "
                    "Example: [{\"condition\": \"Appendicitis\", \"probability\": 0.72}]. "
                    "No markdown, no prose, no explanation — just the JSON array."
                ),
                temperature=0.0,   # Deterministic — prevents creative formatting
                max_tokens=400,
                use_cache=False    # Always fresh for clinical context
            )

            differentials = DifferentialDiagnosis._extract_json_array(response)
            if differentials and isinstance(differentials, list) and len(differentials) > 0:
                # Validate and normalise each entry
                cleaned = []
                for item in differentials:
                    if isinstance(item, dict) and "condition" in item:
                        prob = float(item.get("probability", 0.5))
                        cleaned.append({
                            "condition": str(item["condition"]),
                            "probability": max(0.0, min(1.0, prob))
                        })
                if cleaned:
                    logger.info(f"Differential diagnosis: {len(cleaned)} conditions parsed successfully.")
                    return cleaned

            logger.warning("Differential diagnosis: JSON parse succeeded but list was empty or malformed.")

        except Exception as e:
            logger.warning(f"Differential diagnosis LLM failed (fallback to mock): {e}")

        # Structured fallback — NOT random placeholder text
        return [
            {"condition": "Awaiting complete clinical evaluation", "probability": 0.50},
            {"condition": "Further investigation required", "probability": 0.30},
            {"condition": "Rule out secondary conditions", "probability": 0.20},
        ]


async def generate_differential(context):
    return await DifferentialDiagnosis.generate_differential(context)
