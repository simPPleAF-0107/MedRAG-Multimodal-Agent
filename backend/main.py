from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config import settings
from backend.database.db import init_db
from backend.api import (
    rag_routes, patient_routes, upload_routes, chat_routes, 
    system_routes, voice_routes, reminder_routes, auth_routes, 
    vitals_routes, appointment_routes, notification_routes, tracker_routes,
    knowledge_routes
)
from backend.reminders.scheduler import reminder_scheduler
from backend.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing Extended MedRAG Backend Services...")
    await init_db()
    reminder_scheduler.start()
    logger.info("Database initialized.")
    yield
    # Shutdown actions
    logger.info("Shutting down MedRAG Backend...")
    reminder_scheduler.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Research-Grade Multimodal RAG Healthcare AI System",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration
# Use explicit localhost origins in dev so Authorization headers are not stripped.
# allow_credentials=True requires named origins (not wildcard).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",   # Vite fallback port
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(rag_routes.router, prefix=settings.API_V1_STR)
app.include_router(auth_routes.router, prefix=settings.API_V1_STR)
app.include_router(patient_routes.router, prefix=settings.API_V1_STR)
app.include_router(upload_routes.router, prefix=settings.API_V1_STR)
app.include_router(chat_routes.router, prefix=settings.API_V1_STR)
app.include_router(system_routes.router, prefix=settings.API_V1_STR)
app.include_router(voice_routes.router, prefix=settings.API_V1_STR)
app.include_router(reminder_routes.router, prefix=settings.API_V1_STR)
app.include_router(vitals_routes.router, prefix=settings.API_V1_STR)
app.include_router(appointment_routes.router, prefix=settings.API_V1_STR)
app.include_router(notification_routes.router, prefix=settings.API_V1_STR)
app.include_router(tracker_routes.router, prefix=settings.API_V1_STR)
app.include_router(knowledge_routes.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "Welcome to MedRAG API Interface.",
        "docs": "/docs",
        "health": "ok"
    }

@app.get("/api/v1/health", tags=["devops"])
def health_check():
    """
    Lightweight health-check endpoint for the frontend sidebar ping.
    Returns 200 immediately — no DB query needed.
    """
    return {"status": "ok", "service": "MedRAG API"}
