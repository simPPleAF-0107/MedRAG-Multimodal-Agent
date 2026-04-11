"""
MedRAG ClinicalTrials.gov Seeder
===================================
Fetches clinical trial summaries from the ClinicalTrials.gov API v2 (free, open).

Covers study titles, brief summaries, conditions, interventions, and outcomes
across 15 medical specialties.

Target: ~3,000 trial summaries

Run:  python -m backend.scripts.seed_clinicaltrials
"""
import asyncio
import sys
import os
import time
import hashlib
import uuid as _uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder
from backend.rag.graph_store import graph_store

CTGOV_API_URL = "https://clinicaltrials.gov/api/v2/studies"
BATCH_SIZE = 64
TRIALS_PER_SPECIALTY = 200

SPECIALTY_CONDITIONS = {
    "Cardiology": ["Heart Failure", "Atrial Fibrillation", "Coronary Artery Disease", "Hypertension", "Acute Coronary Syndrome"],
    "Oncology": ["Breast Cancer", "Lung Cancer", "Colorectal Cancer", "Melanoma", "Pancreatic Cancer"],
    "Neurology": ["Stroke", "Epilepsy", "Multiple Sclerosis", "Parkinson Disease", "Alzheimer Disease"],
    "Endocrinology": ["Type 2 Diabetes", "Thyroid Cancer", "Obesity", "Adrenal Insufficiency"],
    "Pulmonology": ["COPD", "Asthma", "Pulmonary Fibrosis", "Pulmonary Embolism"],
    "Gastroenterology": ["Crohn Disease", "Ulcerative Colitis", "Hepatitis C", "Cirrhosis", "GERD"],
    "Nephrology": ["Chronic Kidney Disease", "Diabetic Nephropathy", "Glomerulonephritis"],
    "Rheumatology": ["Rheumatoid Arthritis", "Systemic Lupus Erythematosus", "Ankylosing Spondylitis"],
    "Infectious Disease": ["HIV", "Tuberculosis", "COVID-19", "Hepatitis B", "Sepsis"],
    "Psychiatry": ["Major Depressive Disorder", "Schizophrenia", "Bipolar Disorder", "PTSD"],
    "Dermatology": ["Psoriasis", "Atopic Dermatitis", "Melanoma", "Acne"],
    "Ophthalmology": ["Glaucoma", "Diabetic Retinopathy", "Macular Degeneration"],
    "Pediatrics": ["Childhood Leukemia", "Juvenile Arthritis", "Neonatal Sepsis"],
    "Emergency Medicine": ["Traumatic Brain Injury", "Cardiac Arrest", "Hemorrhagic Shock"],
    "Obstetrics": ["Preeclampsia", "Gestational Diabetes", "Preterm Birth"],
}


def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))


async def _fetch_trials(session, condition: str, max_results: int = 50) -> list[dict]:
    """Fetch clinical trial data from ClinicalTrials.gov API v2."""
    import aiohttp
    
    params = {
        "query.cond": condition,
        "pageSize": min(max_results, 50),
        "format": "json",
        "fields": "NCTId,BriefTitle,BriefSummary,Condition,InterventionName,Phase,OverallStatus,StartDate,PrimaryOutcomeDescription",
    }
    
    try:
        async with session.get(CTGOV_API_URL, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            return data.get("studies", [])
    except Exception as e:
        print(f"  ⚠ ClinicalTrials.gov fetch failed for '{condition}': {e}")
        return []


def _parse_trial(study: dict, specialty: str) -> dict | None:
    """Parse a study JSON into a structured document."""
    try:
        proto = study.get("protocolSection", {})
        ident = proto.get("identificationModule", {})
        desc = proto.get("descriptionModule", {})
        cond_module = proto.get("conditionsModule", {})
        interv_module = proto.get("armsInterventionsModule", {})
        status_module = proto.get("statusModule", {})
        design_module = proto.get("designModule", {})
        
        nct_id = ident.get("nctId", "")
        title = ident.get("briefTitle", "")
        summary = desc.get("briefSummary", "")
        
        if not summary or len(summary) < 50:
            return None
        
        conditions = cond_module.get("conditions", [])
        
        interventions = []
        if interv_module:
            for interv in interv_module.get("interventions", []):
                interventions.append(f"{interv.get('type', '')}: {interv.get('name', '')}")
        
        phase_list = design_module.get("phases", []) if design_module else []
        phase = ", ".join(phase_list) if phase_list else "Not specified"
        
        status = status_module.get("overallStatus", "Unknown")
        
        text_parts = [
            f"Clinical Trial: {title}",
            f"NCT ID: {nct_id}",
            f"Phase: {phase} | Status: {status}",
            f"Conditions: {', '.join(conditions[:5])}",
        ]
        if interventions:
            text_parts.append(f"Interventions: {'; '.join(interventions[:5])}")
        text_parts.append(f"\nSummary: {summary}")
        
        text = "\n".join(text_parts)
        if len(text) > 2000:
            text = text[:2000] + "..."
        
        return {
            "text": text,
            "metadata": {
                "source": "ClinicalTrials.gov",
                "category": "clinical_trials",
                "specialty": specialty,
                "modality": "text",
                "type": "clinical_trial",
                "nct_id": nct_id,
                "phase": phase,
                "status": status,
                "title": title[:200],
            }
        }
    except Exception:
        return None


async def seed_clinicaltrials():
    """Main seeder: fetch and embed clinical trial summaries."""
    import aiohttp

    print("=" * 60)
    print("  MedRAG ClinicalTrials.gov Seeder")
    print(f"  Target: ~{TRIALS_PER_SPECIALTY * len(SPECIALTY_CONDITIONS):,} trial summaries")
    print("=" * 60)

    start = time.time()
    total_ingested = 0
    graph_store.set_bulk_mode(True)

    async with aiohttp.ClientSession() as session:
        all_chunks = []
        
        for specialty, conditions in SPECIALTY_CONDITIONS.items():
            print(f"\n🔬 [{specialty}] Fetching trials...")
            specialty_count = 0
            
            per_condition = TRIALS_PER_SPECIALTY // len(conditions)
            
            for condition in conditions:
                studies = await _fetch_trials(session, condition, max_results=per_condition)
                
                for study in studies:
                    parsed = _parse_trial(study, specialty)
                    if parsed:
                        all_chunks.append(parsed)
                        specialty_count += 1
                        
                        # Graph relationships
                        graph_store.add_relationship(
                            condition.lower(),
                            "HAS_TRIAL",
                            parsed["metadata"]["title"][:60].lower()
                        )
                
                await asyncio.sleep(0.2)  # Rate limit
            
            print(f"  ✅ {specialty}: {specialty_count} trials collected")
        
        print(f"\n📦 Total trials to embed: {len(all_chunks)}")
        
        # Batch embed and store
        for i in range(0, len(all_chunks), BATCH_SIZE):
            batch = all_chunks[i:i + BATCH_SIZE]
            texts = [c["text"] for c in batch]
            
            embeddings = await text_embedder.embed_batch(texts)
            
            points = []
            for emb, chunk in zip(embeddings, batch):
                doc_id = _stable_uuid(f"ctgov_{chunk['metadata'].get('nct_id', str(i))}")
                chunk["metadata"]["document"] = chunk["text"]
                points.append({
                    "id": doc_id,
                    "vector": emb,
                    "payload": chunk["metadata"],
                })
            
            vector_store.store_text_batch(points)
            total_ingested += len(points)
            
            if total_ingested % 200 == 0:
                print(f"  ✅ {total_ingested} trial summaries ingested")
    
    graph_store.set_bulk_mode(False)
    
    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"  🎉 ClinicalTrials.gov seeding complete!")
    print(f"  Total trials: {total_ingested:,}")
    print(f"  Time: {elapsed / 60:.1f} minutes")
    print(f"{'=' * 60}")
    return total_ingested


if __name__ == "__main__":
    asyncio.run(seed_clinicaltrials())
