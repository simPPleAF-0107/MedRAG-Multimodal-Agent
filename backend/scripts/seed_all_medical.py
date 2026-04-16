"""
MedRAG Unified Medical Data Orchestrator
=========================================
Runs all seeder scripts sequentially. Tracks time and point counts.

Run: python -m backend.scripts.seed_all_medical

Current Qdrant stats (as of 2026-04-15):
  - Text embeddings:  ~104,600 points
  - Image embeddings: ~156,300 points
"""
import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config import settings
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

    # ─────────────────────────────────────────────────────────────────────
    # ALREADY SEEDED — do NOT re-run (all confirmed in Qdrant)
    # ─────────────────────────────────────────────────────────────────────

    # 1. seed_specialty_expanded  — 400+ curated specialty paragraphs  ✅ DONE
    # 2. seed_icd10_snomed        — 13 ICD-10 code entries             ✅ DONE
    # 3. seed_medical_guidelines  — 5 clinical guidelines              ✅ DONE
    # 4. seed_medlineplus         — 17 patient education topics (API)  ✅ DONE
    # 5. seed_knowledge           — PubMedQA (1k), MedQA-USMLE (12k),
    #                               MedMCQA (20k), Specialty (90+)     ✅ DONE
    # 6. seed_openfda             — ~2k drug label sections (API)      ✅ DONE
    # 7. seed_clinicaltrials      — ~3k trial summaries (API)          ✅ DONE
    # 8. seed_pubmed_abstracts    — ~5k abstracts (API)                ✅ DONE
    # 9. seed_images              — VQA-RAD (315), PathVQA (2k) (HF)  ✅ DONE
    # 10. seed_local_roco         — ~80k radiology images (ROCO.zip)   ✅ DONE
    # 11. seed_local_slake        — SLAKE multimodal VQA (Slake.zip)   ✅ DONE
    # 12. seed_anti_hallucination — Clinical NLI (30), MIMIC-III (2k),
    #                               CheXpert (1k), Med-MMHL (1.9k)    ✅ DONE (4,956 pts)
    # 13. seed_skin_lesions       — ISIC 2019 (parquet)               ✅ DONE
    # 14. seed_skin_lesions       — DermNet (DermNet.zip)             ✅ DONE

    # 15. HAM10000 Skin Cancer (raw Dataverse download)       ✅ DONE (10,015 pts)

    # ─────────────────────────────────────────────────────────────────────
    # PHASE 1 SEEDERS — NOT YET SEEDED (run these)
    # ─────────────────────────────────────────────────────────────────────

    # 16. Fact Verification (HealthFC, COVID-Fact, BioASQ)
    from backend.scripts.seed_fact_verification import seed_fact_verification
    await seed_fact_verification()

    # 17. Drug Safety (SIDER & RxNorm)
    from backend.scripts.seed_drug_safety import seed_drug_safety
    await seed_drug_safety()

    # 18. Rare Diseases (Orphanet & GARD)
    from backend.scripts.seed_rare_diseases import seed_rare_diseases
    await seed_rare_diseases()

    # 19. Ontologies & Graph (HPO, DO, MeSH)
    from backend.scripts.seed_ontologies import seed_ontologies
    await seed_ontologies()

    # 20. Psychiatry & Mental Health (PsyQA, DSM-5)
    from backend.scripts.seed_psychiatry import seed_psychiatry
    await seed_psychiatry()

    # 21. WikiDoc Clinical Encyclopedia
    from backend.scripts.seed_wikidoc import seed_wikidoc
    await seed_wikidoc()

    # 22. Ophthalmology (ODIR-5K)
    from backend.scripts.seed_odir import seed_odir
    await seed_odir()

    # ─────────────────────────────────────────────────────────────────────
    # Cleanup
    # ─────────────────────────────────────────────────────────────────────
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
    asyncio.run(main())
    