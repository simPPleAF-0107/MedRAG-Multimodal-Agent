from backend.llm.openai_client import openai_client

class VerifierAgent:
    """
    Agent responsible for cross-checking the generated diagnosis
    against the retrieved medical literature and reducing hallucinations.
    """
    
    def __init__(self):
        self.name = "Verifier Agent"
        self.role = "Detect hallucinations and ensure medical safety."

    async def run(self, input_data: dict) -> dict:
        """
        Executes the verification logic.
        input_data expects: {"text_context": str, "image_context": str, "diagnosis_reasoning": str}
        """
        text_context = input_data.get("text_context", "")
        diagnosis_reasoning = input_data.get("diagnosis_reasoning", "")
        
        verification_prompt = f"""
        Please review the following diagnosis reasoning against the provided medical context.
        Identify any facts that contradict the context or seem like unsafe medical hallucinations.

        Context: 
        {text_context}

        Diagnosis Reasoning:
        {diagnosis_reasoning}

        Respond ONLY with 'PASS' if the reasoning is safe and grounded, 
        or provide a short list of corrections if it is not.
        """
        
        verification_result = await openai_client.generate_completion(
            prompt=verification_prompt,
            system_prompt="You are a strict medical validator.",
            temperature=0.0
        )
        
        return {
            "verification_result": verification_result,
            "is_passed": "PASS" in verification_result.upper()
        }

verifier_agent = VerifierAgent()
