import time
import asyncio
import json
import os
from backend.core.agent_workflow import core_pipeline

TEST_CASES = [
    "Patient presents with headache, stiff neck, and high fever.",
    "Patient reports chronic lower back pain radiating down the left leg.",
    "Sharp abdominal pain migrating to the lower right quadrant."
]

async def run_benchmark():
    results = []
    
    print(f"Beginning MedRAG Clinical Benchmark across {len(TEST_CASES)} queries...\n")
    
    for idx, case in enumerate(TEST_CASES):
        print(f"Executing Case {idx+1}: {case[:40]}...")
        start_time = time.time()
        
        # We wrap in manual start/stop to derive total execution time. 
        # (Internal logger will handle stage-by-stage retrieval/LLM times)
        try:
            res = await core_pipeline.run_multimodal_rag_pipeline(text_query=case)
            end_time = time.time()
            total_time = round(end_time - start_time, 2)
            
            results.append({
                "query": case,
                "execution_seconds": total_time,
                "success": True,
                "confidence": res.get("confidence_score", 0),
                "hallucination": res.get("hallucination_score", 0),
                "emergency_flag": res.get("emergency_flag", False)
            })
        except Exception as e:
            end_time = time.time()
            results.append({
                "query": case,
                "execution_seconds": round(end_time - start_time, 2),
                "success": False,
                "error": str(e)
            })
            
    # Compile Results
    avg_time = sum(r["execution_seconds"] for r in results) / len(results)
    avg_conf = sum(r.get("confidence", 0) for r in results if r["success"]) / len(results)
    
    summary = {
        "benchmark_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_cases": len(TEST_CASES),
        "mean_latency_seconds": round(avg_time, 2),
        "mean_confidence": round(avg_conf, 2),
        "case_details": results
    }
    
    os.makedirs(os.path.dirname("backend/evaluation/results.json"), exist_ok=True)
    with open("backend/evaluation/results.json", "w") as f:
        json.dump(summary, f, indent=4)
        
    print("\nBenchmark Complete. Results saved to backend/evaluation/results.json")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
