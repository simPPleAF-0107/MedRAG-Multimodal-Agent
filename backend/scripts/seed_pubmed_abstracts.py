"""
MedRAG PubMed Abstracts Seeder
================================
Fetches high-quality biomedical abstracts from PubMed via NCBI E-utilities API,
covering 15 medical specialties with specialty-specific MeSH term queries.

NCBI API key enables 10 requests/second (vs 3/sec without).

Target: ~5,000 abstracts (~333 per specialty)

Run:  python -m backend.scripts.seed_pubmed_abstracts
"""
import asyncio
import sys
import os
import time
import hashlib
import uuid as _uuid
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder
from backend.rag.graph_store import graph_store

# ── Configuration ──
NCBI_API_KEY = "6cec520b50b2082df20ad516e31a01c76008"
PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
BATCH_SIZE = 64  # Embedding batch size
ABSTRACTS_PER_SPECIALTY = 350
REQUEST_DELAY = 0.12  # ~8 req/sec with API key (conservative)

# ── Specialty → MeSH term mapping ──
SPECIALTY_MESH_QUERIES = {
    "Cardiology": "cardiovascular diseases[MeSH] OR heart failure[MeSH] OR myocardial infarction[MeSH] OR arrhythmia[MeSH]",
    "Neurology": "nervous system diseases[MeSH] OR stroke[MeSH] OR epilepsy[MeSH] OR multiple sclerosis[MeSH] OR Parkinson disease[MeSH]",
    "Oncology": "neoplasms[MeSH] OR cancer[MeSH] OR chemotherapy[MeSH] OR immunotherapy[MeSH]",
    "Pulmonology": "respiratory tract diseases[MeSH] OR asthma[MeSH] OR COPD[MeSH] OR pneumonia[MeSH] OR pulmonary embolism[MeSH]",
    "Gastroenterology": "gastrointestinal diseases[MeSH] OR inflammatory bowel disease[MeSH] OR hepatitis[MeSH] OR pancreatitis[MeSH]",
    "Endocrinology": "endocrine system diseases[MeSH] OR diabetes mellitus[MeSH] OR thyroid diseases[MeSH] OR adrenal insufficiency[MeSH]",
    "Nephrology": "kidney diseases[MeSH] OR renal insufficiency[MeSH] OR nephrotic syndrome[MeSH] OR glomerulonephritis[MeSH]",
    "Rheumatology": "rheumatic diseases[MeSH] OR arthritis, rheumatoid[MeSH] OR lupus erythematosus, systemic[MeSH] OR gout[MeSH]",
    "Infectious Disease": "communicable diseases[MeSH] OR HIV infections[MeSH] OR tuberculosis[MeSH] OR sepsis[MeSH] OR meningitis[MeSH]",
    "Dermatology": "skin diseases[MeSH] OR psoriasis[MeSH] OR melanoma[MeSH] OR eczema[MeSH]",
    "Ophthalmology": "eye diseases[MeSH] OR glaucoma[MeSH] OR diabetic retinopathy[MeSH] OR macular degeneration[MeSH]",
    "Pediatrics": "pediatrics[MeSH] OR infant, newborn, diseases[MeSH] OR child development[MeSH]",
    "Psychiatry": "mental disorders[MeSH] OR depressive disorder[MeSH] OR schizophrenia[MeSH] OR bipolar disorder[MeSH]",
    "Emergency Medicine": "emergencies[MeSH] OR trauma[MeSH] OR resuscitation[MeSH] OR poisoning[MeSH]",
    "Obstetrics": "pregnancy complications[MeSH] OR preeclampsia[MeSH] OR gestational diabetes[MeSH] OR labor, obstetric[MeSH]",
}


def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))


async def _fetch_pmids(session, query: str, retmax: int = 400) -> list[str]:
    """Search PubMed for PMIDs matching a MeSH query."""
    import aiohttp
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "retmode": "json",
        "sort": "relevance",
        "api_key": NCBI_API_KEY,
    }
    try:
        async with session.get(PUBMED_SEARCH_URL, params=params) as resp:
            data = await resp.json()
            return data.get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        print(f"  ⚠ Search failed: {e}")
        return []


async def _fetch_abstracts(session, pmids: list[str]) -> list[dict]:
    """Fetch article details for a list of PMIDs."""
    import aiohttp
    if not pmids:
        return []
    
    results = []
    # Fetch in chunks of 100 (NCBI limit per request)
    for i in range(0, len(pmids), 100):
        chunk = pmids[i:i+100]
        params = {
            "db": "pubmed",
            "id": ",".join(chunk),
            "retmode": "xml",
            "rettype": "abstract",
            "api_key": NCBI_API_KEY,
        }
        try:
            async with session.get(PUBMED_FETCH_URL, params=params) as resp:
                xml_text = await resp.text()
            root = ET.fromstring(xml_text)
            
            for article in root.findall(".//PubmedArticle"):
                try:
                    pmid = article.findtext(".//PMID", "")
                    title = article.findtext(".//ArticleTitle", "")
                    
                    # Get abstract text
                    abstract_parts = []
                    for abs_text in article.findall(".//AbstractText"):
                        label = abs_text.get("Label", "")
                        text = abs_text.text or ""
                        if label:
                            abstract_parts.append(f"{label}: {text}")
                        else:
                            abstract_parts.append(text)
                    abstract = " ".join(abstract_parts)
                    
                    if not abstract or len(abstract) < 100:
                        continue
                    
                    # Get journal and year
                    journal = article.findtext(".//Journal/Title", "Unknown")
                    year = article.findtext(".//PubDate/Year", "")
                    if not year:
                        year = article.findtext(".//PubDate/MedlineDate", "")[:4] if article.findtext(".//PubDate/MedlineDate") else ""
                    
                    results.append({
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract,
                        "journal": journal,
                        "year": year,
                    })
                except Exception:
                    continue
            
            await asyncio.sleep(REQUEST_DELAY)
        except Exception as e:
            print(f"  ⚠ Fetch failed for chunk: {e}")
    
    return results


async def seed_pubmed_abstracts():
    """Main seeder: fetch and embed PubMed abstracts across 15 specialties."""
    import aiohttp

    print("=" * 60)
    print("  MedRAG PubMed Abstract Seeder")
    print(f"  Target: ~{ABSTRACTS_PER_SPECIALTY * len(SPECIALTY_MESH_QUERIES):,} abstracts across {len(SPECIALTY_MESH_QUERIES)} specialties")
    print("=" * 60)

    start = time.time()
    total_ingested = 0
    graph_store.set_bulk_mode(True)

    async with __import__('aiohttp').ClientSession() as session:
        for specialty, mesh_query in SPECIALTY_MESH_QUERIES.items():
            print(f"\n📚 [{specialty}] Searching PubMed...")
            
            # Step 1: Search for PMIDs
            pmids = await _fetch_pmids(session, mesh_query, retmax=ABSTRACTS_PER_SPECIALTY)
            if not pmids:
                print(f"  ⚠ No results for {specialty}")
                continue
            print(f"  Found {len(pmids)} articles")
            
            await asyncio.sleep(REQUEST_DELAY)
            
            # Step 2: Fetch abstracts
            articles = await _fetch_abstracts(session, pmids)
            print(f"  Fetched {len(articles)} abstracts with content")
            
            # Step 3: Batch embed and store
            batch_texts = []
            batch_meta = []
            
            for art in articles:
                text = f"Title: {art['title']}\n\nAbstract: {art['abstract']}"
                metadata = {
                    "source": "PubMed",
                    "category": "research",
                    "specialty": specialty,
                    "modality": "text",
                    "type": "pubmed_abstract",
                    "pmid": art["pmid"],
                    "journal": art["journal"][:100],
                    "year": art["year"],
                    "title": art["title"][:200],
                }
                batch_texts.append(text)
                batch_meta.append(metadata)
            
            # Embed in batches
            for i in range(0, len(batch_texts), BATCH_SIZE):
                chunk_texts = batch_texts[i:i + BATCH_SIZE]
                chunk_meta = batch_meta[i:i + BATCH_SIZE]
                
                embeddings = await text_embedder.embed_batch(chunk_texts)
                
                points = []
                for j, (emb, text, meta) in enumerate(zip(embeddings, chunk_texts, chunk_meta)):
                    doc_id = _stable_uuid(f"pubmed_{meta['pmid']}")
                    meta["document"] = text
                    points.append({
                        "id": doc_id,
                        "vector": emb,
                        "payload": meta,
                    })
                
                vector_store.store_text_batch(points)
                total_ingested += len(points)
            
            # Add graph relationships
            for art in articles[:20]:  # Top 20 per specialty for graph
                graph_store.add_relationship(specialty, "HAS_RESEARCH", art["title"][:60])
            
            print(f"  ✅ {specialty}: {len(articles)} abstracts ingested")
    
    graph_store.set_bulk_mode(False)
    
    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"  🎉 PubMed seeding complete!")
    print(f"  Total abstracts: {total_ingested:,}")
    print(f"  Time: {elapsed / 60:.1f} minutes")
    print(f"{'=' * 60}")
    return total_ingested


if __name__ == "__main__":
    asyncio.run(seed_pubmed_abstracts())
