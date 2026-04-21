from backend.llm.openai_client import openai_client
from backend.llm.prompt_templates import MEDICAL_ASSISTANT_SYSTEM_PROMPT, DIAGNOSIS_PROMPT_TEMPLATE

class ReasoningAgent:
    """
    Agent responsible for analyzing the retrieved context
    and forming a differential diagnosis and reasoning track.
    
    Tuned for maximum accuracy:
    - temperature=0.05 for deterministic, evidence-grounded reasoning
    - max_tokens=2000 to prevent drifting into unsupported territory
    - Explicit evidence citation via prompt engineering
    """
    
    def __init__(self):
        self.name = "Reasoning Agent"
        self.role = "Analyze evidence and establish a differential diagnosis."

    async def run(self, input_data: dict) -> dict:
        """
        Executes the reasoning logic.
        input_data expects: {"text_query": str, "text_context": str, "image_context": str}
        """
        text_query = input_data.get("text_query", "")
        text_context = input_data.get("text_context", "")
        image_context = input_data.get("image_context", "")
        
        diagnosis_prompt = DIAGNOSIS_PROMPT_TEMPLATE.format(
            query=text_query,
            text_context=text_context,
            image_context=image_context
        )
        
        diagnosis_reasoning = await openai_client.generate_completion(
            prompt=diagnosis_prompt,
            system_prompt=MEDICAL_ASSISTANT_SYSTEM_PROMPT,
            temperature=0.05,  # Near-zero temperature = maximum determinism, minimal hallucination
            max_tokens=2000    # Reduced from 2500 — prevents drifting into unsupported claims
        )
        
        return {
            "diagnosis_reasoning": diagnosis_reasoning
        }

reasoning_agent = ReasoningAgent()
