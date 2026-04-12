"""
MedRAG Full Pipeline Benchmark
==============================
Measures end-to-end performance of the entire MedRAG Multimodal Agent,
including Hybrid Retrieval, LLM Reranking, Reasoning, Hallucination Checks,
and final Diagnostic Report generation.
"""
import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.pipeline import CorePipeline
import logging

# Suppress heavy external logs
logging.getLogger("httpx").setLevel(logging.WARNING)

async def run_full_benchmark():
    pipeline = CorePipeline()
    
    test_cases = [
        {
            "user_id": "test_user_01",
            "text_query": "Patient is a 55-year-old male presenting with severe chest pain radiating to the left arm, diaphoresis, and shortness of breath. No previous history of asthma. What is the most likely diagnosis and immediate next steps in the ER?",
            "image_path": None,
            "session_id": "bench_01"
        },
        {
            "user_id": "test_user_01",
            "text_query": "50-year old female with type 2 diabetes presents with a new skin lesion on her foot. It's red, swollen, and warm to the touch. What should be prescribed?",
            "image_path": None,
            "session_id": "bench_02"
        }
    ]
    
    print("=" * 70)
    print(" >>> MedRAG FULL PIPELINE END-TO-END BENCHMARK <<<")
    print("=" * 70)
    print("Benchmarking 2 full clinical workflows (Retrieval -> Reranking -> Reasoning -> Synthesis)")
    
    total_latency = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Simulating Clinical Query...")
        print(f"  Input: '{case['text_query'][:80]}...'")
        
        start_time = time.time()
        # Run entire LangGraph workflow
        result = await pipeline.run_multimodal_rag_pipeline(
            text_query=case["text_query"],
            image=case["image_path"],
            patient_graph=None
        )
        latency = time.time() - start_time
        total_latency += latency
        
        report = result.get('final_payload', {})
        hallucination_flag = not result.get('verification_passed', True)
        
        print(f"  --> Full Turnaround Time: {latency:.2f} seconds")
        print(f"  --> Final Diagnosis Length: {len(report.get('diagnosis', ''))} characters")
        print(f"  --> Treatment Plan Length: {len(report.get('treatment_plan', ''))} characters")
        print(f"  --> Hallucination Detected: {hallucination_flag}")
        
    print("\n" + "=" * 70)
    print(f" [Benchmark Complete]")
    print(f" Average E2E Pipeline Latency: {total_latency / len(test_cases):.2f} seconds per query")
    print("=" * 70)

if __name__ == "__main__":
    from backend.config import settings
    asyncio.run(run_full_benchmark())
