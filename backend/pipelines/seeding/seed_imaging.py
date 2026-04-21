import asyncio
import os
import sys
import logging
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.pipelines.processing.base_processor import PROCESSED_DATA_DIR, load_processed
from backend.rag.image.clip_embedder import clip_embedder
from backend.rag.vector_store import vector_store
from PIL import Image

logger = logging.getLogger(__name__)

async def seed_imaging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
    logger.info("Initializing Imaging Seeding...")
    
    filename = "imaging_cleaned.jsonl"
    filepath = os.path.join(PROCESSED_DATA_DIR, filename)
    
    if not os.path.exists(filepath):
        logger.warning(f"No {filename} found.")
        return
        
    entries = load_processed(filename)
    if not entries:
        logger.warning(f"No entries in {filename}")
        return
        
    logger.info(f"Loaded {len(entries)} imaging records. Beginning CLIP embedding to Qdrant...")
    
    total = len(entries)
    successful = 0
    start_time = time.time()
    
    for i, entry in enumerate(entries):
        img_path = entry.get("image_path")
        if not img_path or not os.path.exists(img_path):
            continue
            
        try:
            with Image.open(img_path) as img:
                rgb_img = img.convert('RGB')
                embedding = await clip_embedder.embed_image(rgb_img)
                
            from backend.pipelines.seeding.seed_from_processed import _stable_uuid
            img_id = _stable_uuid(img_path)
            
            await vector_store.store_image_embedding(
                image_id=img_id,
                embedding=embedding,
                metadata=entry
            )
            successful += 1
            
        except Exception as e:
            if successful < 5:
                logger.error(f"Failed to embed image {img_path}: {e}")
            
        if (i+1) % 50 == 0:
            elapsed = time.time() - start_time
            rate = successful / elapsed if elapsed > 0 else 0
            eta = (total - successful) / rate if rate > 0 else 0
            logger.info(f"  Inserted {successful}/{total} image vectors | Rate: {rate:.1f} img/s | ETA: {eta:.0f}s")

    logger.info(f"✅ Imaging seeding complete: inserted {successful} images into image_embeddings.")

def main():
    asyncio.run(seed_imaging())

if __name__ == "__main__":
    main()
