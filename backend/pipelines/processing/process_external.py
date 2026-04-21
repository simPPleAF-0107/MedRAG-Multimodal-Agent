"""
Process Tier 1 external datasets from data/raw/external/.
Handles: pubmed_abstracts (CSV in zip), clinical_trials (small zip only), healthfc (CSV).
"""
import os
import json
import zipfile
import logging
import pandas as pd
import xml.etree.ElementTree as ET

from backend.pipelines.processing.base_processor import (
    RAW_DATA_DIR, StandardizedEntry, is_medical, detect_specialty,
    extract_symptoms, detect_severity, deduplicate_entries, save_processed,
)

logger = logging.getLogger(__name__)
EXTERNAL_RAW = os.path.join(RAW_DATA_DIR, "external")


# ── 1. PubMed Abstracts ──────────────────────────────────────────────────────
def process_pubmed_abstracts() -> list[dict]:
    """
    Process PubMed abstracts from zip → CSV.
    CSV has columns for different topics, each containing list of abstracts.
    """
    print("\n📖 Processing PubMed Abstracts...")
    entries = []
    zip_path = os.path.join(EXTERNAL_RAW, "pubmed_abstracts", "archive.zip")

    if not os.path.exists(zip_path):
        print("  ⚠️ PubMed abstracts zip not found, skipping.")
        return []

    try:
        with zipfile.ZipFile(zip_path) as z:
            csv_files = [n for n in z.namelist() if n.endswith(".csv")]
            for csv_name in csv_files:
                print(f"  📄 Reading {csv_name}...")
                with z.open(csv_name) as f:
                    df = pd.read_csv(f)

                # Each column contains abstract lists for a topic
                for col in df.columns:
                    if col.endswith("_links"):
                        continue  # Skip link columns

                    for _, cell in df[col].items():
                        if pd.isna(cell):
                            continue
                        # Cell may be a string representation of a list of abstracts
                        text = str(cell).strip()
                        if text.startswith("['") or text.startswith('["'):
                            # Parse as list
                            try:
                                import ast
                                abstracts = ast.literal_eval(text)
                                for abstract in abstracts:
                                    abstract = str(abstract).strip()
                                    if len(abstract.split()) < 50:
                                        continue
                                    if not is_medical(abstract, min_keywords=2):
                                        continue

                                    entry = StandardizedEntry(
                                        text=abstract[:3000],
                                        source="pubmed",
                                        type="evidence",
                                        specialty=detect_specialty(abstract),
                                        severity=detect_severity(abstract),
                                        confidence_weight=0.85,
                                        metadata={"topic": col},
                                    )
                                    entries.append(entry.to_dict())
                            except (ValueError, SyntaxError):
                                # Treat as single text
                                if len(text.split()) >= 50 and is_medical(text):
                                    entry = StandardizedEntry(
                                        text=text[:3000],
                                        source="pubmed",
                                        type="evidence",
                                        specialty=detect_specialty(text),
                                        confidence_weight=0.85,
                                        metadata={"topic": col},
                                    )
                                    entries.append(entry.to_dict())
                        elif len(text.split()) >= 50 and is_medical(text):
                            entry = StandardizedEntry(
                                text=text[:3000],
                                source="pubmed",
                                type="evidence",
                                specialty=detect_specialty(text),
                                confidence_weight=0.85,
                                metadata={"topic": col},
                            )
                            entries.append(entry.to_dict())

    except Exception as e:
        print(f"  ⚠️ Error processing PubMed abstracts: {e}")
        logger.error(f"PubMed abstracts error: {e}")

    print(f"  📊 PubMed Abstracts total: {len(entries)} entries")
    return entries


# ── 2. Clinical Trials (small zip only — skip 725MB tar.gz) ──────────────────
def process_clinical_trials() -> list[dict]:
    """
    Process clinical trials from small zip and XML topic file.
    Skips the massive clinicaltrials_xml.tar.gz (725MB) for Tier 1.
    """
    print("\n📖 Processing Clinical Trials...")
    entries = []
    ct_dir = os.path.join(EXTERNAL_RAW, "clinical_trials")

    if not os.path.isdir(ct_dir):
        print("  ⚠️ Clinical trials directory not found, skipping.")
        return []

    # Process topics2022.xml (small file with trial topics)
    topics_path = os.path.join(ct_dir, "topics2022.xml")
    if os.path.exists(topics_path):
        print(f"  📄 Processing topics2022.xml...")
        try:
            tree = ET.parse(topics_path)
            root = tree.getroot()

            for topic in root.iter():
                if topic.text and len(str(topic.text).strip().split()) >= 10:
                    text = topic.text.strip()
                    if is_medical(text, min_keywords=2):
                        entry = StandardizedEntry(
                            text=text[:2000],
                            source="clinical_trials",
                            type="evidence",
                            specialty=detect_specialty(text),
                            symptoms=extract_symptoms(text),
                            confidence_weight=0.85,
                            metadata={"file": "topics2022"},
                        )
                        entries.append(entry.to_dict())
        except Exception as e:
            print(f"    ⚠️ Error with topics2022.xml: {e}")

    # Process small zip
    small_zip = os.path.join(ct_dir, "clinical-trials.zip")
    if os.path.exists(small_zip):
        print(f"  📄 Processing clinical-trials.zip...")
        try:
            with zipfile.ZipFile(small_zip) as z:
                for name in z.namelist():
                    if name.endswith(".xml"):
                        try:
                            with z.open(name) as f:
                                tree = ET.parse(f)
                                root = tree.getroot()

                                # Extract key fields
                                title = _xml_text(root, ".//brief_title") or _xml_text(root, ".//official_title")
                                summary = _xml_text(root, ".//brief_summary/textblock") or _xml_text(root, ".//brief_summary")
                                conditions = [c.text for c in root.findall(".//condition") if c.text]
                                interventions = [i.findtext("intervention_name", "") for i in root.findall(".//intervention")]

                                if not summary or len(summary.split()) < 20:
                                    continue

                                text = f"Clinical Trial: {title}\n"
                                if conditions:
                                    text += f"Conditions: {', '.join(conditions)}\n"
                                if interventions:
                                    text += f"Interventions: {', '.join(i for i in interventions if i)}\n"
                                text += f"Summary: {summary}"

                                entry = StandardizedEntry(
                                    text=text[:3000],
                                    source="clinical_trials",
                                    type="evidence",
                                    specialty=detect_specialty(text),
                                    disease=conditions[0] if conditions else None,
                                    symptoms=extract_symptoms(summary),
                                    confidence_weight=0.85,
                                    metadata={"trial_title": title[:200] if title else ""},
                                )
                                entries.append(entry.to_dict())
                        except Exception:
                            continue
        except Exception as e:
            print(f"    ⚠️ Error with clinical-trials.zip: {e}")

    print(f"  📊 Clinical Trials total: {len(entries)} entries")
    return entries


def _xml_text(root, xpath: str) -> str:
    """Helper to safely extract text from an XML element."""
    el = root.find(xpath)
    if el is not None and el.text:
        return el.text.strip()
    return ""


# ── 3. HealthFC (CSV) ────────────────────────────────────────────────────────
def process_healthfc() -> list[dict]:
    """
    Process HealthFC fact verification CSV.
    Schema: en_claim, en_explanation, en_top_sentences, label, ...
    """
    print("\n📖 Processing HealthFC...")
    entries = []
    fpath = os.path.join(EXTERNAL_RAW, "healthfc", "Datensatz.csv")

    if not os.path.exists(fpath):
        print("  ⚠️ HealthFC CSV not found, skipping.")
        return []

    try:
        df = pd.read_csv(fpath)
        print(f"  📄 Read {len(df)} rows")

        for _, row in df.iterrows():
            claim = str(row.get("en_claim", "")).strip()
            explanation = str(row.get("en_explanation", "")).strip()
            evidence = str(row.get("en_top_sentences", "")).strip()
            label = row.get("label", "")

            if not claim or len(claim.split()) < 5:
                continue

            combined = f"Health Claim: {claim}\nEvidence: {evidence}\nExplanation: {explanation}"

            entry = StandardizedEntry(
                text=combined[:3000],
                source="healthfc",
                type="fact_verification",
                specialty=detect_specialty(combined),
                confidence_weight=0.85,
                metadata={"label": str(label)},
            )
            entries.append(entry.to_dict())
    except Exception as e:
        print(f"  ⚠️ Error processing HealthFC: {e}")

    print(f"  📊 HealthFC total: {len(entries)} entries")
    return entries


# ── Master runner ─────────────────────────────────────────────────────────────
def process_all_external() -> dict:
    """Run all external dataset processors and save results."""
    print("\n" + "=" * 70)
    print("  🌐 EXTERNAL DATASET PROCESSING PIPELINE")
    print("=" * 70)

    results = {}

    # 1. PubMed Abstracts
    pubmed_entries = process_pubmed_abstracts()
    pubmed_entries = deduplicate_entries(pubmed_entries)
    save_processed(pubmed_entries, "pubmed_abstracts_cleaned.jsonl")
    results["pubmed_abstracts"] = len(pubmed_entries)

    # 2. Clinical Trials (small files only)
    ct_entries = process_clinical_trials()
    ct_entries = deduplicate_entries(ct_entries)
    save_processed(ct_entries, "clinical_trials_cleaned.jsonl")
    results["clinical_trials"] = len(ct_entries)

    # 3. HealthFC
    healthfc_entries = process_healthfc()
    healthfc_entries = deduplicate_entries(healthfc_entries)
    save_processed(healthfc_entries, "healthfc_cleaned.jsonl")
    results["healthfc"] = len(healthfc_entries)

    print("\n" + "=" * 70)
    print("  📊 EXTERNAL PROCESSING SUMMARY")
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
    process_all_external()
