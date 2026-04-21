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
    logger.info(" MEDRAG IMAGING PIPELINE (Process + Append Seed)")
    logger.info("=" * 60)
    
    total_start = time.time()
    
    run_script("backend.pipelines.processing.process_imaging")
    run_script("backend.pipelines.seeding.seed_imaging")
    
    total_time = time.time() - total_start
    logger.info("=" * 60)
    logger.info(f"🏁 5 SMALLEST IMAGING DATASETS PROCESSED & SEEDED IN {total_time/60:.1f} MINUTES!")
    logger.info("=" * 60)
    
    # Auto-cleanup for disk space
    import shutil
    import os
    raw_dir = os.path.join("data", "raw", "imaging")
    targets = ["brats", "isic", "chexpert", "rsna_pneumonia", "mimic_cxr"]
    
    logger.info("🧹 Auto-cleaning raw folders for the successfully seeded datasets...")
    for target in targets:
        target_path = os.path.join(raw_dir, target)
        if os.path.exists(target_path):
            try:
                shutil.rmtree(target_path)
                logger.info(f"  🗑️ Deleted raw dataset: {target}")
            except Exception as e:
                logger.error(f"  ⚠️ Failed to delete {target}: {e}")
                
if __name__ == "__main__":
    main()
