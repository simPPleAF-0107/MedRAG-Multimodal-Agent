"""
Master runner: executes all Tier 1 data processing pipelines in sequence.
Usage: python -m backend.pipelines.processing.run_all_processing
"""
import time
import logging
import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.pipelines.processing.process_text_datasets import process_all_text_datasets
from backend.pipelines.processing.process_ontologies import process_all_ontologies
from backend.pipelines.processing.process_external import process_all_external
from backend.pipelines.processing.process_anti_hallucination import process_all_anti_hallucination
from backend.pipelines.processing.base_processor import PROCESSED_DATA_DIR


def run_all():
    """Run the complete Tier 1 data processing pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    )

    print("\n" + "=" * 70)
    print("  🚀 MEDRAG TIER 1 DATA PROCESSING PIPELINE")
    print("=" * 70)
    print(f"  Output directory: {PROCESSED_DATA_DIR}")
    print("=" * 70)

    total_start = time.time()
    all_results = {}

    # ── Phase 1: Text Datasets ────────────────────────────────────────────────
    start = time.time()
    text_results = process_all_text_datasets()
    all_results.update(text_results)
    print(f"\n  ⏱️ Text processing took {time.time() - start:.1f}s")

    # ── Phase 2: Ontologies ───────────────────────────────────────────────────
    start = time.time()
    ontology_results = process_all_ontologies()
    all_results.update(ontology_results)
    print(f"\n  ⏱️ Ontology processing took {time.time() - start:.1f}s")

    # ── Phase 3: External Datasets ────────────────────────────────────────────
    start = time.time()
    external_results = process_all_external()
    all_results.update(external_results)
    print(f"\n  ⏱️ External processing took {time.time() - start:.1f}s")

    # ── Phase 4: Anti-Hallucination ───────────────────────────────────────────
    start = time.time()
    anti_hall_results = process_all_anti_hallucination()
    all_results.update(anti_hall_results)
    print(f"\n  ⏱️ Anti-hallucination processing took {time.time() - start:.1f}s")

    # ── Final Summary ─────────────────────────────────────────────────────────
    total_time = time.time() - total_start
    total_entries = sum(all_results.values())

    print("\n" + "=" * 70)
    print("  🏁 COMPLETE PROCESSING SUMMARY")
    print("=" * 70)

    # Group by category
    categories = {
        "📖 Text Datasets": ["pubmedqa", "medqa", "medmcqa",
                              "clinical_guidelines", "mtsamples", "mediqa_nli"],
        "🧬 Ontologies": ["icd10", "snomed", "mesh", "orphanet"],
        "🌐 External": ["pubmed_abstracts", "clinical_trials", "healthfc"],
        "🛡️ Anti-Hallucination": ["scifact", "truthfulqa"],
    }

    for cat_name, datasets in categories.items():
        print(f"\n  {cat_name}:")
        cat_total = 0
        for ds in datasets:
            count = all_results.get(ds, 0)
            cat_total += count
            print(f"    {ds:30s} → {count:>8,} entries")
        print(f"    {'SUBTOTAL':30s} → {cat_total:>8,}")

    print(f"\n  {'GRAND TOTAL':32s} → {total_entries:>8,} entries")
    print(f"  ⏱️ Total processing time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print("=" * 70)

    # List output files
    print("\n  📂 Output files in data/processed/:")
    for fname in sorted(os.listdir(PROCESSED_DATA_DIR)):
        if fname.endswith(".jsonl"):
            fpath = os.path.join(PROCESSED_DATA_DIR, fname)
            size_mb = os.path.getsize(fpath) / (1024 * 1024)
            print(f"    {fname:45s} {size_mb:>8.1f} MB")

    return all_results


if __name__ == "__main__":
    run_all()
