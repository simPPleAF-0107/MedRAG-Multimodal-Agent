import os
import zipfile
import logging
import csv
import io
from .base_processor import RAW_DATA_DIR, PROCESSED_DATA_DIR, save_processed

logger = logging.getLogger(__name__)

def process_drugs():
    """Extract drug data and side effects from TSV and DailyMed/DrugBank dumps."""
    source_dir = os.path.join(RAW_DATA_DIR, 'drugs')
    output_file = os.path.join(PROCESSED_DATA_DIR, "drugs_cleaned.jsonl")
    
    if not os.path.exists(source_dir):
        logger.warning(f"Directory {source_dir} not found. Skipping drugs.")
        return 0

    entries = []
    processed_count = 0

    # Generic robust processor for all drug datasets
    for dataset in ["drugbank", "kegg", "openfda", "sider", "dailymed"]:
        dataset_path = os.path.join(source_dir, dataset)
        if not os.path.exists(dataset_path):
            continue
            
        logger.info(f"Scanning dataset: {dataset}...")
        for root, _, files in os.walk(dataset_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if file.endswith('.tsv') or file.endswith('.csv'):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for idx, line in enumerate(f):
                                if idx > 1000: break  # Limit per file
                                if len(line.strip()) > 10:
                                    entries.append({
                                        "text": f"Drug Interaction/Effect: {line.strip()}",
                                        "source": dataset,
                                        "type": "drug_record",
                                        "specialty": "Pharmacology"
                                    })
                                    processed_count += 1
                                    
                    elif file.endswith('.zip'):
                        with zipfile.ZipFile(file_path, 'r') as z:
                            # Try to extract the first 10 text/json/xml files directly from the zip
                            text_files = [n for n in z.namelist() if n.endswith(('.txt', '.json', '.xml', '.tsv', '.csv'))]
                            for n in text_files[:10]:
                                content = z.read(n).decode('utf-8', errors='ignore')
                                # grab chunk
                                chunk = content[:3000].replace('\n', ' ').strip()
                                if len(chunk) > 50:
                                    entries.append({
                                        "text": f"{dataset} Document extract: {chunk}",
                                        "source": dataset,
                                        "type": "drug_document",
                                        "specialty": "Pharmacology"
                                    })
                                    processed_count += 1
                                    
                except Exception as e:
                    pass

                if len(entries) >= 5000:
                    save_processed(entries, "drugs_cleaned.jsonl", append=True)
                    entries.clear()

    if entries:
        save_processed(entries, "drugs_cleaned.jsonl", append=True)

    logger.info(f"Saved {processed_count} drug entries to drugs_cleaned.jsonl")
    return processed_count

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    process_drugs()
