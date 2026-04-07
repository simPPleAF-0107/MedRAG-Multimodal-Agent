from openai import AsyncOpenAI, APIError, RateLimitError
from backend.config import settings
from backend.utils.logger import logger
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from pathlib import Path

class OpenAIClient:
    def __init__(self):
        """
        Initialize the AsyncOpenAI client with API key from settings.
        Configuration includes an explicit timeout for reliability.
        """
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY, 
            timeout=60.0,
            max_retries=2
        )

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((RateLimitError, APIError)),
        reraise=True
    )
    async def generate_completion(
        self, 
        prompt: str, 
        system_prompt: str = "You are a highly capable AI medical assistant.", 
        model: str = "gpt-5.4-mini",
        temperature: float = 0.2,
        max_tokens: int = 1500,
        use_cache: bool = True
    ) -> str:
        """
        Generate a text completion using OpenAI's API.
        Can be used for reasoning or definitive report generation.
        Checks Semantic Cache first to save API costs.
        """
        if use_cache:
            from backend.llm.semantic_cache import semantic_cache
            cached = await semantic_cache.get_cached_response(prompt, system_prompt)
            if cached:
                logger.debug("LLM Cache hit! Returning instant response.")
                return cached
                
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_completion_tokens=max_tokens
            )
            response_text = response.choices[0].message.content
            
            if use_cache:
                from backend.llm.semantic_cache import semantic_cache
                await semantic_cache.set_cached_response(prompt, system_prompt, response_text)
                
            return response_text
        except Exception as e:
            logger.error(f"OpenAI API error during completion: {e}")
            raise
            
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((RateLimitError, APIError)),
        reraise=True
    )
    async def generate_transcription(self, audio_file_path: str) -> str:
        """
        Transcribe an audio file using OpenAI's Whisper model.
        Features automatic retry logic for transient errors.
        """
        try:
            file_path = Path(audio_file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
                
            # Passing path directly bypasses blocking open() in the event loop
            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=file_path
            )
            return response.text
        except Exception as e:
            logger.error(f"OpenAI Audio error during transcription: {e}")
            raise

openai_client = OpenAIClient()
