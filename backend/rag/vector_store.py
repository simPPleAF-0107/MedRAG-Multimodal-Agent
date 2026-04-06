import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from backend.config import settings
import uuid

class VectorStore:
    def __init__(self):
        """
        Initialize persistent Qdrant client for the MedRAG system.
        Creates text and image collections with Cosine similarity space.
        """
        os.makedirs(settings.QDRANT_DB_DIR, exist_ok=True)
        self.client = QdrantClient(path=settings.QDRANT_DB_DIR)
        
        self.text_collection_name = "text_embeddings"
        self.image_collection_name = "image_embeddings"

        # Initialize Text Collection
        if not self.client.collection_exists(self.text_collection_name):
            self.client.create_collection(
                collection_name=self.text_collection_name,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )
            
        # Initialize Image Collection    
        if not self.client.collection_exists(self.image_collection_name):
            self.client.create_collection(
                collection_name=self.image_collection_name,
                vectors_config=models.VectorParams(size=512, distance=models.Distance.COSINE),
            )

    async def store_text_embedding(self, doc_id: str, embedding: list[float], text: str, metadata: dict = None):
        """
        Store a text embedding in Qdrant.
        """
        if metadata is None:
            metadata = {}
        metadata["document"] = text  # Store text in payload
        
        self.client.upsert(
            collection_name=self.text_collection_name,
            points=[
                models.PointStruct(
                    id=doc_id if self._is_valid_uuid(doc_id) else str(uuid.uuid4()), # Qdrant prefers UUIDs
                    vector=embedding,
                    payload=metadata
                )
            ]
        )

    async def store_image_embedding(self, image_id: str, embedding: list[float], metadata: dict = None):
        """
        Store an image embedding in Qdrant.
        """
        if metadata is None:
            metadata = {}
            
        self.client.upsert(
            collection_name=self.image_collection_name,
            points=[
                models.PointStruct(
                    id=image_id if self._is_valid_uuid(image_id) else str(uuid.uuid4()),
                    vector=embedding,
                    payload=metadata
                )
            ]
        )

    async def query_text(self, query_embedding: list[float], n_results: int = 5):
        """
        Query the text collection. Returns data in a format similar to ChromaDB for backward compatibility.
        """
        results = self.client.query_points(
            collection_name=self.text_collection_name,
            query=query_embedding,
            limit=n_results
        ).points
        
        # Format for legacy compatibility
        formatted = {
            "ids": [[res.id for res in results]],
            "documents": [[res.payload.get("document", "") for res in results]],
            "metadatas": [[res.payload for res in results]],
            "distances": [[res.score for res in results]]
        }
        return formatted

    async def query_image(self, query_embedding: list[float], n_results: int = 5):
        """
        Query the image collection.
        """
        results = self.client.query_points(
            collection_name=self.image_collection_name,
            query=query_embedding,
            limit=n_results
        ).points
        
        formatted = {
            "ids": [[res.id for res in results]],
            "metadatas": [[res.payload for res in results]],
            "distances": [[res.score for res in results]]
        }
        return formatted

    def _is_valid_uuid(self, val):
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False

# Singleton instance
vector_store = VectorStore()
