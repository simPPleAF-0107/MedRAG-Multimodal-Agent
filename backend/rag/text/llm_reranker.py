import json
import logging
from backend.llm.openai_client import openai_client

logger = logging.getLogger(__name__)

class LLMReranker:
    """
    Vectorless semantic compression. Evaluates raw text chunks against the query 
    strictly using LLM reasoning to filter out irrelevant noise, drastically increasing precision.
    """
    
    async def rerank(self, query: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
        if not chunks:
            return []
            
        if len(chunks) <= top_k:
            return chunks

        chunks_text = ""
        for i, chunk in enumerate(chunks):
            chunks_text += f"\n--- CHUNK {i} ---\n{chunk.get('document', '')}\n"

        prompt = f"""You are an expert medical reasoning system. Evaluate the relevance of each context chunk to the query. 
Return the index of the top {top_k} most relevant chunks in a JSON array of integers.

User Query: {query}
Retrieved Chunks:
{chunks_text}

Output ONLY a raw JSON array of integers representing the best chunks (e.g., [1, 3, 4]). Do not output markdown code blocks.
"""
        try:
            response = await openai_client.generate_completion(
                prompt=prompt,
                system_prompt="You are an expert context evaluator. Output ONLY valid JSON arrays.",
                temperature=0.0
            )
            
            try:
                # Clean potential markdown formatting
                clean_response = response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:-3]
                elif clean_response.startswith("```"):
                    clean_response = clean_response[3:-3]
                
                best_indices = json.loads(clean_response)
                
                # Filter and return in order of LLM preference
                reranked_chunks = []
                for idx in best_indices:
                    if isinstance(idx, int) and 0 <= idx < len(chunks):
                        reranked_chunks.append(chunks[idx])
                
                if not reranked_chunks:
                    return chunks[:top_k]
                    
                return reranked_chunks
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse LLM reranker output: {response}")
                return chunks[:top_k]
                
        except Exception as e:
            logger.error(f"LLM Reranking failed: {e}")
            return chunks[:top_k]

llm_reranker = LLMReranker()
