"""
Process Tier 1 anti-hallucination datasets from data/raw/anti_hallucination/.
Handles: scifact (CSV), truthfulqa (CSV).
Skips med_mmhl (4GB zip, Tier 2).
"""
import os
import logging
import pandas as pd

from backend.pipelines.processing.base_processor import (
    RAW_DATA_DIR, StandardizedEntry, is_medical, detect_specialty,
    deduplicate_entries, save_processed,
)

logger = logging.getLogger(__name__)
ANTI_HALL_RAW = os.path.join(RAW_DATA_DIR, "anti_hallucination")


# ── 1. SciFact ────────────────────────────────────────────────────────────────
def process_scifact() -> list[dict]:
    """
    Process SciFact claims + corpus CSVs.
    Claims: id, claim, evidence_doc_id, evidence_label, evidence_sentences, cited_doc_ids
    Corpus: id, title, abstract, ...
    """
    print("\n📖 Processing SciFact...")
    entries = []
    scifact_dir = os.path.join(ANTI_HALL_RAW, "scifact")

    if not os.path.isdir(scifact_dir):
        print("  ⚠️ SciFact directory not found, skipping.")
        return []

    # Load corpus first for evidence matching
    corpus = {}
    corpus_file = os.path.join(scifact_dir, "corpus_train.csv")
    if os.path.exists(corpus_file):
        print(f"  📄 Loading corpus...")
        try:
            corpus_df = pd.read_csv(corpus_file)
            for _, row in corpus_df.iterrows():
                doc_id = str(row.get("doc_id", row.get("id", ""))).strip()
                title = str(row.get("title", "")).strip()
                abstract = str(row.get("abstract", "")).strip()
                if doc_id and abstract:
                    corpus[doc_id] = {"title": title, "abstract": abstract}
            print(f"    ✅ Loaded {len(corpus)} corpus documents")
        except Exception as e:
            print(f"    ⚠️ Error loading corpus: {e}")

    # Process claims
    for fname in os.listdir(scifact_dir):
        if not fname.startswith("claims_") or not fname.endswith(".csv"):
            continue
        fpath = os.path.join(scifact_dir, fname)
        split_name = fname.replace("claims_", "").replace(".csv", "")
        print(f"  📄 Processing {fname}...")

        try:
            df = pd.read_csv(fpath)
            for _, row in df.iterrows():
                claim = str(row.get("claim", "")).strip()
                if not claim or len(claim.split()) < 5:
                    continue

                label = str(row.get("evidence_label", "")).strip()
                doc_id = str(row.get("evidence_doc_id", "")).strip()

                # Try to get evidence from corpus
                evidence_text = ""
                if doc_id in corpus:
                    evidence_text = corpus[doc_id].get("abstract", "")

                combined = f"Scientific Claim: {claim}"
                if evidence_text:
                    combined += f"\nEvidence: {evidence_text[:500]}"
                if label and label != "nan":
                    combined += f"\nVerdict: {label}"

                entry = StandardizedEntry(
                    text=combined,
                    source="scifact",
                    type="fact_verification",
                    specialty=detect_specialty(combined),
                    confidence_weight=0.85,
                    metadata={"label": label, "split": split_name},
                )
                entries.append(entry.to_dict())

            print(f"    ✅ {split_name}: {len(df)} claims processed")
        except Exception as e:
            print(f"    ⚠️ Error processing {fname}: {e}")

    print(f"  📊 SciFact total: {len(entries)} entries")
    return entries


# ── 2. TruthfulQA ─────────────────────────────────────────────────────────────
def process_truthfulqa() -> list[dict]:
    """
    Process TruthfulQA CSVs — filter for medical/health categories only.
    Schema: type, category, question, best_answer, correct_answers, incorrect_answers, source
    """
    print("\n📖 Processing TruthfulQA (medical subset)...")
    entries = []
    truthfulqa_dir = os.path.join(ANTI_HALL_RAW, "truthfulqa")

    if not os.path.isdir(truthfulqa_dir):
        print("  ⚠️ TruthfulQA directory not found, skipping.")
        return []

    # Medical-related categories
    medical_categories = {
        "health", "nutrition", "misconceptions", "science",
    }

    for fname in os.listdir(truthfulqa_dir):
        if not fname.endswith(".csv"):
            continue
        fpath = os.path.join(truthfulqa_dir, fname)
        print(f"  📄 Processing {fname}...")

        try:
            df = pd.read_csv(fpath, encoding="utf-8")
            for _, row in df.iterrows():
                category = str(row.get("category", "")).strip().lower()
                question = str(row.get("question", "")).strip()
                best_answer = str(row.get("best_answer", "")).strip()

                # Filter for medical-adjacent categories
                if category not in medical_categories:
                    # Also keep if question contains medical keywords
                    if not is_medical(question, min_keywords=2):
                        continue

                if not question or not best_answer:
                    continue

                combined = (
                    f"Question: {question}\n"
                    f"Correct Answer: {best_answer}"
                )

                entry = StandardizedEntry(
                    text=combined,
                    source="truthfulqa",
                    type="fact_verification",
                    specialty=detect_specialty(combined),
                    confidence_weight=0.85,
                    metadata={"category": category},
                )
                entries.append(entry.to_dict())
        except Exception as e:
            print(f"    ⚠️ Error processing {fname}: {e}")

    print(f"  📊 TruthfulQA (medical subset) total: {len(entries)} entries")
    return entries


# ── Master runner ─────────────────────────────────────────────────────────────
def process_all_anti_hallucination() -> dict:
    """Run all anti-hallucination processors and save results."""
    print("\n" + "=" * 70)
    print("  🛡️ ANTI-HALLUCINATION PROCESSING PIPELINE")
    print("=" * 70)

    results = {}

    # 1. SciFact
    scifact_entries = process_scifact()
    scifact_entries = deduplicate_entries(scifact_entries)
    save_processed(scifact_entries, "scifact_cleaned.jsonl")
    results["scifact"] = len(scifact_entries)

    # 2. TruthfulQA
    truthfulqa_entries = process_truthfulqa()
    truthfulqa_entries = deduplicate_entries(truthfulqa_entries)
    save_processed(truthfulqa_entries, "truthfulqa_cleaned.jsonl")
    results["truthfulqa"] = len(truthfulqa_entries)

    print("\n" + "=" * 70)
    print("  📊 ANTI-HALLUCINATION PROCESSING SUMMARY")
    print("=" * 70)
    total = 0
    for name, count in results.items():
        print(f"  {name:30s} → {count:>8,} entries")
        total += count
    print(f"  {'TOTAL':30s} → {total:>8,} entries")
    print("=" * 70)

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    process_all_anti_hallucination()
