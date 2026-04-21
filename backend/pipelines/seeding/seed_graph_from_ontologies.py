"""
Wave 2: Seed Knowledge Graph from Ontology Mappings
=====================================================
Builds rich ontology-derived relationships beyond what the basic seeder does.
Creates structured mappings:
  - symptom → disease edges
  - disease → ICD-10 code edges
  - disease → SNOMED concept edges
  - drug interaction edges
  - disease → specialty edges
"""
import os
import sys
import json
import logging
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.pipelines.processing.base_processor import PROCESSED_DATA_DIR, load_processed, extract_symptoms
from backend.rag.graph_store import graph_store

logger = logging.getLogger(__name__)


def seed_symptom_disease_edges() -> int:
    """Create symptom → MAY_INDICATE → disease edges from diagnostic cases."""
    entries = load_processed("diagnostic_cases.jsonl")
    if not entries:
        logger.warning("diagnostic_cases.jsonl not found — skipping symptom→disease edges")
        return 0

    count = 0
    for entry in entries:
        disease = entry.get("disease", "")
        symptoms = entry.get("symptoms", [])
        if not disease or disease == "Unknown":
            continue

        disease_lower = disease.lower()
        for symptom in symptoms:
            if symptom and len(symptom) > 2:
                graph_store.add_relationship(symptom.lower(), "MAY_INDICATE", disease_lower)
                count += 1

        # Disease → specialty
        specialty = entry.get("specialty", "")
        if specialty and specialty != "General":
            graph_store.add_relationship(disease_lower, "BELONGS_TO_SPECIALTY", specialty.lower())
            count += 1

        # Disease → differentials
        for diff in entry.get("differentials", []):
            if diff:
                graph_store.add_relationship(disease_lower, "DIFFERENTIAL_OF", diff.lower())
                count += 1

    logger.info(f"Symptom→Disease edges: {count}")
    return count


def seed_icd_edges() -> int:
    """Create disease → CODED_AS → ICD-10 edges."""
    entries = load_processed("icd10_cleaned.jsonl")
    if not entries:
        return 0

    count = 0
    for entry in entries:
        text = entry.get("text", "")
        metadata = entry.get("metadata", {})
        icd_code = metadata.get("icd_code", "")
        disease = entry.get("disease", "")

        if icd_code and disease:
            graph_store.add_relationship(disease.lower(), "ICD10_CODE", icd_code.lower())
            count += 1
        elif icd_code and text:
            # Extract disease name from text description
            desc = text.split("Description:")[-1].strip()[:100] if "Description:" in text else text[:100]
            graph_store.add_relationship(desc.lower(), "ICD10_CODE", icd_code.lower())
            count += 1

    logger.info(f"ICD-10 edges: {count}")
    return count


def seed_snomed_edges() -> int:
    """Create disease → SNOMED_CONCEPT → snomed_id edges."""
    entries = load_processed("snomed_cleaned.jsonl")
    if not entries:
        return 0

    count = 0
    for entry in entries:
        metadata = entry.get("metadata", {})
        concept_id = metadata.get("snomed_concept_id", "")
        disease = entry.get("disease", "")
        text = entry.get("text", "")

        if concept_id:
            entity = disease.lower() if disease else text[:80].lower()
            graph_store.add_relationship(entity, "SNOMED_CONCEPT", f"snomed:{concept_id}")
            count += 1

    logger.info(f"SNOMED edges: {count}")
    return count


def seed_drug_edges() -> int:
    """Create drug → TREATS / HAS_SIDE_EFFECT edges."""
    entries = load_processed("drugs_cleaned.jsonl")
    if not entries:
        logger.info("No drugs_cleaned.jsonl found — skipping drug edges")
        return 0

    count = 0
    for entry in entries:
        text = entry.get("text", "")
        source = entry.get("source", "")

        # Extract drug name (heuristic: first ~3 words before a colon or comma)
        drug_name = ""
        if "Drug Concept:" in text:
            drug_name = text.split("Drug Concept:")[-1].split(",")[0].strip()
        elif text:
            drug_name = text.split(",")[0].split(":")[0].strip()[:50]

        if not drug_name or len(drug_name) < 3:
            continue

        drug_lower = drug_name.lower()
        graph_store.add_relationship(drug_lower, "IS_A", "drug")
        count += 1

        # Extract symptoms from context for side-effect edges
        symptoms = extract_symptoms(text)
        for symptom in symptoms[:3]:
            graph_store.add_relationship(drug_lower, "MAY_CAUSE", symptom.lower())
            count += 1

    logger.info(f"Drug edges: {count}")
    return count


def seed_mesh_edges() -> int:
    """Create MeSH descriptor → hierarchy edges."""
    entries = load_processed("mesh_cleaned.jsonl")
    if not entries:
        return 0

    count = 0
    for entry in entries:
        disease = entry.get("disease", "")
        specialty = entry.get("specialty", "")
        text = entry.get("text", "")

        if disease and specialty and specialty != "General":
            graph_store.add_relationship(disease.lower(), "MESH_CATEGORY", specialty.lower())
            count += 1

    logger.info(f"MeSH edges: {count}")
    return count


def run_graph_seeding():
    """Execute full graph seeding pipeline."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")

    logger.info("=" * 60)
    logger.info(" SEEDING KNOWLEDGE GRAPH FROM ONTOLOGY MAPPINGS")
    logger.info("=" * 60)

    start = time.time()

    graph_store.set_bulk_mode(True)

    total = 0
    total += seed_symptom_disease_edges()
    total += seed_icd_edges()
    total += seed_snomed_edges()
    total += seed_drug_edges()
    total += seed_mesh_edges()

    graph_store.set_bulk_mode(False)  # Flush + rebuild index

    elapsed = time.time() - start

    logger.info(f"\n📊 Graph Seeding Complete:")
    logger.info(f"  Total edges added: {total}")
    logger.info(f"  Graph nodes: {graph_store.graph.number_of_nodes()}")
    logger.info(f"  Graph edges: {graph_store.graph.number_of_edges()}")
    logger.info(f"  Time: {elapsed:.1f}s")

    return total


if __name__ == "__main__":
    run_graph_seeding()
