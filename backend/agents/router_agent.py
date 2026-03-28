import json
from backend.llm.openai_client import openai_client

class AgenticRouter:
    """
    Intelligent query router.
    Classifies a raw text message into intent categories to save complex RAG pipeline costs.
    """
    
    async def route_query(self, message: str) -> str:
        prompt = f"""
Analyze the following query and classify it into exactly one of these categories:
1. 'small_talk': Greetings, general non-medical chat, thanks, simple affirmations.
2. 'clinical_query': Specific medical questions, symptom description, asking for diagnosis/treatment, medical advice.
3. 'summarization': Requests to summarize past reports, medical history, or long text.

Query: "{message}"

Return ONLY a JSON object with one key "category" and the value of your chosen category.
"""
        
        try:
            # We explicitly bypass caching here because router logic is purely structural 
            # and extremely cheap to run with small token counts.
            response = await openai_client.generate_completion(
                prompt=prompt,
                system_prompt="You are a strict API router. Return only raw JSON without markdown formatting.",
                max_tokens=50,
                temperature=0.0,
                use_cache=False
            )
            # Safe JSON extraction
            clean_json = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            return data.get("category", "clinical_query")
        except Exception as e:
            print(f"Agentic Router Error: {e}")
            return "clinical_query" # Safest fallback route

agentic_router = AgenticRouter()
