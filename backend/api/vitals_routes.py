from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from backend.utils.logger import logger

router = APIRouter(prefix="/vitals", tags=["iot-telemetry"])

class VitalsPayload(BaseModel):
    heart_rate: int
    spo2: int
    temperature_c: float
    timestamp: str

@router.post("/{patient_id}/stream")
async def ingest_vitals_stream(patient_id: int, payload: VitalsPayload):
    """
    Ingest high-frequency IoT telemetry data from wearables.
    Performs immediate anomaly detection.
    """
    alerts = []
    
    if payload.heart_rate > 100 or payload.heart_rate < 50:
        alerts.append(f"Abnormal Heart Rate detected: {payload.heart_rate} bpm")
        
    if payload.spo2 < 92:
        alerts.append(f"Hypoxia Risk: SpO2 dropped to {payload.spo2}%")
        
    if payload.temperature_c > 38.0:
        alerts.append(f"Fever detected: {payload.temperature_c}°C")
        
    if alerts:
        logger.warning(f"[URGENT ALERT - Patient {patient_id}] " + " | ".join(alerts))
        # In a real system, send a websocket broadcast or PUSH notification here
        
    return {
        "status": "received",
        "anomalies_detected": len(alerts) > 0,
        "alerts": alerts
    }
