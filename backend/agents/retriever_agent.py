import asyncio
import logging
from backend.rag.text.retriever import text_retriever
from backend.rag.image.clip_embedder import clip_embedder
from backend.rag.vector_store import vector_store
from backend.rag.text.llm_reranker import llm_reranker

logger = logging.getLogger(__name__)

_JACCARD_DEDUP_THRESHOLD = 0.70  # Chunks sharing >70% tokens are near-duplicates
_RELEVANCE_SCORE_FLOOR = 0.40   # Chunks below this score are filtered out after reranking


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


def _classify_evidence_quality(scores: list[float]) -> str:
    """
    Classify the overall quality of retrieved evidence based on relevance scores.
    Returns: HIGH / MODERATE / LOW / INSUFFICIENT
    """
    if not scores:
        return "INSUFFICIENT"
    avg = sum(scores) / len(scores)
    best = max(scores)
    num_good = sum(1 for s in scores if s >= 0.50)

    if avg >= 0.65 and num_good >= 3:
        return "HIGH"
    elif avg >= 0.45 and num_good >= 2:
        return "MODERATE"
    elif best >= 0.40:
        return "LOW"
    else:
        return "INSUFFICIENT"


def _format_numbered_chunks(chunks: list[dict]) -> str:
    """
    Format evidence chunks with numbered headers for citation enforcement.
    The LLM is instructed to cite [Evidence: Chunk X] using these numbers.
    """
    if not chunks:
        return "No relevant medical evidence was retrieved for this query."

    formatted_parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        source = meta.get("source", "unknown")
        specialty = meta.get("specialty", "")
        header = f"[Chunk {i}]"
        if specialty:
            header += f" (Specialty: {specialty})"
        if source and source != "unknown":
            header += f" (Source: {source})"
        formatted_parts.append(f"{header}\n{chunk['document']}")

    return "\n\n".join(formatted_parts)


class RetrieverAgent:
    """
    Agent responsible for gathering evidence and context
    from the vector database using both text and image modalities.

    Pipeline:
      1. Hybrid retrieval (40 candidates: dense + BM25 sparse + RRF fusion)
      2. Cross-encoder reranker (40 → 10 chunks with relevance scores)
      3. Relevance threshold filtering (remove chunks with score < 0.40)
      4. Jaccard deduplication (removes near-duplicate evidence chunks)
      5. Evidence quality classification (HIGH/MODERATE/LOW/INSUFFICIENT)
      6. Numbered chunk formatting for citation enforcement
    """

    def __init__(self):
        self.name = "Retriever Agent"
        self.role = "Gather diagnostic evidence from medical literature and patient history."

    async def _get_text_context(self, text_query: str) -> tuple:
        """Returns (context_string, retrieval_scores_list, evidence_quality)"""
        if not text_query:
            return "No relevant text documents found.", [0.0], "INSUFFICIENT"

        try:
            logger.info(f"Retriever: Starting hybrid search for query: {text_query[:80]}...")
            text_results = await text_retriever.retrieve(query=text_query, top_k=40)
            logger.info(f"Retriever: Got {len(text_results)} results from hybrid search")

            # Cross-encoder/LLM reranker: compress 40 → 3 most relevant chunks (Top-3 Strict Mode)
            reranked_results = await llm_reranker.rerank(query=text_query, chunks=text_results, top_k=3)
            logger.info(f"Retriever: Got {len(reranked_results)} results after reranking")

            if not reranked_results:
                return "No relevant text documents found.", [0.0], "INSUFFICIENT"

            # ── P2: Relevance threshold filtering ─────────────────────────────
            # Remove chunks with score below the floor — prevents noisy context
            pre_filter_count = len(reranked_results)
            reranked_results = [
                r for r in reranked_results
                if r.get("score", 0.0) >= _RELEVANCE_SCORE_FLOOR
            ]
            filtered_count = pre_filter_count - len(reranked_results)
            if filtered_count:
                logger.info(
                    f"Relevance filter: {pre_filter_count} → {len(reranked_results)} chunks "
                    f"({filtered_count} below threshold {_RELEVANCE_SCORE_FLOOR})"
                )

            if not reranked_results:
                return (
                    "Retrieved evidence did not meet the relevance threshold for this query. "
                    "The system's knowledge base may not adequately cover this topic.",
                    [0.0],
                    "INSUFFICIENT"
                )

            # Deduplicate near-identical chunks to maximise evidence diversity
            reranked_results = _deduplicate_chunks(reranked_results)

            scores = [r.get("score", 0.5) for r in reranked_results]

            # ── P6: Format with numbered headers for citation enforcement ─────
            context = _format_numbered_chunks(reranked_results)

            # Classify evidence quality
            evidence_quality = _classify_evidence_quality(scores)

            logger.info(
                f"Retriever: evidence_quality={evidence_quality}, "
                f"num_chunks={len(reranked_results)}, scores={scores}"
            )
            return context, scores, evidence_quality

        except Exception as e:
            logger.error(f"Retriever text context failed: {e}", exc_info=True)
            return "Retrieval error occurred.", [0.0], "INSUFFICIENT"

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
            # 1. Fetch image context first
            image_context = await self._get_image_context(image)
            
            # 2. Joint Reasoning: Inject image findings into text query
            combined_query = text_query
            if image_context and image_context != "No relevant image context found." and image_context != "Image analysis unavailable.":
                combined_query = f"{text_query}. Image findings: {image_context}"
                logger.info("Retriever: Aligned image findings into text query for joint reasoning.")

            # 3. Retrieve text context using the combined multimodal query
            text_context, retrieval_scores, evidence_quality = await self._get_text_context(combined_query)

            logger.info(
                f"RetrieverAgent complete: text_len={len(text_context)}, "
                f"scores={retrieval_scores}, evidence_quality={evidence_quality}, "
                f"image_len={len(image_context)}"
            )

            return {
                "text_context": text_context,
                "image_context": image_context,
                "retrieval_scores": retrieval_scores,
                "evidence_quality": evidence_quality,
            }
        except Exception as e:
            logger.error(f"RetrieverAgent.run failed: {e}", exc_info=True)
            return {
                "text_context": "",
                "image_context": "",
                "retrieval_scores": [0.0],
                "evidence_quality": "INSUFFICIENT",
            }


retriever_agent = RetrieverAgent()
