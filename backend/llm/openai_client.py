from openai import AsyncOpenAI
from backend.config import settings

class OpenAIClient:
    def __init__(self):
        """
        Initialize the AsyncOpenAI client with API key from settings.
        """
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_completion(
        self, 
        prompt: str, 
        system_prompt: str = "You are a highly capable AI medical assistant.", 
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.2,
        max_tokens: int = 1500
    ) -> str:
        """
        Generate a text completion using OpenAI's API.
        Can be used for reasoning or definitive report generation.
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")

openai_client = OpenAIClient()
