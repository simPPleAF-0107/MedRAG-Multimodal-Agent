from backend.llm.openai_client import openai_client
from backend.llm.prompt_templates import REPORT_PROMPT_TEMPLATE

class ReportAgent:
    """
    Agent responsible for taking validated reasoning and
    formatting it into a structured, professional medical report.
    """
    
    def __init__(self):
        self.name = "Report Agent"
        self.role = "Synthesize diagnosis into a final clinical report."

    async def run(self, input_data: dict) -> dict:
        """
        Executes the report generation logic.
        input_data expects: {"diagnosis_reasoning": str, "verification_passed": bool}
        """
        diagnosis_reasoning = input_data.get("diagnosis_reasoning", "")
        verification_passed = input_data.get("verification_passed", True)
        
        if not verification_passed:
            return {
                "final_report": "Error: Diagnosis failed verification constraints."
            }
            
        report_prompt = REPORT_PROMPT_TEMPLATE.format(
            diagnosis_reasoning=diagnosis_reasoning
        )
        
        final_report = await openai_client.generate_completion(
            prompt=report_prompt,
            system_prompt="You are a medical scribe that formatting clinical reasoning into standard reports.",
            temperature=0.1
        )
        
        return {
            "final_report": final_report
        }

report_agent = ReportAgent()
