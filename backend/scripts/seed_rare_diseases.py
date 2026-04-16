"""
MedRAG Rare Diseases Seeder
===========================
Seeds rare disease databases to cover specialty gaps.
1. Orphanet (ordo_orphanet.owl)
2. GARD (Genetic and Rare Diseases) API Fallback
"""
import asyncio
import sys
import os
import hashlib
import uuid as _uuid
import re

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

async def seed_rare_diseases(limit: int = 5000):
    print("======================================================================")
    print("  🚀 MedRAG Rare Diseases Seeder")
    print("======================================================================")
    
    total = 0
    ordo_path = os.path.join(RESEARCH_DIR, "Orphanet", "ordo_orphanet.owl")
    
    if not os.path.exists(ordo_path):
        logger.warning(f"Orphanet OWL not found at {ordo_path}")
    else:
        print("\n📚 Loading Orphanet Rare Diseases Ontology (ORDO)...")
        # We'll use a regex-based parser since OWL XML is very heavy for standard parsers
        # We are looking for <owl:Class rdf:about="http://www.orpha.net/ORDO/Orphanet_XXXX">
        # followed by <rdfs:label>Disease Name</rdfs:label>
        
        count = 0
        current_id = None
        current_label = None
        current_def = None
        
        try:
            with open(ordo_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if "<Class rdf:about=\"http://www.orpha.net/ORDO/Orphanet_" in line:
                        m = re.search(r"Orphanet_(\d+)", line)
                        if m:
                            current_id = m.group(1)
                            current_label = None
                            current_def = None
                    
                    elif current_id and "<rdfs:label" in line:
                        m = re.search(r"<rdfs:label[^>]*>(.*?)</rdfs:label>", line)
                        if m:
                            current_label = m.group(1)
                            
                    elif current_id and "<obo:IAO_0000115" in line: # Definition tag in ORDO
                        m = re.search(r"<obo:IAO_0000115[^>]*>(.*?)</obo:IAO_0000115>", line)
                        if m:
                            current_def = m.group(1)
                            
                    elif current_id and "</Class>" in line:
                        if current_label:
                            desc = current_def if current_def else "A rare disease classified by Orphanet."
                            text = f"Rare Disease Database (Orphanet):\nDisease Name: {current_label}\nOrphanet ID: ORPHA:{current_id}\nDescription: {desc}"
                            
                            doc_id = _stable_uuid(f"orphanet_{current_id}")
                            emb = await text_embedder.embed_text(text)
                            
                            await vector_store.store_text_embedding(
                                doc_id=doc_id,
                                embedding=emb,
                                text=text,
                                metadata={
                                    "source": "Orphanet",
                                    "category": "rare_disease",
                                    "specialty": "Genetics / Rare Diseases"
                                }
                            )
                            count += 1
                            if count % 200 == 0:
                                print(f"      ✅ Ingested {count} orphan diseases...")
                            if limit and count >= limit:
                                break
                        current_id = None
                        
        except Exception as e:
            logger.error(f"Error parsing ORDO: {e}")
            
        total += count
        print(f"   ✅ Orphanet complete — {count} rare diseases ingested")

    print("\n======================================================================")
    print(f"  🏁 RARE DISEASES SEEDING COMPLETE! Total inserted: {total}")
    print("======================================================================")
    return total

if __name__ == "__main__":
    asyncio.run(seed_rare_diseases())
