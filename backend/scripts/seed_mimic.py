import os
import asyncio
import csv
from backend.rag.text.chunker import text_chunker
from backend.rag.text.embedder import text_embedder
from backend.rag.vector_store import vector_store
import hashlib
import uuid as _uuid
import logging

def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))

logger = logging.getLogger(__name__)

async def seed_mimic(limit: int = 5000):
    print("======================================================================")
    print("  🚀 MedRAG Clinical EHR (MIMIC-IV) Seeder")
    print("======================================================================")

    dataset_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "Research", "latest", "MIMIC"
    )
    
    # Target clinical notes rather than raw structured tables for deeper LLM reasoning.
    notes_csv = os.path.join(dataset_dir, "discharge.csv")

    if not os.path.exists(notes_csv):
        logger.warning(f"MIMIC-IV discharge notes not found at {notes_csv}.")
        logger.warning("MIMIC-IV is restricted. You must have PhysioNet access and manually drop 'discharge.csv' here.")
        return 0

    print("📚 Parsing MIMIC-IV Clinical Discharge Summaries...")
    
    total = 0
    try:
        # Notes can be very large; handle them gracefully
        with open(notes_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                note_id = row.get("note_id", "")
                subject_id = row.get("subject_id", "")
                text = row.get("text", "")
                
                if not text or not note_id:
                    continue
                    
                # We do not want to embed massive raw logs. We chunk them into sensible clinical blocks.
                chunks = text_chunker.chunk_text(text)
                
                for chunk in chunks:
                    doc_id = _stable_uuid(f"mimic_{note_id}_{hash(chunk)}")
                    emb = await text_embedder.embed_text(chunk)
                    
                    await vector_store.store_text_embedding(
                        doc_id=doc_id,
                        embedding=emb,
                        text=chunk,
                        metadata={
                            "source": "MIMIC-IV",
                            "category": "clinical_ehr",
                            "note_id": note_id,
                            "subject_id": subject_id
                        }
                    )
                
                total += 1
                if total % 100 == 0:
                    print(f"      ✅ Ingested {total} MIMIC-IV Clinical Discharge notes...")
                
                if limit > 0 and total >= limit:
                    break

    except Exception as e:
        logger.error(f"Failed to parse MIMIC-IV CSV stream: {e}")

    print("\n======================================================================")
    print(f"  🏁 MIMIC-IV SEEDING COMPLETE! Total inserted: {total}")
    print("======================================================================")
    return total

if __name__ == "__main__":
    asyncio.run(seed_mimic())
