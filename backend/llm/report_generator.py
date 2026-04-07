import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    @staticmethod
    def format_final_report(data: dict) -> str:
        """
        Formats the final comprehensive medical report including all advanced intelligence metrics.
        Accepts EITHER the raw AgentState dict OR the final_payload dict.
        """
        try:
            report = []
            report.append("=== MEDRAG COMPREHENSIVE MEDICAL REPORT ===")
            report.append(f"Diagnosis: {data.get('diagnosis', 'N/A')}")
            
            report.append("\n--- Differential Diagnosis ---")
            # Support both state key ('differential') and payload key ('differential_diagnosis')
            differentials = data.get('differential_diagnosis', data.get('differential', []))
            if differentials:
                for diff in differentials:
                    if isinstance(diff, dict):
                        condition = diff.get('condition', 'Unknown')
                        prob = diff.get('probability', 0)
                        report.append(f"- {condition}: {prob*100:.0f}%")
                    else:
                        report.append(f"- {diff}")
            else:
                report.append("See diagnosis above for differential analysis.")
                
            report.append(f"\n--- Metrics ---")
            # Support both state keys and payload keys
            confidence = data.get('confidence_score', data.get('confidence', 0))
            hallucination = data.get('hallucination_score', 0)
            risk_score = data.get('risk_score', 0)
            risk_level = data.get('risk_level', data.get('risk_assessment', {}).get('risk_level', 'Unknown'))
            emergency = data.get('emergency_flag', False)
            specialty = data.get('recommended_specialty', 'General')
            
            report.append(f"Confidence Score: {confidence:.1f}%")
            report.append(f"Hallucination Score: {hallucination:.2f}")
            report.append(f"Risk Score: {risk_score}/100 ({risk_level})")
            report.append(f"Emergency Flag: {'⚠️ YES' if emergency else '✅ None'}")
            report.append(f"Recommended Specialty: {specialty}")

            report.append("\n--- Recommendations ---")
            recs = data.get('recommendations', {})
            if isinstance(recs, dict) and recs:
                meal = recs.get('meal_plan', 'N/A')
                activity = recs.get('activity_plan', 'N/A')
                report.append(f"Meal Plan: {meal}")
                report.append(f"Activity Plan: {activity}")
            else:
                report.append("Follow up with your specialist for personalized recommendations.")

            report.append("\n--- Retrieved Evidence ---")
            # Support both state key ('evidence_text') and payload key ('evidence')
            evidence = data.get('evidence', data.get('evidence_text', ''))
            if evidence and len(str(evidence).strip()) > 10:
                evidence_str = str(evidence)[:800]
                report.append(evidence_str)
            else:
                report.append("Diagnosis based on clinical reasoning and LLM medical knowledge.")

            return "\n".join(report)
        except Exception as e:
            logger.error(f"Report generation formatting failed: {e}")
            return "Error generating formatted report."

report_generator = ReportGenerator()
