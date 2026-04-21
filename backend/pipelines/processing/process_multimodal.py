import os
import zipfile
import json
import logging
from .base_processor import RAW_DATA_DIR, PROCESSED_DATA_DIR, save_processed
from PIL import Image
import io

logger = logging.getLogger(__name__)

def process_multimodal():
    """Extract multimodal images and map to captions/questions."""
    source_dir = os.path.join(RAW_DATA_DIR, 'multimodal')
    output_file = os.path.join(PROCESSED_DATA_DIR, "multimodal_cleaned.jsonl")
    image_out_dir = os.path.join(PROCESSED_DATA_DIR, "images")
    os.makedirs(image_out_dir, exist_ok=True)
    
    if not os.path.exists(source_dir):
        logger.warning(f"Directory {source_dir} not found. Skipping multimodal.")
        return 0

    entries = []
    processed_count = 0

    # Look for zip archives
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.zip'):
                zip_path = os.path.join(root, file)
                logger.info(f"Processing images from {zip_path}")
                try:
                    with zipfile.ZipFile(zip_path, 'r') as z:
                        # Extract images directly
                        image_files = [n for n in z.namelist() if n.lower().endswith(('.png', '.jpg', '.jpeg'))]
                        json_files = [n for n in z.namelist() if n.lower().endswith('.json')]
                        
                        # Just extract images and build basic records
                        for img_name in image_files:
                            try:
                                img_data = z.read(img_name)
                                
                                # Use PIL to verify it's a real image and resize if massive locally
                                img = Image.open(io.BytesIO(img_data)).convert('RGB')
                                img.thumbnail((1024, 1024)) # Optimize disk space internally while keeping res
                                
                                # Save out
                                safe_name = os.path.basename(img_name).replace(" ", "_")
                                # Avoid collision if multiple zips have same name
                                safe_name = f"{processed_count}_{safe_name}" 
                                dest_path = os.path.join(image_out_dir, safe_name)
                                
                                img.save(dest_path, format="JPEG", quality=85)
                                
                                entries.append({
                                    "image_path": dest_path,
                                    "source": file,
                                    "type": "multimodal_image",
                                    "specialty": "Radiology",
                                    "metadata": {
                                        # To be enriched by CLIP or associated JSON map if parsed
                                        "original_filename": img_name
                                    }
                                })
                                processed_count += 1
                                
                                if len(entries) >= 5000:
                                    save_processed(entries, "multimodal_cleaned.jsonl", append=True)
                                    entries.clear()
                                    
                            except Exception as e:
                                logger.warning(f"Skipped broken image {img_name}: {e}")
                                
                except Exception as e:
                    logger.error(f"Failed extracting {zip_path}: {e}")

    if entries:
        save_processed(entries, "multimodal_cleaned.jsonl", append=True)

    logger.info(f"Saved {processed_count} images to data/processed/images/ and created multimodal_cleaned.jsonl")
    return processed_count

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    process_multimodal()
