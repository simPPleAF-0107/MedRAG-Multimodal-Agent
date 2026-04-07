# System prompts
MEDICAL_ASSISTANT_SYSTEM_PROMPT = """You are MedRAG, an advanced AI medical assistant and diagnostician powered by Retrieval-Augmented Generation.

Your capabilities:
- Analyze clinical text queries, patient symptoms, and uploaded medical documents
- Process medical imaging context (X-rays, CT scans, MRI) when image descriptions are provided  
- Synthesize retrieved medical literature with your clinical training
- Generate comprehensive, evidence-based diagnostic assessments

Rules:
1. Always ground your reasoning in the retrieved context when available
2. Clearly distinguish between evidence-supported conclusions and clinical judgment
3. Never fabricate specific statistics, study names, or patient data
4. Always include safety warnings for serious or emergency conditions
5. Be precise with medical terminology but explain in patient-friendly language when appropriate"""

# Prompts for reasoning and diagnosis
DIAGNOSIS_PROMPT_TEMPLATE = """Analyze the following patient query and all available context to provide a comprehensive medical assessment.

══════════════════════════════════
PATIENT QUERY / SYMPTOMS:
══════════════════════════════════
{query}

══════════════════════════════════
RETRIEVED MEDICAL EVIDENCE (Text):
══════════════════════════════════
{text_context}

══════════════════════════════════
MEDICAL IMAGE ANALYSIS:
══════════════════════════════════
{image_context}

══════════════════════════════════
INSTRUCTIONS:
══════════════════════════════════
Using ALL available context above (patient query, retrieved evidence, and image analysis), provide:

1. **Preliminary Reasoning**: 
   - Identify the key clinical findings from the query and evidence
   - Correlate symptoms with the retrieved medical literature
   - If image context is provided, integrate visual findings into your reasoning

2. **Differential Diagnosis**: 
   - List 3-5 most likely conditions in order of probability
   - For each, explain supporting evidence from the retrieved context
   - Include any conditions suggested by image analysis

3. **Recommendations**:
   - Immediate next steps (tests, imaging, referrals)
   - Red flag symptoms that warrant emergency care
   - General management advice including lifestyle modifications
   - Specialist referral if indicated

Important: Base your reasoning on the retrieved evidence. If the evidence is limited or not directly relevant, state this clearly and supplement with general medical knowledge while noting the distinction."""

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

RISK_ANALYSIS_PROMPT = """Analyze the following patient data and diagnosis to determine clinical risk.
Patient Data: {patient_data}
Diagnosis: {diagnosis}

Evaluate risk across these dimensions:
1. Severity of condition (mild/moderate/severe/critical)
2. Urgency of intervention needed
3. Potential complications if untreated
4. Patient-specific risk factors

Return a precise numerical risk score between 0 and 100 on the first line.
- 0-20: Low risk (routine follow-up)
- 21-40: Moderate risk (scheduled care needed)  
- 41-60: Elevated risk (prompt evaluation required)
- 61-80: High risk (urgent care recommended)
- 81-100: Critical risk (emergency intervention needed)

Output the justification on the subsequent lines.
"""

DIFFERENTIAL_DIAGNOSIS_PROMPT = """Generate a detailed differential diagnosis based on the provided symptoms and patient history.
Symptoms/Query: {symptoms}
History: {history}

List the top 3-5 possible conditions in order of likelihood. For each condition:
1. Name the condition
2. Probability estimate (high/moderate/low)
3. Key supporting findings from the symptoms
4. Key findings that would confirm or rule out this diagnosis
5. Recommended diagnostic tests
"""

HALLUCINATION_CHECK_PROMPT = """Cross-check the generated medical report against the retrieved evidence to identify contradictions or unsupported claims.

Retrieved Evidence:
{evidence}

Generated Report:
{report}

IMPORTANT: The AI uses both retrieved evidence AND its own medical training. 
- Claims that are medically accurate but not in the evidence are NOT hallucinations
- Only flag claims that CONTRADICT the evidence or are clearly fabricated
- Common medical knowledge (anatomy, standard treatments) does not need evidence backing

Return a hallucination score between 0.0 and 1.0 on the first line:
- 0.0-0.2: Report is well-supported by evidence and medically accurate
- 0.2-0.4: Minor gaps but no contradictions, medically sound
- 0.4-0.6: Some claims not well-supported, but no clear fabrication
- 0.6-0.8: Contains claims that may contradict evidence
- 0.8-1.0: Contains clear contradictions or fabricated medical claims

Provide specific flags on subsequent lines.
"""
