"""
MedRAG Drug Safety Seeder
=========================
Seeds drug safety databases for adverse event detection and pharmacovigilance.
1. SIDER: Extracted Side Effects
2. RxNorm: (To be integrated later or via direct API to NLM)
"""
import asyncio
import sys
import os
import hashlib
import uuid as _uuid
import gzip
import csv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder
from backend.utils.logger import logger

RESEARCH_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "Research", "latest"
)

def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))

async def seed_drug_safety(limit: int = 5000):
    print("======================================================================")
    print("  🚀 MedRAG Drug Safety Seeder")
    print("======================================================================")
    
    total = 0
    
    # 1. SIDER
    sider_path = os.path.join(RESEARCH_DIR, "SIDER", "meddra_all_se.tsv.gz")
    
    if not os.path.exists(sider_path):
        logger.warning(f"SIDER dataset not found at {sider_path}")
    else:
        print("\n📚 Loading SIDER Database...")
        # Format: STITCH_FLAT, STITCH_STEREO, UMLS_CONCEPT, MEDDRA_CONCEPT, UMLS_CONCEPT_NAME, MEDDRA_CONCEPT_NAME
        # We really care about mapping Drug (STITCH IDs) to Side Effect (MEDDRA_CONCEPT_NAME)
        # SIDER 4.1 often maps compound ID to side effect names directly
        
        # A simple mapping to avoid redundant embeddings: Drug ID -> List of side effects
        drug_se_map = {}
        
        try:
            with gzip.open(sider_path, 'rt', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                for row in reader:
                    if len(row) >= 6:
                        drug_id = row[0] # e.g., CID100000085
                        se_name = row[5] # e.g., "Abdominal pain"
                        
                        if drug_id not in drug_se_map:
                            drug_se_map[drug_id] = set()
                        drug_se_map[drug_id].add(se_name)
        except Exception as e:
            logger.error(f"Error parsing SIDER: {e}")
            
        count = 0
        for drug_id, side_effects in list(drug_se_map.items())[:limit]:
            se_list = ", ".join(sorted(list(side_effects)[:30])) # limit to top 30 per drug to avoid huge chunks
            if len(side_effects) > 30:
                se_list += f" (and {len(side_effects)-30} more)"
                
            text = f"Pharmacovigilance Data from SIDER:\nCompound ID: {drug_id}\nKnown Adverse Effects / Side Effects: {se_list}"
            
            doc_id = _stable_uuid(f"sider_{drug_id}")
            emb = await text_embedder.embed_text(text)
            
            await vector_store.store_text_embedding(
                doc_id=doc_id,
                embedding=emb,
                text=text,
                metadata={
                    "source": "SIDER",
                    "category": "drug_safety",
                    "specialty": "Pharmacology"
                }
            )
            count += 1
            if count % 200 == 0:
                print(f"      ✅ Ingested {count} SIDER compound profiles...")
                
        total += count
        print(f"   ✅ SIDER complete — {count} drug profiles ingested")

    print("\n======================================================================")
    print(f"  🏁 DRUG SAFETY SEEDING COMPLETE! Total inserted: {total}")
    print("======================================================================")
    return total

if __name__ == "__main__":
    asyncio.run(seed_drug_safety())
