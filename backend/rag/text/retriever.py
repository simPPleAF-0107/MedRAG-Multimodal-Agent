from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder
from backend.rag.text.sparse_retriever import sparse_retriever
import asyncio
import logging
import re

logger = logging.getLogger(__name__)

# Medical entity patterns for query expansion
MEDICAL_ENTITIES = {
    # Anatomy terms → expanded search terms
    "molar": ["molar tooth", "dental", "wisdom tooth", "third molar", "impacted tooth"],
    "tooth": ["dental", "molar", "wisdom tooth", "oral surgery", "toothache"],
    "heart": ["cardiac", "cardiovascular", "coronary", "myocardial"],
    "brain": ["cerebral", "neurological", "intracranial", "cognitive"],
    "lung": ["pulmonary", "respiratory", "bronchial", "alveolar"],
    "kidney": ["renal", "nephro", "glomerular", "urinary"],
    "liver": ["hepatic", "hepato", "biliary", "cirrhosis"],
    "stomach": ["gastric", "gastrointestinal", "epigastric", "abdominal"],
    "skin": ["dermatological", "cutaneous", "epidermis", "rash"],
    "eye": ["ocular", "ophthalmic", "retinal", "visual"],
    "bone": ["skeletal", "orthopedic", "fracture", "osteo"],
    "joint": ["articular", "arthritis", "synovial", "musculoskeletal"],
    # Symptom terms
    "pain": ["ache", "tenderness", "discomfort", "soreness", "painful"],
    "swelling": ["edema", "inflammation", "swollen", "enlargement"],
    "fever": ["pyrexia", "febrile", "temperature", "hyperthermia"],
    "bleeding": ["hemorrhage", "haemorrhage", "blood loss"],
    "headache": ["cephalalgia", "migraine", "head pain"],
    "cough": ["tussis", "expectoration", "productive cough"],
    "rash": ["eruption", "exanthema", "dermatitis", "urticaria"],
}

class TextRetriever:
    """
    Enhanced hybrid retriever with:
    1. HyDE (Hypothetical Document Embedding) for query expansion
    2. Dense vector search (Qdrant cosine similarity)
    3. BM25 sparse keyword search (full corpus indexed)
    4. Medical entity-aware query expansion
    5. Reciprocal Rank Fusion (RRF) to merge results
    """
    
    def _expand_query_with_entities(self, query: str) -> str:
        """Expand query with related medical terms for better retrieval coverage."""
        expanded_terms = []
        query_lower = query.lower()
        
        for term, expansions in MEDICAL_ENTITIES.items():
            if term in query_lower:
                # Add 2 most relevant expansions
                expanded_terms.extend(expansions[:2])
        
        if expanded_terms:
            expanded = query + " " + " ".join(expanded_terms)
            logger.info(f"Query expanded with medical entities: +{len(expanded_terms)} terms")
            return expanded
        return query
    
    def _guess_specialty(self, query: str) -> str | None:
        """Guess the target specialty from the query to enable filtered retrieval."""
        query_lower = query.lower()
        specialty_keywords = {
            "Cardiology": ["heart", "cardiac", "cardiovascular", "bp", "hypertension", "afib", "ecg"],
            "Neurology": ["brain", "stroke", "seizure", "neurological", "nerve", "headache", "migraine"],
            "Oncology": ["cancer", "tumor", "neoplasm", "chemo", "oncology", "malignancy"],
            "Pulmonology": ["lung", "respiratory", "asthma", "copd", "breathing", "pneumonia"],
            "Gastroenterology": ["stomach", "gi", "liver", "bowel", "hepatic", "gastric", "reflux"],
            "Endocrinology": ["diabetes", "thyroid", "blood sugar", "hormone", "endocrine", "insulin"],
            "Nephrology": ["kidney", "renal", "dialysis", "gfr", "nephropathy"],
            "Rheumatology": ["joint", "arthritis", "rheumatoid", "lupus", "autoimmune", "gout"],
            "Infectious Disease": ["infection", "fever", "antibiotic", "sepsis", "virus", "bacterial"],
            "Dermatology": ["skin", "rash", "lesion", "melanoma", "dermatitis", "eczema"],
            "Ophthalmology": ["eye", "vision", "retina", "glaucoma", "visual"],
            "Pediatrics": ["child", "pediatric", "infant", "neonatal", "baby", "toddler"],
            "Psychiatry": ["depression", "anxiety", "psychiatric", "mental", "schizophrenia", "bipolar"],
            "Emergency Medicine": ["trauma", "emergency", "crash", "resuscitation", "bleeding", "shock"],
            "Obstetrics": ["pregnancy", "pregnant", "labor", "maternal", "fetal", "delivery"],
        }
        for spec, keywords in specialty_keywords.items():
            if any(kw in query_lower for kw in keywords):
                return spec
        return None

    # Cosine similarity floor: chunks below this are filtered before RRF
    DENSE_SIMILARITY_FLOOR = 0.30

    async def retrieve(self, query: str, top_k: int = 40, use_hyde: bool = True,
                       extracted_symptoms: list[str] = None,
                       specialty_hint: str = None) -> list[dict]:
        """
        Multi-strategy retrieval pipeline with symptom-aware filtering:
        1. Expand query with medical entities
        2. Generate HyDE hypothetical document
        3. Use extracted symptoms OR guess specialty from query
        4. Run dense (Qdrant with filter) + sparse (BM25) in parallel
           - Diagnostic DB queried FIRST (PRIMARY)
           - Reference DB queried SECOND (SUPPORT)
        5. Boost scoring for diagnostic matches with high symptom overlap
        6. Fuse results with RRF
        """
        # Step 1: Medical entity expansion for BM25
        expanded_query = self._expand_query_with_entities(query)
        
        # Step 2: Use symptom extractor hint or guess specialty for payload filtering
        specialty_filter = specialty_hint or self._guess_specialty(query)
        if specialty_filter:
            logger.info(f"Retriever: Applied specialty filter -> {specialty_filter}")
        
        # Step 2b: Build symptom-based payload filters for diagnostic DB
        symptom_filters = None
        if extracted_symptoms:
            logger.info(f"Retriever: {len(extracted_symptoms)} extracted symptoms available for filtering")
        
        # Step 2: HyDE for dense search
        search_query = query
        if use_hyde:
            from backend.rag.text.hyde_generator import hyde_generator
            logger.info("Generating HyDE document...")
            search_query = await hyde_generator.generate_hypothetical_document(query)
            
        # Step 3: Parallel dense + sparse retrieval
        async def get_dense():
            query_embedding = await text_embedder.embed_text(search_query)
            
            # Formulate metadata filter if specialty was guessed
            filters = {"specialty": specialty_filter} if specialty_filter else None
            
            # Query Diagnostic DB FIRST (PRIMARY — high precision mapping)
            diag_results = await vector_store.query_diagnostic(
                query_embedding=query_embedding, n_results=int(top_k), filters=filters
            )
            
            # Query Reference DB SECOND (SUPPORT — broad context)
            ref_results = await vector_store.query_reference(
                query_embedding=query_embedding, n_results=int(top_k), filters=filters
            )

            def extract_formatted(res, source_label):
                f = []
                if res and res.get("documents") and res["documents"][0]:
                    scores = res.get("distances", [[]])[0]
                    for i in range(len(res["documents"][0])):
                        cosine_score = scores[i] if i < len(scores) else 0.5
                        if cosine_score < self.DENSE_SIMILARITY_FLOOR: continue
                        f.append({
                            "id": res["ids"][0][i],
                            "document": res["documents"][0][i],
                            "metadata": res["metadatas"][0][i] if res.get("metadatas") else {},
                            "score": cosine_score,
                            "source": source_label
                        })
                return f

            diag_formatted = extract_formatted(diag_results, "diagnostic")
            ref_formatted = extract_formatted(ref_results, "reference")
            
            # Boost diagnostic results that have symptom overlap
            if extracted_symptoms:
                for chunk in diag_formatted:
                    meta = chunk.get("metadata", {})
                    chunk_symptoms = meta.get("symptoms", [])
                    if isinstance(chunk_symptoms, list) and chunk_symptoms:
                        overlap = set(s.lower() for s in extracted_symptoms) & set(s.lower() for s in chunk_symptoms)
                        if overlap:
                            # Boost score by up to 0.15 based on symptom overlap ratio
                            boost = 0.15 * (len(overlap) / max(len(extracted_symptoms), 1))
                            chunk["score"] = min(1.0, chunk["score"] + boost)
                            chunk["source"] = "diagnostic_boosted"
                            logger.debug(f"Boosted diagnostic chunk by {boost:.3f} ({len(overlap)} symptom overlap)")
            
            formatted = diag_formatted + ref_formatted
            # Sort by cosine similarity over combined results
            formatted.sort(key=lambda x: x["score"], reverse=True)
            formatted = formatted[:int(top_k * 1.5)]
            logger.info(f"Dense retrieval: {len(formatted)} chunks above similarity floor {self.DENSE_SIMILARITY_FLOOR}")
            return formatted

        # Use expanded query for BM25 (better keyword coverage)
        dense_results, sparse_results = await asyncio.gather(
            get_dense(),
            sparse_retriever.retrieve(query=expanded_query, top_k=top_k)
        )
        
        logger.info(f"Retrieval: {len(dense_results)} dense + {len(sparse_results)} sparse results")
        
        # Step 4: Reciprocal Rank Fusion (RRF)
        rrf_k = 45  # Lower = more weight to top-ranked docs (was 60)
        fused_scores = {}
        chunk_map = {}
        
        for rank, chunk in enumerate(dense_results):
            fused_scores[chunk["id"]] = fused_scores.get(chunk["id"], 0) + 1 / (rrf_k + rank + 1)
            chunk_map[chunk["id"]] = chunk
            
        for rank, chunk in enumerate(sparse_results):
            fused_scores[chunk["id"]] = fused_scores.get(chunk["id"], 0) + 1 / (rrf_k + rank + 1)
            if chunk["id"] not in chunk_map:
                chunk_map[chunk["id"]] = chunk
            else:
                chunk_map[chunk["id"]]["source"] = "hybrid"
                
        sorted_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)
        
        results = [chunk_map[idx] for idx in sorted_ids[:top_k]]
        logger.info(f"RRF fusion: {len(results)} final results (hybrid: {sum(1 for r in results if r.get('source') == 'hybrid')})")
        
        return results

text_retriever = TextRetriever()
