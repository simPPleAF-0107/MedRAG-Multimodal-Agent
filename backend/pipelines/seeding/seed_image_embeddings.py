import asyncio
import os
import sys
import json
import logging
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.pipelines.processing.base_processor import PROCESSED_DATA_DIR, load_processed
from backend.rag.image.clip_embedder import clip_embedder
from backend.rag.vector_store import vector_store
from PIL import Image

logger = logging.getLogger(__name__)

async def seed_images():
    logging.basicConfig(level=logging.INFO)
    logger.info("Initializing Multimodal Seeding...")
    
    filename = "multimodal_cleaned.jsonl"
    filepath = os.path.join(PROCESSED_DATA_DIR, filename)
    
    if not os.path.exists(filepath):
        logger.warning(f"No {filename} found. Make sure process_multimodal has run.")
        return
        
    entries = load_processed(filename)
    if not entries:
        logger.warning("No entries in multimodal_cleaned.jsonl")
        return
        
    logger.info(f"Loaded {len(entries)} image records. Beginning CLIP embedding to Qdrant...")
    
    total = len(entries)
    successful = 0
    start_time = time.time()
    
    for i, entry in enumerate(entries):
        img_path = entry.get("image_path")
        if not img_path or not os.path.exists(img_path):
            continue
            
        try:
            # We open the image and compute CLIP embedding
            with Image.open(img_path) as img:
                # Convert explicitly to RGB to avoid alpha channel errors during tensor comp
                rgb_img = img.convert('RGB')
                embedding = await clip_embedder.embed_image(rgb_img)
                
            # Store in Qdrant
            # Use original filename as UUID seed to prevent duplicates if restarted
            from backend.pipelines.seeding.seed_from_processed import _stable_uuid
            img_id = _stable_uuid(img_path)
            
            await vector_store.store_image_embedding(
                image_id=img_id,
                embedding=embedding,
                metadata=entry
            )
            successful += 1
            
        except Exception as e:
            logger.error(f"Failed to embed image {img_path}: {e}")
            
        if (i+1) % 50 == 0:
            elapsed = time.time() - start_time
            rate = successful / elapsed if elapsed > 0 else 0
            eta = (total - successful) / rate if rate > 0 else 0
            logger.info(f"  Inserted {successful}/{total} image vectors | Rate: {rate:.1f} img/s | ETA: {eta:.0f}s")

    logger.info(f"✅ Multimodal seeding complete: inserted {successful} images into image_embeddings.")

def main():
    asyncio.run(seed_images())

if __name__ == "__main__":
    main()
