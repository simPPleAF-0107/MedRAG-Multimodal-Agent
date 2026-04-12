"""
MedRAG Unified Medical Data Orchestrator
=========================================
Runs all seeder scripts sequentially. Tracks time and point counts.

Run: python -m backend.scripts.seed_all_medical
"""
import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.vector_store import vector_store

async def main():
    print("=" * 70)
    print("  🚀 MedRAG UNIFIED MEDICAL KNOWLEDGE MEGA-SEEDER 🚀")
    print("=" * 70)
    print("This will download, chunk, and embed thousands of medical documents.")
    print("Depending on hardware and network, this may take 1-4 hours.")
    print("If interrupted, it is safe to re-run (duplicates are prevented via consistent UUIDs).")
    print("=" * 70)
    print()

    start_count = vector_store.get_text_count()
    start_time = time.time()

    # Import seeders dynamically to avoid loading everything at once if a run fails
    
    # 1. Base datasets (fastest first)
    from backend.scripts.seed_specialty_expanded import seed_specialty_expanded
    await seed_specialty_expanded()
    
    from backend.scripts.seed_icd10_snomed import seed_icd10
    await seed_icd10()
    
    from backend.scripts.seed_medical_guidelines import seed_medical_guidelines
    await seed_medical_guidelines()
    
    from backend.scripts.seed_medlineplus import seed_medlineplus
    await seed_medlineplus()

    # 2. Large API datasets
    from backend.scripts.seed_openfda import seed_openfda
    await seed_openfda()
    
    from backend.scripts.seed_clinicaltrials import seed_clinicaltrials
    await seed_clinicaltrials()
    
    from backend.scripts.seed_pubmed_abstracts import seed_pubmed_abstracts
    await seed_pubmed_abstracts()
    
    # Invalidate BM25 cache
    bm25_path = os.path.join(os.path.dirname(settings.QDRANT_DB_DIR), "vector-db", "bm25_index.pkl")
    if os.path.exists(bm25_path):
        os.remove(bm25_path)
        print("🗑️ Cleared BM25 cache index for rebuild on next retrieval query.")

    end_count = vector_store.get_text_count()
    elapsed = time.time() - start_time
    delta = end_count - start_count
    
    print("\n" + "=" * 70)
    print(f"  🏁 ALL MEDICAL SEEDING COMPLETE 🏁")
    print(f"  Total pipeline time: {elapsed / 60:.1f} minutes")
    print(f"  New embeddings added to Qdrant: {delta:,}")
    print(f"  Total Qdrant collection size: {end_count:,}")
    print("=" * 70)

if __name__ == "__main__":
    from backend.config import settings
    asyncio.run(main())
