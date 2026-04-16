"""
MedRAG Ontologies & Knowledge Graph Seeder
==========================================
Seeds foundational ontologies for GraphRAG and semantic retrieval.
1. HPO (Human Phenotype Ontology) - hp.obo
2. DO (Disease Ontology) - doid.obo
3. MeSH - desc2026.xml
"""
import asyncio
import sys
import os
import hashlib
import uuid as _uuid
import re
import xml.etree.ElementTree as ET

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

async def parse_obo(file_path: str, source_name: str, limit: int = None):
    if not os.path.exists(file_path):
        logger.warning(f"{source_name} not found at {file_path}")
        return 0
        
    print(f"\n📚 Loading {source_name} ({os.path.basename(file_path)})...")
    count = 0
    
    current_term = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line == "[Term]":
                    if "id" in current_term and "name" in current_term:
                        text = f"Ontology: {source_name}\nID: {current_term['id']}\nName: {current_term['name']}"
                        if "def" in current_term:
                            text += f"\nDescription: {current_term['def']}"
                            
                        doc_id = _stable_uuid(f"{source_name}_{current_term['id']}")
                        emb = await text_embedder.embed_text(text)
                        
                        await vector_store.store_text_embedding(
                            doc_id=doc_id,
                            embedding=emb,
                            text=text,
                            metadata={
                                "source": source_name,
                                "category": "ontology",
                                "specialty": "General Medicine"
                            }
                        )
                        count += 1
                        if count % 500 == 0:
                            print(f"      ✅ Ingested {count} {source_name} terms...")
                        if limit and count >= limit:
                            break
                    current_term = {}
                elif line.startswith("id:"):
                    current_term["id"] = line[3:].strip()
                elif line.startswith("name:"):
                    current_term["name"] = line[5:].strip()
                elif line.startswith("def:"):
                    # e.g., def: "Description here" [Ref]
                    m = re.search(r'"(.*?)"', line)
                    if m:
                        current_term["def"] = m.group(1)
    except Exception as e:
        logger.error(f"Error parsing OBO ({source_name}): {e}")
        
    print(f"   ✅ {source_name} complete — {count} terms ingested")
    return count

async def parse_mesh(file_path: str, limit: int = None):
    if not os.path.exists(file_path):
        logger.warning(f"MeSH XML not found at {file_path}")
        return 0
        
    print(f"\n📚 Loading MeSH XML ({os.path.basename(file_path)})...")
    count = 0
    try:
        # Use iterparse to save memory on large XMLs
        context = ET.iterparse(file_path, events=("end",))
        for event, elem in context:
            if elem.tag == "DescriptorRecord":
                ui = elem.findtext(".//DescriptorUI")
                name = elem.findtext(".//DescriptorName/String")
                scope = elem.findtext(".//ScopeNote")
                
                if ui and name:
                    text = f"Ontology: MeSH (Medical Subject Headings)\nID: {ui}\nName: {name}"
                    if scope:
                        text += f"\nDescription: {scope}"
                        
                    doc_id = _stable_uuid(f"MeSH_{ui}")
                    # Await inside a loop for embeddings can be slow, but it works
                    emb = await text_embedder.embed_text(text)
                    
                    await vector_store.store_text_embedding(
                        doc_id=doc_id,
                        embedding=emb,
                        text=text,
                        metadata={
                            "source": "MeSH",
                            "category": "ontology",
                            "specialty": "General Medicine"
                        }
                    )
                    count += 1
                    if count % 1000 == 0:
                        print(f"      ✅ Ingested {count} MeSH terms...")
                    if limit and count >= limit:
                        break
                
                # Free memory
                elem.clear()
    except Exception as e:
        logger.error(f"Error parsing MeSH XML: {e}")
        
    print(f"   ✅ MeSH complete — {count} terms ingested")
    return count

async def seed_ontologies(limit: int = 5000):
    print("======================================================================")
    print("  🚀 MedRAG Ontologies & Knowledge Graph Seeder")
    print("======================================================================")
    
    total = 0
    
    total += await parse_obo(os.path.join(RESEARCH_DIR, "HPO", "hp.obo"), "HPO", limit)
    total += await parse_obo(os.path.join(RESEARCH_DIR, "DO", "doid.obo"), "Disease Ontology", limit)
    
    # Check for descXXXX.xml or similar
    mesh_dir = os.path.join(RESEARCH_DIR, "MeSH")
    mesh_file = None
    if os.path.exists(mesh_dir):
        for f in os.listdir(mesh_dir):
            if f.startswith("desc") and f.endswith(".xml"):
                mesh_file = os.path.join(mesh_dir, f)
                break
                
    if mesh_file:
        total += await parse_mesh(mesh_file, limit)
    else:
        logger.warning("No MeSH XML file found in Research/latest/MeSH/")

    print("\n======================================================================")
    print(f"  🏁 ONTOLOGIES SEEDING COMPLETE! Total inserted: {total}")
    print("======================================================================")
    return total

if __name__ == "__main__":
    asyncio.run(seed_ontologies())
