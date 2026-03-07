# MedRAG Multimodal Healthcare Agent

A Research-Grade Medical Artificial Intelligence Platform powered by Multimodal Retrieval-Augmented Generation (RAG).

## Overview
MedRAG is an advanced orchestration of specialized reasoning agents evaluating patient histories, visual diagnostic imaging (X-rays, scans), and textual symptom logging. It produces fully explainable clinical outputs fortified by extensive guardrails against hallucinations and diagnostic bias.

### Key Capabilities
- **Multimodal Intelligence:** Processes both text contexts and images simultaneously (CLIP/Transformer embeddings).
- **Explainability:** Built-in verification routing, hallucination auditing, and bounding heatmaps.
- **Safety Firewalls:** Automated Emergency/Triage detection algorithms triggering alerts on severe keywords.
- **Personalized Telemetry:** Longitudinal graph memory compiling patient Mood, Cycle, and Activity logs for holistic assessments. 

## System Architecture

The project contains three major codebases seamlessly interacting:

1. **FastAPI Backend (`/backend`)**
   - Core Intelligence Orchestrator (`pipeline.py`) routing inputs through 10 distinct AI sub-modules.
   - Vector Store (ChromaDB) for high-performance context retrieval.
   - DevOps Testing and Latency performance profiling (`/tests`, `/evaluation`).

2. **React Web Application (`/frontend-web`)**
   - Fully interactive clinical dashboard tailored for desktop environments.
   - Interactive Rechart data visualization for tracking metrics.

3. **Flutter Mobile Application (`/mobile_app`)**
   - Clean materialized architecture intended for Android/iOS point-of-care mobile execution.
   - Binds to universal API state providers.

## Getting Started

### 1. Backend Initialization
Ensure Python 3.10+ is active. 

```bash
pip install -r requirements.txt
# Populate .env with necessary keys (OPENAI_API_KEY if utilizing OpenAI hooks)
uvicorn backend.main:app --reload
```

*The API will route locally to `http://localhost:8000`.*
*You can insert artificial demo patient data via `python -m backend.utils.demo_data_generator`.*

### 2. Frontend Web Interface
Navigate into the React repository:
```bash
cd frontend-web
npm install
npm run dev
```

### 3. Mobile Execution
Ensure a Flutter-compatible Android emulator is running.
```bash
cd mobile_app
flutter pub get
flutter run
```

## Testing & Evaluation
System benchmarks and logic gating can be profiled at scale:
```bash
# Run logic unit tests
pytest backend/tests/

# Profile system throughput latency and aggregate confidence metrics
python -m backend.evaluation.benchmark
```

*All latency traces are saved out natively to `backend/logs/performance.log`.*
