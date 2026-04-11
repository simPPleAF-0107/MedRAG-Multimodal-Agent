import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.rag.text.embedder import text_embedder
from backend.rag.vector_store import vector_store

async def test():
    try:
        print("Embedding...")
        e = await text_embedder.embed_text("hello world")
        print(f"Embedding type: {type(e)}, len: {len(e)}, first: {type(e[0])}")
        
        print("Storing...")
        await vector_store.store_text_embedding("test_123", e, "hello world", {"test": True})
        print("Success!")
    except Exception as ex:
        with open("clean_error.txt", "w", encoding="utf-8") as f:
            import traceback
            f.write(traceback.format_exc())
            f.write("\n\n" + str(ex))
        print("Failed. Check clean_error.txt")

asyncio.run(test())
