"""
MedRAG Anti-Hallucination Datasets Seeder
=========================================
Seeds four advanced datasets specialized for reducing LLM hallucinations:
1. Clinical NLI: MEDIQA-NLI + curated fallback  (HuggingFace Parquet, always succeeds)
2. MIMIC-III:    Clinical Grounding             (Local zip — "mimic iii.zip")
                 Reads NOTEEVENTS/NOTEEVENTS_random.csv directly from inside the zip.
3. CheXpert:     Uncertainty in Imaging         (Local zip — "CheXpert.zip")
                 Reads train.csv + images directly from inside the zip.
4. Med-MMHL:     Explicit Misinformation        (Local — GitHub clone + Dropbox CSVs)
                 Looks for fakenews_article/train.csv (columns: content, det_fake_label)
                 Downloaded from the Dropbox link in the Med-MMHL README.

NOTE on MedNLI:
  bigbio/mednli is permanently broken — HuggingFace datasets >=3.x dropped support
  for dataset loading scripts, and trust_remote_code was removed entirely.
  We use MEDIQA-NLI (the direct successor, standard Parquet format) with a
  curated 30-pair clinical NLI fallback corpus that always runs offline.

File layout expected under Research/latest/:
  mimic iii.zip         <- zip with space in name (as downloaded)
  CheXpert.zip
  Med-MMHL/
    fakenews_article/train.csv   (content, det_fake_label columns)
    sentence/train.csv
"""
import asyncio
import sys
import os
import io
import hashlib
import uuid as _uuid
import time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder
from backend.rag.image.clip_embedder import clip_embedder
from backend.utils.logger import logger

RESEARCH_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "Research", "latest"
)

def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))


# =============================================================================
# 1. CLINICAL NLI
#    bigbio/mednli is permanently broken (custom scripts deprecated in datasets
#    >=3.x, trust_remote_code removed). Strategy:
#      a) Try MEDIQA-NLI (successor to MedNLI, standard Parquet, no scripts).
#      b) Always seed the 30-pair curated corpus as offline insurance.
# =============================================================================

# 30 high-quality curated clinical NLI pairs — always seeded regardless.
# Labels: entailment | contradiction | neutral
_FALLBACK_NLI = [
    ("Patient has a history of type 2 diabetes mellitus managed with metformin.",
     "The patient requires insulin therapy.", "neutral"),
    ("Chest X-ray shows bilateral infiltrates consistent with pneumonia.",
     "The patient has pneumonia.", "entailment"),
    ("Patient's troponin level is 0.01 ng/mL, within normal range.",
     "The patient is having a myocardial infarction.", "contradiction"),
    ("ECG reveals ST-elevation in leads II, III, and aVF.",
     "The patient likely has an inferior wall MI.", "entailment"),
    ("Patient denies chest pain, shortness of breath, and palpitations.",
     "The patient has no cardiac symptoms.", "entailment"),
    ("Blood cultures grew Staphylococcus aureus.",
     "The infection is caused by a gram-negative organism.", "contradiction"),
    ("CT head shows no acute intracranial hemorrhage.",
     "The patient has a brain bleed.", "contradiction"),
    ("Serum creatinine is 3.5 mg/dL, elevated from baseline of 1.0 mg/dL.",
     "The patient has acute kidney injury.", "entailment"),
    ("Patient is on warfarin with INR of 3.2.",
     "The patient has a supratherapeutic INR.", "entailment"),
    ("MRI lumbar spine shows herniated disc at L4-L5 with nerve root compression.",
     "The patient's back pain may be radicular.", "entailment"),
    ("Thyroid-stimulating hormone (TSH) is 0.01 mIU/L.",
     "The patient likely has hypothyroidism.", "contradiction"),
    ("Colonoscopy revealed a 2 cm polyp in the sigmoid colon.",
     "No polyps were found during the colonoscopy.", "contradiction"),
    ("Patient is allergic to penicillin.",
     "Amoxicillin can be safely administered to this patient.", "contradiction"),
    ("HbA1c is 9.5%, above the target of 7%.",
     "The patient's diabetes is poorly controlled.", "entailment"),
    ("Echocardiogram shows ejection fraction of 25%.",
     "The patient has severely reduced cardiac function.", "entailment"),
    ("Urine dipstick shows 3+ protein.",
     "The patient may have nephrotic syndrome.", "neutral"),
    ("The patient's O2 saturation is 88% on room air.",
     "The patient is hypoxic.", "entailment"),
    ("CBC reveals WBC of 18,000/uL with left shift.",
     "There is evidence of systemic infection.", "entailment"),
    ("Patient's blood pressure is 180/110 mmHg on two readings.",
     "The patient has stage 2 hypertension.", "entailment"),
    ("Lumbar puncture shows xanthochromia and elevated RBCs.",
     "The CSF findings are consistent with subarachnoid hemorrhage.", "entailment"),
    ("Patient's potassium level is 2.8 mEq/L.",
     "The patient is hyperkalemic.", "contradiction"),
    ("Skin biopsy confirms melanoma with Breslow depth of 1.8 mm.",
     "Sentinel lymph node biopsy may be indicated.", "entailment"),
    ("The patient has been on corticosteroids for 3 months.",
     "The patient is at risk for adrenal suppression.", "entailment"),
    ("Spirometry shows FEV1/FVC ratio of 0.62 with 15% post-bronchodilator improvement.",
     "The patient has obstructive lung disease.", "entailment"),
    ("Patient has no family history of cardiovascular disease.",
     "Family history increases this patient's cardiac risk.", "contradiction"),
    ("DEXA scan shows T-score of -2.7 at the lumbar spine.",
     "The patient has osteoporosis.", "entailment"),
    ("Anti-dsDNA antibodies are positive at high titer.",
     "The patient may have systemic lupus erythematosus.", "entailment"),
    ("Liver enzymes (ALT 450, AST 380) are significantly elevated.",
     "The patient has normal liver function.", "contradiction"),
    ("Patient presents with sudden onset severe headache described as 'worst of my life'.",
     "Subarachnoid hemorrhage must be ruled out.", "entailment"),
    ("Hemoglobin A1c is 5.4%.",
     "The patient has diabetes mellitus.", "contradiction"),
]


async def seed_clinical_nli(max_entries: int = 5000):
    """Seed clinical NLI data for contradiction / entailment detection.

    Tries MEDIQA-NLI (HuggingFace Parquet) first, then falls back to the
    embedded curated corpus. The curated corpus is always seeded regardless.
    """
    print("\n🧠 [1/4] Loading Clinical NLI (Reasoning & Inference)...")
    total_count = 0

    # ── Attempt: MEDIQA-NLI (Parquet, no custom scripts needed) ──────────────
    try:
        from datasets import load_dataset
        print("   Trying MEDIQA-NLI (bigbio/mediqa_nli) ...")
        ds = load_dataset("bigbio/mediqa_nli", "mediqa_nli_source", split="train")

        count = 0
        for row in ds:
            if count >= max_entries:
                break
            premise    = str(row.get("premise", "") or row.get("sentence1", ""))
            hypothesis = str(row.get("hypothesis", "") or row.get("sentence2", ""))
            label      = str(row.get("label", row.get("gold_label", "unknown")))
            if not premise or not hypothesis:
                continue

            chunk = (
                f"Clinical Context: {premise}\n"
                f"Logical Hypothesis: {hypothesis}\n"
                f"Truth Value: {label}"
            )
            doc_id = _stable_uuid(f"mediqa_nli_{count}")
            emb = await text_embedder.embed_text(chunk)
            await vector_store.store_text_embedding(
                doc_id=doc_id, embedding=emb, text=chunk,
                metadata={"source": "MEDIQA-NLI", "category": "clinical_reasoning", "label": label}
            )
            count += 1
            if count % 1000 == 0:
                print(f"   ✅ MEDIQA-NLI: {count} pairs ingested")

        print(f"   ✅ MEDIQA-NLI complete — {count} entries")
        total_count += count

    except Exception as e:
        print(f"   ⚠️  MEDIQA-NLI unavailable ({type(e).__name__}). Using curated fallback.")

    # ── Always: curated 30-pair clinical NLI corpus ───────────────────────────
    print(f"   Seeding {len(_FALLBACK_NLI)} curated clinical NLI pairs ...")
    for i, (premise, hypothesis, label) in enumerate(_FALLBACK_NLI):
        chunk = (
            f"Clinical Context: {premise}\n"
            f"Logical Hypothesis: {hypothesis}\n"
            f"Truth Value: {label}"
        )
        doc_id = _stable_uuid(f"mednli_curated_{i}")
        emb = await text_embedder.embed_text(chunk)
        await vector_store.store_text_embedding(
            doc_id=doc_id, embedding=emb, text=chunk,
            metadata={"source": "MedNLI_Curated", "category": "clinical_reasoning", "label": label}
        )
    total_count += len(_FALLBACK_NLI)
    print(f"   ✅ Curated NLI complete — {len(_FALLBACK_NLI)} pairs seeded")

    print(f"   ✅ Clinical NLI total — {total_count} entries")
    return total_count


# =============================================================================
# 2. MIMIC-III — Clinical Notes (reads directly from zip, no extraction needed)
# =============================================================================
async def seed_mimic_iii(limit: int = 2000):
    """Seed MIMIC-III clinical notes for real-world grounding.

    Reads NOTEEVENTS_random.csv directly from inside "mimic iii.zip"
    without extracting it — no disk space wasted.

    Zip internal path:
      MIMIC -III (10000 patients)/NOTEEVENTS/NOTEEVENTS_random.csv

    Columns used: ROW_ID, CATEGORY, DESCRIPTION, TEXT, ISERROR
    """
    print("\n🏥 [2/4] Loading MIMIC-III (Clinical Grounding — from zip)...")

    zip_path = os.path.join(RESEARCH_DIR, "mimic iii.zip")
    if not os.path.exists(zip_path):
        print(f"  ⚠️  mimic iii.zip not found at {zip_path}")
        print("      Please ensure the file is at: Research/latest/mimic iii.zip")
        return 0

    NOTEEVENTS_INNER = "MIMIC -III (10000 patients)/NOTEEVENTS/NOTEEVENTS_random.csv"

    USEFUL_CATEGORIES = {
        "Discharge summary",
        "Radiology",
        "ECG",
        "Echo",
        "Physician",
        "Nursing",
        "Nursing/other",
    }

    try:
        import pandas as pd
        print(f"   📂 Opening {zip_path} ...")
        with zipfile.ZipFile(zip_path, "r") as z:
            with z.open(NOTEEVENTS_INNER) as f:
                df = pd.read_csv(
                    f,
                    nrows=limit,
                    usecols=["ROW_ID", "CATEGORY", "DESCRIPTION", "TEXT", "ISERROR"],
                    low_memory=False,
                )
    except KeyError:
        print(f"  ❌ '{NOTEEVENTS_INNER}' not found inside the zip.")
        return 0
    except Exception as e:
        print(f"  ❌ Error reading MIMIC-III zip: {e}")
        return 0

    df = df[df["ISERROR"].isna() | (df["ISERROR"] == 0)]
    df = df[df["TEXT"].notna()]

    count = 0
    for _, row in df.iterrows():
        category    = str(row.get("CATEGORY", "")).strip()
        description = str(row.get("DESCRIPTION", "")).strip()
        text        = str(row.get("TEXT", "")).strip()

        if category not in USEFUL_CATEGORIES or len(text) < 50:
            continue

        chunk = f"[MIMIC-III | {category}] {description}\n\n{text[:1900]}"

        doc_id = _stable_uuid(f"mimic3_{count}")
        emb = await text_embedder.embed_text(chunk)
        await vector_store.store_text_embedding(
            doc_id=doc_id,
            embedding=emb,
            text=chunk,
            metadata={
                "source": "MIMIC-III",
                "category": "clinical_notes",
                "note_category": category,
                "description": description[:100],
            }
        )
        count += 1
        if count % 500 == 0:
            print(f"   ✅ MIMIC-III: {count} notes ingested")

    print(f"   ✅ MIMIC-III complete — {count} clinical notes ingested")
    return count


# =============================================================================
# 3. CheXpert — Chest X-ray Uncertainty Labels (reads directly from zip)
# =============================================================================
async def seed_chexpert(limit: int = 1000):
    """Seed CheXpert chest X-rays with uncertainty labels.

    Reads train.csv and images directly from CheXpert.zip without extracting.

    Zip internal structure:
      train.csv                              <- label manifest at root
      train/patient00001/study1/view1_frontal.jpg
      ...

    CheXpert label values:
       1.0 -> Positive
      -1.0 -> Uncertain  (key for teaching "unsure" instead of hallucinating)
       0.0 -> Negative
    """
    print("\n🩻 [3/4] Loading CheXpert (Imaging & Uncertainty)...")

    zip_path = os.path.join(RESEARCH_DIR, "CheXpert.zip")
    if not os.path.exists(zip_path):
        print(f"  ⚠️  CheXpert.zip not found at {zip_path}")
        print("      Please ensure the file is at: Research/latest/CheXpert.zip")
        return 0

    LABEL_COLS = [
        "No Finding", "Enlarged Cardiomediastinum", "Cardiomegaly",
        "Lung Opacity", "Lung Lesion", "Edema", "Consolidation",
        "Pneumonia", "Atelectasis", "Pneumothorax", "Pleural Effusion",
        "Pleural Other", "Fracture", "Support Devices",
    ]

    try:
        import pandas as pd
        from PIL import Image
        print(f"   📂 Opening {zip_path} ...")
        with zipfile.ZipFile(zip_path, "r") as z:
            with z.open("train.csv") as f:
                df = pd.read_csv(f, nrows=limit)
    except Exception as e:
        print(f"  ❌ Error reading CheXpert.zip: {e}")
        return 0

    count = 0
    try:
        from PIL import Image
        with zipfile.ZipFile(zip_path, "r") as z:
            available = set(z.namelist())

            for _, row in df.iterrows():
                img_rel = str(row.get("Path", ""))

                # Normalise path — strip any leading prefix up to "train/"
                if "train/" in img_rel:
                    img_inner = img_rel[img_rel.index("train/"):]
                else:
                    img_inner = img_rel

                if img_inner not in available:
                    continue

                try:
                    with z.open(img_inner) as img_file:
                        pil_image = Image.open(io.BytesIO(img_file.read())).convert("RGB")
                    img_emb = await clip_embedder.embed_image(pil_image)
                except Exception:
                    continue

                flags = []
                for col in LABEL_COLS:
                    val = row.get(col)
                    if val == 1.0:
                        flags.append(f"{col}: Positive")
                    elif val == -1.0:
                        flags.append(f"{col}: Uncertain")

                desc = ("CheXpert Chest X-ray. Findings: " + ", ".join(flags)
                        if flags else "CheXpert Chest X-ray. No significant findings.")

                doc_id = _stable_uuid(f"chexpert_{count}")
                await vector_store.store_image_embedding(
                    image_id=doc_id,
                    embedding=img_emb,
                    metadata={
                        "source": "CheXpert",
                        "category": "radiology",
                        "specialty": "Radiology",
                        "diagnosis": desc,
                    }
                )
                count += 1
                if count % 200 == 0:
                    print(f"   ✅ CheXpert: {count} images ingested")

    except Exception as e:
        print(f"  ❌ Error during CheXpert image loop: {e}")

    print(f"   ✅ CheXpert complete — {count} images ingested")
    return count


# =============================================================================
# 4. Med-MMHL — Medical Misinformation Detection
# =============================================================================
async def seed_med_mmhl(limit: int = 2000):
    """Seed Med-MMHL misinformation articles as anti-hallucination constraints.

    The Med-MMHL GitHub repo does NOT include the actual dataset files.
    The data must be downloaded separately from Dropbox (link in README.md).

    After downloading and unzipping, place the data folders inside:
      Research/latest/Med-MMHL/

    Expected CSV structure per task directory:
      fakenews_article/train.csv  ->  columns: content, det_fake_label
      sentence/train.csv          ->  columns: content, det_fake_label

    det_fake_label:  1 = fake/misinformation,  0 = real/correct
    """
    print("\n🛑 [4/4] Loading Med-MMHL (Anti-Hallucination Misinformation)...")

    # The GitHub clone creates Med-MMHL/, and the Dropbox data is extracted
    # inside it as another Med-MMHL/ subfolder.  Try nested path first.
    mmhl_dir = os.path.join(RESEARCH_DIR, "Med-MMHL", "Med-MMHL")
    if not os.path.isdir(mmhl_dir):
        mmhl_dir = os.path.join(RESEARCH_DIR, "Med-MMHL")   # flat fallback
    if not os.path.exists(mmhl_dir):
        print(f"  ⚠️  Med-MMHL directory not found at {mmhl_dir}")
        print("      Please clone: https://github.com/styxsys0927/Med-MMHL")
        print("      Then download the actual data from the Dropbox link in the README.")
        return 0

    DATA_SUBDIRS = ["fakenews_article", "sentence", "fakenews_tweet"]
    CSV_FILES    = ["train.csv", "dev.csv", "test.csv"]

    import pandas as pd

    all_rows  = []
    found_any = False

    for subdir in DATA_SUBDIRS:
        subdir_path = os.path.join(mmhl_dir, subdir)
        if not os.path.isdir(subdir_path):
            continue
        for csv_name in CSV_FILES:
            csv_path = os.path.join(subdir_path, csv_name)
            if not os.path.exists(csv_path):
                continue
            try:
                df = pd.read_csv(csv_path, low_memory=False)
                if "content" not in df.columns:
                    continue
                df["_source_file"] = f"{subdir}/{csv_name}"
                all_rows.append(df)
                found_any = True
                print(f"   📄 Found {subdir}/{csv_name} — {len(df)} rows")
            except Exception as e:
                print(f"  ⚠️  Could not read {csv_path}: {e}")

    if not found_any:
        print("  ⚠️  No Med-MMHL data CSVs found.")
        print("      The GitHub repo only contains code — the actual dataset must be")
        print("      downloaded from Dropbox (see Research/latest/Med-MMHL/README.md).")
        print("      After downloading, place folders like 'fakenews_article/' inside")
        print("      Research/latest/Med-MMHL/ and re-run this script.")
        return 0

    combined = pd.concat(all_rows, ignore_index=True)
    if len(combined) > limit:
        combined = combined.sample(n=limit, random_state=42)

    count = 0
    for _, row in combined.iterrows():
        content = str(row.get("content", "")).strip()
        if len(content) < 20:
            continue

        label_val = row.get("det_fake_label", None)
        is_fake   = bool(label_val == 1) if label_val is not None else None
        label_str = "MISINFORMATION" if is_fake else "VERIFIED" if is_fake is False else "UNKNOWN"

        chunk = f"[Med-MMHL | {label_str}]\n{content[:2000]}"

        doc_id = _stable_uuid(f"medmmhl_{count}")
        emb = await text_embedder.embed_text(chunk)
        await vector_store.store_text_embedding(
            doc_id=doc_id,
            embedding=emb,
            text=chunk,
            metadata={
                "source": "Med-MMHL",
                "category": "hallucination_detection",
                "veracity": label_str,
                "is_misinformation": is_fake,
                "source_file": str(row.get("_source_file", "unknown")),
            }
        )
        count += 1
        if count % 500 == 0:
            print(f"   ✅ Med-MMHL: {count} entries ingested")

    print(f"   ✅ Med-MMHL complete — {count} entries ingested")
    return count


# =============================================================================
# Main
# =============================================================================
async def main():
    print("=" * 70)
    print("  ⚖️  MedRAG Anti-Hallucination Pipeline (Advanced Datasets)")
    print("=" * 70)
    start = time.time()

    c1 = await seed_clinical_nli()
    c2 = await seed_mimic_iii()
    c3 = await seed_chexpert()
    c4 = await seed_med_mmhl()

    elapsed = time.time() - start
    print("\n" + "=" * 70)
    print(f"  🏁 ANTI-HALLUCINATION SEEDING COMPLETE 🏁")
    print(f"  Time:                  {elapsed / 60:.1f} minutes")
    print(f"  Clinical NLI pairs:    {c1:,}")
    print(f"  MIMIC-III notes:       {c2:,}")
    print(f"  CheXpert images:       {c3:,}")
    print(f"  Med-MMHL entries:      {c4:,}")
    print(f"  Total ingested:        {c1+c2+c3+c4:,}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
