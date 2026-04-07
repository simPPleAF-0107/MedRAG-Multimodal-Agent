import asyncio
import logging
from backend.rag.text.retriever import text_retriever
from backend.rag.image.clip_embedder import clip_embedder
from backend.rag.vector_store import vector_store
from backend.rag.text.llm_reranker import llm_reranker

logger = logging.getLogger(__name__)

class RetrieverAgent:
    """
    Agent responsible for gathering evidence and context
    from the vector database using both text and image modalities.
    """
    
    def __init__(self):
        self.name = "Retriever Agent"
        self.role = "Gather diagnostic evidence from medical literature and patient history."

    async def _get_text_context(self, text_query: str) -> tuple:
        """Returns (context_string, retrieval_scores_list)"""
        if not text_query:
            return "No relevant text documents found.", [0.0]
        
        try:
            # Retrieve expanded context (top 15) using Hybrid search
            logger.info(f"Retriever: Starting hybrid search for query: {text_query[:80]}...")
            text_results = await text_retriever.retrieve(query=text_query, top_k=15)
            logger.info(f"Retriever: Got {len(text_results)} results from hybrid search")
            
            # Rerank down to top 5 using LLM (Vectorless compression)
            reranked_results = await llm_reranker.rerank(query=text_query, chunks=text_results, top_k=5)
            logger.info(f"Retriever: Got {len(reranked_results)} results after reranking")
            
            if not reranked_results:
                return "No relevant text documents found.", [0.0]
            
            # Extract similarity scores from the reranked results
            scores = [r.get("score", 0.75) for r in reranked_results]
            context = "\n\n".join([res['document'] for res in reranked_results])
            
            logger.info(f"Retriever: Evidence length={len(context)}, scores={scores}")
            return context, scores
            
        except Exception as e:
            logger.error(f"Retriever text context failed: {e}", exc_info=True)
            return "Retrieval error occurred.", [0.0]

    async def _get_image_context(self, image) -> str:
        if not image:
            return "No relevant image context found."
        
        try:
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
        except Exception as e:
            logger.error(f"Retriever image context failed: {e}")
            return "Image analysis unavailable."

    async def run(self, input_data: dict) -> dict:
        """
        Executes the retrieval logic concurrently.
        """
        text_query = input_data.get("text_query", "")
        image = input_data.get("image")
        
        try:
            # Parallel retrieval
            text_result, image_context = await asyncio.gather(
                self._get_text_context(text_query),
                self._get_image_context(image)
            )
            
            # _get_text_context returns a tuple (context_str, scores)
            text_context, retrieval_scores = text_result
            
            logger.info(f"RetrieverAgent complete: text_len={len(text_context)}, scores={retrieval_scores}, image_len={len(image_context)}")
                        
            return {
                "text_context": text_context,
                "image_context": image_context,
                "retrieval_scores": retrieval_scores,
            }
        except Exception as e:
            logger.error(f"RetrieverAgent.run failed: {e}", exc_info=True)
            return {
                "text_context": "",
                "image_context": "",
                "retrieval_scores": [0.0],
            }

retriever_agent = RetrieverAgent()
