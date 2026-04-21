import os
import json
import zipfile
import csv
import logging
import io
from .base_processor import RAW_DATA_DIR, PROCESSED_DATA_DIR, save_processed

logger = logging.getLogger(__name__)

def process_clinical_notes():
    """Extract clinical notes from MIMIC ZIP files and save to JSONL."""
    source_dir = os.path.join(RAW_DATA_DIR, 'clinical_notes')
    output_file = os.path.join(PROCESSED_DATA_DIR, "clinical_notes_cleaned.jsonl")
    
    if not os.path.exists(source_dir):
        logger.warning(f"Directory {source_dir} not found. Skipping.")
        return 0

    entries = []
    processed_count = 0

    target_zip = os.path.join(source_dir, "mimic_iii", "MIMIC -III (10000 patients).zip")
    
    if not os.path.exists(target_zip):
        logger.warning(f"Expected MIMIC zip not found at {target_zip}. Searching...")
        # Fallback to search any zip
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.zip') and 'mimic' in file.lower():
                    target_zip = os.path.join(root, file)
                    break
            if os.path.exists(target_zip): break

    if os.path.exists(target_zip):
        logger.info(f"Processing clinical notes from {target_zip}...")
        try:
            with zipfile.ZipFile(target_zip, 'r') as z:
                # Find NOTEEVENTS.csv or similar
                csv_filename = None
                for name in z.namelist():
                    if name.lower().endswith("noteevents.csv"):
                        csv_filename = name
                        break
                
                if csv_filename:
                    # Stream the CSV directly from the zip without unzipping fully into RAM
                    with z.open(csv_filename) as f:
                        text_wrapper = io.TextIOWrapper(f, encoding='utf-8', errors='replace')
                        reader = csv.DictReader(text_wrapper)
                        
                        for row in reader:
                            # We only care about Discharge summaries and Radiology to avoid nursing noise
                            category = row.get("CATEGORY", row.get("category", "")).lower()
                            if "discharge" in category or "radiology" in category:
                                text = row.get("TEXT", row.get("text", "")).strip()
                                if len(text) > 100:
                                    entry = {
                                        "text": text,
                                        "source": "MIMIC-III",
                                        "type": "clinical_note",
                                        "specialty": category.capitalize(),
                                        "metadata": {
                                            "subject_id": row.get("SUBJECT_ID", row.get("subject_id", "")),
                                            "hadm_id": row.get("HADM_ID", row.get("hadm_id", "")),
                                            "chartdate": row.get("CHARTDATE", row.get("chartdate", "")),
                                        }
                                    }
                                    entries.append(entry)
                                    processed_count += 1
                                    
                                    if len(entries) >= 5000:
                                        # Flush to disk to save RAM
                                        save_processed(entries, "clinical_notes_cleaned.jsonl", append=True)
                                        entries.clear()
                                        
        except Exception as e:
            logger.error(f"Failed to process MIMIC zip {target_zip}: {e}")
    else:
        logger.warning("No MIMIC zip files found in data/raw/clinical_notes/")

    if entries:
        save_processed(entries, "clinical_notes_cleaned.jsonl", append=True)

    logger.info(f"Saved {processed_count} clinical notes to clinical_notes_cleaned.jsonl")
    return processed_count

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    process_clinical_notes()
