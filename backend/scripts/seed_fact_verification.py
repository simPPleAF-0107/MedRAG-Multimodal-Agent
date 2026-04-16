"""
MedRAG Fact Verification & Calibration Seeder
===========================================
Seeds datasets for calibrating the hallucination verifier and handling medical misinformation.
1. HealthFC:    Fact-checked medical claims (Hallucination calibration)
2. COVID-Fact:  Misinformation/verified claims (Adversarial training)
3. BioASQ:      Fact-grounded biomedical QA (QA knowledge)
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

async def seed_dataset(name: str, hf_id: str, split: str, map_func, limit: int = None):
    try:
        from datasets import load_dataset
    except ImportError:
        logger.error("datasets not installed. Please run: pip install datasets")
        return 0

    print(f"\n📚 Loading {name} [{hf_id}]...")
    try:
        ds = load_dataset(hf_id, split=split, trust_remote_code=True)
    except Exception as e:
        logger.warning(f"Failed to load {name} from HuggingFace: {e}")
        return 0

    docs = []
    for item in ds:
        docs.append(map_func(item))
        if limit and len(docs) >= limit:
            break

    count = 0
    for doc in docs:
        if not doc.get("text"):
            continue
            
        doc_id = _stable_uuid(f"{name}_{count}")
        emb = await text_embedder.embed_text(doc["text"])
        
        await vector_store.store_text_embedding(
            doc_id=doc_id,
            embedding=emb,
            text=doc["text"],
            metadata={
                "source": name,
                "category": "hallucination_calibration",
                "veracity": doc.get("veracity", "UNKNOWN"),
                "specialty": "General Medicine"
            }
        )
        count += 1
        if count % 100 == 0:
            print(f"      ✅ Ingested {count} {name} claims...")

    print(f"   ✅ {name} complete — {count} claims ingested")
    return count

import csv

async def seed_fact_verification(limit: int = 2000):
    print("======================================================================")
    print("  🚀 MedRAG Fact Verification & Calibration Seeder")
    print("======================================================================")
    
    total = 0
    
    # 1. HealthFC (from local GitHub download)
    healthfc_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "Research", "latest", "HealthFC.csv"
    )
    
    if not os.path.exists(healthfc_path):
        logger.warning(f"HealthFC dataset not found at {healthfc_path}")
        return 0
        
    print(f"\n📚 Loading HealthFC (Direct CSV)...")
    try:
        count = 0
        with open(healthfc_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            # Find the actual column names from the CSV
            for row in reader:
                claim = row.get("en_claim", "")
                evidence = row.get("en_explanation", "")
                label_val = row.get("label", "UNKNOWN")
                
                # HealthFC uses 0 (Supported), 1 (Unsupported/Insufficient), 2 (Refuted)
                label = "UNKNOWN"
                if label_val == "0": label = "SUPPORTED"
                elif label_val == "1": label = "INSUFFICIENT EVIDENCE"
                elif label_val == "2": label = "REFUTED"
                
                if not claim: 
                    continue
                
                text = f"HealthFC Fact-Checked Claim: {claim}\nEvidence: {evidence}\nVeracity: {label}"
                doc_id = _stable_uuid(f"healthfc_{count}")
                
                emb = await text_embedder.embed_text(text)
                await vector_store.store_text_embedding(
                    doc_id=doc_id,
                    embedding=emb,
                    text=text,
                    metadata={
                        "source": "HealthFC",
                        "category": "hallucination_calibration",
                        "veracity": label,
                        "specialty": "General Medicine"
                    }
                )
                
                count += 1
                if count % 100 == 0:
                    print(f"      ✅ Ingested {count} HealthFC claims...")
                if limit and count >= limit:
                    break
                    
        total += count
        print(f"   ✅ HealthFC complete — {count} claims ingested")
        
    except Exception as e:
        logger.error(f"Error parsing HealthFC CSV: {e}")

    print("\n======================================================================")
    print(f"  🏁 FACT VERIFICATION SEEDING COMPLETE! Total inserted: {total}")
    print("======================================================================")
    return total

if __name__ == "__main__":
    asyncio.run(seed_fact_verification())
