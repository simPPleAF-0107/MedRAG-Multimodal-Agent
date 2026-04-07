from rank_bm25 import BM25Okapi
from backend.rag.vector_store import vector_store
import logging
import numpy as np

logger = logging.getLogger(__name__)

class SparseRetriever:
    """
    Implements vectorless keyword-based sparse retrieval (BM25) over the Qdrant text corpus.
    Enhances recall for exact medical terminology, drug names, and dosages.
    
    Uses paginated scrolling to index ALL documents, not just the first 10K.
    """
    def __init__(self):
        self.bm25 = None
        self.corpus_docs = []
        self.corpus_ids = []
        self.corpus_metadatas = []
        self._initialized = False

    def _initialize_index(self):
        if self._initialized:
            return
            
        try:
            # Paginated scrolling to fetch ALL documents from Qdrant (not just first 10K)
            all_records = []
            offset = None
            page_size = 5000
            
            while True:
                records, next_offset = vector_store.client.scroll(
                    collection_name=vector_store.text_collection_name,
                    limit=page_size,
                    offset=offset,
                    with_payload=True
                )
                
                if not records:
                    break
                    
                all_records.extend(records)
                logger.info(f"BM25 index: loaded {len(all_records)} documents so far...")
                
                if next_offset is None:
                    break
                offset = next_offset
            
            if all_records:
                self.corpus_docs = [r.payload.get("document", "") for r in all_records]
                self.corpus_ids = [str(r.id) for r in all_records]
                self.corpus_metadatas = [r.payload for r in all_records]
                
                # Improved tokenization: lowercase, remove punctuation, filter stopwords
                import re
                STOPWORDS = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                           'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                           'would', 'could', 'should', 'may', 'might', 'can', 'shall',
                           'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                           'as', 'into', 'through', 'during', 'before', 'after', 'above',
                           'below', 'between', 'and', 'but', 'or', 'nor', 'not', 'so',
                           'if', 'then', 'than', 'that', 'this', 'it', 'its', 'which',
                           'who', 'what', 'where', 'when', 'how', 'all', 'each', 'every',
                           'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
                           'only', 'own', 'same', 'very'}
                
                tokenized_corpus = []
                for doc in self.corpus_docs:
                    # Clean and tokenize
                    clean = re.sub(r'[^a-zA-Z0-9\s-]', ' ', doc.lower())
                    tokens = [t for t in clean.split() if t not in STOPWORDS and len(t) > 2]
                    tokenized_corpus.append(tokens)
                
                self.bm25 = BM25Okapi(tokenized_corpus)
                logger.info(f"Initialized BM25 index with {len(self.corpus_docs)} documents (ALL indexed).")
            else:
                logger.warning("No documents found in Qdrant to build BM25 index.")
        except Exception as e:
            logger.error(f"Failed to initialize BM25 index: {e}")
            
        self._initialized = True

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Retrieves top_k chunks using BM25 keyword matching.
        Uses improved tokenization with stopword removal.
        """
        if not self._initialized:
            self._initialize_index()

        if not self.bm25 or not self.corpus_docs:
            return []

        import re
        # Same tokenization as indexing
        clean_query = re.sub(r'[^a-zA-Z0-9\s-]', ' ', query.lower())
        tokenized_query = [t for t in clean_query.split() if len(t) > 2]
        
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
