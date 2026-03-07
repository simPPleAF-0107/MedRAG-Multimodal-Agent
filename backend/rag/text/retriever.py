from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder

class TextRetriever:
    """
    Handles retrieving the most relevant text chunks from ChromaDB
    given a search query.
    """
    
    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Embeds the query and fetches the top_k most similar documents.
        """
        # Embed the query
        query_embedding = await text_embedder.embed_text(query)
        
        # Query ChromaDB collection
        results = await vector_store.query_text(
            query_embedding=query_embedding,
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        if results and results.get("documents") and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    "distance": results["distances"][0][i] if results.get("distances") else None
                })
        
        return formatted_results

text_retriever = TextRetriever()
