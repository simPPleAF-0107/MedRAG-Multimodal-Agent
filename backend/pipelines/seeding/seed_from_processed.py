"""
Unified seeder: reads processed JSONL files and seeds into Qdrant collections.
Handles clearing old data, embedding with BioBERT, and batch insertion.

Usage:
    python -m backend.pipelines.seeding.seed_from_processed [--clear]

Options:
    --clear    Clear ALL existing Qdrant collections before seeding (recommended for fresh start)
"""
import asyncio
import os
import sys
import json
import time
import uuid
import hashlib
import logging
import argparse

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.pipelines.processing.base_processor import PROCESSED_DATA_DIR, load_processed
from backend.rag.text.embedder import text_embedder
from backend.rag.vector_store import vector_store
from backend.rag.text.chunker import text_chunker
from backend.rag.graph_store import graph_store

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
BATCH_SIZE = 64                    # Embedding batch size (higher = faster on GPU)
CHUNK_LONG_ENTRIES = True          # Split entries > 500 words into chunks

# Per-file entry limits — prevents multi-day embedding runs on CPU.
# Prioritise quality over quantity: even 5K good entries >> 100K noisy ones.
DIAGNOSTIC_LIMIT = 5000            # Per file for diagnostic DB (highest value)
REFERENCE_LIMIT = 3000             # Per file for reference DB
ONTOLOGY_LIMIT = 2000              # Per file for ontology entries (short text, high dedup)


# ── File → Collection mapping ────────────────────────────────────────────────
# Diagnostic DB: high-quality symptom→disease mappings
DIAGNOSTIC_FILES = [
    "pubmedqa_cleaned.jsonl",
    "medqa_cleaned.jsonl",
    "medmcqa_cleaned.jsonl",
]

# Reference DB: supporting evidence, guidelines, clinical notes
REFERENCE_FILES = [
    "clinical_guidelines_cleaned.jsonl",
    "mtsamples_cleaned.jsonl",
    "pubmed_abstracts_cleaned.jsonl",
    "clinical_trials_cleaned.jsonl",
    "healthfc_cleaned.jsonl",
    "mediqa_nli_cleaned.jsonl",
    "scifact_cleaned.jsonl",
    "truthfulqa_cleaned.jsonl",
    "clinical_notes_cleaned.jsonl",
    "drugs_cleaned.jsonl",
    # Ontologies go to reference too (text descriptions)
    "icd10_cleaned.jsonl",
    "snomed_cleaned.jsonl",
    "mesh_cleaned.jsonl",
    "orphanet_cleaned.jsonl",
]

# Graph DB: ontology files that also seed relationships
GRAPH_SEED_FILES = [
    "icd10_cleaned.jsonl",
    "snomed_cleaned.jsonl",
    "mesh_cleaned.jsonl",
    "orphanet_cleaned.jsonl",
]


def _stable_uuid(text: str) -> str:
    """Generate a deterministic UUID from text content."""
    return str(uuid.UUID(hashlib.md5(text.encode()).hexdigest()))


def clear_all_collections():
    """Delete and recreate all Qdrant collections."""
    from qdrant_client.http import models

    print("\n🗑️ Clearing all Qdrant collections...")

    for coll_name in [vector_store.diagnostic_collection_name,
                      vector_store.reference_collection_name,
                      vector_store.image_collection_name]:
        try:
            if vector_store.client.collection_exists(coll_name):
                vector_store.client.delete_collection(coll_name)
                print(f"  ❌ Deleted: {coll_name}")
        except Exception as e:
            print(f"  ⚠️ Error deleting {coll_name}: {e}")

    # Recreate collections
    vector_store.client.create_collection(
        collection_name=vector_store.diagnostic_collection_name,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
    )
    vector_store.client.create_collection(
        collection_name=vector_store.reference_collection_name,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
    )
    vector_store.client.create_collection(
        collection_name=vector_store.image_collection_name,
        vectors_config=models.VectorParams(size=512, distance=models.Distance.COSINE),
    )
    print("  ✅ Recreated all collections (diagnostic, reference, image)")

    # Recreate payload indexes
    vector_store._ensure_payload_indexes()
    print("  ✅ Payload indexes recreated")

    # Clear knowledge graph
    graph_store.graph.clear()
    graph_store.save_graph()
    print("  ✅ Knowledge graph cleared")

    # Clear BM25 cache
    try:
        from backend.rag.text.sparse_retriever import _BM25_CACHE_PATH
        if os.path.exists(_BM25_CACHE_PATH):
            os.remove(_BM25_CACHE_PATH)
            print("  ✅ BM25 cache cleared")
    except ImportError:
        print("  ⚠️ Could not locate BM25 cache path, skipping")


async def seed_collection(
    file_list: list[str],
    collection_type: str,  # "diagnostic" or "reference"
    store_fn,
) -> int:
    """
    Seed a Qdrant collection from a list of processed JSONL files.

    Args:
        file_list: List of JSONL filenames in data/processed/
        collection_type: "diagnostic" or "reference" (for logging)
        store_fn: Function to call for batch storage (e.g. vector_store.store_diagnostic_batch)

    Returns:
        Total number of points inserted.
    """
    total_inserted = 0

    for filename in file_list:
        filepath = os.path.join(PROCESSED_DATA_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  ⚠️ {filename} not found, skipping.")
            continue

        # Determine per-file limit based on collection type and data source
        is_ontology = any(ont in filename for ont in ["icd10", "snomed", "mesh", "orphanet"])
        if collection_type == "diagnostic":
            limit = DIAGNOSTIC_LIMIT
        elif is_ontology:
            limit = ONTOLOGY_LIMIT
        else:
            limit = REFERENCE_LIMIT

        print(f"\n  📥 Seeding {filename} → {collection_type}_embeddings (limit: {limit})")
        entries = load_processed(filename)

        if not entries:
            print(f"    ⚠️ No entries found in {filename}, skipping.")
            continue

        if len(entries) > limit:
            entries = entries[:limit]
            print(f"    📏 Limited to {limit} entries (of {len(load_processed(filename))} total)")

        # Optionally chunk long entries
        if CHUNK_LONG_ENTRIES:
            entries = _chunk_long_entries(entries)

        # Process in batches
        file_inserted = 0
        file_start = time.time()
        for batch_start in range(0, len(entries), BATCH_SIZE):
            batch = entries[batch_start:batch_start + BATCH_SIZE]

            # Prepare texts for batch embedding
            texts = [e.get("text", "") for e in batch]
            try:
                embeddings = await text_embedder.embed_batch(texts)
            except Exception as e:
                logger.error(f"Embedding batch failed: {e}")
                continue

            # Build Qdrant points
            points = []
            for entry, embedding in zip(batch, embeddings):
                doc_id = _stable_uuid(entry.get("text", "")[:500])

                payload = {
                    "document": entry.get("text", ""),
                    "source": entry.get("source", "unknown"),
                    "category": entry.get("type", "evidence"),
                    "specialty": entry.get("specialty", "General"),
                    "modality": "text",
                }
                # Add optional metadata fields
                if entry.get("disease"):
                    payload["disease"] = entry["disease"]
                if entry.get("symptoms"):
                    payload["symptoms"] = entry["symptoms"] if isinstance(entry["symptoms"], list) else [entry["symptoms"]]
                if entry.get("severity"):
                    payload["severity"] = entry["severity"]
                if entry.get("metadata"):
                    for k, v in entry["metadata"].items():
                        if k not in payload and v:
                            payload[k] = str(v)[:200]

                points.append({
                    "id": doc_id,
                    "vector": embedding,
                    "payload": payload,
                })

            # Store batch
            try:
                store_fn(points)
                file_inserted += len(points)
            except Exception as e:
                logger.error(f"Batch store failed: {e}")

            # Progress every 10 batches
            if (batch_start // BATCH_SIZE + 1) % 10 == 0:
                elapsed = time.time() - file_start
                rate = file_inserted / elapsed if elapsed > 0 else 0
                eta = (len(entries) - file_inserted) / rate if rate > 0 else 0
                print(f"    ... {file_inserted}/{len(entries)} embedded ({rate:.0f}/s, ETA: {eta:.0f}s)")

        elapsed = time.time() - file_start
        total_inserted += file_inserted
        print(f"    ✅ {filename}: {file_inserted} points in {elapsed:.1f}s")

    return total_inserted


def _chunk_long_entries(entries: list[dict], max_words: int = 500) -> list[dict]:
    """Split entries with very long text into smaller chunks."""
    result = []
    for entry in entries:
        text = entry.get("text", "")
        if len(text.split()) <= max_words:
            result.append(entry)
        else:
            chunks = text_chunker.chunk_text(text)
            for i, chunk in enumerate(chunks):
                chunked_entry = dict(entry)
                chunked_entry["text"] = chunk
                if chunked_entry.get("metadata"):
                    chunked_entry["metadata"] = dict(chunked_entry["metadata"])
                    chunked_entry["metadata"]["chunk_index"] = i
                else:
                    chunked_entry["metadata"] = {"chunk_index": i}
                result.append(chunked_entry)
    if len(result) > len(entries):
        print(f"    📦 Chunked {len(entries)} entries → {len(result)} chunks")
    return result


def seed_knowledge_graph():
    """Seed the knowledge graph from ontology JSONL files."""
    print("\n🧬 Seeding Knowledge Graph...")

    graph_store.set_bulk_mode(True)
    total_edges = 0

    for filename in GRAPH_SEED_FILES:
        filepath = os.path.join(PROCESSED_DATA_DIR, filename)
        if not os.path.exists(filepath):
            continue

        entries = load_processed(filename)
        # Limit graph entries — ontologies are huge but most entries are simple terms
        max_graph = 10000
        if len(entries) > max_graph:
            entries = entries[:max_graph]
            print(f"  📏 {filename}: limited to {max_graph} entries for graph")
        source_name = filename.replace("_cleaned.jsonl", "")
        count = 0

        for entry in entries:
            disease = entry.get("disease", "")
            specialty = entry.get("specialty", "General")
            source = entry.get("source", source_name)

            if disease:
                # Disease → Specialty edge
                if specialty and specialty != "General":
                    graph_store.add_relationship(disease.lower(), "BELONGS_TO_SPECIALTY", specialty.lower())
                    count += 1

                # Disease → Source edge
                graph_store.add_relationship(disease.lower(), "DOCUMENTED_IN", source.lower())
                count += 1

                # Symptoms → Disease edges
                symptoms = entry.get("symptoms", [])
                if isinstance(symptoms, list):
                    for symptom in symptoms[:5]:  # Limit edges per entry
                        graph_store.add_relationship(symptom.lower(), "MAY_INDICATE", disease.lower())
                        count += 1

            # ICD/SNOMED code → disease edges
            metadata = entry.get("metadata", {})
            if metadata.get("icd_code"):
                graph_store.add_relationship(
                    metadata["icd_code"].lower(), "CODES_FOR", disease.lower() if disease else entry.get("text", "unknown")[:50].lower()
                )
                count += 1
            if metadata.get("snomed_concept_id"):
                graph_store.add_relationship(
                    f"snomed:{metadata['snomed_concept_id']}", "IDENTIFIES",
                    disease.lower() if disease else entry.get("text", "unknown")[:50].lower()
                )
                count += 1

        total_edges += count
        print(f"  ✅ {filename}: {count} graph edges added")

    graph_store.set_bulk_mode(False)  # Flush and rebuild index
    print(f"\n  📊 Knowledge Graph: {graph_store.graph.number_of_nodes()} nodes, "
          f"{graph_store.graph.number_of_edges()} edges")
    return total_edges


async def run_seeding(clear: bool = False):
    """Main seeding pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    )

    print("\n" + "=" * 70)
    print("  🚀 MEDRAG UNIFIED SEEDING PIPELINE")
    print("=" * 70)

    if clear:
        clear_all_collections()

    total_start = time.time()

    # ── Phase 1: Seed Diagnostic DB ───────────────────────────────────────────
    print("\n" + "-" * 70)
    print("  🧠 Phase 1: Seeding DIAGNOSTIC collection")
    print("-" * 70)
    diag_count = await seed_collection(
        DIAGNOSTIC_FILES, "diagnostic", vector_store.store_diagnostic_batch
    )

    # ── Phase 2: Seed Reference DB ────────────────────────────────────────────
    print("\n" + "-" * 70)
    print("  📚 Phase 2: Seeding REFERENCE collection")
    print("-" * 70)
    ref_count = await seed_collection(
        REFERENCE_FILES, "reference", vector_store.store_reference_batch
    )

    # ── Phase 3: Seed Knowledge Graph ─────────────────────────────────────────
    print("\n" + "-" * 70)
    print("  🧬 Phase 3: Seeding Knowledge Graph")
    print("-" * 70)
    graph_edges = seed_knowledge_graph()

    # ── Final Summary ─────────────────────────────────────────────────────────
    total_time = time.time() - total_start

    print("\n" + "=" * 70)
    print("  🏁 SEEDING COMPLETE")
    print("=" * 70)
    print(f"  Diagnostic DB:  {diag_count:>8,} points")
    print(f"  Reference DB:   {ref_count:>8,} points")
    print(f"  Knowledge Graph: {graph_edges:>7,} edges")
    print(f"  ⏱️ Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print("=" * 70)

    # Verify counts
    print("\n  📊 Qdrant Collection Counts:")
    print(f"    diagnostic_embeddings: {vector_store.get_diagnostic_count():,}")
    print(f"    reference_embeddings:  {vector_store.get_reference_count():,}")
    print(f"    Knowledge Graph nodes: {graph_store.graph.number_of_nodes():,}")
    print(f"    Knowledge Graph edges: {graph_store.graph.number_of_edges():,}")


def main():
    parser = argparse.ArgumentParser(description="MedRAG Unified Seeding Pipeline")
    parser.add_argument("--clear", action="store_true",
                        help="Clear all existing collections before seeding")
    args = parser.parse_args()
    asyncio.run(run_seeding(clear=args.clear))


if __name__ == "__main__":
    main()
