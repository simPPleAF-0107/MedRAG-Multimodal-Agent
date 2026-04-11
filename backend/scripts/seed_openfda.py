"""
MedRAG OpenFDA Drug Label Seeder
==================================
Fetches drug labels from the OpenFDA API (free, no key needed) and chunks
them into focused sections for optimal retrieval.

Covers: indications, warnings, adverse reactions, dosage, drug interactions,
contraindications, mechanism of action, pharmacokinetics.

Target: ~2,000 drug label sections from top prescribed medications.

Run:  python -m backend.scripts.seed_openfda
"""
import asyncio
import sys
import os
import time
import hashlib
import uuid as _uuid
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder
from backend.rag.graph_store import graph_store

OPENFDA_URL = "https://api.fda.gov/drug/label.json"
BATCH_SIZE = 64

# Label sections to extract and chunk separately
LABEL_SECTIONS = [
    ("indications_and_usage", "Indications & Usage"),
    ("warnings_and_cautions", "Warnings & Precautions"),
    ("warnings", "Warnings"),
    ("adverse_reactions", "Adverse Reactions"),
    ("dosage_and_administration", "Dosage & Administration"),
    ("drug_interactions", "Drug Interactions"),
    ("contraindications", "Contraindications"),
    ("clinical_pharmacology", "Clinical Pharmacology"),
    ("mechanism_of_action", "Mechanism of Action"),
    ("overdosage", "Overdosage"),
    ("pregnancy", "Pregnancy"),
    ("pediatric_use", "Pediatric Use"),
    ("geriatric_use", "Geriatric Use"),
]

# Drug → specialty mapping for metadata enrichment
DRUG_SPECIALTY_MAP = {
    "metformin": "Endocrinology", "insulin": "Endocrinology", "levothyroxine": "Endocrinology",
    "glipizide": "Endocrinology", "pioglitazone": "Endocrinology", "semaglutide": "Endocrinology",
    "lisinopril": "Cardiology", "amlodipine": "Cardiology", "atorvastatin": "Cardiology",
    "metoprolol": "Cardiology", "losartan": "Cardiology", "warfarin": "Cardiology",
    "digoxin": "Cardiology", "amiodarone": "Cardiology", "clopidogrel": "Cardiology",
    "apixaban": "Cardiology", "rivaroxaban": "Cardiology", "rosuvastatin": "Cardiology",
    "omeprazole": "Gastroenterology", "pantoprazole": "Gastroenterology",
    "esomeprazole": "Gastroenterology", "mesalamine": "Gastroenterology",
    "infliximab": "Gastroenterology", "lactulose": "Gastroenterology",
    "albuterol": "Pulmonology", "fluticasone": "Pulmonology", "montelukast": "Pulmonology",
    "tiotropium": "Pulmonology", "budesonide": "Pulmonology", "prednisone": "Pulmonology",
    "sertraline": "Psychiatry", "fluoxetine": "Psychiatry", "escitalopram": "Psychiatry",
    "quetiapine": "Psychiatry", "lithium": "Psychiatry", "aripiprazole": "Psychiatry",
    "olanzapine": "Psychiatry", "bupropion": "Psychiatry", "venlafaxine": "Psychiatry",
    "gabapentin": "Neurology", "levetiracetam": "Neurology", "carbamazepine": "Neurology",
    "levodopa": "Neurology", "sumatriptan": "Neurology", "topiramate": "Neurology",
    "amoxicillin": "Infectious Disease", "azithromycin": "Infectious Disease",
    "ciprofloxacin": "Infectious Disease", "doxycycline": "Infectious Disease",
    "vancomycin": "Infectious Disease", "fluconazole": "Infectious Disease",
    "methotrexate": "Rheumatology", "adalimumab": "Rheumatology",
    "hydroxychloroquine": "Rheumatology", "allopurinol": "Rheumatology",
    "tamsulosin": "Urology", "finasteride": "Urology",
    "latanoprost": "Ophthalmology", "timolol": "Ophthalmology",
    "pembrolizumab": "Oncology", "tamoxifen": "Oncology",
    "ibuprofen": "General", "acetaminophen": "General", "aspirin": "General",
}

# Search terms to query OpenFDA for diverse drug coverage
SEARCH_QUERIES = [
    "diabetes", "hypertension", "cholesterol", "depression", "anxiety",
    "infection", "asthma", "pain", "cancer", "seizure",
    "heart failure", "anticoagulant", "thyroid", "arthritis", "allergy",
    "migraine", "psoriasis", "HIV", "tuberculosis", "pneumonia",
    "GERD", "IBD", "osteoporosis", "COPD", "glaucoma",
    "bipolar", "schizophrenia", "insomnia", "nausea", "anemia",
]


def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))


def _guess_specialty(drug_name: str, text: str) -> str:
    """Guess specialty from drug name or text content."""
    drug_lower = drug_name.lower()
    for drug, spec in DRUG_SPECIALTY_MAP.items():
        if drug in drug_lower:
            return spec
    # Fallback: keyword scan
    text_lower = text.lower()
    specialty_keywords = {
        "Cardiology": ["heart", "cardiac", "cardiovascular", "angina", "hypertension"],
        "Endocrinology": ["diabetes", "thyroid", "insulin", "glucose", "hormonal"],
        "Gastroenterology": ["gastric", "esophageal", "hepatic", "liver", "bowel"],
        "Pulmonology": ["pulmonary", "respiratory", "bronchial", "asthma", "lung"],
        "Oncology": ["cancer", "tumor", "neoplasm", "malignant", "chemotherapy"],
        "Psychiatry": ["depression", "anxiety", "psychosis", "bipolar", "psychiatric"],
        "Neurology": ["seizure", "epilepsy", "migraine", "neurological", "parkinson"],
        "Infectious Disease": ["infection", "bacterial", "antiviral", "antibiotic", "fungal"],
    }
    for spec, keywords in specialty_keywords.items():
        if any(kw in text_lower for kw in keywords):
            return spec
    return "General"


async def _fetch_drug_labels(session, search_term: str, limit: int = 20) -> list[dict]:
    """Fetch drug labels from OpenFDA for a given search term."""
    import aiohttp
    params = {
        "search": f'openfda.substance_name:"{search_term}" OR indications_and_usage:"{search_term}"',
        "limit": limit,
    }
    try:
        async with session.get(OPENFDA_URL, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            return data.get("results", [])
    except Exception as e:
        print(f"  ⚠ OpenFDA fetch failed for '{search_term}': {e}")
        return []


def _extract_drug_name(label: dict) -> str:
    """Extract the most readable drug name from a label."""
    openfda = label.get("openfda", {})
    names = openfda.get("brand_name", []) or openfda.get("generic_name", []) or openfda.get("substance_name", [])
    if names:
        return names[0]
    return "Unknown Drug"


def _chunk_label(label: dict, drug_name: str) -> list[dict]:
    """Split a drug label into section-based chunks with metadata."""
    chunks = []
    for field_key, section_name in LABEL_SECTIONS:
        content_list = label.get(field_key, [])
        if not content_list:
            continue
        content = content_list[0] if isinstance(content_list, list) else str(content_list)
        
        # Skip very short or boilerplate sections
        if len(content) < 50:
            continue
        
        # Truncate extremely long sections
        if len(content) > 2000:
            content = content[:2000] + "..."
        
        text = f"Drug: {drug_name}\nSection: {section_name}\n\n{content}"
        specialty = _guess_specialty(drug_name, content)
        
        chunks.append({
            "text": text,
            "metadata": {
                "source": "OpenFDA",
                "category": "drug_knowledge",
                "specialty": specialty,
                "modality": "text",
                "type": "drug_label",
                "drug_name": drug_name[:100],
                "section": section_name,
            }
        })
    
    return chunks


async def seed_openfda():
    """Main seeder: fetch drug labels from OpenFDA and embed them."""
    import aiohttp

    print("=" * 60)
    print("  MedRAG OpenFDA Drug Label Seeder")
    print(f"  Searching {len(SEARCH_QUERIES)} drug categories")
    print("=" * 60)

    start = time.time()
    total_ingested = 0
    seen_drugs = set()
    graph_store.set_bulk_mode(True)

    async with aiohttp.ClientSession() as session:
        all_chunks = []
        
        for query in SEARCH_QUERIES:
            print(f"\n💊 Searching: '{query}'...")
            labels = await _fetch_drug_labels(session, query, limit=25)
            
            for label in labels:
                drug_name = _extract_drug_name(label)
                if drug_name.lower() in seen_drugs:
                    continue
                seen_drugs.add(drug_name.lower())
                
                chunks = _chunk_label(label, drug_name)
                all_chunks.extend(chunks)
                
                # Graph relationships
                specialty = chunks[0]["metadata"]["specialty"] if chunks else "General"
                graph_store.add_relationship(drug_name.lower(), "TREATS", specialty.lower())
                
                # Extract contraindications for graph
                for c in chunks:
                    if c["metadata"]["section"] == "Contraindications":
                        graph_store.add_relationship(drug_name.lower(), "CONTRAINDICATED_IN", c["text"][:60].lower())
                    elif c["metadata"]["section"] == "Adverse Reactions":
                        graph_store.add_relationship(drug_name.lower(), "SIDE_EFFECT", c["text"][:60].lower())
            
            await asyncio.sleep(0.3)  # Rate limiting
        
        print(f"\n📦 Total chunks to embed: {len(all_chunks)}")
        
        # Batch embed and store
        for i in range(0, len(all_chunks), BATCH_SIZE):
            batch = all_chunks[i:i + BATCH_SIZE]
            texts = [c["text"] for c in batch]
            
            embeddings = await text_embedder.embed_batch(texts)
            
            points = []
            for j, (emb, chunk) in enumerate(zip(embeddings, batch)):
                doc_id = _stable_uuid(f"openfda_{chunk['metadata']['drug_name']}_{chunk['metadata']['section']}")
                chunk["metadata"]["document"] = chunk["text"]
                points.append({
                    "id": doc_id,
                    "vector": emb,
                    "payload": chunk["metadata"],
                })
            
            vector_store.store_text_batch(points)
            total_ingested += len(points)
            
            if total_ingested % 200 == 0:
                print(f"  ✅ {total_ingested} drug label sections ingested")
    
    graph_store.set_bulk_mode(False)
    
    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"  🎉 OpenFDA seeding complete!")
    print(f"  Unique drugs: {len(seen_drugs)}")
    print(f"  Total sections: {total_ingested:,}")
    print(f"  Time: {elapsed / 60:.1f} minutes")
    print(f"{'=' * 60}")
    return total_ingested


if __name__ == "__main__":
    asyncio.run(seed_openfda())
