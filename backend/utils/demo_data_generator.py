import asyncio
import random
from datetime import datetime, timedelta
from backend.database.db import async_session
from backend.database.models import User, Patient, Report

async def seed_demo_environment():
    """
    Constructs a pristine demonstration environment pre-loaded with realistic medical datasets
    representing advanced capabilities.
    """
    print("Initializing Demo Data Environment...")
    async with async_session() as session:
        # Create Demo Doctor
        demo_doc = User(username="dr_alan_turing", email="alan@medrag.ai", hashed_password="hashed_secure_pbkdf2")
        session.add(demo_doc)
        await session.commit()
        await session.refresh(demo_doc)

        # Create Sample Patients
        patients = [
            Patient(doctor_id=demo_doc.id, first_name="Evelyn", last_name="Carter", date_of_birth=datetime(1982, 4, 15), medical_history_summary="Type 2 Diabetes, Hypertension"),
            Patient(doctor_id=demo_doc.id, first_name="Marcus", last_name="Chen", date_of_birth=datetime(1995, 8, 22), medical_history_summary="Asthma, Seasonal Allergies")
        ]
        session.add_all(patients)
        await session.commit()
        
        for p in patients:
            await session.refresh(p)

        # Create Historical RAG Reports
        reports = [
            Report(
                patient_id=patients[0].id,
                chief_complaint="Sharp chest pain and dyspnea.",
                diagnosis_reasoning="Symptoms align with acute myocardial ischemia.",
                retrieved_evidence="Source_EMR_Cardiology_442",
                final_report="Elevated troponin suspected based on textual description. Immediate ECG required.",
                confidence_score=92.5,
                risk_score=85.0,
                hallucination_score=0.01,
                emergency_flag=True
            ),
            Report(
                patient_id=patients[1].id,
                chief_complaint="Persistent dry cough for 3 weeks.",
                diagnosis_reasoning="Unlikely pneumonia. High probability of allergic asthma exacerbation.",
                retrieved_evidence="Source_Guidelines_Pulmonary",
                final_report="Recommend stepping up inhaled corticosteroid therapy.",
                confidence_score=88.0,
                risk_score=25.0,
                hallucination_score=0.04,
                emergency_flag=False
            )
        ]
        
        session.add_all(reports)
        await session.commit()
        
        print(f"Successfully injected {len(patients)} Patients and {len(reports)} RAG Reports.")

if __name__ == "__main__":
    asyncio.run(seed_demo_environment())
