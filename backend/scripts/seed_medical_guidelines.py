"""
MedRAG Medical Guidelines Seeder
====================================
Curated list of clinical practitioner guidelines spanning emergency, 
screening, algorithms, etc.

Run: python -m backend.scripts.seed_medical_guidelines
"""
import asyncio
import sys
import os
import time
import hashlib
import uuid as _uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder
from backend.rag.graph_store import graph_store

BATCH_SIZE = 64

GUIDELINES = [
    {
        "specialty": "Emergency Medicine",
        "title": "ACLS Cardiac Arrest Algorithm",
        "text": "Advanced Cardiovascular Life Support (ACLS) Cardiac Arrest: For VF/pVT, shock, CPR 2 min, Epinephrine q3-5 min, consider Amiodarone. For Asystole/PEA, CPR 2 mins, Epinephrine q3-5 min, identify reversible causes (H's and T's: Hypovolemia, Hypoxia, Hydrogen ion acidosis, Hypo/Hyperkalemia, Hypothermia, Tension pneumothorax, Tamponade, Toxins, Thrombosis pulm/coronary)."
    },
    {
        "specialty": "Infectious Disease",
        "title": "Surviving Sepsis Campaign 1-Hour Bundle",
        "text": "Surviving Sepsis Campaign: Measure lactate level. Re-measure if initial lactate > 2 mmol/L. Obtain blood cultures prior to administration of antibiotics. Administer broad-spectrum antibiotics. Begin rapid administration of 30 mL/kg crystalloid for hypotension or lactate ≥ 4 mmol/L. Apply vasopressors if hypotensive during or after fluid resuscitation to maintain MAP ≥ 65 mm Hg. First choice vasopressor is norepinephrine."
    },
    {
        "specialty": "Cardiology",
        "title": "AHA/ACC Hypertension Guidelines",
        "text": "Hypertension Guidelines: Normal BP <120/<80. Elevated: 120-129/<80. Stage 1: 130-139 or 80-89. Stage 2: ≥140 or ≥90. First line agents for nonblack patients: Thiazides, CCBs, ACEIs, or ARBs. For black patients: Thiazides or CCBs. Target BP < 130/80 for most adults with clinical CVD or 10-year ASCVD risk ≥ 10%."
    },
    {
        "specialty": "Endocrinology",
        "title": "ADA Diabetes Management",
        "text": "Type 2 Diabetes ADA Guidelines: A1C goal for many nonpregnant adults is < 7.0%. Metformin is the preferred initial pharmacologic agent. For patients with ASCVD or heart failure, a SGLT2 inhibitor or GLP-1 receptor agonist with demonstrated cardiovascular benefit is recommended. Start dual therapy if A1C ≥ 1.5% over target."
    },
    {
         "specialty": "General",
         "title": "USPSTF Colon Cancer Screening",
         "text": "Colorectal Cancer Screening (USPSTF): Screen all adults aged 45 to 75 years. Options include: colonoscopy every 10 years, FIT yearly, sDNA-FIT every 1-3 years, CT colonography every 5 years, flexible sigmoidoscopy every 5 years."
    }
]

def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))

async def seed_medical_guidelines():
    print("=" * 60)
    print("  MedRAG Clinical Guidelines Seeder")
    print("=" * 60)

    start = time.time()
    points = []
    
    embeddings = await text_embedder.embed_batch([g["text"] for g in GUIDELINES])
    
    for emb, g in zip(embeddings, GUIDELINES):
        meta = {
            "source": "Clinical_Guidelines",
            "category": "guidelines",
            "modality": "text",
            "specialty": g["specialty"],
            "title": g["title"],
            "document": f"CLINICAL GUIDELINE: {g['title']}\n\n{g['text']}"
        }
        
        points.append({
            "id": _stable_uuid(f"guideline_{g['title']}"),
            "vector": emb,
            "payload": meta
        })
        
        graph_store.add_relationship(g["specialty"].lower(), "HAS_GUIDELINE", g["title"].lower())
        
    vector_store.store_text_batch(points)
    
    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"  🎉 Guidelines seeding complete: {len(points)} docs")
    print(f"  Time: {elapsed:.1f} sec")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(seed_medical_guidelines())
