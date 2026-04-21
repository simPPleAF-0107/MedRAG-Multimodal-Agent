from rank_bm25 import BM25Okapi
from backend.rag.vector_store import vector_store
import logging
import numpy as np
import pickle
import os
import re

logger = logging.getLogger(__name__)

# Persistent cache stored next to the vector DB
_BM25_CACHE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "vector-db", "bm25_index.pkl"
)

_STOPWORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'can', 'shall', 'to', 'of', 'in', 'for',
    'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'between', 'and', 'but', 'or',
    'nor', 'not', 'so', 'if', 'then', 'than', 'that', 'this', 'it',
    'its', 'which', 'who', 'what', 'where', 'when', 'how', 'all', 'each',
    'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
    'no', 'only', 'own', 'same', 'very'
}


def _tokenize(text: str) -> list[str]:
    """Shared tokenizer: lowercase, strip punctuation, remove stopwords."""
    clean = re.sub(r'[^a-zA-Z0-9\s-]', ' ', text.lower())
    return [t for t in clean.split() if t not in _STOPWORDS and len(t) > 2]


class SparseRetriever:
    """
    BM25 sparse retriever (keyword recall) over the Qdrant text corpus.

    Caching strategy:
    - First run  : builds index from all 31K Qdrant docs (~3-4s), pickles to disk
    - Later runs : loads pickle in ~0.1s; invalidated when collection size changes
    
    Enhances recall for exact medical terminology, drug names, and dosages
    where dense vector search may underperform.
    """

    def __init__(self):
        self.bm25 = None
        self.corpus_docs: list[str] = []
        self.corpus_ids: list[str] = []
        self.corpus_metadatas: list[dict] = []
        self._initialized = False

    # ── Cache helpers ────────────────────────────────────────────────────────

    def _get_collection_size(self) -> int:
        try:
            diag_count = vector_store.client.get_collection(vector_store.diagnostic_collection_name).points_count
            ref_count = vector_store.client.get_collection(vector_store.reference_collection_name).points_count
            return diag_count + ref_count
        except Exception:
            return -1

    def _load_from_cache(self, collection_size: int) -> bool:
        if not os.path.exists(_BM25_CACHE_PATH):
            return False
        try:
            with open(_BM25_CACHE_PATH, 'rb') as f:
                cached = pickle.load(f)
            if cached.get('collection_size') != collection_size:
                logger.info(
                    f"BM25 cache stale "
                    f"(cached={cached.get('collection_size')}, current={collection_size}). Rebuilding..."
                )
                return False
            self.bm25 = cached['bm25']
            self.corpus_docs = cached['corpus_docs']
            self.corpus_ids = cached['corpus_ids']
            self.corpus_metadatas = cached['corpus_metadatas']
            logger.info(f"BM25 index loaded from disk cache ({len(self.corpus_docs)} docs, ~0.1s).")
            return True
        except Exception as e:
            logger.warning(f"BM25 cache load failed (will rebuild): {e}")
            return False

    def _save_to_cache(self, collection_size: int):
        try:
            os.makedirs(os.path.dirname(_BM25_CACHE_PATH), exist_ok=True)
            with open(_BM25_CACHE_PATH, 'wb') as f:
                pickle.dump({
                    'collection_size': collection_size,
                    'bm25': self.bm25,
                    'corpus_docs': self.corpus_docs,
                    'corpus_ids': self.corpus_ids,
                    'corpus_metadatas': self.corpus_metadatas,
                }, f, protocol=pickle.HIGHEST_PROTOCOL)
            logger.info(f"BM25 index persisted to disk: {_BM25_CACHE_PATH}")
        except Exception as e:
            logger.warning(f"BM25 cache save failed (non-critical): {e}")

    # ── Index build ──────────────────────────────────────────────────────────

    def _initialize_index(self):
        if self._initialized:
            return

        collection_size = self._get_collection_size()

        # Fast path: load from disk
        if self._load_from_cache(collection_size):
            self._initialized = True
            return

        # Slow path: paginated scroll from Qdrant then pickle
        try:
            all_records = []
            # Scroll both diagnostic and reference collections
            for coll_name in [vector_store.diagnostic_collection_name, vector_store.reference_collection_name]:
                offset = None
                page_size = 5000
                while True:
                    records, next_offset = vector_store.client.scroll(
                        collection_name=coll_name,
                        limit=page_size,
                        offset=offset,
                        with_payload=True
                    )
                    if not records:
                        break
                    all_records.extend(records)
                    logger.info(f"BM25 index: loaded {len(all_records)} documents from {coll_name}...")
                    if next_offset is None:
                        break
                    offset = next_offset

            if all_records:
                self.corpus_docs = [r.payload.get("document", "") for r in all_records]
                self.corpus_ids = [str(r.id) for r in all_records]
                self.corpus_metadatas = [r.payload for r in all_records]

                tokenized_corpus = [_tokenize(doc) for doc in self.corpus_docs]
                self.bm25 = BM25Okapi(tokenized_corpus)
                logger.info(f"Initialized BM25 index with {len(self.corpus_docs)} documents (ALL indexed).")

                self._save_to_cache(collection_size)
            else:
                logger.warning("No documents found in Qdrant to build BM25 index.")
        except Exception as e:
            logger.error(f"Failed to initialize BM25 index: {e}")

        self._initialized = True

    # ── Public API ───────────────────────────────────────────────────────────

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve top_k chunks via BM25 keyword matching."""
        if not self._initialized:
            self._initialize_index()

        if not self.bm25 or not self.corpus_docs:
            return []

        tokenized_query = _tokenize(query)
        doc_scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(doc_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = doc_scores[idx]
            if score > 0:
                results.append({
                    "id": self.corpus_ids[idx],
                    "document": self.corpus_docs[idx],
                    "metadata": self.corpus_metadatas[idx] if self.corpus_metadatas else {},
                    "score": float(score),
                    "source": "sparse_bm25"
                })

        return results


sparse_retriever = SparseRetriever()
