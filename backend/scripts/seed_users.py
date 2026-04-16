"""
seed_users.py — Production-Grade MedRAG User & Patient Seeder
=============================================================
Wipes existing users, patients, and reports, then creates:
  • 20 Doctors across diverse medical specialties
  • 60 Patients with realistic demographics, vitals, conditions, and reports
Usage:
    cd Prototype
    python -m backend.scripts.seed_users
"""

import asyncio
import json
import random
import hashlib
import sys
from datetime import datetime, timedelta, timezone

# Fix Windows terminal encoding for emoji output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from sqlalchemy import text

# ── Project imports ──────────────────────────────────────────────────────────
from backend.database.db import engine, AsyncSessionLocal, Base
from backend.database.models import User, Patient, Report
from backend.core.security import get_password_hash

# ══════════════════════════════════════════════════════════════════════════════
#  REFERENCE DATA
# ══════════════════════════════════════════════════════════════════════════════

SPECIALTIES = [
    "Cardiology", "Neurology", "Dermatology", "Orthopedics",
    "Pulmonology", "Gastroenterology", "Endocrinology", "Oncology",
    "Rheumatology", "Nephrology", "Pediatrics", "Psychiatry",
    "Ophthalmology", "Urology", "General Practice", "Immunology",
    "Radiology", "Pathology", "Emergency Medicine", "Geriatrics",
]

DOCTOR_FIRST_NAMES = [
    "Arjun", "Sarah", "Michael", "Priya", "James", "Emily",
    "Robert", "Aisha", "William", "Chen", "David", "Fatima",
    "Liam", "Sophia", "Rajesh", "Olga", "Benjamin", "Grace",
    "Samuel", "Nadia",
]

DOCTOR_LAST_NAMES = [
    "Sharma", "Williams", "Johnson", "Patel", "Anderson", "Kim",
    "Thompson", "Hassan", "Brown", "Liu", "Garcia", "Ali",
    "Martinez", "Ivanova", "Nguyen", "O'Brien", "Chen", "Taylor",
    "Khatri", "Rossi",
]

PATIENT_FIRST_NAMES = [
    "John", "Jane", "Alex", "Maria", "Robert", "Emily", "David",
    "Sarah", "Michael", "Lisa", "Daniel", "Amanda", "James",
    "Jennifer", "Christopher", "Jessica", "Matthew", "Ashley",
    "Andrew", "Brittany", "Joshua", "Megan", "Ryan", "Lauren",
    "Brandon", "Stephanie", "Kevin", "Nicole", "Brian", "Rachel",
    "Tyler", "Kayla", "Justin", "Hannah", "Nathan", "Samantha",
    "Aaron", "Elizabeth", "Adam", "Christina", "Thomas", "Danielle",
    "Jason", "Victoria", "Ethan", "Amber", "Mark", "Tiffany",
    "Charles", "Melody", "Patrick", "Abigail", "Sean", "Chloe",
    "Derek", "Natalie", "Kyle", "Maya", "Trevor", "Sophia",
]

PATIENT_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
    "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson",
    "Martin", "Lee", "Perez", "Thompson", "White", "Harris",
    "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres",
    "Hill", "Flores", "Green", "Adams", "Nelson", "Baker",
    "Carter", "Mitchell", "Roberts", "Turner", "Phillips", "Campbell",
    "Parker", "Evans", "Edwards", "Collins", "Stewart", "Morris",
    "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey",
]

BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
SEXES = ["Male", "Female"]

CONDITIONS_POOL = [
    "Hypertension (Stage 1)", "Hypertension (Stage 2)", "Type 2 Diabetes",
    "Type 1 Diabetes", "Hyperlipidemia", "Asthma (Mild)", "Asthma (Moderate)",
    "COPD", "Rheumatoid Arthritis", "Osteoarthritis", "Generalized Anxiety Disorder",
    "Major Depressive Disorder", "Migraine with Aura", "Migraine without Aura",
    "Iron Deficiency Anemia", "Chronic Kidney Disease (Stage 2)",
    "Chronic Kidney Disease (Stage 3a)", "Atrial Fibrillation",
    "Congestive Heart Failure (NYHA II)", "Coronary Artery Disease",
    "Hypothyroidism", "Hyperthyroidism", "GERD", "Peptic Ulcer Disease",
    "Inflammatory Bowel Disease", "Celiac Disease", "Psoriasis",
    "Eczema", "Seasonal Allergies", "Sleep Apnea", "Obesity",
    "Osteoporosis", "Gout", "Epilepsy", "Multiple Sclerosis",
]

ALLERGIES_POOL = [
    "Penicillin", "Sulfa Drugs", "Aspirin", "Latex", "Ibuprofen",
    "Codeine", "Morphine", "Shellfish", "Peanuts", "Tree Nuts",
    "Eggs", "Soy", "Contrast Dye", "ACE Inhibitors", "NSAIDs",
    "None Known",
]

MEDICATIONS_POOL = [
    {"name": "Lisinopril", "dose": "10mg", "freq": "Once daily", "purpose": "Blood Pressure"},
    {"name": "Metformin", "dose": "500mg", "freq": "Twice daily", "purpose": "Blood Sugar"},
    {"name": "Atorvastatin", "dose": "20mg", "freq": "Once daily", "purpose": "Cholesterol"},
    {"name": "Amlodipine", "dose": "5mg", "freq": "Once daily", "purpose": "Blood Pressure"},
    {"name": "Omeprazole", "dose": "20mg", "freq": "Once daily", "purpose": "Acid Reflux"},
    {"name": "Sertraline", "dose": "50mg", "freq": "Once daily", "purpose": "Anxiety/Depression"},
    {"name": "Levothyroxine", "dose": "50mcg", "freq": "Once daily", "purpose": "Thyroid"},
    {"name": "Albuterol", "dose": "90mcg", "freq": "As needed", "purpose": "Asthma Rescue"},
    {"name": "Montelukast", "dose": "10mg", "freq": "Once daily", "purpose": "Asthma/Allergies"},
    {"name": "Losartan", "dose": "50mg", "freq": "Once daily", "purpose": "Blood Pressure"},
    {"name": "Gabapentin", "dose": "300mg", "freq": "Twice daily", "purpose": "Nerve Pain"},
    {"name": "Metoprolol", "dose": "25mg", "freq": "Once daily", "purpose": "Heart Rate"},
    {"name": "Furosemide", "dose": "20mg", "freq": "Once daily", "purpose": "Fluid Retention"},
    {"name": "Aspirin", "dose": "81mg", "freq": "Once daily", "purpose": "Cardiac Prevention"},
    {"name": "Vitamin D3", "dose": "2000 IU", "freq": "Once daily", "purpose": "Supplement"},
]

REPORT_TITLES = [
    "Cardiovascular Risk Assessment", "Metabolic Panel Review",
    "Pulmonary Function Analysis", "Rheumatology Screening",
    "Mental Health Follow-up", "Neurological Assessment",
    "Endocrine Function Review", "Renal Function Panel",
    "Hepatic Function Review", "Dermatological Evaluation",
    "Orthopedic Assessment", "Oncology Screening Review",
    "Annual Physical Examination", "Post-Procedure Follow-up",
    "Urgent Care Evaluation",
]


def _generate_vitals(risk_score: int) -> dict:
    """Generate plausible vitals scaled to risk."""
    base_sys = random.randint(110, 125) + int(risk_score * 0.4)
    base_dia = random.randint(68, 78) + int(risk_score * 0.2)
    hr = random.randint(60, 75) + int(risk_score * 0.3)
    return {
        "bp": f"{min(base_sys, 180)}/{min(base_dia, 110)}",
        "heartRate": min(hr, 120),
        "temp": f"{round(random.uniform(97.8, 99.2), 1)}°F",
        "weight": f"{random.randint(110, 240)} lbs",
        "height": random.choice(['5\'4"', '5\'6"', '5\'8"', '5\'10"', '6\'0"', '6\'2"']),
        "bmi": round(random.uniform(18.5, 38.0), 1),
        "spO2": f"{max(random.randint(93, 100) - int(risk_score * 0.05), 88)}%",
    }


def _generate_risk_trend() -> list:
    """Generate 7-point risk trend."""
    base = random.randint(15, 70)
    return [
        {"name": d, "risk": max(5, min(100, base + random.randint(-8, 12)))}
        for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    ]


def _generate_lab_results(risk_score: int) -> list:
    """Generate plausible lab results."""
    labs = []
    tests = [
        ("HbA1c", "5.2%", "7.8%", "< 5.7%"),
        ("Fasting Glucose", "82 mg/dL", "162 mg/dL", "70-100 mg/dL"),
        ("Total Cholesterol", "168 mg/dL", "248 mg/dL", "< 200 mg/dL"),
        ("LDL Cholesterol", "88 mg/dL", "168 mg/dL", "< 100 mg/dL"),
        ("HDL Cholesterol", "62 mg/dL", "38 mg/dL", "> 40 mg/dL"),
        ("Creatinine", "0.9 mg/dL", "1.9 mg/dL", "0.7-1.3 mg/dL"),
        ("TSH", "2.1 mIU/L", "5.8 mIU/L", "0.4-4.0 mIU/L"),
        ("Hemoglobin", "14.2 g/dL", "10.8 g/dL", "12.0-17.5 g/dL"),
    ]
    for test_name, good_val, bad_val, ref_range in tests:
        val = bad_val if risk_score > 55 and random.random() > 0.4 else good_val
        status = "high" if val == bad_val else "normal"
        labs.append({
            "test": test_name, "value": val,
            "range": ref_range, "status": status,
            "date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
        })
    return labs


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN SEEDER
# ══════════════════════════════════════════════════════════════════════════════

async def seed():
    print("=" * 70)
    print("  🚀 MedRAG Production User & Patient Seeder")
    print("=" * 70)

    # ── Init tables ──
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # ── Wipe existing data (order matters due to FKs) ──
        print("\n  🗑️  Wiping existing records...")
        for tbl in ["reports", "mood_logs", "activity_logs", "cycle_logs",
                     "ai_feedback", "notifications", "appointments", "patients", "users"]:
            try:
                await session.execute(text(f"DELETE FROM {tbl}"))
            except Exception:
                pass  # Table might not exist yet
        await session.commit()
        print("  ✅ All tables cleared.\n")

        # ── CREATE 20 DOCTORS ──
        print("  👨‍⚕️  Creating 20 Doctors...")
        doctors = []
        for i in range(20):
            fname = DOCTOR_FIRST_NAMES[i]
            lname = DOCTOR_LAST_NAMES[i]
            specialty = SPECIALTIES[i]
            email = f"dr.{fname.lower()}.{lname.lower()}@medrag.com"
            username = f"Dr. {fname} {lname}"

            doc = User(
                username=username,
                email=email,
                hashed_password=get_password_hash("password123"),
                role="doctor",
                specialty=specialty,
                is_active=True,
            )
            session.add(doc)
            doctors.append(doc)
            print(f"      ✅ {username} — {specialty}")

        await session.commit()
        for d in doctors:
            await session.refresh(d)

        # ── CREATE 60 PATIENTS ──
        print(f"\n  🏥 Creating 60 Patients (assigned to {len(doctors)} doctors)...\n")
        patients_created = []

        for i in range(60):
            fname = PATIENT_FIRST_NAMES[i]
            lname = PATIENT_LAST_NAMES[i]
            sex = random.choice(SEXES)
            age = random.randint(18, 82)
            risk = random.randint(5, 95)

            if risk < 30:
                status = "Stable"
            elif risk < 60:
                status = "Moderate"
            elif risk < 80:
                status = "High Risk"
            else:
                status = "Critical"

            # Create user account for patient
            email = f"{fname.lower()}.{lname.lower()}@email.com"
            user_acct = User(
                username=f"{fname} {lname}",
                email=email,
                hashed_password=get_password_hash("password123"),
                role="patient",
                is_active=True,
            )
            session.add(user_acct)
            await session.flush()

            # Assign to a doctor (round-robin)
            assigned_doctor = doctors[i % len(doctors)]

            conds = random.sample(CONDITIONS_POOL, k=random.randint(1, 4))
            allrgs = random.sample(ALLERGIES_POOL, k=random.randint(0, 3))
            meds = random.sample(MEDICATIONS_POOL, k=random.randint(1, 5))
            vitals = _generate_vitals(risk)
            labs = _generate_lab_results(risk)
            risk_trend = _generate_risk_trend()

            days_ago = random.randint(1, 60)
            last_visit = datetime.now(timezone.utc) - timedelta(days=days_ago)

            patient = Patient(
                user_account_id=user_acct.id,
                doctor_id=assigned_doctor.id,
                first_name=fname,
                last_name=lname,
                date_of_birth=datetime(datetime.now().year - age, random.randint(1, 12), random.randint(1, 28)),
                age=age,
                sex=sex,
                blood_type=random.choice(BLOOD_TYPES),
                phone=f"+1 (555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
                address=f"{random.randint(100, 9999)} {random.choice(['Maple', 'Oak', 'Pine', 'Cedar', 'Elm', 'Lake', 'Park'])} {random.choice(['Ave', 'St', 'Dr', 'Ln', 'Blvd'])}, Chicago, IL",
                emergency_contact=json.dumps({"name": f"Family of {fname}", "relation": "Spouse", "phone": f"+1 (555) {random.randint(100,999)}-{random.randint(1000,9999)}"}),
                insurance=json.dumps({"provider": random.choice(["BlueCross", "Aetna", "United", "Cigna", "Medicare"]), "policyNo": f"POL-{random.randint(100000,999999)}"}),
                vitals=json.dumps(vitals),
                risk=risk,
                status=status,
                last_visit=last_visit,
                conditions=json.dumps(conds),
                allergies=json.dumps(allrgs),
                medications=json.dumps(meds),
                lab_results=json.dumps(labs),
                risk_trend=json.dumps(risk_trend),
                visit_history=json.dumps([
                    {"date": (datetime.now() - timedelta(days=d)).strftime("%Y-%m-%d"),
                     "type": random.choice(["Follow-up", "Lab Review", "Annual Physical", "Urgent Visit"]),
                     "doctor": assigned_doctor.username,
                     "summary": f"Routine clinical follow-up. {'Elevated markers noted.' if risk > 50 else 'Vitals within normal limits.'}"}
                    for d in sorted(random.sample(range(1, 180), k=random.randint(2, 4)), reverse=True)
                ]),
                medical_history_summary=f"{fname} {lname} is a {age}-year-old {sex.lower()} with {', '.join(conds[:2])}. {'High-risk profile requiring close monitoring.' if risk > 60 else 'Generally stable health status.'}",
            )
            session.add(patient)
            await session.flush()
            patients_created.append((patient, risk, status, assigned_doctor.username))

            # ── Generate 1-3 Reports per patient ──
            num_reports = random.randint(1, 3)
            for r in range(num_reports):
                conf = round(random.uniform(0.55, 0.98), 2)
                r_score = round(risk / 100.0 + random.uniform(-0.1, 0.1), 2)
                report = Report(
                    patient_id=patient.id,
                    chief_complaint=f"{random.choice(conds)} evaluation and follow-up",
                    diagnosis_reasoning=f"Clinical assessment based on presented symptoms, lab results, and patient history for {fname} {lname}.",
                    final_report=f"## Diagnostic Report for {fname} {lname}\n\n"
                                 f"**Risk Score:** {risk}/100 ({status})\n\n"
                                 f"**Active Conditions:** {', '.join(conds)}\n\n"
                                 f"### Assessment\n"
                                 f"Patient presents with {'stable' if risk < 50 else 'elevated'} risk markers. "
                                 f"{'Continue current management.' if risk < 50 else 'Recommend specialist referral and medication adjustment.'}\n\n"
                                 f"### Plan\n"
                                 f"- Follow-up in {'3 months' if risk < 30 else '2 weeks' if risk > 70 else '6 weeks'}\n"
                                 f"- {'Maintain current medications' if risk < 50 else 'Adjust medication regimen'}\n"
                                 f"- Lab work to be repeated prior to next visit",
                    confidence_score=conf,
                    risk_score=r_score,
                    hallucination_score=round(random.uniform(0.02, 0.18), 3),
                    emergency_flag=(risk > 85),
                    recommended_specialty=random.choice(SPECIALTIES[:10]),
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90)),
                )
                session.add(report)

            if (i + 1) % 10 == 0:
                print(f"      ✅ Created {i + 1}/60 patients...")

        await session.commit()

        # ── Summary ──
        print("\n" + "=" * 70)
        print("  🏁 SEEDING COMPLETE!")
        print("=" * 70)
        print(f"  👨‍⚕️  Doctors created:  20")
        print(f"  🏥 Patients created: 60")
        print(f"  📋 Reports created:  ~{sum(random.randint(1,3) for _ in range(60))}")
        print()
        print("  📧 Login credentials (all accounts):")
        print("     Email: <firstname>.<lastname>@medrag.com (doctors)")
        print("            <firstname>.<lastname>@email.com  (patients)")
        print("     Password: password123")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(seed())
