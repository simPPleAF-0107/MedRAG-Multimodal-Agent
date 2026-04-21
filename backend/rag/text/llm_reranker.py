import json
import logging
import asyncio
from backend.llm.openai_client import openai_client

logger = logging.getLogger(__name__)

# ── Cross-Encoder Model (loaded lazily on first use) ──────────────────────────
_cross_encoder = None
_cross_encoder_failed = False


def _load_cross_encoder():
    """Lazy-load the cross-encoder model. Returns None if unavailable."""
    global _cross_encoder, _cross_encoder_failed
    if _cross_encoder_failed:
        return None
    if _cross_encoder is not None:
        return _cross_encoder
    try:
        from sentence_transformers import CrossEncoder
        logger.info("Loading cross-encoder model: cross-encoder/ms-marco-MiniLM-L-6-v2 ...")
        _cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)
        logger.info("Cross-encoder model loaded successfully.")
        return _cross_encoder
    except Exception as e:
        logger.warning(f"Cross-encoder model failed to load (will fallback to LLM reranker): {e}")
        _cross_encoder_failed = True
        return None


class LLMReranker:
    """
    Two-stage reranker:
      Stage 1 (preferred): Cross-encoder model scores (query, chunk) pairs locally
      Stage 2 (fallback):  LLM-based JSON scoring via GPT-5.4-mini

    The cross-encoder is dramatically more accurate for relevance scoring,
    runs locally (no API cost), and is faster than an LLM call.
    """

    async def rerank(self, query: str, chunks: list[dict], top_k: int = 10) -> list[dict]:
        if not chunks:
            return []

        if len(chunks) <= top_k:
            # Assign default scores based on position
            for i, chunk in enumerate(chunks):
                chunk["score"] = round(0.85 - (i * 0.05), 2)
            return chunks

        # ── Stage 1: Try cross-encoder ────────────────────────────────────────
        cross_encoder_result = await self._cross_encoder_rerank(query, chunks, top_k)
        if cross_encoder_result is not None:
            return cross_encoder_result

        # ── Stage 2: Fallback to LLM reranking ────────────────────────────────
        logger.info("Cross-encoder unavailable, falling back to LLM reranker...")
        return await self._llm_rerank(query, chunks, top_k)

    async def _cross_encoder_rerank(self, query: str, chunks: list[dict], top_k: int) -> list[dict] | None:
        """Score all (query, chunk) pairs with the cross-encoder model."""
        model = _load_cross_encoder()
        if model is None:
            return None

        try:
            # Build (query, document) pairs for the cross-encoder
            pairs = [(query, chunk.get("document", "")[:512]) for chunk in chunks]

            # Run in executor thread (model inference is blocking)
            loop = asyncio.get_running_loop()
            scores = await loop.run_in_executor(None, model.predict, pairs)

            # Attach scores and sort descending
            scored_chunks = []
            for i, chunk in enumerate(chunks):
                c = chunk.copy()
                # Cross-encoder scores can be negative; normalize to 0-1 via sigmoid-like mapping
                raw_score = float(scores[i])
                # Simple min-max normalization across this batch
                c["raw_ce_score"] = raw_score
                scored_chunks.append(c)

            # Normalize scores to 0.0 - 1.0 range
            raw_scores = [c["raw_ce_score"] for c in scored_chunks]
            min_s, max_s = min(raw_scores), max(raw_scores)
            score_range = max_s - min_s if max_s != min_s else 1.0

            for c in scored_chunks:
                c["score"] = round((c["raw_ce_score"] - min_s) / score_range, 4)
                del c["raw_ce_score"]

            # Sort by score descending, take top_k
            scored_chunks.sort(key=lambda x: x["score"], reverse=True)
            result = scored_chunks[:top_k]

            logger.info(
                f"Cross-encoder reranker: {len(chunks)} → {len(result)} chunks, "
                f"scores={[c['score'] for c in result]}"
            )
            return result

        except Exception as e:
            logger.error(f"Cross-encoder reranking failed: {e}")
            return None

    async def _llm_rerank(self, query: str, chunks: list[dict], top_k: int) -> list[dict]:
        """Fallback: LLM-based reranking via GPT-5.4-mini."""
        chunks_text = ""
        for i, chunk in enumerate(chunks):
            doc = chunk.get('document', '')[:500]  # Truncate long docs
            chunks_text += f"\n--- CHUNK {i} ---\n{doc}\n"

        prompt = f"""You are an expert medical context evaluator. Evaluate how relevant each chunk is to the patient's query.

User Query: {query}

Retrieved Chunks:
{chunks_text}

Return a JSON array of objects with "index" (chunk number) and "relevance" (0.0-1.0 score).
Rank by relevance and return only the top {top_k} most relevant chunks.
Example: [{{"index": 2, "relevance": 0.92}}, {{"index": 0, "relevance": 0.78}}]

Output ONLY valid JSON. No markdown code blocks, no explanation."""

        try:
            response = await openai_client.generate_completion(
                prompt=prompt,
                system_prompt="You are an expert medical context evaluator. Output ONLY valid JSON arrays.",
                temperature=0.0,
                max_tokens=300
            )

            try:
                clean_response = response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.startswith("```"):
                    clean_response = clean_response[3:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]
                clean_response = clean_response.strip()

                parsed = json.loads(clean_response)

                # Handle both old format [1, 3, 4] and new format [{"index": 1, "relevance": 0.9}]
                reranked_chunks = []
                if parsed and isinstance(parsed[0], dict):
                    # New format with scores
                    for item in parsed:
                        idx = item.get("index", 0)
                        score = item.get("relevance", 0.5)
                        if isinstance(idx, int) and 0 <= idx < len(chunks):
                            chunk = chunks[idx].copy()
                            chunk["score"] = round(float(score), 3)
                            reranked_chunks.append(chunk)
                else:
                    # Old format: plain index array
                    for i, idx in enumerate(parsed):
                        if isinstance(idx, int) and 0 <= idx < len(chunks):
                            chunk = chunks[idx].copy()
                            chunk["score"] = round(0.85 - (i * 0.05), 2)
                            reranked_chunks.append(chunk)

                if not reranked_chunks:
                    return self._fallback_with_scores(chunks, top_k)

                logger.info(f"LLM Reranker: returned {len(reranked_chunks)} chunks with scores {[c['score'] for c in reranked_chunks]}")
                return reranked_chunks[:top_k]

            except json.JSONDecodeError:
                logger.error(f"Failed to parse LLM reranker output: {response}")
                return self._fallback_with_scores(chunks, top_k)

        except Exception as e:
            logger.error(f"LLM Reranking failed: {e}")
            return self._fallback_with_scores(chunks, top_k)

    def _fallback_with_scores(self, chunks: list[dict], top_k: int) -> list[dict]:
        """Fallback: return top_k chunks with position-based scores."""
        result = []
        for i, chunk in enumerate(chunks[:top_k]):
            c = chunk.copy()
            c["score"] = round(0.7 - (i * 0.03), 2)
            result.append(c)
        return result

llm_reranker = LLMReranker()
