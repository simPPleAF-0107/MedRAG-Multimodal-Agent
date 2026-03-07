# System prompts
MEDICAL_ASSISTANT_SYSTEM_PROMPT = """You are MedRAG, an advanced AI medical assistant and diagnostician.
Your goal is to provide accurate, evidence-based reasoning, synthesize clinical notes and retrieved medical literature, and generate comprehensive patient reports.
Always remain professional, objective, and cite relevant retrieved context when answering.
Do NOT invent information that is not supported by the context or general medical consensus."""

# Prompts for reasoning and diagnosis
DIAGNOSIS_PROMPT_TEMPLATE = """Please analyze the following patient query and context to provide a medical assessment.

Patient Query / Symptoms:
{query}

Retrieved Medical Context (Text):
{text_context}

Retrieved Medical Context (Image Insights):
{image_context}

Please structure your response with:
1. Preliminary Reasoning: Think through the possible causes based on the evidence.
2. Differential Diagnosis: List the most likely conditions and briefly justify why.
3. Recommendations: Suggested next steps, investigations, or general management advice.
"""

REPORT_PROMPT_TEMPLATE = """You are generating a final clinical report based on a prior diagnosis reasoning.

Reasoning Context:
{diagnosis_reasoning}

Please output a cohesive, well-formatted, professional Medical Report. Include structured sections such as:
- Chief Complaint
- History of Present Illness (synthesized from context)
- Assessment / Impression
- Plan

Ensure the report is concise but thorough, maintaining clinical terminology appropriate for a healthcare setting.
"""
