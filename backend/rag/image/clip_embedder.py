import asyncio
from backend.config import settings
from sentence_transformers import SentenceTransformer
from PIL import Image

class ClipEmbedder:
    def __init__(self):
        """
        Initialize the CLIP model from sentence-transformers.
        """
        # Using a standard open-source CLIP model suitable for sentence-transformers
        # e.g. 'clip-ViT-B-32'
        self.model = SentenceTransformer('clip-ViT-B-32')

    async def embed_image(self, image: Image.Image) -> list[float]:
        """
        Generate embedding for a given PIL Image.
        """
        loop = asyncio.get_running_loop()
        embedding = await loop.run_in_executor(None, self.model.encode, image)
        return embedding.tolist()

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate text embedding in the same multimodal space as the images.
        Useful when querying images with a text search.
        """
        loop = asyncio.get_running_loop()
        embedding = await loop.run_in_executor(None, self.model.encode, text)
        return embedding.tolist()

clip_embedder = ClipEmbedder()
