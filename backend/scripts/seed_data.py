"""
MedRAG Demo Data Seeder
Seeds the database with demo doctors, patients, reports, and health logs.
Run: python -m backend.scripts.seed_data  (from the Prototype directory)
"""
import asyncio
import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database.db import engine, AsyncSessionLocal, Base
from backend.database.models import User, Patient, Report, MoodLog, ActivityLog, CycleLog
from backend.core.security import get_password_hash
from datetime import datetime, timezone, timedelta


async def seed():
    print("MedRAG Database Seeder Starting...")

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created/verified.")

    async with AsyncSessionLocal() as db:
        # Check if data already exists
        from sqlalchemy.future import select
        existing = await db.execute(select(User))
        if existing.scalars().first():
            print("⚠️  Database already has data. Skipping seed. Delete medrag.db to re-seed.")
            return

        password_hash = get_password_hash("password123")

        # ── DOCTORS (30 doctors across all major specialties) ──
        DOCTORS = [
            # Original 5
            ("dr.smith@medrag.com",  "dr.smith@medrag.com",  "Cardiology"),
            ("dr.jones@medrag.com",  "dr.jones@medrag.com",  "Neurology"),
            ("1234567890",           "dr.patel@medrag.com",  "Orthopaedics"),
            ("dr.lee@medrag.com",    "dr.lee@medrag.com",    "Gynaecology"),
            ("dr.evans@medrag.com",  "dr.evans@medrag.com",  "General"),
            # Expanded specialties
            ("dr.chen@medrag.com",   "dr.chen@medrag.com",   "Oncology"),
            ("dr.kumar@medrag.com",  "dr.kumar@medrag.com",  "Hematology"),
            ("dr.garcia@medrag.com", "dr.garcia@medrag.com", "Nephrology"),
            ("dr.wilson@medrag.com", "dr.wilson@medrag.com", "Pulmonology"),
            ("dr.ahmed@medrag.com",  "dr.ahmed@medrag.com",  "Endocrinology"),
            ("dr.park@medrag.com",   "dr.park@medrag.com",   "Rheumatology"),
            ("dr.taylor@medrag.com", "dr.taylor@medrag.com", "Gastroenterology"),
            ("dr.brown@medrag.com",  "dr.brown@medrag.com",  "Infectious Disease"),
            ("dr.kim@medrag.com",    "dr.kim@medrag.com",    "Dermatology"),
            ("dr.singh@medrag.com",  "dr.singh@medrag.com",  "Ophthalmology"),
            ("dr.martinez@medrag.com","dr.martinez@medrag.com","ENT / Otolaryngology"),
            ("dr.nguyen@medrag.com", "dr.nguyen@medrag.com", "Urology"),
            ("dr.ali@medrag.com",    "dr.ali@medrag.com",    "Obstetrics"),
            ("dr.thomas@medrag.com", "dr.thomas@medrag.com", "Pediatrics"),
            ("dr.white@medrag.com",  "dr.white@medrag.com",  "Psychiatry"),
            ("dr.clark@medrag.com",  "dr.clark@medrag.com",  "Emergency Medicine"),
            ("dr.moore@medrag.com",  "dr.moore@medrag.com",  "Dental / Oral Surgery"),
            ("dr.hall@medrag.com",   "dr.hall@medrag.com",   "Radiology"),
            ("dr.scott@medrag.com",  "dr.scott@medrag.com",  "Anesthesiology"),
            ("dr.adams@medrag.com",  "dr.adams@medrag.com",  "Pathology"),
            ("dr.baker@medrag.com",  "dr.baker@medrag.com",  "Neurosurgery"),
            ("dr.wright@medrag.com", "dr.wright@medrag.com", "Plastic Surgery"),
            ("dr.king@medrag.com",   "dr.king@medrag.com",   "Vascular Surgery"),
            ("dr.hill@medrag.com",   "dr.hill@medrag.com",   "Geriatrics"),
            ("dr.green@medrag.com",  "dr.green@medrag.com",  "Palliative Care"),
        ]

        doctor_objects = []
        for username, email, specialty in DOCTORS:
            doc = User(
                username=username, email=email,
                hashed_password=password_hash,
                role="doctor", specialty=specialty
            )
            doctor_objects.append(doc)

        db.add_all(doctor_objects)
        await db.flush()
        # Map named references for patient assignment below
        doc1, doc2, doc3, doc4, doc5 = doctor_objects[:5]
        print(f"✅ Seeded {len(doctor_objects)} doctors across {len(DOCTORS)} specialties")

        # ── PATIENT USER ACCOUNTS ──
        pat_user1 = User(username="john.doe@email.com", email="john.doe@email.com",
                          hashed_password=password_hash, role="patient")
        pat_user2 = User(username="jane.smith@email.com", email="jane.smith@email.com",
                          hashed_password=password_hash, role="patient")
        pat_user3 = User(username="0987654321", email="bob.user@email.com",
                          hashed_password=password_hash, role="patient")
        pat_user4 = User(username="alice.w@email.com", email="alice.w@email.com",
                          hashed_password=password_hash, role="patient")
        pat_user5 = User(username="mike.t@email.com", email="mike.t@email.com",
                          hashed_password=password_hash, role="patient")
        pat_user6 = User(username="sarah.c@email.com", email="sarah.c@email.com",
                          hashed_password=password_hash, role="patient")
        
        db.add_all([pat_user1, pat_user2, pat_user3, pat_user4, pat_user5, pat_user6])
        await db.flush()
        print(f"✅ Seeded 6 patient user accounts")

        now = datetime.now(timezone.utc)

        # ── PATIENT RECORDS ──
        p1 = Patient(
            user_account_id=pat_user1.id, doctor_id=doc1.id,
            first_name="John", last_name="Doe",
            age=58, sex="Male", blood_type="O+",
            phone="+1 (555) 123-4567",
            address="142 Maple Ave, Springfield, IL 62704",
            emergency_contact='{"name":"Mary Doe","relation":"Spouse","phone":"+1 (555) 123-4568"}',
            insurance='{"provider":"BlueCross BlueShield","policyNo":"BC-8827341","group":"GRP-44021"}',
            vitals='{"bp":"148/92","heartRate":82,"temp":"98.6°F","weight":"198 lbs","height":"5\'10\\"","bmi":28.4,"spO2":"96%"}',
            risk=68, status="High Risk",
            conditions='["Hypertension (Stage 2)","Type 2 Diabetes","Hyperlipidemia","Suspected Rheumatoid Arthritis"]',
            allergies='["Penicillin","Sulfa Drugs"]',
            medications='[{"name":"Lisinopril","dose":"20mg","freq":"Once daily","purpose":"Blood Pressure"},{"name":"Metformin","dose":"500mg","freq":"Twice daily","purpose":"Blood Sugar"}]',
            lab_results='[{"test":"HbA1c","value":"7.2%","range":"<5.7%","status":"high","date":"2026-03-18"},{"test":"Fasting Glucose","value":"142 mg/dL","range":"70-100 mg/dL","status":"high","date":"2026-03-18"}]',
            risk_trend='[{"name":"Jan","risk":42},{"name":"Feb","risk":48},{"name":"Mar","risk":55},{"name":"Apr","risk":52},{"name":"May","risk":58},{"name":"Jun","risk":62},{"name":"Jul","risk":68}]',
            medical_history_summary="John Doe is a 58-year-old male with a 12-year history of hypertension and a 6-year history of Type 2 Diabetes.",
            last_visit=now - timedelta(days=11),
            date_of_birth=datetime(1968, 5, 14, tzinfo=timezone.utc)
        )

        p2 = Patient(
            user_account_id=pat_user2.id, doctor_id=doc1.id,
            first_name="Jane", last_name="Smith",
            age=34, sex="Female", blood_type="A+",
            phone="+1 (555) 234-5678",
            address="88 Oak Street, Apt 4B, Chicago, IL 60614",
            emergency_contact='{"name":"Robert Smith","relation":"Brother","phone":"+1 (555) 234-5679"}',
            insurance='{"provider":"Aetna","policyNo":"AE-5519882","group":"GRP-77103"}',
            vitals='{"bp":"118/74","heartRate":72,"temp":"98.4°F","weight":"138 lbs","height":"5\'6\\"","bmi":22.3,"spO2":"99%"}',
            risk=42, status="Stable",
            conditions='["Generalized Anxiety Disorder","Iron Deficiency Anemia (resolved)","Seasonal Allergies"]',
            allergies='["Latex","Ibuprofen"]',
            medications='[{"name":"Sertraline","dose":"50mg","freq":"Once daily","purpose":"Anxiety"}]',
            medical_history_summary="Jane Smith is a 34-year-old female diagnosed with GAD in 2024, well-managed on Sertraline.",
            last_visit=now - timedelta(days=16),
            date_of_birth=datetime(1992, 8, 22, tzinfo=timezone.utc)
        )

        p3 = Patient(
            user_account_id=pat_user3.id, doctor_id=doc1.id,
            first_name="Bob", last_name="User",
            age=71, sex="Male", blood_type="B-",
            phone="+1 (555) 345-6789",
            address="305 Pine Lane, Evanston, IL 60201",
            risk=85, status="Critical",
            conditions='["Congestive Heart Failure (NYHA III)","Atrial Fibrillation","CKD Stage 3a","COPD"]',
            allergies='["ACE Inhibitors","Codeine"]',
            vitals='{"bp":"156/96","heartRate":98,"temp":"98.8°F","weight":"215 lbs","height":"5\'8\\"","bmi":32.7,"spO2":"91%"}',
            medical_history_summary="Bob User is a 71-year-old male with complex multi-morbidity: CHF NYHA III, AFib, CKD 3a, COPD.",
            last_visit=now - timedelta(days=10),
            date_of_birth=datetime(1955, 11, 3, tzinfo=timezone.utc)
        )

        p4 = Patient(
            user_account_id=pat_user4.id, doctor_id=doc2.id,
            first_name="Alice", last_name="Wong",
            age=28, sex="Female", blood_type="AB+",
            phone="+1 (555) 456-7890",
            address="1200 Lakeshore Dr, Unit 12C, Chicago, IL 60611",
            risk=25, status="Stable",
            conditions='["Migraine with Aura","Mild Asthma (well-controlled)"]',
            allergies='["Shellfish"]',
            vitals='{"bp":"112/68","heartRate":66,"temp":"98.2°F","weight":"125 lbs","height":"5\'4\\"","bmi":21.5,"spO2":"99%"}',
            medical_history_summary="Alice Wong is a 28-year-old female with migraine with aura and mild persistent asthma.",
            last_visit=now - timedelta(days=21),
            date_of_birth=datetime(1998, 2, 17, tzinfo=timezone.utc)
        )

        p5 = Patient(
            user_account_id=pat_user5.id, doctor_id=doc4.id,
            first_name="Mike", last_name="Taylor",
            age=45, sex="Male", blood_type="O-",
            phone="+1 (555) 567-8901",
            address="400 West St, Chicago, IL",
            risk=30, status="Stable",
            conditions='["Hyperlipidemia"]',
            medical_history_summary="Mike Taylor, male, 45, hyperlipidemia.",
            last_visit=now - timedelta(days=60),
            date_of_birth=datetime(1981, 6, 10, tzinfo=timezone.utc)
        )

        p6 = Patient(
            user_account_id=pat_user6.id, doctor_id=doc4.id,
            first_name="Sarah", last_name="Connor",
            age=31, sex="Female", blood_type="A-",
            phone="+1 (555) 678-9012",
            address="500 North Ave, Chicago, IL",
            risk=10, status="Stable",
            conditions='["PCOS"]',
            medical_history_summary="Sarah Connor, female, 31, PCOS.",
            last_visit=now - timedelta(days=5),
            date_of_birth=datetime(1995, 3, 21, tzinfo=timezone.utc)
        )

        db.add_all([p1, p2, p3, p4, p5, p6])
        await db.flush()
        print(f"✅ Seeded 6 patients")

        # ── REPORTS ──
        reports = [
            Report(patient_id=p1.id, chief_complaint="Elevated CRP and joint pain",
                   diagnosis_reasoning="Bilateral joint stiffness >45min in mornings. Elevated CRP 8.4 and ESR 38.",
                   final_report="Elevated CRP (8.4) and ESR (38) with localized joint pain. Recommend anti-CCP antibody testing and rheumatology consultation.",
                   confidence_score=85.0, risk_score=68.0, hallucination_score=0.1, emergency_flag=False),
            Report(patient_id=p1.id, chief_complaint="HbA1c rising, metabolic review",
                   diagnosis_reasoning="HbA1c 7.2% up from 6.8%. Fasting glucose 142.",
                   final_report="Diabetes control deteriorating. Metformin increased. Consider GLP-1 agonist if no improvement in 3 months.",
                   confidence_score=92.0, risk_score=55.0, hallucination_score=0.05, emergency_flag=False),
            Report(patient_id=p2.id, chief_complaint="Mental health follow-up for GAD",
                   diagnosis_reasoning="GAD-7 score improved from 14 to 8 on Sertraline 50mg.",
                   final_report="Significant improvement in daily functioning. No side effects. Continue current regimen.",
                   confidence_score=90.0, risk_score=20.0, hallucination_score=0.02, emergency_flag=False),
            Report(patient_id=p3.id, chief_complaint="Acute dyspnea and lower extremity edema",
                   diagnosis_reasoning="BNP 820, SpO2 91%, bilateral LE edema 3+.",
                   final_report="Acute-on-chronic HF exacerbation. IV diuresis initiated. Monitor I&O, daily weights.",
                   confidence_score=91.0, risk_score=85.0, hallucination_score=0.08, emergency_flag=True),
            Report(patient_id=p4.id, chief_complaint="Migraine management review",
                   diagnosis_reasoning="Migraine frequency reduced from 8 to 2/month on Topiramate.",
                   final_report="Significant improvement with Topiramate 25mg daily. Continue current regimen.",
                   confidence_score=94.0, risk_score=15.0, hallucination_score=0.01, emergency_flag=False),
        ]
        db.add_all(reports)
        print(f"✅ Seeded {len(reports)} reports")

        # ── MOOD LOGS ──
        mood_logs = [
            MoodLog(patient_id=p1.id, mood_score=5, notes="Feeling moderate joint pain today"),
            MoodLog(patient_id=p1.id, mood_score=4, notes="Stiffness worse in the morning"),
            MoodLog(patient_id=p2.id, mood_score=7, notes="Good day, anxiety manageable"),
            MoodLog(patient_id=p2.id, mood_score=8, notes="Feeling positive and calm"),
            MoodLog(patient_id=p3.id, mood_score=3, notes="Shortness of breath limiting activity"),
            MoodLog(patient_id=p4.id, mood_score=9, notes="No migraine episodes this week"),
        ]
        db.add_all(mood_logs)
        print(f"✅ Seeded {len(mood_logs)} mood logs")

        # ── ACTIVITY LOGS ──
        activity_logs = [
            ActivityLog(patient_id=p1.id, activity_type="Walking", duration_minutes=20, intensity="Low"),
            ActivityLog(patient_id=p2.id, activity_type="Yoga", duration_minutes=45, intensity="Medium"),
            ActivityLog(patient_id=p2.id, activity_type="Jogging", duration_minutes=30, intensity="Medium"),
            ActivityLog(patient_id=p4.id, activity_type="Cycling", duration_minutes=60, intensity="High"),
            ActivityLog(patient_id=p4.id, activity_type="Swimming", duration_minutes=40, intensity="Medium"),
        ]
        db.add_all(activity_logs)
        print(f"✅ Seeded {len(activity_logs)} activity logs")

        await db.commit()
        print("\n🎉 Database seeding complete!")
        print(f"\n📋 Demo Credentials (all passwords: password123):")
        print(f"   Doctors ({len(DOCTORS)} total):")
        for username, email, specialty in DOCTORS:
            print(f"     {username:<30s} [{specialty}]")
        print("   Patients:")
        print("     john.doe@email.com")
        print("     jane.smith@email.com")
        print("     0987654321")
        print("     alice.w@email.com")
        print("     mike.t@email.com")
        print("     sarah.c@email.com")


if __name__ == "__main__":
    asyncio.run(seed())
