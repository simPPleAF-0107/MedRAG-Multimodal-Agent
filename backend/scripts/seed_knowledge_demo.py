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

def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))

async def _embed_and_store(doc_id: str, text: str, metadata: dict):
    embedding = await text_embedder.embed_text(text)
    await vector_store.store_text_embedding(
        doc_id=doc_id,
        embedding=embedding,
        text=text,
        metadata=metadata,
    )

async def seed_pubmedqa():
    from datasets import load_dataset
    print("\n📚 [1/4] Loading PubMedQA (Fast Demo, max 50 entries)…")
    ds = load_dataset("qiaojin/PubMedQA", "pqa_labeled", split="train")

    count = 0
    for row in ds:
        if count >= 50: break
        question = row.get("question", "")
        contexts = row.get("context", {})
        long_answer = row.get("long_answer", "")
        context_strs = contexts.get("contexts", []) if isinstance(contexts, dict) else []
        context_text = " ".join(context_strs) if context_strs else ""
        chunk = f"Question: {question}\nContext: {context_text}\nAnswer: {long_answer}"
        
        doc_id = _stable_uuid(f"pubmedqa_demo_{count}")
        await _embed_and_store(doc_id, chunk, {"source": "PubMedQA", "type": "biomedical_qa"})
        count += 1
    print(f"   ✅ PubMedQA complete — {count} entries")
    return count

async def seed_medqa():
    from datasets import load_dataset
    print("\n📚 [2/4] Loading MedQA-USMLE (Fast Demo, max 50 entries)…")
    ds = load_dataset("GBaker/MedQA-USMLE-4-options", split="train")

    count = 0
    for row in ds:
        if count >= 50: break
        question = row.get("question", "")
        options = row.get("options", {})
        answer = row.get("answer", "")
        opts_str = " | ".join([f"{k}: {v}" for k, v in options.items()]) if isinstance(options, dict) else str(options)
        chunk = f"Clinical Question: {question}\nOptions: {opts_str}\nCorrect Answer: {answer}"
        
        doc_id = _stable_uuid(f"medqa_demo_{count}")
        await _embed_and_store(doc_id, chunk, {"source": "MedQA-USMLE"})
        count += 1
    print(f"   ✅ MedQA complete — {count} entries")
    return count

async def seed_specialty_knowledge():
    print("\n📚 [3/3] Embedding curated specialty knowledge base (Fast Demo)…")
    # Using brief hardcoded texts
    texts = [
        "Oncology: Cancer staging uses TNM system. Common cancers include lung, breast, colorectal.",
        "Cardiology: Acute myocardial infarction presents with chest pain, elevated troponin, and ECG changes."
    ]
    count = 0
    for i, text in enumerate(texts):
        doc_id = _stable_uuid(f"specialty_demo_{i}")
        await _embed_and_store(doc_id, text, {"source": "MedRAG_Curated"})
        count += 1
    print(f"   ✅ Specialty complete — {count} entries")
    return count

async def main():
    print("=" * 60)
    print("  MedRAG Knowledge Base Seeder — FAST DEMO")
    print("=" * 60)
    start = time.time()
    total = await seed_pubmedqa() + await seed_medqa() + await seed_specialty_knowledge()
    elapsed = time.time() - start
    print("\n" + "=" * 60)
    print(f"  🎉 Fast Seeding complete! Ingested {total} entries in {elapsed:.1f}s.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
