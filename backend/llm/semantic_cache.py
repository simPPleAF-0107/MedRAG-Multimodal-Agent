import json
import hashlib
from backend.config import settings

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class SemanticCache:
    """
    Robust Caching layer for LLM Generations.
    Saves API credits and reduces latency by returning cached responses
    for identical RAG or conversation prompts.
    """
    def __init__(self):
        self.redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
        if REDIS_AVAILABLE:
            # We don't fail immediately, we fail gracefully on operations if redis is offline
            self.client = redis.from_url(self.redis_url, decode_responses=True)
        else:
            self.client = None

    async def get_cached_response(self, prompt: str, system_prompt: str) -> str:
        if not self.client:
            return None
        # Hash the combined prompt to create a unique ID
        combined = f"{system_prompt}|{prompt}"
        prompt_hash = hashlib.sha256(combined.encode()).hexdigest()
        try:
            return await self.client.get(f"llm_cache:{prompt_hash}")
        except Exception as e:
            print(f"Redis cache Read Error: {e}")
            return None

    async def set_cached_response(self, prompt: str, system_prompt: str, response: str):
        if not self.client:
            return
        combined = f"{system_prompt}|{prompt}"
        prompt_hash = hashlib.sha256(combined.encode()).hexdigest()
        try:
            # Cache the response for 24 hours
            await self.client.setex(f"llm_cache:{prompt_hash}", 86400, response)
        except Exception as e:
            print(f"Redis cache Write Error: {e}")

semantic_cache = SemanticCache()
