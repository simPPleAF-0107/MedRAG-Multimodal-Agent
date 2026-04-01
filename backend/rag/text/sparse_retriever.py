from rank_bm25 import BM25Okapi
from backend.rag.vector_store import vector_store
import logging
import numpy as np

logger = logging.getLogger(__name__)

class SparseRetriever:
    """
    Implements vectorless keyword-based sparse retrieval (BM25) over the ChromaDB text corpus.
    Enhances recall for exact medical terminology and dosages.
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
            # Fetch all documents from Qdrant by scrolling
            records, _ = vector_store.client.scroll(
                collection_name=vector_store.text_collection_name,
                limit=10000,
                with_payload=True
            )
            
            if records:
                self.corpus_docs = [r.payload.get("document", "") for r in records]
                self.corpus_ids = [str(r.id) for r in records]
                self.corpus_metadatas = [r.payload for r in records]
                
                # Tokenize for BM25
                tokenized_corpus = [doc.lower().split() for doc in self.corpus_docs]
                self.bm25 = BM25Okapi(tokenized_corpus)
                logger.info(f"Initialized BM25 index with {len(self.corpus_docs)} documents.")
            else:
                logger.warning("No documents found in Qdrant to build BM25 index.")
        except Exception as e:
            logger.error(f"Failed to initialize BM25 index: {e}")
            
        self._initialized = True

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Retrieves top_k chunks using strict keyword matching (BM25).
        """
        if not self._initialized:
            self._initialize_index()

        if not self.bm25 or not self.corpus_docs:
            return []

        tokenized_query = query.lower().split()
        
        # Get BM25 scores
        doc_scores = self.bm25.get_scores(tokenized_query)
        
        # Get top K indices
        top_indices = np.argsort(doc_scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = doc_scores[idx]
            if score > 0:
                results.append({
                    "id": self.corpus_ids[idx],
                    "document": self.corpus_docs[idx],
                    "metadata": self.corpus_metadatas[idx] if self.corpus_metadatas else {},
                    "score": score,
                    "source": "sparse_bm25"
                })
                
        return results

sparse_retriever = SparseRetriever()
