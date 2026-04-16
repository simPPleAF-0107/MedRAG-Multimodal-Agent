import json
import logging
from backend.llm.openai_client import openai_client

logger = logging.getLogger(__name__)

class LLMReranker:
    """
    Vectorless semantic compression. Evaluates raw text chunks against the query 
    strictly using LLM reasoning to filter out irrelevant noise, drastically increasing precision.
    Now returns relevance scores alongside the reranked chunks for confidence calibration.
    """
    
    async def rerank(self, query: str, chunks: list[dict], top_k: int = 12) -> list[dict]:
        if not chunks:
            return []
            
        if len(chunks) <= top_k:
            # Assign default scores based on position
            for i, chunk in enumerate(chunks):
                chunk["score"] = round(0.85 - (i * 0.05), 2)
            return chunks

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
