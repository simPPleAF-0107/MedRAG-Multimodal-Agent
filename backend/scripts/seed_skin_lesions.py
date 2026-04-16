"""
MedRAG Dermatology Vector Seeder
=================================
Seeds dermatology images and clinical metadata from local Research datasets
to cover "knowledge gaps" preventing accurate differential diagnosis of skin lesions.

Designed to utilize CUDA / GPU acceleration for bulk ingestion.

Run manually via terminal:
    python -m backend.scripts.seed_skin_lesions --limit 500
"""

import asyncio
import sys
import os
import io
import time
import zipfile
import hashlib
import uuid as _uuid
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder
from backend.rag.image.clip_embedder import clip_embedder
from backend.utils.logger import logger

RESEARCH_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "Research", "latest"
)

# Comprehensive mapping of ISIC abbreviation tags to textbook clinical diagnoses
DX_MAP = {
    "akiec": "Actinic keratoses and intraepithelial carcinoma / Bowen's disease",
    "bcc": "Basal cell carcinoma",
    "bkl": "Benign keratosis-like lesion (solar lentigines / seborrheic keratoses)",
    "df": "Dermatofibroma",
    "nv": "Melanocytic nevus",
    "mel": "Melanoma",
    "vasc": "Vascular lesion (angiomas, angiokeratomas, pyogenic granulomas)",
    "NV": "Melanocytic nevus",
    "MEL": "Melanoma",
    "BCC": "Basal cell carcinoma",
}

def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))


async def _process_parquet_dir(parquet_dir: str, source_name: str, limit: int = None):
    if not os.path.exists(parquet_dir):
        logger.warning(f"Parquet directory not found at {parquet_dir}")
        return 0

    try:
        import pandas as pd
    except ImportError:
        logger.error("pandas or pyarrow not installed. Please run: pip install pandas pyarrow fastparquet")
        return 0

    count = 0
    parquets = [f for f in os.listdir(parquet_dir) if f.endswith('.parquet')]
    
    if not parquets:
        logger.warning(f"No parquet files found in {parquet_dir}")
        return 0

    print(f"\n📚 Loading {source_name} datasets from Parquet...")
    
    for p in parquets:
        if limit is not None and count >= limit:
            break
            
        p_path = os.path.join(parquet_dir, p)
        print(f"   Parsing {p}...")
        df = pd.read_parquet(p_path)
        
        for _, row in df.iterrows():
            if limit is not None and count >= limit:
                break
            
            # Extract Image Bytes
            img_col = row.get("image", None)
            if img_col is None or not isinstance(img_col, dict) or "bytes" not in img_col:
                continue
            
            try:
                img_bytes = img_col["bytes"]
                pil_image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            except Exception:
                continue
            
            # Extract Metadata
            dx = row.get("dx", row.get("label", "unknown"))
            if str(dx).isdigit():
                diagnosis = "Skin Lesion (Label: " + str(dx) + ")"
            else:
                diagnosis = DX_MAP.get(str(dx).lower(), str(dx))
                
            age = row.get("age", "Unknown")
            sex = row.get("sex", "Unknown")
            loc = row.get("localization", "Unknown")
            
            clinical_text = (
                f"Dermatology Case from {source_name}:\n"
                f"Final Diagnosis: {diagnosis}\n"
                f"Patient Profile: {age}-year-old {sex}\n"
                f"Anatomical Location: {loc}"
            )
            
            doc_id = _stable_uuid(f"{source_name}_{count}")
            
            # 1. Embed Text
            text_emb = await text_embedder.embed_text(clinical_text)
            await vector_store.store_text_embedding(
                doc_id=doc_id,
                embedding=text_emb,
                text=clinical_text,
                metadata={"source": source_name, "specialty": "Dermatology", "diagnosis": diagnosis}
            )
            
            # 2. Embed Image
            img_emb = await clip_embedder.embed_image(pil_image)
            # Since Qdrant is currently locally hosted, we drop the raw bytes from payload to save disk
            # For production, we would upload to S3 and save the URL.
            await vector_store.store_image_embedding(
                image_id=doc_id,
                embedding=img_emb,
                metadata={"source": source_name, "specialty": "Dermatology", "diagnosis": diagnosis}
            )
            
            count += 1
            if count % 100 == 0:
                print(f"      ✅ Ingested {count} multimodal pairs...")

    return count


async def seed_dermnet_zip(limit: int = None):
    zip_path = os.path.join(RESEARCH_DIR, "DermNet.zip")
    if not os.path.exists(zip_path):
        logger.warning(f"DermNet.zip not found at {zip_path}")
        return 0

    print("\n📚 Loading DermNet from Zip...")
    count = 0
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        for file_info in z.infolist():
            if limit is not None and count >= limit:
                break
                
            if file_info.is_dir() or not file_info.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
                
            # Path usually looks like: train/Acne and Rosacea Photos/acne-123.jpg
            parts = file_info.filename.split('/')
            if len(parts) >= 2:
                folder_name = parts[-2]
            else:
                folder_name = "Unknown Skin Condition"
                
            diagnosis = folder_name.replace("Photos", "").replace("_", " ").strip()
            
            try:
                img_data = z.read(file_info.filename)
                pil_image = Image.open(io.BytesIO(img_data)).convert("RGB")
            except Exception:
                continue

            clinical_text = f"Dermatology Case from DermNet NZ:\nVisual findings indicate: {diagnosis}"
            doc_id = _stable_uuid(f"dermnet_{count}")
            
            # 1. Embed Text
            text_emb = await text_embedder.embed_text(clinical_text)
            await vector_store.store_text_embedding(
                doc_id=doc_id,
                embedding=text_emb,
                text=clinical_text,
                metadata={"source": "DermNet", "specialty": "Dermatology", "diagnosis": diagnosis}
            )
            
            # 2. Embed Image
            img_emb = await clip_embedder.embed_image(pil_image)
            await vector_store.store_image_embedding(
                image_id=doc_id,
                embedding=img_emb,
                metadata={"source": "DermNet", "specialty": "Dermatology", "diagnosis": diagnosis}
            )
            
            count += 1
            if count % 100 == 0:
                print(f"      ✅ Ingested {count} DermNet pairs...")

    return count


async def seed_ham10000_raw(limit: int = None):
    """Seed HAM10000 from the raw Dataverse download (JPG images + CSV metadata).

    Expected directory structure under Research/latest/:
      ham10000/
        dataverse_files/
          HAM10000_metadata              <- CSV (lesion_id, image_id, dx, age, sex, localization)
          HAM10000_images_combined_600x450/
            ISIC_0024306.jpg
            ...
    """
    meta_path = os.path.join(RESEARCH_DIR, "ham10000", "dataverse_files", "HAM10000_metadata")
    img_dir = os.path.join(RESEARCH_DIR, "ham10000", "dataverse_files", "HAM10000_images_combined_600x450")

    if not os.path.exists(meta_path):
        logger.warning(f"HAM10000 metadata not found at {meta_path}")
        return 0
    if not os.path.isdir(img_dir):
        logger.warning(f"HAM10000 image directory not found at {img_dir}")
        return 0

    try:
        import pandas as pd
    except ImportError:
        logger.error("pandas not installed. Please run: pip install pandas")
        return 0

    print(f"\n📚 Loading HAM10000 from raw Dataverse download...")
    df = pd.read_csv(meta_path)
    if limit:
        df = df.head(limit)

    count = 0
    for _, row in df.iterrows():
        image_id_str = str(row.get("image_id", ""))
        img_path = os.path.join(img_dir, f"{image_id_str}.jpg")

        if not os.path.exists(img_path):
            continue

        try:
            pil_image = Image.open(img_path).convert("RGB")
        except Exception:
            continue

        dx = str(row.get("dx", "unknown"))
        diagnosis = DX_MAP.get(dx.lower(), dx)
        age = row.get("age", "Unknown")
        sex = row.get("sex", "Unknown")
        loc = row.get("localization", "Unknown")

        clinical_text = (
            f"Dermatology Case from HAM10000:\n"
            f"Final Diagnosis: {diagnosis}\n"
            f"Patient Profile: {age}-year-old {sex}\n"
            f"Anatomical Location: {loc}"
        )

        doc_id = _stable_uuid(f"ham10000_raw_{count}")

        # 1. Embed Text
        text_emb = await text_embedder.embed_text(clinical_text)
        await vector_store.store_text_embedding(
            doc_id=doc_id,
            embedding=text_emb,
            text=clinical_text,
            metadata={"source": "HAM10000", "specialty": "Dermatology", "diagnosis": diagnosis}
        )

        # 2. Embed Image
        img_emb = await clip_embedder.embed_image(pil_image)
        await vector_store.store_image_embedding(
            image_id=doc_id,
            embedding=img_emb,
            metadata={"source": "HAM10000", "specialty": "Dermatology", "diagnosis": diagnosis}
        )

        count += 1
        if count % 200 == 0:
            print(f"      ✅ Ingested {count} HAM10000 multimodal pairs...")

    print(f"   ✅ HAM10000 complete — {count} multimodal pairs ingested")
    return count

async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of images per dataset to seed")
    args = parser.parse_args()

    print("=" * 70)
    print("  🧬 MedRAG Dermatology Deep-Seeder (GPU Accelerated) 🧬")
    print("=" * 70)
    if args.limit:
        print(f"  [Mode] Limiting to {args.limit} records per dataset.")
    else:
        print("  [Mode] FULL EXTRACTION. This may take hours.")
    print("=" * 70)
    
    start = time.time()
    
    isic_2019_dir = os.path.join(RESEARCH_DIR, "isic2019")
    ham_dir = os.path.join(RESEARCH_DIR, "ISIC", "skin_cancer_data", "data")
    
    c1 = await _process_parquet_dir(isic_2019_dir, "ISIC 2019 Archive", limit=args.limit)
    c2 = await _process_parquet_dir(ham_dir, "HAM10000 Skin Cancer", limit=args.limit)
    c3 = await seed_dermnet_zip(limit=args.limit)
    
    elapsed = time.time() - start
    total = c1 + c2 + c3
    
    print("\n" + "=" * 70)
    print(f"  🏁 DERMATOLOGY SEEDING COMPLETE 🏁")
    print(f"  New Multimodal Pairs Extracted: {total:,}")
    print(f"  Processing Time: {elapsed / 60:.1f} minutes")
    print("  These datasets now link directly to the multimodal RAG agent.")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
