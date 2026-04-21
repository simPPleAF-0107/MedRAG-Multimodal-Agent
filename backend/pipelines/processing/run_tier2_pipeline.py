import subprocess
import sys
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
logger = logging.getLogger(__name__)

def run_script(module_name: str, args=None):
    logger.info(f"🚀 Running {module_name}...")
    start = time.time()
    
    cmd = [sys.executable, "-m", module_name]
    if args:
        cmd.extend(args)
        
    result = subprocess.run(cmd)
    
    elapsed = time.time() - start
    if result.returncode == 0:
        logger.info(f"✅ {module_name} completed in {elapsed:.1f}s\n")
    else:
        logger.error(f"❌ {module_name} failed with exit code {result.returncode}\n")
        sys.exit(result.returncode)

def main():
    logger.info("=" * 60)
    logger.info(" MEDRAG TIER 2 PIPELINE (Process + Append Seed)")
    logger.info("=" * 60)
    
    total_start = time.time()
    
    # 1. Processing
    run_script("backend.pipelines.processing.process_clinical_notes")
    run_script("backend.pipelines.processing.process_drugs")
    run_script("backend.pipelines.processing.process_multimodal")
    
    # 2. Seeding (Additive)
    logger.info(">>> Appending text datasets to existing Reference Collection...")
    run_script("backend.pipelines.seeding.seed_from_processed") # without --clear
    
    logger.info(">>> Generating CLIP Embeddings for Multimodal Images...")
    run_script("backend.pipelines.seeding.seed_image_embeddings")
    
    total_time = time.time() - total_start
    logger.info("=" * 60)
    logger.info(f"🏁 ALL TIER 2 DATASETS PROCESSED & SEEDED IN {total_time/60:.1f} MINUTES!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
