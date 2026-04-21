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
        # Connect to Docker Qdrant if URL is set, otherwise use local file mode
        if settings.QDRANT_URL:
            logger.info(f"Connecting to Qdrant server at {settings.QDRANT_URL}")
            self.client = QdrantClient(url=settings.QDRANT_URL)
        else:
            os.makedirs(settings.QDRANT_DB_DIR, exist_ok=True)
            self.client = QdrantClient(path=settings.QDRANT_DB_DIR)
        
        self.diagnostic_collection_name = "diagnostic_embeddings"
        self.reference_collection_name = "reference_embeddings"
        self.image_collection_name = "image_embeddings"

        # Initialize Diagnostic Collection
        if not self.client.collection_exists(self.diagnostic_collection_name):
            self.client.create_collection(
                collection_name=self.diagnostic_collection_name,
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
            )
            
        # Initialize Reference Collection
        if not self.client.collection_exists(self.reference_collection_name):
            self.client.create_collection(
                collection_name=self.reference_collection_name,
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
            "disease": models.PayloadSchemaType.KEYWORD,
            "symptoms": models.PayloadSchemaType.KEYWORD,
            "severity": models.PayloadSchemaType.KEYWORD,
            "source": models.PayloadSchemaType.KEYWORD,
            "category": models.PayloadSchemaType.KEYWORD,
            "modality": models.PayloadSchemaType.KEYWORD,
        }
        try:
            for collection_name in [self.diagnostic_collection_name, self.reference_collection_name]:
                collection_info = self.client.get_collection(collection_name)
                existing_indexes = set(collection_info.payload_schema.keys()) if collection_info.payload_schema else set()
                
                for field_name, field_type in index_fields.items():
                    if field_name not in existing_indexes:
                        self.client.create_payload_index(
                            collection_name=collection_name,
                            field_name=field_name,
                            field_schema=field_type,
                        )
                        logger.info(f"Created payload index: {field_name} ({field_type}) in {collection_name}")
        except Exception as e:
            logger.warning(f"Payload index creation skipped (non-critical): {e}")

    async def store_diagnostic_embedding(self, doc_id: str, embedding: list[float], text: str, metadata: dict = None):
        if metadata is None: metadata = {}
        metadata["document"] = text
        self.client.upsert(
            collection_name=self.diagnostic_collection_name,
            points=[models.PointStruct(id=doc_id if self._is_valid_uuid(doc_id) else str(uuid.uuid4()), vector=embedding, payload=metadata)]
        )

    async def store_reference_embedding(self, doc_id: str, embedding: list[float], text: str, metadata: dict = None):
        if metadata is None: metadata = {}
        metadata["document"] = text
        self.client.upsert(
            collection_name=self.reference_collection_name,
            points=[models.PointStruct(id=doc_id if self._is_valid_uuid(doc_id) else str(uuid.uuid4()), vector=embedding, payload=metadata)]
        )

    def store_diagnostic_batch(self, points: list[dict]):
        if not points: return
        qdrant_points = [
            models.PointStruct(
                id=p["id"] if self._is_valid_uuid(p["id"]) else str(uuid.uuid4()),
                vector=p["vector"],
                payload=p["payload"]
            ) for p in points
        ]
        self.client.upsert(collection_name=self.diagnostic_collection_name, points=qdrant_points)

    def store_reference_batch(self, points: list[dict]):
        if not points: return
        qdrant_points = [
            models.PointStruct(
                id=p["id"] if self._is_valid_uuid(p["id"]) else str(uuid.uuid4()),
                vector=p["vector"],
                payload=p["payload"]
            ) for p in points
        ]
        self.client.upsert(collection_name=self.reference_collection_name, points=qdrant_points)

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

    async def query_diagnostic(self, query_embedding: list[float], n_results: int = 5, filters: dict = None):
        """Query the highly structured Diagnostic DB. Returns top matches reflecting Symptom->Disease mapping."""
        return await self._query_collection(self.diagnostic_collection_name, query_embedding, n_results, filters)

    async def query_reference(self, query_embedding: list[float], n_results: int = 5, filters: dict = None):
        """Query the general Reference DB (PubMed, Guidelines, etc)."""
        return await self._query_collection(self.reference_collection_name, query_embedding, n_results, filters)

    async def _query_collection(self, collection_name: str, query_embedding: list[float], n_results: int = 5, filters: dict = None):
        must_conditions = []
        query_filter = None
        if filters:
            for key, val in filters.items():
                if val: must_conditions.append(models.FieldCondition(key=key, match=models.MatchValue(value=val)))
            if must_conditions:
                query_filter = models.Filter(must=must_conditions)
        
        try:
            results = self.client.query_points(
                collection_name=collection_name,
                query=query_embedding,
                query_filter=query_filter,
                limit=n_results
            ).points
        except Exception as e:
            logger.warning(f"Query on {collection_name} failed: {e}")
            results = []
            
        # Fallback to unfiltered if too restrictive
        if len(results) < 2 and query_filter:
            logger.info(f"Filtered query returned {len(results)} results in {collection_name}, falling back to unfiltered.")
            try:
                results = self.client.query_points(
                    collection_name=collection_name,
                    query=query_embedding,
                    limit=n_results
                ).points
            except Exception: pass
            
        return {
            "ids": [[res.id for res in results]],
            "documents": [[res.payload.get("document", "") for res in results]],
            "metadatas": [[res.payload for res in results]],
            "distances": [[res.score for res in results]]
        }

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

    def get_diagnostic_count(self) -> int:
        try: return self.client.get_collection(self.diagnostic_collection_name).points_count
        except Exception: return 0

    def get_reference_count(self) -> int:
        try: return self.client.get_collection(self.reference_collection_name).points_count
        except Exception: return 0

    def _is_valid_uuid(self, val):
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False

# Singleton instance
vector_store = VectorStore()
