from backend.llm.openai_client import openai_client

class HyDEGenerator:
    """
    Hypothetical Document Embeddings (HyDE).
    Generates a hypothetical clinical note or hypothetical medical record that perfectly answers the given query.
    This generated text is then embedded for dense retrieval, acting as a much stronger semantic 
    anchor than a short, poorly phrased user query.
    """
    
    async def generate_hypothetical_document(self, query: str) -> str:
        prompt = (
            f"Please write a comprehensive, hypothetical medical snippet or clinical note "
            f"that directly addresses or contains the information answering the following patient query. "
            f"Write it in a formal, clinical tone as if it were extracted from a medical textbook "
            f"or an electronic health record. The query is: '{query}'"
        )
        try:
            hypothetical_doc = await openai_client.generate_completion(
                prompt=prompt,
                system_prompt="You are a clinical NLP assistant generating hypothetical documents for vector search.",
                max_tokens=250,
                temperature=0.3
            )
            return hypothetical_doc
        except Exception as e:
            # Fallback to the original query if OpenAI LLM fails
            print(f"HyDE Generation failed, falling back to raw query: {e}")
            return query

hyde_generator = HyDEGenerator()
