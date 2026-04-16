"""
MedRAG Psychiatry & Mental Health Seeder
========================================
Seeds QA and criteria for psychiatry and mental health.
1. PsyQA (English subset)
2. DSM-5 Diagnostics (Curated fallback criteria)
"""
import asyncio
import sys
import os
import hashlib
import uuid as _uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder
from backend.utils.logger import logger

def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))

DSM_5_DATA = [
    {
        "disorder": "Major Depressive Disorder",
        "criteria": "Five (or more) of the following symptoms have been present during the same 2-week period and represent a change from previous functioning: depressed mood, loss of interest or pleasure, weight change, insomnia or hypersomnia, psychomotor agitation or retardation, fatigue, feelings of worthlessness or guilt, diminished ability to think or concentrate, recurrent thoughts of death or suicidal ideation.",
    },
    {
        "disorder": "Generalized Anxiety Disorder",
        "criteria": "Excessive anxiety and worry occurring more days than not for at least 6 months, about a number of events or activities. The individual finds it difficult to control the worry. Associated with three (or more) of the following six symptoms: restlessness, being easily fatigued, difficulty concentrating, irritability, muscle tension, sleep disturbance.",
    },
    {
        "disorder": "Schizophrenia",
        "criteria": "Two (or more) of the following, each present for a significant portion of time during a 1-month period: delusions, hallucinations, disorganized speech, grossly disorganized or catatonic behavior, negative symptoms. Continuous signs of the disturbance persist for at least 6 months.",
    },
    {
        "disorder": "Bipolar I Disorder",
        "criteria": "Criteria have been met for at least one manic episode. The manic episode may have been preceded by and may be followed by hypomanic or major depressive episodes. Symptoms include inflated self-esteem, decreased need for sleep, more talkative, flight of ideas, distractibility, increase in goal-directed activity, excessive involvement in risky activities.",
    },
    {
        "disorder": "Obsessive-Compulsive Disorder",
        "criteria": "Presence of obsessions, compulsions, or both. Obsessions are recurrent and persistent thoughts. Compulsions are repetitive behaviors or mental acts that the individual feels driven to perform in response to an obsession. The obsessions or compulsions are time-consuming (e.g., take more than 1 hour per day) or cause clinically significant distress.",
    }
]

async def seed_psychiatry(limit: int = 1500):
    print("======================================================================")
    print("  🚀 MedRAG Psychiatry & Mental Health Seeder")
    print("======================================================================")
    
    total = 0
    
    # 1. DSM-5
    print("\n📚 Loading DSM-5 Curated Criteria...")
    for item in DSM_5_DATA:
        text = f"DSM-5 Diagnostic Criteria:\nDisorder: {item['disorder']}\nCriteria: {item['criteria']}"
        doc_id = _stable_uuid(f"dsm5_{item['disorder']}")
        emb = await text_embedder.embed_text(text)
        
        await vector_store.store_text_embedding(
            doc_id=doc_id,
            embedding=emb,
            text=text,
            metadata={
                "source": "DSM-5",
                "category": "psychiatry",
                "specialty": "Psychiatry"
            }
        )
        total += 1
    print(f"   ✅ DSM-5 complete — {len(DSM_5_DATA)} disorders ingested")
    
    # 2. PsyQA (English or fallback translation subset)
    # Using 'KarelDO/psyqa' or standard PsyQA mappings on HF if available.
    try:
        from datasets import load_dataset
        print("\n📚 Loading PsyQA (Mental Health QA)...")
        # Often PsyQA is Chinese; if 'sunblaze-ucb/PsyQA' we might need to translate or just embed English
        # For demonstration, we'll try to load a known subset
        ds = load_dataset("KarelDO/psyqa", split="train", trust_remote_code=True)
        count = 0
        for row in ds:
            q = row.get("question", "")
            a = row.get("answer", "")
            if len(q) > 10 and len(a) > 10:
                text = f"Mental Health Query (PsyQA):\nPatient: {q}\nProfessional Response: {a}"
                doc_id = _stable_uuid(f"psyqa_{count}")
                emb = await text_embedder.embed_text(text)
                
                await vector_store.store_text_embedding(
                    doc_id=doc_id,
                    embedding=emb,
                    text=text,
                    metadata={
                        "source": "PsyQA",
                        "category": "psychiatry",
                        "specialty": "Psychiatry"
                    }
                )
                count += 1
                if count % 200 == 0:
                    print(f"      ✅ Ingested {count} PsyQA pairs...")
                if limit and count >= limit:
                    break
        total += count
        print(f"   ✅ PsyQA complete — {count} QA pairs ingested")
    except Exception as e:
        logger.warning(f"PsyQA huggingface dataset skipped (or not found). Error: {e}")

    print("\n======================================================================")
    print(f"  🏁 PSYCHIATRY SEEDING COMPLETE! Total inserted: {total}")
    print("======================================================================")
    return total

if __name__ == "__main__":
    asyncio.run(seed_psychiatry())
