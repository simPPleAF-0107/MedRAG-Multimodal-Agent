"""
MedRAG Retrieval Benchmark Script
=================================
Tests the latency and precision of the multi-strategy hybrid retrieval pipeline,
including the new specialty payload filters.
"""
import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.text.retriever import TextRetriever
from backend.rag.vector_store import vector_store
import logging

# Suppress debug logs for clean output
logging.getLogger("qdrant_client").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

async def run_benchmark():
    retriever = TextRetriever()
    
    test_queries = [
        "What is the recommended HbA1c target for a diabetes mellitus type 2 patient?",
        "What are the severe adverse side effects and contraindications for lisinopril?",
        "What is the first line treatment for a severe asthma exacerbation in the ER?",
        "What does the ICD-10 code J45.909 stand for?",
        "Is there any recent randomized clinical trial data for Pembrolizumab in melanoma?",
    ]
    
    print("=" * 70)
    print(" >>> MedRAG RETRIEVAL PERFORMANCE BENCHMARK <<<")
    total_count = vector_store.get_diagnostic_count() + vector_store.get_reference_count()
    print(f" Total Text Documents Available: {total_count:,}")
    print("=" * 70)
    
    total_time = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Query: '{query}'")
        
        # Test latency
        start_time = time.time()
        results = await retriever.retrieve(query, top_k=5, use_hyde=False) # Disable HyDE to measure raw DB performance
        latency = time.time() - start_time
        total_time += latency
        
        print(f"  --> Latency: {latency * 1000:.1f} ms")
        
        # Analyze sources
        if not results:
            print("  [No results found]")
            continue
            
        print(f"  --> Top {len(results)} Context Sources:")
        for r in results:
            source = r['metadata'].get('source', 'Unknown')
            specialty = r['metadata'].get('specialty', 'Unknown')
            modality = r['metadata'].get('modality', 'text')
            
            # Print a snippet of the doc
            snippet = r['document'][:80].replace("\n", " ").strip()
            print(f"     - [{source} | {specialty}] {snippet}...")
            
    print("\n" + "=" * 70)
    print(f" [Benchmark Complete]")
    print(f" Average Retrieval Latency: {(total_time / len(test_queries)) * 1000:.1f} ms per query")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_benchmark())
