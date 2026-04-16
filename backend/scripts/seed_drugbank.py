import os
import asyncio
import xml.etree.ElementTree as ET
from backend.rag.text.chunker import text_chunker
from backend.rag.text.embedder import text_embedder
from backend.rag.vector_store import vector_store
import hashlib
import uuid as _uuid
import logging

def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))

logger = logging.getLogger(__name__)

async def seed_drugbank(limit: int = -1):
    print("======================================================================")
    print("  🚀 MedRAG Pharmacovigilance & DrugBank Seeder")
    print("======================================================================")

    # Note: DrugBank XML uses a namespace, e.g., {http://www.drugbank.ca}
    ns = {'db': 'http://www.drugbank.ca'}

    dataset_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "Research", "latest", "DrugBank"
    )
    xml_file = os.path.join(dataset_dir, "full database.xml")

    if not os.path.exists(xml_file):
        logger.warning(f"DrugBank dataset not found at {xml_file}.")
        logger.warning(f"Please drop the academic 'full database.xml' into {dataset_dir}")
        return 0

    print("📚 Parsing massive DrugBank XML database (this may take a few minutes)...")
    
    total = 0
    try:
        # Use iterparse for memory-efficient parsing of huge XMLs (DrugBank is 1GB+)
        context = ET.iterparse(xml_file, events=('end',))
        
        for event, elem in context:
            if elem.tag.endswith('}drug'):
                # Extract drug details
                name_elem = elem.find('db:name', ns)
                if name_elem is None or not name_elem.text:
                    elem.clear()
                    continue
                    
                name = name_elem.text
                description = getattr(elem.find('db:description', ns), 'text', "") or ""
                indication = getattr(elem.find('db:indication', ns), 'text', "") or ""
                pharmacodynamics = getattr(elem.find('db:pharmacodynamics', ns), 'text', "") or ""
                mechanism = getattr(elem.find('db:mechanism-of-action', ns), 'text', "") or ""
                toxicity = getattr(elem.find('db:toxicity', ns), 'text', "") or ""

                # Compile structured factual block
                content = f"DrugBank Profile: {name}\n\n"
                if description: content += f"Description: {description}\n\n"
                if indication: content += f"Indication: {indication}\n\n"
                if pharmacodynamics: content += f"Pharmacodynamics: {pharmacodynamics}\n\n"
                if mechanism: content += f"Mechanism of Action: {mechanism}\n\n"
                if toxicity: content += f"Toxicity: {toxicity}\n\n"
                
                # Check for significant interactions
                interactions = elem.find('db:drug-interactions', ns)
                inter_text = ""
                if interactions is not None:
                    inter_count = 0
                    for inter in interactions.findall('db:drug-interaction', ns):
                        iname = getattr(inter.find('db:name', ns), 'text', "")
                        desc = getattr(inter.find('db:description', ns), 'text', "")
                        if iname and desc:
                            inter_text += f"- {iname}: {desc}\n"
                            inter_count += 1
                            if inter_count > 10:  # Limit top 10 interactions to avoid massive chunking overload
                                inter_text += "- (Additional interactions omitted for brevity)\n"
                                break
                    if inter_text:
                        content += f"Notable Drug Interactions:\n{inter_text}"

                # Chunk and Embed
                chunks = text_chunker.chunk_text(content)
                for chunk in chunks:
                    doc_id = _stable_uuid(f"drugbank_{name}_{hash(chunk)}")
                    emb = await text_embedder.embed_text(chunk)
                    
                    await vector_store.store_text_embedding(
                        doc_id=doc_id,
                        embedding=emb,
                        text=chunk,
                        metadata={
                            "source": "DrugBank",
                            "category": "pharmacology",
                            "drug_name": name
                        }
                    )
                
                total += 1
                if total % 100 == 0:
                    print(f"      ✅ Ingested {total} DrugBank pharmacological profiles...")
                
                # Clean up memory
                elem.clear()

                if limit > 0 and total >= limit:
                    break

    except Exception as e:
        logger.error(f"Failed to parse DrugBank XML stream: {e}")

    print("\n======================================================================")
    print(f"  🏁 DRUGBANK SEEDING COMPLETE! Total inserted: {total}")
    print("======================================================================")
    return total

if __name__ == "__main__":
    asyncio.run(seed_drugbank())
