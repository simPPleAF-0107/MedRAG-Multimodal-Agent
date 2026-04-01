import asyncio
from backend.core.pipeline import core_pipeline

async def main():
    try:
        res = await core_pipeline.run_multimodal_rag_pipeline('chest pain', None)
        print(res)
    except Exception as e:
        print(f'Error: {e}')

asyncio.run(main())
