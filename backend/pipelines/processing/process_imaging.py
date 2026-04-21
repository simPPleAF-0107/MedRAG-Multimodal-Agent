import os
import zipfile
import json
import logging
from .base_processor import RAW_DATA_DIR, PROCESSED_DATA_DIR, save_processed
from PIL import Image
import io

logger = logging.getLogger(__name__)

TARGET_DATASETS = ["brats", "isic", "chexpert", "rsna_pneumonia", "mimic_cxr"]

def process_imaging():
    """Extract specifically the 5 smallest imaging datasets."""
    source_dir = os.path.join(RAW_DATA_DIR, 'imaging')
    output_file = "imaging_cleaned.jsonl"
    image_out_dir = os.path.join(PROCESSED_DATA_DIR, "images")
    os.makedirs(image_out_dir, exist_ok=True)
    
    if not os.path.exists(source_dir):
        logger.warning(f"Directory {source_dir} not found. Skipping imaging.")
        return 0

    entries = []
    processed_count = 0

    # Process only the target datasets
    for dataset_name in TARGET_DATASETS:
        dataset_path = os.path.join(source_dir, dataset_name)
        if not os.path.exists(dataset_path):
            logger.warning(f"Dataset directory {dataset_path} not found.")
            continue
            
        logger.info(f"Processing imaging dataset: {dataset_name}")
        
        # Look for zip archives in the dataset directory
        for root, _, files in os.walk(dataset_path):
            for file in files:
                if file.endswith('.zip'):
                    zip_path = os.path.join(root, file)
                    logger.info(f"  Extracting images from {zip_path}")
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as z:
                            image_files = [n for n in z.namelist() if n.lower().endswith(('.png', '.jpg', '.jpeg'))]
                            
                            for img_name in image_files:
                                try:
                                    img_data = z.read(img_name)
                                    
                                    # Use PIL to resize and verify
                                    img = Image.open(io.BytesIO(img_data)).convert('RGB')
                                    img.thumbnail((768, 768)) # Resize slightly smaller for massive datasets
                                    
                                    safe_name = os.path.basename(img_name).replace(" ", "_")
                                    # Use dataset prefix and count to ensure uniqueness
                                    safe_name = f"{dataset_name}_{processed_count}_{safe_name}" 
                                    dest_path = os.path.join(image_out_dir, safe_name)
                                    
                                    img.save(dest_path, format="JPEG", quality=85)
                                    
                                    entries.append({
                                        "image_path": dest_path,
                                        "source": dataset_name,
                                        "type": "medical_imaging",
                                        "specialty": "Radiology", 
                                        "metadata": {
                                            "original_filename": img_name
                                        }
                                    })
                                    processed_count += 1
                                    
                                    if len(entries) >= 5000:
                                        save_processed(entries, output_file, append=True)
                                        entries.clear()
                                        
                                except Exception as e:
                                    # Log only first few errors to avoid spam
                                    if processed_count < 5:
                                        logger.warning(f"    Skipped broken image {img_name}: {e}")
                                    
                    except Exception as e:
                        logger.error(f"  Failed extracting {zip_path}: {e}")

    # Flush remaining
    if entries:
        save_processed(entries, output_file, append=True)

    logger.info(f"Saved {processed_count} images for datasets {TARGET_DATASETS} to data/processed/images/ -> {output_file}")
    return processed_count

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
    process_imaging()
