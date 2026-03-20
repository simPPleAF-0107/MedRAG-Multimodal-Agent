import os
from fpdf import FPDF
from datetime import datetime

class ClinicalPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "MedRAG Clinical Report", border=False, ln=True, align="C")
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", border=False, ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_clinical_pdf(pipeline_result: dict, output_path: str = "clinical_report.pdf"):
    """
    Format AI JSON Output into a polished Doctor-ready PDF format.
    """
    pdf = ClinicalPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Helper for fast unicode stripping in base FPDF
    def clean_txt(t):
        if not isinstance(t, str): return str(t)
        return t.encode('latin-1', 'replace').decode('latin-1')
    
    # 1. Diagnosis
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "1. AI Diagnosis & Reasoning", ln=True)
    
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(0, 0, 0)
    diagnosis_text = pipeline_result.get("diagnosis", "No diagnosis provided.")
    pdf.multi_cell(0, 8, txt=clean_txt(diagnosis_text))
    pdf.ln(5)

    # 2. Risk Metrics
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "2. Clinical Guardrail Metrics", ln=True)
    
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(0, 0, 0)
    
    confidence = pipeline_result.get("confidence_score", 0.0)
    risk_score = pipeline_result.get("risk_score", 0)
    hallucination = pipeline_result.get("hallucination_score", 0.0)
    emergency = pipeline_result.get("emergency_flag", False)
    
    metrics = f"Confidence Score: {confidence}/1.0\nRisk Score: {risk_score}/10\nHallucination Index: {hallucination}/1.0\nEmergency Flag: {'YES' if emergency else 'NO'}"
    pdf.multi_cell(0, 8, txt=metrics)
    pdf.ln(5)

    # 3. Recommendations
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "3. Recommended Plan", ln=True)
    
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(0, 0, 0)
    recs = pipeline_result.get("recommendations", {})
    meal_plan = recs.get("meal_plan", "None")
    activity_plan = recs.get("activity_plan", "None")
    
    pdf.multi_cell(0, 8, txt=clean_txt(f"Activity Plan: {activity_plan}\nMeal Plan: {meal_plan}"))
    pdf.ln(5)

    # 4. Evidence Context
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "4. Retrieved Contextual Evidence", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(50, 50, 50)
    evidence = pipeline_result.get("evidence", "No evidence retrieved.")
    pdf.multi_cell(0, 6, txt=clean_txt(evidence))
    
    # 5. Image
    heatmap_path = pipeline_result.get("heatmap", "")
    if heatmap_path and os.path.exists(heatmap_path):
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "5. Vision Heatmap Bounding Box", ln=True)
        pdf.image(heatmap_path, x=15, w=150)

    pdf.output(output_path)
    return output_path
