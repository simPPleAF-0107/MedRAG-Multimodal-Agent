from sentence_transformers import SentenceTransformer
from backend.config import settings
import asyncio

class TextEmbedder:
    def __init__(self):
        """
        Initialize the sentence-transformers model.
        Loads the model specified in the settings.
        """
        # Load the pre-trained model for text embeddings
        self.model = SentenceTransformer(settings.TEXT_EMBEDDING_MODEL)

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a given text string.
        Since SentenceTransformer is blocking, we run it in an executor thread.
        """
        loop = asyncio.get_running_loop()
        # encode returns a numpy array, we convert to list
        embedding = await loop.run_in_executor(None, self.model.encode, text)
        return embedding.tolist()

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of strings.
        """
        loop = asyncio.get_running_loop()
        embeddings = await loop.run_in_executor(None, self.model.encode, texts)
        return embeddings.tolist()

text_embedder = TextEmbedder()
