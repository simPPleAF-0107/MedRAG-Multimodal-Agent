"""
MedRAG Local ROCO Ingestion Script
====================================
Parses the massive local `ROCO.zip` archive containing ~80,000 radiology images.
It reconstructs the complex mapping between PMC IDs and ROCO IDs,
and embeds them via CLIP into the Qdrant multimodal vector database.
"""
import sys
import os
import asyncio
import hashlib
import uuid as _uuid
import time
import zipfile
import io
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.image.clip_embedder import clip_embedder
from backend.rag.vector_store import vector_store

def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))

async def seed_local_roco():
    zip_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../research/ROCO.zip"))
    
    if not os.path.exists(zip_path):
        print(f"[ERROR] Could not find ROCO.zip at {zip_path}")
        return 0

    print(f"\n[INFO] Opening {zip_path} (6.6 GB Archive) - This may take a moment to scan the file tree...")
    
    total_embedded = 0
    seen_images_cache = {}
    
    caption_map = {}
    image_map = {}
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            print("[INFO] Building Metadata Mapping Tables...")
            
            # 1. Build Dictionary Mapping
            for split in ['train', 'validation', 'test']:
                caption_path = f"all_data/{split}/radiology/captions.txt"
                dlinks_path = f"all_data/{split}/radiology/dlinks.txt"
                
                if caption_path in zf.namelist():
                    lines = zf.read(caption_path).decode('utf-8', errors='ignore').splitlines()
                    for line in lines:
                        if "\t" in line:
                            roco_id, caption = line.split("\t", 1)
                            caption_map[roco_id.strip()] = caption.strip()

                if dlinks_path in zf.namelist():
                    lines = zf.read(dlinks_path).decode('utf-8', errors='ignore').splitlines()
                    for line in lines:
                        parts = line.split("\t")
                        if len(parts) >= 3:
                            roco_id = parts[0].strip()
                            pmc_link = parts[1]
                            # Example: wget -r ftp://.../PMC4083729.tar.gz
                            import re
                            match = re.search(r'(PMC\d+)\.tar\.gz', pmc_link)
                            if match:
                                pmc_id = match.group(1)
                                img_code = parts[2].strip()
                                filename = f"{pmc_id}_{img_code}"
                                image_map[filename] = roco_id

            total_mapped = len(image_map)
            print(f"[INFO] Successfully mapped {total_mapped} ROCO images to their PMC filenames.")
            
            # 2. Iterate and Extract Images
            print("[INFO] Beginning Vector Extraction Pipeline...")
            count = 0
            
            for name in zf.namelist():
                if "radiology/images" in name and name.endswith(".jpg"):
                    filename = name.split("/")[-1]
                    roco_id = image_map.get(filename)
                    
                    if roco_id and roco_id in caption_map:
                        caption = caption_map[roco_id]
                        doc_id = _stable_uuid(f"roco_local_{roco_id}")
                        
                        try:
                            # Read raw bytes
                            img_bytes = zf.read(name)
                            img_hash = hashlib.md5(img_bytes).hexdigest()
                            
                            # Embed
                            if img_hash in seen_images_cache:
                                embedding = seen_images_cache[img_hash]
                            else:
                                img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                                embedding = await clip_embedder.embed_image(img)
                                # Keep cache small to avoid RAM bloat over 80k images
                                if len(seen_images_cache) < 2000:
                                    seen_images_cache[img_hash] = embedding
                            
                            # Storage Metadata
                            metadata = {
                                "source": "ROCO-Local",
                                "type": "radiology_contextual",
                                "description": caption[:500]
                            }

                            await vector_store.store_image_embedding(
                                image_id=doc_id,
                                embedding=embedding,
                                metadata=metadata
                            )
                            count += 1
                            total_embedded += 1
                            
                            if count % 1000 == 0:
                                print(f"   [SUCCESS] Embedded {count:,} ROCO images...")
                                
                        except Exception as e:
                            # Catch silent corruptions in huge datadumps
                            pass
                            
            print(f"[SUCCESS] Complete! Total ROCO vectors ingested: {count:,}")
                    
    except Exception as e:
        print(f"[ERROR] Failed to process zip archive: {e}")
        
    return total_embedded

async def main():
    print("=" * 60)
    print("  MedRAG Local ROCO Ingestion via Memory ZIP Parsing")
    print("=" * 60)

    start = time.time()
    total = await seed_local_roco()
    elapsed = time.time() - start
    
    print("\n" + "=" * 60)
    print(f"  [DONE] ROCO Local Seeding complete!")
    print(f"  Total multimodal vectors created: {total:,}")
    print(f"  Time elapsed: {elapsed / 60:.1f} minutes")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
