"""
Process Tier 1 ontology datasets from data/raw/ontologies/.
Handles: ICD-10 (pickled HTML), SNOMED (RF2 TSV), MeSH (XML), Orphanet (OWL).
Skips UMLS and LOINC for Tier 1 (large archives, Tier 2 priority).
"""
import os
import json
import zipfile
import pickle
import re
import logging
import xml.etree.ElementTree as ET

from backend.pipelines.processing.base_processor import (
    RAW_DATA_DIR, StandardizedEntry, detect_specialty,
    deduplicate_entries, save_processed,
)

logger = logging.getLogger(__name__)
ONTOLOGY_RAW = os.path.join(RAW_DATA_DIR, "ontologies")


# ── 1. ICD-10 (Pickled HTML pages) ───────────────────────────────────────────
def process_icd10() -> list[dict]:
    """
    Process ICD-10 from zip of pickled HTML pages.
    Each .pkl file is a scraped HTML page for one ICD-10 code.
    We extract the code from filename and description from HTML title.
    """
    print("\n📖 Processing ICD-10...")
    entries = []
    zip_path = os.path.join(ONTOLOGY_RAW, "icd10", "archive.zip")

    if not os.path.exists(zip_path):
        print("  ⚠️ ICD-10 zip not found, skipping.")
        return []

    with zipfile.ZipFile(zip_path) as z:
        pkl_files = [n for n in z.namelist() if n.endswith(".pkl")]
        print(f"  📄 Found {len(pkl_files)} ICD-10 code files")

        processed = 0
        for pkl_name in pkl_files:
            try:
                # Extract ICD code from filename
                # e.g. ..._A00.0.pkl → A00.0
                code_match = re.search(r'([A-Z]\d{2}(?:\.\d{1,2})?)\.\w+$', pkl_name)
                if not code_match:
                    continue
                icd_code = code_match.group(1)

                with z.open(pkl_name) as f:
                    html_bytes = pickle.load(f)

                if isinstance(html_bytes, bytes):
                    html_str = html_bytes.decode("utf-8", errors="replace")
                else:
                    html_str = str(html_bytes)

                # Extract title (contains code + description)
                title_match = re.search(r'<title>(.*?)</title>', html_str, re.IGNORECASE)
                if not title_match:
                    continue
                title = title_match.group(1).strip()

                # Extract description from title
                # Format: "2018 ICD-10-CM Diagnosis Code A00.0: Cholera due to ..."
                desc_match = re.search(r':\s*(.+)$', title)
                description = desc_match.group(1).strip() if desc_match else title

                # Try to extract additional text content (clinical notes, includes, excludes)
                # Remove HTML tags for cleaner text
                text_content = re.sub(r'<[^>]+>', ' ', html_str)
                text_content = re.sub(r'\s+', ' ', text_content).strip()

                # Find relevant clinical sections
                clinical_text = ""
                for pattern in [r'Clinical Information(.*?)(?:Approximate Synonyms|$)',
                                r'Applicable To(.*?)(?:Type \d|$)']:
                    match = re.search(pattern, text_content, re.IGNORECASE | re.DOTALL)
                    if match:
                        clinical_text += match.group(1).strip()[:500] + " "

                combined = f"ICD-10 Code: {icd_code}\nDescription: {description}"
                if clinical_text.strip():
                    combined += f"\nClinical Information: {clinical_text.strip()}"

                entry = StandardizedEntry(
                    text=combined,
                    source="icd10",
                    type="ontology",
                    specialty=detect_specialty(description),
                    disease=description,
                    confidence_weight=0.95,
                    metadata={"icd_code": icd_code},
                )
                entries.append(entry.to_dict())
                processed += 1

                if processed % 5000 == 0:
                    print(f"    ... processed {processed} ICD-10 codes")

            except Exception as e:
                continue  # Skip corrupt pickles

    print(f"  📊 ICD-10 total: {len(entries)} entries")
    return entries


# ── 2. SNOMED CT (RF2 Format) ────────────────────────────────────────────────
def process_snomed() -> list[dict]:
    """
    Process SNOMED CT from RF2 zip files.
    Reads sct2_Description_Snapshot file (TSV) for concept descriptions.
    Schema: id, effectiveTime, active, moduleId, conceptId, languageCode, typeId, term, caseSignificanceId
    """
    print("\n📖 Processing SNOMED CT...")
    entries = []
    snomed_dir = os.path.join(ONTOLOGY_RAW, "snomed")

    if not os.path.isdir(snomed_dir):
        print("  ⚠️ SNOMED directory not found, skipping.")
        return []

    for zip_name in os.listdir(snomed_dir):
        if not zip_name.endswith(".zip"):
            continue
        zip_path = os.path.join(snomed_dir, zip_name)
        print(f"  📄 Processing {zip_name}...")

        try:
            with zipfile.ZipFile(zip_path) as z:
                # Find the Snapshot Description file
                desc_files = [n for n in z.namelist()
                              if "Description_Snapshot" in n and n.endswith(".txt")]
                if not desc_files:
                    print(f"    ⚠️ No Description file found in {zip_name}")
                    continue

                desc_file = desc_files[0]
                print(f"    📄 Reading {desc_file}...")

                with z.open(desc_file) as f:
                    header = f.readline().decode("utf-8").strip().split("\t")
                    term_idx = header.index("term") if "term" in header else 7
                    concept_idx = header.index("conceptId") if "conceptId" in header else 4
                    active_idx = header.index("active") if "active" in header else 2

                    count = 0
                    for line in f:
                        try:
                            fields = line.decode("utf-8").strip().split("\t")
                            # Only active descriptions
                            if fields[active_idx] != "1":
                                continue
                            term = fields[term_idx].strip()
                            concept_id = fields[concept_idx].strip()

                            if not term or len(term.split()) < 2:
                                continue

                            entry = StandardizedEntry(
                                text=f"SNOMED Concept [{concept_id}]: {term}",
                                source="snomed",
                                type="ontology",
                                specialty=detect_specialty(term),
                                disease=term,
                                confidence_weight=0.95,
                                metadata={"snomed_concept_id": concept_id},
                            )
                            entries.append(entry.to_dict())
                            count += 1

                            if count % 50000 == 0:
                                print(f"      ... processed {count} SNOMED terms")
                        except (IndexError, UnicodeDecodeError):
                            continue

                    print(f"    ✅ {count} active descriptions extracted")
        except Exception as e:
            print(f"    ⚠️ Error processing {zip_name}: {e}")

    print(f"  📊 SNOMED CT total: {len(entries)} entries")
    return entries


# ── 3. MeSH (XML) ────────────────────────────────────────────────────────────
def process_mesh() -> list[dict]:
    """
    Process MeSH descriptors from XML files.
    Main file: desc2026.zip contains DescriptorRecordSet.
    """
    print("\n📖 Processing MeSH...")
    entries = []
    mesh_dir = os.path.join(ONTOLOGY_RAW, "mesh")

    if not os.path.isdir(mesh_dir):
        print("  ⚠️ MeSH directory not found, skipping.")
        return []

    # Try desc2026.zip first (main descriptors)
    desc_zip = os.path.join(mesh_dir, "desc2026.zip")
    if os.path.exists(desc_zip):
        print(f"  📄 Processing desc2026.zip...")
        try:
            with zipfile.ZipFile(desc_zip) as z:
                xml_files = [n for n in z.namelist() if n.endswith(".xml")]
                for xf in xml_files:
                    with z.open(xf) as f:
                        tree = ET.parse(f)
                        root = tree.getroot()

                        for record in root.findall(".//DescriptorRecord"):
                            name_el = record.find(".//DescriptorName/String")
                            if name_el is None:
                                continue
                            name = name_el.text.strip() if name_el.text else ""

                            # Get scope note (definition)
                            scope_note = ""
                            for concept in record.findall(".//Concept"):
                                sn = concept.find("ScopeNote")
                                if sn is not None and sn.text:
                                    scope_note = sn.text.strip()
                                    break

                            ui = record.find("DescriptorUI")
                            mesh_id = ui.text.strip() if ui is not None and ui.text else ""

                            if not name:
                                continue

                            text = f"MeSH Term [{mesh_id}]: {name}"
                            if scope_note:
                                text += f"\nDefinition: {scope_note}"

                            entry = StandardizedEntry(
                                text=text,
                                source="mesh",
                                type="ontology",
                                specialty=detect_specialty(text),
                                disease=name if "disease" in name.lower() or "syndrome" in name.lower() else None,
                                confidence_weight=0.9,
                                metadata={"mesh_id": mesh_id},
                            )
                            entries.append(entry.to_dict())
        except Exception as e:
            print(f"    ⚠️ Error processing MeSH descriptors: {e}")

    # Also process supplementary concepts
    supp_zip = os.path.join(mesh_dir, "supp2026.zip")
    if os.path.exists(supp_zip):
        print(f"  📄 Processing supp2026.zip (supplementary)...")
        try:
            with zipfile.ZipFile(supp_zip) as z:
                xml_files = [n for n in z.namelist() if n.endswith(".xml")]
                for xf in xml_files:
                    with z.open(xf) as f:
                        tree = ET.parse(f)
                        root = tree.getroot()

                        for record in root.findall(".//SupplementalRecord"):
                            name_el = record.find(".//SupplementalRecordName/String")
                            if name_el is None:
                                continue
                            name = name_el.text.strip() if name_el.text else ""

                            note_el = record.find(".//Note")
                            note = note_el.text.strip() if note_el is not None and note_el.text else ""

                            ui = record.find("SupplementalRecordUI")
                            mesh_id = ui.text.strip() if ui is not None and ui.text else ""

                            if not name:
                                continue

                            text = f"MeSH Supplement [{mesh_id}]: {name}"
                            if note:
                                text += f"\nNote: {note[:500]}"

                            entry = StandardizedEntry(
                                text=text,
                                source="mesh_supplement",
                                type="ontology",
                                specialty=detect_specialty(text),
                                confidence_weight=0.85,
                                metadata={"mesh_id": mesh_id},
                            )
                            entries.append(entry.to_dict())
        except Exception as e:
            print(f"    ⚠️ Error processing MeSH supplements: {e}")

    print(f"  📊 MeSH total: {len(entries)} entries")
    return entries


# ── 4. Orphanet (OWL/RDF) ────────────────────────────────────────────────────
def process_orphanet() -> list[dict]:
    """
    Process Orphanet rare disease OWL files.
    Extract disease names and definitions from OWL classes.
    """
    print("\n📖 Processing Orphanet...")
    entries = []
    orphanet_dir = os.path.join(ONTOLOGY_RAW, "orphanet")

    if not os.path.isdir(orphanet_dir):
        print("  ⚠️ Orphanet directory not found, skipping.")
        return []

    # Process OWL files directly
    for fname in os.listdir(orphanet_dir):
        if not fname.endswith(".owl"):
            continue
        fpath = os.path.join(orphanet_dir, fname)
        print(f"  📄 Processing {fname} ({os.path.getsize(fpath) / 1e6:.0f}MB)...")

        try:
            # OWL files can be large; use iterparse for memory efficiency
            ns = {
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "obo": "http://purl.obolibrary.org/obo/",
                "skos": "http://www.w3.org/2004/02/skos/core#",
            }

            context = ET.iterparse(fpath, events=("end",))
            count = 0

            for event, elem in context:
                if elem.tag == f"{{{ns['owl']}}}Class" or elem.tag == "Class":
                    # Get class URI
                    about = elem.get(f"{{{ns['rdf']}}}about", "") or elem.get("rdf:about", "")

                    # Get label
                    label = None
                    for label_tag in [f"{{{ns['rdfs']}}}label", "label"]:
                        label_el = elem.find(label_tag)
                        if label_el is not None and label_el.text:
                            label = label_el.text.strip()
                            break

                    # Get definition
                    definition = ""
                    for def_tag in [f"{{{ns['obo']}}}IAO_0000115",
                                    f"{{{ns['skos']}}}definition",
                                    "definition"]:
                        def_el = elem.find(def_tag)
                        if def_el is not None and def_el.text:
                            definition = def_el.text.strip()
                            break

                    if label and ("orpha" in about.lower() or "disease" in label.lower()):
                        text = f"Rare Disease: {label}"
                        if definition:
                            text += f"\nDefinition: {definition[:500]}"

                        orpha_id = about.split("/")[-1] if about else ""
                        entry = StandardizedEntry(
                            text=text,
                            source="orphanet",
                            type="ontology",
                            specialty=detect_specialty(text),
                            disease=label,
                            severity="moderate",
                            confidence_weight=0.9,
                            metadata={"orphanet_id": orpha_id},
                        )
                        entries.append(entry.to_dict())
                        count += 1

                    elem.clear()  # Free memory

            print(f"    ✅ {count} rare diseases extracted from {fname}")
        except Exception as e:
            print(f"    ⚠️ Error processing {fname}: {e}")
            logger.error(f"Orphanet processing error for {fname}: {e}")

    print(f"  📊 Orphanet total: {len(entries)} entries")
    return entries


# ── Master runner ─────────────────────────────────────────────────────────────
def process_all_ontologies() -> dict:
    """Run all ontology processors and save results."""
    print("\n" + "=" * 70)
    print("  🧬 ONTOLOGY PROCESSING PIPELINE")
    print("=" * 70)

    results = {}

    # 1. ICD-10
    icd_entries = process_icd10()
    icd_entries = deduplicate_entries(icd_entries)
    save_processed(icd_entries, "icd10_cleaned.jsonl")
    results["icd10"] = len(icd_entries)

    # 2. SNOMED CT
    snomed_entries = process_snomed()
    snomed_entries = deduplicate_entries(snomed_entries)
    save_processed(snomed_entries, "snomed_cleaned.jsonl")
    results["snomed"] = len(snomed_entries)

    # 3. MeSH
    mesh_entries = process_mesh()
    mesh_entries = deduplicate_entries(mesh_entries)
    save_processed(mesh_entries, "mesh_cleaned.jsonl")
    results["mesh"] = len(mesh_entries)

    # 4. Orphanet
    orphanet_entries = process_orphanet()
    orphanet_entries = deduplicate_entries(orphanet_entries)
    save_processed(orphanet_entries, "orphanet_cleaned.jsonl")
    results["orphanet"] = len(orphanet_entries)

    print("\n" + "=" * 70)
    print("  📊 ONTOLOGY PROCESSING SUMMARY")
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
    process_all_ontologies()
