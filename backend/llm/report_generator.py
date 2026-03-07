import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    @staticmethod
    def format_final_report(data: dict) -> str:
        """
        Formats the final comprehensive medical report including all advanced intelligence metrics.
        """
        try:
            report = []
            report.append("=== MEDRAG COMPREHENSIVE MEDICAL REPORT ===")
            report.append(f"Diagnosis: {data.get('diagnosis', 'N/A')}")
            
            report.append("\n--- Differential Diagnosis ---")
            for diff in data.get('differential_diagnosis', []):
                report.append(f"- {diff.get('condition', 'Unknown')}: {diff.get('probability', 0)*100}%")
                
            report.append(f"\n--- Metrics ---")
            report.append(f"Confidence Score: {data.get('confidence_score', 0)}")
            report.append(f"Hallucination Score: {data.get('hallucination_score', 0)}")
            report.append(f"Risk Score: {data.get('risk_score', 0)}")
            flag = "CRITICAL" if data.get('emergency_flag') else "None"
            report.append(f"Emergency Flag: {flag}")

            report.append("\n--- Recommendations ---")
            recs = data.get('recommendations', {})
            report.append(f"Meal Plan: {recs.get('meal_plan', 'N/A')}")
            report.append(f"Activity Plan: {recs.get('activity_plan', 'N/A')}")

            report.append("\n--- Evidence ---")
            report.append(str(data.get('evidence', 'No evidence provided.'))[:500] + "...")

            return "\n".join(report)
        except Exception as e:
            logger.error(f"Report generation formatting failed: {e}")
            return "Error generating formatted report."

report_generator = ReportGenerator()
