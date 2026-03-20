import asyncio
from backend.rag.text.retriever import text_retriever
from backend.rag.image.clip_embedder import clip_embedder
from backend.rag.vector_store import vector_store
from backend.rag.text.llm_reranker import llm_reranker

class RetrieverAgent:
    """
    Agent responsible for gathering evidence and context
    from the vector database using both text and image modalities.
    """
    
    def __init__(self):
        self.name = "Retriever Agent"
        self.role = "Gather diagnostic evidence from medical literature and patient history."

    async def _get_text_context(self, text_query: str) -> str:
        if not text_query:
            return "No relevant text documents found."
            
        # Retrieve expanded context (top 15) using Hybrid search
        text_results = await text_retriever.retrieve(query=text_query, top_k=15)
        
        # Rerank down to top 5 using LLM (Vectorless compression)
        reranked_results = await llm_reranker.rerank(query=text_query, chunks=text_results, top_k=5)
        
        if not reranked_results:
            return "No relevant text documents found."
            
        return "\n\n".join([res['document'] for res in reranked_results])

    async def _get_image_context(self, image) -> str:
        if not image:
            return "No relevant image context found."
            
        image_embedding = await clip_embedder.embed_image(image)
        image_results = await vector_store.query_image(query_embedding=image_embedding, n_results=3)
        if image_results and image_results.get("metadatas") and image_results["metadatas"][0]:
            image_contexts = []
            for meta in image_results["metadatas"][0]:
                if "description" in meta:
                    image_contexts.append(meta["description"])
            if image_contexts:
                return "\n".join(image_contexts)
        return "No relevant image context found."

    async def run(self, input_data: dict) -> dict:
        """
        Executes the retrieval logic concurrently.
        """
        text_query = input_data.get("text_query", "")
        image = input_data.get("image")
        
        # Parallel retrieval
        text_context, image_context = await asyncio.gather(
            self._get_text_context(text_query),
            self._get_image_context(image)
        )
                    
        return {
            "text_context": text_context,
            "image_context": image_context
        }

retriever_agent = RetrieverAgent()
