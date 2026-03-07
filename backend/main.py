from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config import settings
from backend.database.db import init_db
from backend.api import rag_routes, patient_routes, upload_routes, chat_routes, system_routes
from backend.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing Extended MedRAG Backend Services...")
    await init_db()
    logger.info("Database initialized.")
    yield
    # Shutdown actions
    logger.info("Shutting down MedRAG Backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Research-Grade Multimodal RAG Healthcare AI System",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(rag_routes.router, prefix=settings.API_V1_STR)
app.include_router(patient_routes.router, prefix=settings.API_V1_STR)
app.include_router(upload_routes.router, prefix=settings.API_V1_STR)
app.include_router(chat_routes.router, prefix=settings.API_V1_STR)
app.include_router(system_routes.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "Welcome to MedRAG API Interface.",
        "docs": "/docs",
        "health": "ok"
    }
