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
    
    async def retrieve(self, query: str, top_k: int = 10, use_hyde: bool = True) -> list[dict]:
        """
        Multi-strategy retrieval pipeline:
        1. Expand query with medical entities
        2. Generate HyDE hypothetical document
        3. Run dense (Qdrant) + sparse (BM25) in parallel
        4. Fuse results with RRF
        """
        # Step 1: Medical entity expansion for BM25
        expanded_query = self._expand_query_with_entities(query)
        
        # Step 2: HyDE for dense search
        search_query = query
        if use_hyde:
            from backend.rag.text.hyde_generator import hyde_generator
            logger.info("Generating HyDE document...")
            search_query = await hyde_generator.generate_hypothetical_document(query)
            
        # Step 3: Parallel dense + sparse retrieval
        async def get_dense():
            query_embedding = await text_embedder.embed_text(search_query)
            results = await vector_store.query_text(
                query_embedding=query_embedding,
                n_results=top_k
            )
            formatted = []
            if results and results.get("documents") and results["documents"][0]:
                scores = results.get("distances", [[]])[0]
                for i in range(len(results["documents"][0])):
                    formatted.append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "score": scores[i] if i < len(scores) else 0.5,
                        "source": "dense_vector"
                    })
            return formatted

        # Use expanded query for BM25 (better keyword coverage)
        dense_results, sparse_results = await asyncio.gather(
            get_dense(),
            sparse_retriever.retrieve(query=expanded_query, top_k=top_k)
        )
        
        logger.info(f"Retrieval: {len(dense_results)} dense + {len(sparse_results)} sparse results")
        
        # Step 4: Reciprocal Rank Fusion (RRF)
        rrf_k = 60
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
