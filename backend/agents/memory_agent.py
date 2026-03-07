class MemoryAgent:
    """
    Agent responsible for maintaining session and longitudinal 
    patient context across multiple interaction turns.
    """
    
    def __init__(self):
        self.name = "Memory Agent"
        self.role = "Compile and synthesize historical patient context."

    async def run(self, input_data: dict) -> dict:
        """
        Extracts relevant long-term memory points from the patient's
        historical reports and log databases.
        """
        patient_history = input_data.get("patient_history", {})
        
        # In a full system, this agent would selectively vector-search past encounters.
        # Here we synthesize the attached relationships.
        
        past_reports = patient_history.get("reports", []) if isinstance(patient_history, dict) else getattr(patient_history, "reports", [])
        
        compiled_history = "No significant prior history."
        if past_reports:
            compiled_history = "Prior Reports Summary: \n"
            for r in past_reports[-3:]: # Take latest 3
                cc = r.get("chief_complaint") if isinstance(r, dict) else r.chief_complaint
                compiled_history += f"- {cc}\n"

        return {
            "historical_context": compiled_history
        }

memory_agent = MemoryAgent()
