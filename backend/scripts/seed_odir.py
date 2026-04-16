"""
MedRAG Ophthalmology Seeder
===========================
Seeds the ODIR-5K dataset containing fundus images for 8 eye diseases.
"""
import asyncio
import sys
import os
import hashlib
import uuid as _uuid
from PIL import Image
import csv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder
from backend.rag.image.clip_embedder import clip_embedder
from backend.utils.logger import logger

RESEARCH_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "Research", "latest"
)

def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))

async def seed_odir(limit: int = 2000):
    print("======================================================================")
    print("  🚀 MedRAG ODIR-5K Ophthalmology Seeder")
    print("======================================================================")
    
    total = 0
    odir_dir = os.path.join(RESEARCH_DIR, "ODIR-5K", "archive")
    csv_path = os.path.join(odir_dir, "full_df.csv")
    img_dir = os.path.join(odir_dir, "preprocessed_images")
    
    if not os.path.exists(csv_path) or not os.path.exists(img_dir):
        logger.warning(f"ODIR-5K dataset not found at {odir_dir}")
        return 0
        
    print("\n📚 Loading ODIR-5K Ophthalmology Images...")
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # ODIR-5K has columns like filepath, labels, target, Patient Age, Patient Sex
                # Typically filenames are "0_right.jpg" etc. 
                # Let's extract the target terms
                filename = row.get("filename") or row.get("file_name") # Try common variants
                if not filename:
                    # ODIR full_df often has Left-Fundus and Right-Fundus columns for filenames
                    lf = row.get("Left-Fundus")
                    rf = row.get("Right-Fundus")
                    filenames = [f for f in (lf, rf) if f]
                else:
                    filenames = [filename]
                    
                keywords = row.get("Left-Diagnostic Keywords", "") + " " + row.get("Right-Diagnostic Keywords", "")
                age = row.get("Patient Age", "Unknown")
                sex = row.get("Patient Sex", "Unknown")
                
                for fname in filenames:
                    if not fname: continue
                    img_path = os.path.join(img_dir, fname)
                    if not os.path.exists(img_path):
                        # Some versions use ODIR-5K/ODIR-5K/...
                        img_path = os.path.join(odir_dir, "ODIR-5K", "Training Images", fname)
                        if not os.path.exists(img_path):
                            continue
                    
                    try:
                        pil_image = Image.open(img_path).convert("RGB")
                    except Exception:
                        continue
                        
                    clinical_text = (
                        f"Ophthalmology Fundus Exam (ODIR-5K):\n"
                        f"Patient: {age} year old {sex}\n"
                        f"Diagnostic Keywords: {keywords}"
                    )
                    
                    doc_id = _stable_uuid(f"odir_{fname}")
                    
                    # 1. Embed Image
                    img_emb = await clip_embedder.embed_image(pil_image)
                    await vector_store.store_image_embedding(
                        image_id=doc_id,
                        embedding=img_emb,
                        metadata={"source": "ODIR-5K", "specialty": "Ophthalmology", "keywords": keywords}
                    )
                    
                    # 2. Embed Text
                    text_emb = await text_embedder.embed_text(clinical_text)
                    await vector_store.store_text_embedding(
                        doc_id=doc_id,
                        embedding=text_emb,
                        text=clinical_text,
                        metadata={"source": "ODIR-5K", "specialty": "Ophthalmology"}
                    )
                    
                    total += 1
                    if total % 100 == 0:
                        print(f"      ✅ Ingested {total} ODIR-5K images...")
                    if limit and total >= limit:
                        break
                        
                if limit and total >= limit:
                    break
    except Exception as e:
        logger.error(f"Error parsing ODIR-5K: {e}")

    print("\n======================================================================")
    print(f"  🏁 OPHTHALMOLOGY SEEDING COMPLETE! Total inserted: {total}")
    print("======================================================================")
    return total

if __name__ == "__main__":
    asyncio.run(seed_odir())
