"""
MedRAG WikiDoc Clinical Encyclopedia Seeder
===========================================
Seeds Wikipedia/WikiDoc medical articles using the clinical terminology API.
"""
import asyncio
import sys
import os
import hashlib
import uuid as _uuid
import wikipedia

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder
from backend.utils.logger import logger
from backend.rag.text.chunker import text_chunker

def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))

TARGET_ARTICLES = [
    "Ehlers-Danlos syndrome", "Marfan syndrome", "Huntington's disease",
    "Cystic fibrosis", "Sickle cell anemia", "Hemophilia", "Progeria",
    "Gaucher's disease", "Fabry disease", "Pompe disease", "Tay-Sachs disease",
    "Niemann-Pick disease", "Amyotrophic lateral sclerosis", "Multiple sclerosis",
    "Myasthenia gravis", "Lupus erythematosus", "Rheumatoid arthritis",
    "Scleroderma", "Sjogren's syndrome", "Ankylosing spondylitis",
    "Sarcoidosis", "Amyloidosis", "Vasculitis", "Behcet's disease",
    "Kawasaki disease", "Takayasu's arteritis", "Wegener's granulomatosis",
    "Churg-Strauss syndrome", "Polyarteritis nodosa", "Microscopic polyangiitis",
    "Henoch-Schonlein purpura", "Goodpasture syndrome", "Alport syndrome",
    "Polycystic kidney disease", "Medullary cystic kidney disease",
    "Alström syndrome", "Bardet-Biedl syndrome", "Joubert syndrome",
    "Meckel-Gruber syndrome", "Zellweger syndrome", "Refsum disease",
    "X-linked adrenoleukodystrophy", "Krabbe disease", "Metachromatic leukodystrophy"
]

async def seed_wikidoc(limit: int = 1500):
    print("======================================================================")
    print("  🚀 MedRAG WikiDoc & Rare Encyclopedia Seeder")
    print("======================================================================")
    
    total = 0
    print("\n📚 Loading WikiDoc Clinical Encyclopedia...")
    
    for title in TARGET_ARTICLES:
        try:
            page = wikipedia.page(title, auto_suggest=False)
            content = page.content
            
            # Use the default chunk size of text_chunker (500 w/ overlap 50)
            chunks = text_chunker.chunk_text(content)
            for j, chunk in enumerate(chunks):
                if len(chunk) < 50:
                    continue
                    
                text = f"Clinical Encyclopedia ({title}):\n{chunk}"
                doc_id = _stable_uuid(f"wiki_{title}_{j}")
                emb = await text_embedder.embed_text(text)
                
                await vector_store.store_text_embedding(
                    doc_id=doc_id,
                    embedding=emb,
                    text=text,
                    metadata={
                        "source": "WikiDoc",
                        "category": "rare_disease",
                        "specialty": "General Medicine",
                        "disease": title
                    }
                )
                total += 1
                if total % 100 == 0:
                    print(f"      ✅ Ingested {total} WikiDoc chunks...")
                if limit and total >= limit:
                    break
                    
        except Exception as e:
            logger.warning(f"Failed to fetch {title} from Wiki: {e}")
            
        if limit and total >= limit:
            break

    print("\n======================================================================")
    print(f"  🏁 WIKIDOC SEEDING COMPLETE! Total inserted: {total}")
    print("======================================================================")
    return total

if __name__ == "__main__":
    asyncio.run(seed_wikidoc())
