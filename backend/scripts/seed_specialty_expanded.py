"""
MedRAG Expanded Specialty Knowledge Base Seeder
=================================================
Expands the curated specialty knowledge base to 400+ paragraphs across 32 specialties.

Run: python -m backend.scripts.seed_specialty_expanded
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
from backend.scripts.seed_knowledge import SPECIALTY_KNOWLEDGE as OLD_SK

BATCH_SIZE = 64

# Add new specialties and more paragraphs
NEW_SPECIALTIES = {
    "Geriatrics": [
        "Frailty is a clinical syndrome characterized by decreased physiologic reserve and increased vulnerability to stressors. It is associated with increased risk of falls, hospitalization, and mortality. Assessment includes unintentional weight loss, self-reported exhaustion, weakness (grip strength), slow walking speed, and low physical activity.",
        "Polypharmacy (taking 5+ medications) increases the risk of adverse drug events and drug-drug interactions in older adults. The Beers Criteria lists potentially inappropriate medications for older adults, including anticholinergics (confusion, urinary retention), benzodiazepines (falls, delirium), and certain NSAIDs (GI bleeding, renal toxicity).",
        "Delirium is an acute, fluctuating disturbance in attention and awareness. It is a medical emergency often triggered by infection (e.g., UTI, pneumonia), medications, electrolyte imbalance, or surgery. Prevention strategies include early mobilization, reorientation, sleep hygiene, and avoiding physical restraints.",
    ],
    "Sports Medicine": [
        "Concussion (mild traumatic brain injury) management requires cognitive and physical rest followed by a graduated return-to-play protocol. Symptoms include headache, dizziness, amnesia, confusion, and sleep disturbances. Neuroimaging (CT) is indicated only if criteria for severe injury (e.g., focal deficit, worsening headache) are met.",
        "Anterior Cruciate Ligament (ACL) tears often present with a 'pop' and immediate knee swelling following a pivoting or deceleration injury. The Lachman test is the most sensitive physical exam finding. Management options range from physical therapy for sedentary patients to surgical reconstruction for active individuals.",
    ],
    "Allergy / Immunology": [
        "Anaphylaxis requires immediate intramuscular epinephrine (0.3 mg-0.5 mg in adults, 0.01 mg/kg in children) typically in the anterolateral thigh. Secondary treatments include H1/H2 antihistamines, systemic corticosteroids, and bronchodilators. Patients must be observed for biphasic reactions.",
        "Allergic rhinitis management depends on severity: mild intermittent symptoms are treated with oral second-generation antihistamines (e.g., cetirizine, loratadine), while moderate-to-severe or persistent symptoms are best managed with intranasal corticosteroids (e.g., fluticasone).",
    ],
    "Endocrinology": [
        "Primary adrenal insufficiency (Addison's disease) presents with fatigue, weight loss, hyperpigmentation, hypotension, hyponatremia, and hyperkalemia. Diagnosis is confirmed by low morning cortisol and lack of response to Cosyntropin (ACTH stimulation test). Treatment requires both glucocorticoid (hydrocortisone) and mineralocorticoid (fludrocortisone) replacement.",
        "Osteoporosis diagnosis is made by a T-score of -2.5 or lower on DEXA scan or the presence of a fragility fracture. First-line pharmacotherapy includes oral bisphosphonates (alendronate). Denosumab is an alternative. Adequate calcium and vitamin D intake and weight-bearing exercise are essential adjuncts.",
    ],
    "Cardiology": [
        "Heart Failure with Preserved Ejection Fraction (HFpEF) management focuses on symptom relief (loop diuretics) and treating comorbidities (hypertension, afib, diabetes). SGLT2 inhibitors (empagliflozin, dapagliflozin) are the first drugs shown to reduce cardiovascular mortality and hospitalizations in this group.",
        "Atrial Fibrillation rate control is typically achieved with beta-blockers (metoprolol) or non-dihydropyridine calcium channel blockers (diltiazem, verapamil). Stroke risk is assessed using the CHA2DS2-VASc score; a score of 2+ in men or 3+ in women generally warrants oral anticoagulation (DOACs preferred over warfarin).",
    ]
}

def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))

async def seed_specialty_expanded():
    print("=" * 60)
    print("  MedRAG Expanded Specialty Knowledge Seeder")
    print("=" * 60)

    start = time.time()
    all_docs = []
    
    merged_sk = OLD_SK.copy()
    for k, v in NEW_SPECIALTIES.items():
        if k in merged_sk:
            merged_sk[k].extend(v)
        else:
            merged_sk[k] = v

    graph_store.set_bulk_mode(True)
    
    for specialty, paragraphs in merged_sk.items():
        for i, text in enumerate(paragraphs):
            all_docs.append({
                "text": f"Topic: {specialty}\n\n{text}",
                "metadata": {
                    "source": "MedRAG_Curated_Expanded",
                    "category": "specialty_reference",
                    "modality": "text",
                    "specialty": specialty,
                    "type": "clinical_knowledge"
                }
            })
            graph_store.add_relationship(specialty.lower(), "HAS_KNOWLEDGE", text[:60].lower())

    points = []
    
    for i in range(0, len(all_docs), BATCH_SIZE):
        batch = all_docs[i:i+BATCH_SIZE]
        texts = [d["text"] for d in batch]
        embeddings = await text_embedder.embed_batch(texts)
        
        for emb, d in zip(embeddings, batch):
            d["metadata"]["document"] = d["text"]
            points.append({
                "id": _stable_uuid(f"spec_exp_{d['metadata']['specialty']}_{d['text'][:20]}"),
                "vector": emb,
                "payload": d["metadata"]
            })
            
    vector_store.store_text_batch(points)
    graph_store.set_bulk_mode(False)
    
    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"  🎉 Expanded specialty seeding complete: {len(points)} docs across {len(merged_sk)} specialties")
    print(f"  Time: {elapsed:.1f} sec")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(seed_specialty_expanded())
