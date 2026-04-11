import os
import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
from backend.config import settings
import uuid

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        """
        Initialize persistent Qdrant client for the MedRAG system.
        Creates text and image collections with Cosine similarity space.
        Adds payload field indexes for filtered retrieval by specialty, source, category.
        """
        os.makedirs(settings.QDRANT_DB_DIR, exist_ok=True)
        self.client = QdrantClient(path=settings.QDRANT_DB_DIR)
        
        self.text_collection_name = "text_embeddings"
        self.image_collection_name = "image_embeddings"

        # Initialize Text Collection
        if not self.client.collection_exists(self.text_collection_name):
            self.client.create_collection(
                collection_name=self.text_collection_name,
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
            )
            
        # Initialize Image Collection    
        if not self.client.collection_exists(self.image_collection_name):
            self.client.create_collection(
                collection_name=self.image_collection_name,
                vectors_config=models.VectorParams(size=512, distance=models.Distance.COSINE),
            )

        # ── Payload indexes for filtered retrieval ──
        self._ensure_payload_indexes()

    def _ensure_payload_indexes(self):
        """Create payload field indexes for fast filtered queries (idempotent)."""
        index_fields = {
            "specialty": models.PayloadSchemaType.KEYWORD,
            "source": models.PayloadSchemaType.KEYWORD,
            "category": models.PayloadSchemaType.KEYWORD,
            "modality": models.PayloadSchemaType.KEYWORD,
        }
        try:
            collection_info = self.client.get_collection(self.text_collection_name)
            existing_indexes = set(collection_info.payload_schema.keys()) if collection_info.payload_schema else set()
            
            for field_name, field_type in index_fields.items():
                if field_name not in existing_indexes:
                    self.client.create_payload_index(
                        collection_name=self.text_collection_name,
                        field_name=field_name,
                        field_schema=field_type,
                    )
                    logger.info(f"Created payload index: {field_name} ({field_type})")
        except Exception as e:
            logger.warning(f"Payload index creation skipped (non-critical): {e}")

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

    def store_text_batch(self, points: list[dict]):
        """
        Bulk-upsert text embeddings into Qdrant for fast seeding.
        
        Each item in `points` should be:
            {"id": str, "vector": list[float], "payload": dict}
        
        Payload must include a "document" key with the original text.
        Call this synchronously from seeding scripts for maximum throughput.
        """
        if not points:
            return
        
        qdrant_points = []
        for p in points:
            point_id = p["id"] if self._is_valid_uuid(p["id"]) else str(uuid.uuid4())
            qdrant_points.append(
                models.PointStruct(
                    id=point_id,
                    vector=p["vector"],
                    payload=p["payload"]
                )
            )
        
        self.client.upsert(
            collection_name=self.text_collection_name,
            points=qdrant_points
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

    async def query_text_filtered(self, query_embedding: list[float], n_results: int = 5,
                                   specialty: str = None, source: str = None, category: str = None):
        """
        Query the text collection with optional payload filters.
        Filters narrow the search to documents matching the specified metadata fields.
        Falls back to unfiltered search if the filtered query returns too few results.
        """
        must_conditions = []
        if specialty:
            must_conditions.append(
                models.FieldCondition(key="specialty", match=models.MatchValue(value=specialty))
            )
        if source:
            must_conditions.append(
                models.FieldCondition(key="source", match=models.MatchValue(value=source))
            )
        if category:
            must_conditions.append(
                models.FieldCondition(key="category", match=models.MatchValue(value=category))
            )
        
        query_filter = models.Filter(must=must_conditions) if must_conditions else None
        
        results = self.client.query_points(
            collection_name=self.text_collection_name,
            query=query_embedding,
            query_filter=query_filter,
            limit=n_results
        ).points
        
        # Fallback: if filtered query returns too few, run unfiltered
        if len(results) < 3 and query_filter:
            logger.info(f"Filtered query returned {len(results)} results, falling back to unfiltered")
            results = self.client.query_points(
                collection_name=self.text_collection_name,
                query=query_embedding,
                limit=n_results
            ).points
        
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

    def get_text_count(self) -> int:
        """Return the current number of points in the text collection."""
        try:
            info = self.client.get_collection(self.text_collection_name)
            return info.points_count
        except Exception:
            return 0

    def _is_valid_uuid(self, val):
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False

# Singleton instance
vector_store = VectorStore()
