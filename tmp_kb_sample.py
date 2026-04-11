import sys
import os
import json

sys.path.insert(0, os.path.abspath('.'))

try:
    with open('vector-db/knowledge_graph.json', 'r') as f:
        kg = json.load(f)
        print("=== KNOWLEDGE GRAPH SAMPLES ===")
        print(json.dumps(kg.get('nodes', [])[:3], indent=2))
        print("Edges (Links):")
        print(json.dumps(kg.get('links', [])[:3], indent=2))
except Exception as e:
    print(f"Graph error: {e}")

try:
    from backend.rag.vector_store import vector_store
    # Getting 2 records from Qdrant
    results, _ = vector_store.client.scroll(collection_name='text_embeddings', limit=2)
    print("\n=== VECTOR DB EXPERT SAMPLES ===")
    for r in results:
        print(f"Document ID: {r.id}")
        payload_data = r.payload
        # Truncate text if it's too long for display
        if 'document' in payload_data and len(payload_data['document']) > 300:
            payload_data['document'] = payload_data['document'][:300] + "... [TRUNCATED]"
        print(json.dumps(payload_data, indent=2))
        print("-" * 40)
except Exception as e:
    print(f"Vector DB error: {e}")
