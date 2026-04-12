"""
MedRAG MedlinePlus Seeder
=============================
Fetches patient-friendly health topics from MedlinePlus Connect.
Great for simplifying technical explanations or translating jargon.

Run: python -m backend.scripts.seed_medlineplus
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

# Mapping common SNOMED CT codes to general medical conditions
CONDITIONS = {
    # Cardiology
    "70995007": "Pulmonary hypertension",
    "48447003": "Chronic heart failure",
    "53741008": "Coronary arteriosclerosis",
    "38341003": "Hypertensive disorder",
    # Neurology
    "230690007": "Stroke",
    "84757009": "Epilepsy",
    "80690008": "Parkinson's disease",
    # Pulmonology
    "195967001": "Asthma",
    "13645005": "COPD",
    "413839001": "Pneumonia",
    # Gastroenterology
    "1162890002": "GERD",
    "34000006": "Crohn's disease",
    "64766004": "Ulcerative colitis",
    # Endocrinology
    "44054006": "Type 2 diabetes",
    "40930008": "Hypothyroidism",
    # Oncology
    "254837009": "Malignant neoplasm of breast",
    "93880001": "Primary malignant neoplasm of lung",
}

def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))

async def _fetch_topic(session, code: str, name: str) -> dict | None:
    """Fetch patient-friendly topic info from Wikipedia API."""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name.replace(' ', '_')}"
    
    try:
        async with session.get(url, timeout=10) as resp:
            if resp.status != 200:
                # Try simple title case if first attempt fails
                url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name.title().replace(' ', '_')}"
                async with session.get(url, timeout=10) as resp2:
                    if resp2.status != 200:
                        print(f"  ⚠ Fetch failed for {name}: {resp2.status}")
                        return None
                    data = await resp2.json()
            else:
                data = await resp.json()
            
            title = data.get("title", name)
            summary = data.get("extract", "")
            
            if not summary:
                return None
            
            text = f"Patient Education: {title}\n\n{summary}"
            
            return {
                "text": text,
                "metadata": {
                    "source": "Wikipedia_Patient_Education",
                    "category": "patient_education",
                    "modality": "text",
                    "type": "health_topic",
                    "title": title[:200]
                }
            }
    except Exception as e:
        print(f"  ⚠ Fetch failed for {name}: {e}")
        return None

async def seed_medlineplus():
    print("=" * 60)
    print("  MedRAG MedlinePlus Seeder")
    print(f"  Target: Patient-friendly topics for {len(CONDITIONS)} conditions")
    print("=" * 60)

    start = time.time()
    total_ingested = 0
    graph_store.set_bulk_mode(True)

    async with __import__('aiohttp').ClientSession(headers={'User-Agent': 'MedRAG_Agent/1.0 (medrag_dev@example.com)'}) as session:
        all_chunks = []
        for code, name in CONDITIONS.items():
            print(f"📘 Fetching: {name}")
            data = await _fetch_topic(session, code, name)
            if data:
                # Add specialty metadata naively based on condition lists in actual implementation
                data["metadata"]["specialty"] = "General" 
                all_chunks.append(data)
                graph_store.add_relationship(name.lower(), "PATIENT_EDUCATION", data["metadata"]["title"][:60].lower())
            await asyncio.sleep(0.5)

        print(f"\n📦 Embed and store {len(all_chunks)} patient topic summaries...")
        for i in range(0, len(all_chunks), BATCH_SIZE):
            batch = all_chunks[i:i + BATCH_SIZE]
            texts = [c["text"] for c in batch]
            embeddings = await text_embedder.embed_batch(texts)
            
            points = []
            for emb, chunk in zip(embeddings, batch):
                doc_id = _stable_uuid(f"medlineplus_{chunk['metadata']['title']}")
                chunk["metadata"]["document"] = chunk["text"]
                points.append({
                    "id": doc_id,
                    "vector": emb,
                    "payload": chunk["metadata"],
                })
            
            vector_store.store_text_batch(points)
            total_ingested += len(points)
            
    graph_store.set_bulk_mode(False)
    
    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"  🎉 MedlinePlus seeding complete: {total_ingested} docs")
    print(f"  Time: {elapsed:.1f} sec")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(seed_medlineplus())
