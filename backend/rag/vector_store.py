import os
import chromadb
from chromadb.config import Settings
from backend.config import settings

class VectorStore:
    def __init__(self):
        """
        Initialize persistent ChromaDB client for the MedRAG system.
        Creates text and image collections with Cosine similarity space.
        """
        # Ensure the directory exists
        os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        # Get or create collections
        self.text_collection = self.client.get_or_create_collection(
            name="text_embeddings",
            metadata={"hnsw:space": "cosine"}
        )
        self.image_collection = self.client.get_or_create_collection(
            name="image_embeddings",
            metadata={"hnsw:space": "cosine"}
        )

    async def store_text_embedding(self, doc_id: str, embedding: list[float], text: str, metadata: dict = None):
        """
        Store a text embedding in ChromaDB.
        """
        if metadata is None:
            metadata = {}
        
        self.text_collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata]
        )

    async def store_image_embedding(self, image_id: str, embedding: list[float], metadata: dict = None):
        """
        Store an image embedding in ChromaDB.
        """
        if metadata is None:
            metadata = {}
            
        self.image_collection.add(
            ids=[image_id],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    async def query_text(self, query_embedding: list[float], n_results: int = 5):
        """
        Query the text collection.
        """
        results = self.text_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results

    async def query_image(self, query_embedding: list[float], n_results: int = 5):
        """
        Query the image collection.
        """
        results = self.image_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results

# Singleton instance
vector_store = VectorStore()
