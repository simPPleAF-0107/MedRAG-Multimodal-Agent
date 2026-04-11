import asyncio
import logging
from backend.rag.text.retriever import text_retriever
from backend.rag.image.clip_embedder import clip_embedder
from backend.rag.vector_store import vector_store
from backend.rag.text.llm_reranker import llm_reranker

logger = logging.getLogger(__name__)

_JACCARD_DEDUP_THRESHOLD = 0.70  # Chunks sharing >70% tokens are near-duplicates


def _jaccard(a: str, b: str) -> float:
    """Fast Jaccard similarity on word token sets."""
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def _deduplicate_chunks(chunks: list[dict], threshold: float = _JACCARD_DEDUP_THRESHOLD) -> list[dict]:
    """
    Remove near-duplicate evidence chunks using Jaccard token overlap.
    Assumes chunks are already sorted by score descending — keeps highest-scoring copy.
    """
    kept = []
    for candidate in chunks:
        is_dup = any(
            _jaccard(candidate["document"], existing["document"]) >= threshold
            for existing in kept
        )
        if not is_dup:
            kept.append(candidate)
    removed = len(chunks) - len(kept)
    if removed:
        logger.info(f"Deduplication: {len(chunks)} → {len(kept)} chunks ({removed} near-duplicates removed)")
    return kept


class RetrieverAgent:
    """
    Agent responsible for gathering evidence and context
    from the vector database using both text and image modalities.

    Pipeline:
      1. Hybrid retrieval (25 candidates: dense + BM25 sparse + RRF fusion)
      2. LLM reranker (25 → 8 chunks with relevance scores)
      3. Jaccard deduplication (removes near-duplicate evidence chunks)
    """

    def __init__(self):
        self.name = "Retriever Agent"
        self.role = "Gather diagnostic evidence from medical literature and patient history."

    async def _get_text_context(self, text_query: str) -> tuple:
        """Returns (context_string, retrieval_scores_list)"""
        if not text_query:
            return "No relevant text documents found.", [0.0]

        try:
            logger.info(f"Retriever: Starting hybrid search for query: {text_query[:80]}...")
            text_results = await text_retriever.retrieve(query=text_query, top_k=40)
            logger.info(f"Retriever: Got {len(text_results)} results from hybrid search")

            # LLM reranker: compress 25 → 8 most relevant chunks
            reranked_results = await llm_reranker.rerank(query=text_query, chunks=text_results, top_k=12)
            logger.info(f"Retriever: Got {len(reranked_results)} results after reranking")

            if not reranked_results:
                return "No relevant text documents found.", [0.0]

            # Deduplicate near-identical chunks to maximise evidence diversity
            reranked_results = _deduplicate_chunks(reranked_results)

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
                image_contexts = [
                    meta["description"]
                    for meta in image_results["metadatas"][0]
                    if "description" in meta
                ]
                if image_contexts:
                    return "\n".join(image_contexts)
            return "No relevant image context found."
        except Exception as e:
            logger.error(f"Retriever image context failed: {e}")
            return "Image analysis unavailable."

    async def run(self, input_data: dict) -> dict:
        """Executes retrieval concurrently across text and image modalities."""
        text_query = input_data.get("text_query", "")
        image = input_data.get("image")

        try:
            text_result, image_context = await asyncio.gather(
                self._get_text_context(text_query),
                self._get_image_context(image)
            )
            text_context, retrieval_scores = text_result

            logger.info(
                f"RetrieverAgent complete: text_len={len(text_context)}, "
                f"scores={retrieval_scores}, image_len={len(image_context)}"
            )

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
