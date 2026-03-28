from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder
from backend.rag.text.sparse_retriever import sparse_retriever
import asyncio

class TextRetriever:
    """
    Handles retrieving the most relevant text chunks from ChromaDB and BM25,
    fusing the results via Reciprocal Rank Fusion (RRF) for Hybrid search.
    """
    
    async def retrieve(self, query: str, top_k: int = 10, use_hyde: bool = True) -> list[dict]:
        """
        Embeds the query and fetches the top_k most similar documents.
        """
        search_query = query
        if use_hyde:
            from backend.rag.text.hyde_generator import hyde_generator
            print("Generating HyDE document...")
            search_query = await hyde_generator.generate_hypothetical_document(query)
            
        # Dense retrieval
        async def get_dense():
            query_embedding = await text_embedder.embed_text(search_query)
            results = await vector_store.query_text(
                query_embedding=query_embedding,
                n_results=top_k
            )
            formatted = []
            if results and results.get("documents") and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    formatted.append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "source": "dense_vector"
                    })
            return formatted

        # Run concurrent dense and sparse retrieval
        dense_results, sparse_results = await asyncio.gather(
            get_dense(),
            sparse_retriever.retrieve(query=query, top_k=top_k)
        )
        
        # Reciprocal Rank Fusion (RRF)
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
                
        # Sort chunks by fused score
        sorted_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)
        
        # Return the top_k fused results
        return [chunk_map[idx] for idx in sorted_ids[:top_k]]

text_retriever = TextRetriever()
