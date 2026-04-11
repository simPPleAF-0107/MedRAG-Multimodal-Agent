"""
MedRAG Local SLAKE Ingestion Script
====================================
Parses the local `Slake.zip` archive without extracting raw files to disk,
and ingests its Q&A pairs and images directly into the Qdrant multimodal vector database.
"""
import sys
import os
import asyncio
import hashlib
import uuid as _uuid
import time
import zipfile
import json
import io
from PIL import Image

# Add project root to path for backend module resolution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.image.clip_embedder import clip_embedder
from backend.rag.vector_store import vector_store

def _stable_uuid(text: str) -> str:
    """Deterministic UUID from a string to avoid duplicates on re-runs."""
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))

async def seed_local_slake():
    zip_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../research/Slake.zip"))
    
    if not os.path.exists(zip_path):
        print(f"[ERROR] Could not find Slake.zip at {zip_path}")
        return 0

    print(f"\n[INFO] Opening {zip_path}...")
    
    total_embedded = 0
    seen_images_cache = {}  # Cache embeddings to prevent re-computing identical image bytes
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            json_files = ['Slake1.0/train.json', 'Slake1.0/validate.json', 'Slake1.0/test.json']
            
            for file_name in json_files:
                try:
                    with zf.open(file_name) as f:
                        data = json.load(f)
                        print(f"\n[INFO] Found {len(data)} entries in {file_name}")
                        
                        count_for_file = 0
                        for row in data:
                            img_path = f"Slake1.0/imgs/{row.get('img_name')}"
                            question = row.get("question", "")
                            answer = row.get("answer", "")
                            location = row.get("location", "")
                            modality = row.get("modality", "")
                            
                            doc_id = _stable_uuid(f"slake_local_{row.get('img_id')}_{row.get('qid')}")
                            
                            # Deduplicate question entries to avoid empty QAs
                            if not question or not answer:
                                continue
                                
                            try:
                                # Open image from zip entirely in memory
                                with zf.open(img_path) as img_file:
                                    img_bytes = img_file.read()
                                    
                                # Compute or pull cached embedding
                                img_hash = hashlib.md5(img_bytes).hexdigest()
                                if img_hash in seen_images_cache:
                                    embedding = seen_images_cache[img_hash]
                                else:
                                    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                                    embedding = await clip_embedder.embed_image(img)
                                    seen_images_cache[img_hash] = embedding

                                metadata = {
                                    "source": "SLAKE-Local",
                                    "type": "multimodal_medical_vqa",
                                    "question": question[:200],
                                    "modality": modality,
                                    "anatomy": location,
                                    "description": f"[{modality}] Medical Query: {question} Findings: {answer}"
                                }

                                await vector_store.store_image_embedding(
                                    image_id=doc_id,
                                    embedding=embedding,
                                    metadata=metadata
                                )
                                count_for_file += 1
                                total_embedded += 1
                                
                                if count_for_file % 100 == 0:
                                    print(f"   [SUCCESS] Embedded {count_for_file} entries from {file_name.split('/')[-1]}...")
                                    
                            except KeyError:
                                print(f"  [WARN] Missing image file in zip: {img_path}")
                            except Exception as e:
                                print(f"  [WARN] Error processing {img_path}: {e}")
                                
                        print(f"[SUCCESS] Finished {file_name}: {count_for_file} total embeddings.")
                        
                except KeyError:
                    print(f"  [WARN] JSON file not found in zip: {file_name}")
                    
    except Exception as e:
        print(f"[ERROR] Failed to process zip archive: {e}")
        
    return total_embedded

async def main():
    print("=" * 60)
    print("  MedRAG Local SLAKE Ingestion via Memory ZIP Parsing")
    print("=" * 60)

    start = time.time()
    
    total = await seed_local_slake()
    
    elapsed = time.time() - start
    print("\n" + "=" * 60)
    print(f"  [DONE] SLAKE Local Seeding complete!")
    print(f"  Total multimodal vectors created: {total:,}")
    print(f"  Time elapsed: {elapsed / 60:.1f} minutes")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
