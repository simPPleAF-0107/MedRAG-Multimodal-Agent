import asyncio
from PIL import Image
import numpy as np
from backend.core.pipeline import core_pipeline

async def test():
    img = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))
    res = await core_pipeline.run_multimodal_rag_pipeline('Chest X-ray analysis', image=img)
    print(res)

if __name__ == "__main__":
    asyncio.run(test())
