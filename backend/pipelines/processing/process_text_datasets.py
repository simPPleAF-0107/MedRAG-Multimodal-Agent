"""
Process Tier 1 text datasets from data/raw/text/.
Handles: pubmedqa, medqa, medmcqa, clinical_guidelines, mtsamples, mediqa_nli (HF download).
"""
import os
import json
import zipfile
import logging
import pandas as pd

from backend.pipelines.processing.base_processor import (
    RAW_DATA_DIR, StandardizedEntry, is_medical, detect_specialty,
    extract_symptoms, detect_severity, deduplicate_entries, save_processed,
)

logger = logging.getLogger(__name__)
TEXT_RAW = os.path.join(RAW_DATA_DIR, "text")


# ── 1. PubMedQA ──────────────────────────────────────────────────────────────
def process_pubmedqa() -> list[dict]:
    """
    Process PubMedQA parquet files (pqa_labeled, pqa_artificial, pqa_unlabeled).
    Schema: pubid, question, context (dict), long_answer, final_decision
    """
    print("\n📖 Processing PubMedQA...")
    entries = []
    base = os.path.join(TEXT_RAW, "pubmedqa")

    for split_dir in ["pqa_labeled", "pqa_artificial", "pqa_unlabeled"]:
        split_path = os.path.join(base, split_dir)
        if not os.path.isdir(split_path):
            continue
        for fname in os.listdir(split_path):
            if not fname.endswith(".parquet"):
                continue
            fpath = os.path.join(split_path, fname)
            print(f"  📄 Reading {split_dir}/{fname}...")
            df = pd.read_parquet(fpath)
            for _, row in df.iterrows():
                question = str(row.get("question", "")).strip()
                long_answer = str(row.get("long_answer", "")).strip()
                final_decision = str(row.get("final_decision", "")).strip()

                # Build context from dict of contexts
                context_dict = row.get("context", {})
                if isinstance(context_dict, dict):
                    parts = []
                    for v in context_dict.values():
                        try:
                            if isinstance(v, (list, tuple)):
                                parts.append(" ".join(str(x) for x in v))
                            elif hasattr(v, '__iter__') and not isinstance(v, str):
                                parts.append(" ".join(str(x) for x in v))
                            elif v is not None:
                                parts.append(str(v))
                        except Exception:
                            parts.append(str(v))
                    context_text = " ".join(parts)
                elif isinstance(context_dict, str):
                    context_text = context_dict
                else:
                    context_text = str(context_dict) if context_dict is not None else ""

                combined_text = f"Question: {question}\nContext: {context_text}\nAnswer: {long_answer}"
                if len(combined_text.split()) < 20:
                    continue

                symptoms = extract_symptoms(combined_text)
                entry = StandardizedEntry(
                    text=combined_text,
                    source="pubmedqa",
                    type="diagnostic",
                    specialty=detect_specialty(combined_text),
                    symptoms=symptoms if symptoms else None,
                    severity=detect_severity(combined_text),
                    metadata={"final_decision": final_decision, "split": split_dir},
                )
                entries.append(entry.to_dict())

            print(f"    ✅ {split_dir}: {len(df)} rows processed")

    print(f"  📊 PubMedQA total: {len(entries)} entries")
    return entries


# ── 2. MedQA (USMLE) ─────────────────────────────────────────────────────────
def process_medqa() -> list[dict]:
    """
    Process MedQA from zip → JSONL files.
    Schema per line: question, answer, options (dict), answer_idx, meta_info
    """
    print("\n📖 Processing MedQA (USMLE)...")
    entries = []
    zip_path = os.path.join(TEXT_RAW, "medqa", "data_clean.zip")

    if not os.path.exists(zip_path):
        print("  ⚠️ MedQA zip not found, skipping.")
        return []

    with zipfile.ZipFile(zip_path) as z:
        jsonl_files = [n for n in z.namelist()
                       if n.endswith(".jsonl") and "questions/US" in n]
        for jf in jsonl_files:
            split_name = os.path.basename(jf).replace(".jsonl", "")
            print(f"  📄 Reading {jf}...")
            with z.open(jf) as f:
                for line in f:
                    try:
                        item = json.loads(line.decode("utf-8"))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue

                    question = item.get("question", "").strip()
                    answer = item.get("answer", "").strip()
                    options = item.get("options", {})

                    if not question or not answer:
                        continue

                    # Build structured text
                    options_text = " | ".join(
                        f"{k}: {v}" for k, v in options.items()
                    ) if isinstance(options, dict) else ""
                    combined = (
                        f"Clinical Question: {question}\n"
                        f"Options: {options_text}\n"
                        f"Correct Answer: {answer}"
                    )

                    symptoms = extract_symptoms(question)
                    entry = StandardizedEntry(
                        text=combined,
                        source="medqa",
                        type="diagnostic",
                        specialty=detect_specialty(combined),
                        disease=answer,
                        symptoms=symptoms if symptoms else None,
                        severity=detect_severity(combined),
                        confidence_weight=0.9,
                        metadata={"split": split_name,
                                  "meta_info": item.get("meta_info", "")},
                    )
                    entries.append(entry.to_dict())

            print(f"    ✅ {split_name}: done")

    print(f"  📊 MedQA total: {len(entries)} entries")
    return entries


# ── 3. MedMCQA ────────────────────────────────────────────────────────────────
def process_medmcqa() -> list[dict]:
    """
    Process MedMCQA parquet files.
    Schema: id, question, opa..opd, cop (correct option 0-3), exp, subject_name, topic_name
    """
    print("\n📖 Processing MedMCQA...")
    entries = []
    base = os.path.join(TEXT_RAW, "medmcqa")
    option_keys = ["opa", "opb", "opc", "opd"]

    for fname in os.listdir(base):
        if not fname.endswith(".parquet"):
            continue
        fpath = os.path.join(base, fname)
        split_name = fname.replace(".parquet", "").split("-")[0]
        print(f"  📄 Reading {fname}...")
        df = pd.read_parquet(fpath)

        for _, row in df.iterrows():
            question = str(row.get("question", "")).strip()
            if not question or len(question.split()) < 8:
                continue

            cop = row.get("cop")  # Correct option index (0-3)
            options = {k: str(row.get(k, "")) for k in option_keys}
            correct_answer = options.get(option_keys[int(cop)], "") if pd.notna(cop) else ""
            explanation = str(row.get("exp", "")).strip()
            subject = str(row.get("subject_name", "")).strip()
            topic = str(row.get("topic_name", "")).strip()

            options_text = " | ".join(f"{k.upper()}: {v}" for k, v in options.items())
            combined = (
                f"Question: {question}\n"
                f"Options: {options_text}\n"
                f"Answer: {correct_answer}\n"
                f"Explanation: {explanation}"
            )

            # Map subject_name to specialty
            specialty = _medmcqa_subject_to_specialty(subject)

            symptoms = extract_symptoms(question)
            entry = StandardizedEntry(
                text=combined,
                source="medmcqa",
                type="diagnostic",
                specialty=specialty,
                disease=correct_answer if correct_answer else None,
                symptoms=symptoms if symptoms else None,
                severity=detect_severity(combined),
                confidence_weight=0.85,
                metadata={"subject": subject, "topic": topic, "split": split_name},
            )
            entries.append(entry.to_dict())

        print(f"    ✅ {split_name}: {len(df)} rows processed")

    print(f"  📊 MedMCQA total: {len(entries)} entries")
    return entries


def _medmcqa_subject_to_specialty(subject: str) -> str:
    """Map MedMCQA subject_name to our specialty taxonomy."""
    mapping = {
        "anatomy": "General", "physiology": "General", "biochemistry": "General",
        "pathology": "General", "pharmacology": "General", "microbiology": "Infectious Disease",
        "forensic medicine": "General", "ent": "ENT / Otolaryngology",
        "ophthalmology": "Ophthalmology", "dermatology": "Dermatology",
        "psychiatry": "Psychiatry", "radiology": "Radiology",
        "pediatrics": "Pediatrics", "surgery": "General",
        "gynaecology & obstetrics": "Obstetrics", "medicine": "General",
        "dental": "Dental / Oral Surgery", "anaesthesia": "Anesthesiology",
        "orthopaedics": "Orthopedics", "skin": "Dermatology",
        "preventive medicine": "General", "social & preventive medicine": "General",
    }
    return mapping.get(subject.lower().strip(), detect_specialty(subject))


# ── 4. Clinical Guidelines (JSONL) ───────────────────────────────────────────
def process_clinical_guidelines() -> list[dict]:
    """
    Process clinical guidelines JSONL (stream — file is 878MB).
    Schema: id, source, title, clean_text, raw_text, url, overview
    """
    print("\n📖 Processing Clinical Guidelines (streaming 878MB JSONL)...")
    entries = []
    fpath = os.path.join(TEXT_RAW, "clinical_guidelines", "open_guidelines.jsonl")

    if not os.path.exists(fpath):
        print("  ⚠️ Clinical guidelines file not found, skipping.")
        return []

    count = 0
    with open(fpath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue

            text = item.get("clean_text", "") or item.get("raw_text", "")
            if not text or len(text.split()) < 30:
                continue

            # Only keep medically relevant guidelines
            if not is_medical(text, min_keywords=3):
                continue

            title = item.get("title", "")
            source_name = item.get("source", "guideline")

            entry = StandardizedEntry(
                text=text[:5000],  # Cap length to prevent huge entries
                source=f"guideline_{source_name}",
                type="evidence",
                specialty=detect_specialty(text),
                severity=detect_severity(text),
                confidence_weight=0.95,  # Guidelines are high quality
                metadata={"title": title, "guideline_source": source_name},
            )
            entries.append(entry.to_dict())
            count += 1

            if count % 5000 == 0:
                print(f"    ... processed {count} guidelines so far")

    print(f"  📊 Clinical Guidelines total: {len(entries)} entries")
    return entries


# ── 5. MTSamples (CSV) ───────────────────────────────────────────────────────
def process_mtsamples() -> list[dict]:
    """
    Process MTSamples clinical transcriptions CSV.
    Schema: description, medical_specialty, sample_name, transcription, keywords
    """
    print("\n📖 Processing MTSamples...")
    entries = []
    fpath = os.path.join(TEXT_RAW, "mtsamples", "mtsamples.csv")

    if not os.path.exists(fpath):
        print("  ⚠️ MTSamples CSV not found, skipping.")
        return []

    df = pd.read_csv(fpath)
    print(f"  📄 Read {len(df)} rows")

    for _, row in df.iterrows():
        transcription = str(row.get("transcription", "")).strip()
        description = str(row.get("description", "")).strip()
        specialty_raw = str(row.get("medical_specialty", "")).strip()
        keywords = str(row.get("keywords", "")).strip()

        if not transcription or len(transcription.split()) < 20:
            continue

        # Use the raw specialty if available
        specialty = _mtsamples_specialty_map(specialty_raw)

        combined = f"Clinical Transcription ({specialty_raw}):\n{transcription}"
        entry = StandardizedEntry(
            text=combined[:5000],
            source="mtsamples",
            type="clinical_note",
            specialty=specialty,
            symptoms=extract_symptoms(description + " " + transcription),
            severity=detect_severity(transcription),
            confidence_weight=0.8,
            metadata={"description": description[:200], "keywords": keywords[:200]},
        )
        entries.append(entry.to_dict())

    print(f"  📊 MTSamples total: {len(entries)} entries")
    return entries


def _mtsamples_specialty_map(raw_spec: str) -> str:
    """Map MTSamples specialty names to our taxonomy."""
    s = raw_spec.strip().lower()
    mapping = {
        "allergy / immunology": "Rheumatology",
        "bariatrics": "Gastroenterology",
        "cardiovascular / pulmonary": "Cardiology",
        "dentistry": "Dental / Oral Surgery",
        "dermatology": "Dermatology",
        "endocrinology": "Endocrinology",
        "ent - otolaryngology": "ENT / Otolaryngology",
        "gastroenterology": "Gastroenterology",
        "general medicine": "General",
        "hematology - oncology": "Oncology",
        "nephrology": "Nephrology",
        "neurology": "Neurology",
        "neurosurgery": "Neurosurgery",
        "obstetrics / gynecology": "Obstetrics",
        "ophthalmology": "Ophthalmology",
        "orthopedic": "Orthopedics",
        "pediatrics - neonatal": "Pediatrics",
        "psychiatry / psychology": "Psychiatry",
        "radiology": "Radiology",
        "rheumatology": "Rheumatology",
        "surgery": "General",
        "urology": "Urology",
    }
    return mapping.get(s, detect_specialty(raw_spec))


# ── 6. MedIQA NLI (download from HuggingFace) ───────────────────────────────
def process_mediqa_nli() -> list[dict]:
    """
    Download and process MedIQA NLI from HuggingFace.
    Used for anti-hallucination / fact verification.
    """
    print("\n📖 Processing MedIQA NLI (downloading from HuggingFace)...")
    entries = []

    try:
        from datasets import load_dataset
        dataset = load_dataset("bigbio/mediqa_nli", "mediqa_nli_source", split="train",
                               trust_remote_code=True)
        print(f"  📄 Downloaded {len(dataset)} rows")

        for item in dataset:
            premise = str(item.get("premise", "")).strip()
            hypothesis = str(item.get("hypothesis", "")).strip()
            label = str(item.get("label", "")).strip()

            if not premise or not hypothesis:
                continue

            combined = f"Premise: {premise}\nHypothesis: {hypothesis}\nLabel: {label}"
            entry = StandardizedEntry(
                text=combined,
                source="mediqa_nli",
                type="fact_verification",
                specialty=detect_specialty(combined),
                confidence_weight=0.85,
                metadata={"label": label},
            )
            entries.append(entry.to_dict())
    except Exception as e:
        print(f"  ⚠️ Failed to download MedIQA NLI: {e}")
        logger.error(f"MedIQA NLI download failed: {e}")

    print(f"  📊 MedIQA NLI total: {len(entries)} entries")
    return entries


# ── Master runner ─────────────────────────────────────────────────────────────
def process_all_text_datasets() -> dict:
    """Run all text dataset processors and save results."""
    print("\n" + "=" * 70)
    print("  🧠 TEXT DATASET PROCESSING PIPELINE")
    print("=" * 70)

    results = {}

    # 1. PubMedQA
    pubmedqa_entries = process_pubmedqa()
    pubmedqa_entries = deduplicate_entries(pubmedqa_entries)
    save_processed(pubmedqa_entries, "pubmedqa_cleaned.jsonl")
    results["pubmedqa"] = len(pubmedqa_entries)

    # 2. MedQA
    medqa_entries = process_medqa()
    medqa_entries = deduplicate_entries(medqa_entries)
    save_processed(medqa_entries, "medqa_cleaned.jsonl")
    results["medqa"] = len(medqa_entries)

    # 3. MedMCQA
    medmcqa_entries = process_medmcqa()
    medmcqa_entries = deduplicate_entries(medmcqa_entries)
    save_processed(medmcqa_entries, "medmcqa_cleaned.jsonl")
    results["medmcqa"] = len(medmcqa_entries)

    # 4. Clinical Guidelines
    guidelines_entries = process_clinical_guidelines()
    guidelines_entries = deduplicate_entries(guidelines_entries)
    save_processed(guidelines_entries, "clinical_guidelines_cleaned.jsonl")
    results["clinical_guidelines"] = len(guidelines_entries)

    # 5. MTSamples
    mtsamples_entries = process_mtsamples()
    mtsamples_entries = deduplicate_entries(mtsamples_entries)
    save_processed(mtsamples_entries, "mtsamples_cleaned.jsonl")
    results["mtsamples"] = len(mtsamples_entries)

    # 6. MedIQA NLI
    mediqa_entries = process_mediqa_nli()
    mediqa_entries = deduplicate_entries(mediqa_entries)
    save_processed(mediqa_entries, "mediqa_nli_cleaned.jsonl")
    results["mediqa_nli"] = len(mediqa_entries)

    print("\n" + "=" * 70)
    print("  📊 TEXT PROCESSING SUMMARY")
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
    process_all_text_datasets()
