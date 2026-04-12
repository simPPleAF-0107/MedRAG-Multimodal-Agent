"""
MedRAG ICD-10 & SNOMED Seeder
==============================
Vocabulary mappings to ground the LLM in standardized healthcare tech schemas.

Run: python -m backend.scripts.seed_icd10
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

ICD10_CODES = [
    # J Codes - Respiratory
    ("J45.909", "Unspecified asthma, uncomplicated", "Pulmonology"),
    ("J44.9", "Chronic obstructive pulmonary disease, unspecified", "Pulmonology"),
    ("J18.9", "Pneumonia, unspecified organism", "Pulmonology"),
    # I Codes - Circulatory
    ("I10", "Essential (primary) hypertension", "Cardiology"),
    ("I48.91", "Unspecified atrial fibrillation", "Cardiology"),
    ("I25.10", "Atherosclerotic heart disease of native coronary artery without angina", "Cardiology"),
    # E Codes - Endocrine
    ("E11.9", "Type 2 diabetes mellitus without complications", "Endocrinology"),
    ("E03.9", "Hypothyroidism, unspecified", "Endocrinology"),
    ("E78.5", "Hyperlipidemia, unspecified", "Endocrinology"),
    # F Codes - Mental
    ("F32.9", "Major depressive disorder, single episode, unspecified", "Psychiatry"),
    ("F41.1", "Generalized anxiety disorder", "Psychiatry"),
    # M Codes - Musculoskeletal
    ("M54.5", "Low back pain", "Orthopedics"),
    ("M17.9", "Osteoarthritis of knee, unspecified", "Orthopedics"),
]

def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))

async def seed_icd10():
    print("=" * 60)
    print("  MedRAG ICD-10 Code Seeder")
    print("=" * 60)

    start = time.time()
    all_docs = []
    
    for code, desc, spec in ICD10_CODES:
        text = f"ICD-10-CM code: {code}\nDescription: {desc}"
        all_docs.append({
            "text": text,
            "metadata": {
                "source": "ICD-10-CM",
                "category": "diagnosis_codes",
                "modality": "text",
                "specialty": spec,
                "icd_code": code
            }
        })
        graph_store.add_relationship(desc.lower(), "MAPPED_TO_ICD10", code.lower())

    points = []
    embeddings = await text_embedder.embed_batch([d["text"] for d in all_docs])
    
    for emb, d in zip(embeddings, all_docs):
        d["metadata"]["document"] = d["text"]
        points.append({
            "id": _stable_uuid(f"icd10_{d['metadata']['icd_code']}"),
            "vector": emb,
            "payload": d["metadata"]
        })
        
    vector_store.store_text_batch(points)
    
    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"  🎉 ICD-10 seeding complete: {len(points)} docs")
    print(f"  Time: {elapsed:.1f} sec")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(seed_icd10())
