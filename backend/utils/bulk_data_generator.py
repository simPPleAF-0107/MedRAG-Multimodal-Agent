import asyncio
import random
from datetime import datetime, timedelta
from backend.database.db import AsyncSessionLocal, init_db
from backend.database.models import User, Patient, Report

# Sample medical terms to construct bulk data
FIRST_NAMES = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley", "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle", "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa", "Edward", "Deborah", "Ronald", "Stephanie"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"]

CONDITIONS = ["Type 2 Diabetes", "Hypertension", "Asthma", "Seasonal Allergies", "Hyperlipidemia", "GERD", "Hypothyroidism", "Osteoarthritis", "Migraines", "Anxiety", "Depression", "None", "None", "None"]
CHIEF_COMPLAINTS = [
    "Sharp chest pain and dyspnea.",
    "Persistent dry cough for 3 weeks.",
    "Dull headache on the right side of the head, sensitivity to light.",
    "Lower back pain radiating down the left leg, worse when sitting.",
    "Abdominal pain in the lower right quadrant, accompanied by nausea.",
    "Shortness of breath after walking up one flight of stairs.",
    "Frequent urination and increased thirst over the past month.",
    "Joint stiffness in hands and knees, worse in the morning.",
    "Acid reflux after meals, burning sensation in the throat.",
    "Fatigue, weight gain, and feeling cold constantly.",
    "Sudden extreme dizziness and vertigo when changing head positions.",
    "Painful urination with dark, cloudy urine.",
    "Spiked a fever of 102F with severe body aches and chills.",
    "Skin rash on the forearms, intensely itchy.",
    "Blurry vision in the right eye, started yesterday."
]

DIAGNOSIS_REASONING_POOL = [
    "Symptoms point towards an ischemic event. ECG needed immediately.",
    "Likely allergic asthma exacerbation or viral URI.",
    "Classic presentation of a migraine without aura.",
    "Suspicious for sciatica due to L4-L5 disc herniation.",
    "High index of suspicion for acute appendicitis.",
    "Possible congestive heart failure exacerbation or COPD.",
    "Suggestive of uncontrolled diabetes mellitus.",
    "Consistent with progression of osteoarthritis.",
    "Classic symptoms of gastroesophageal reflux disease.",
    "Clinical picture strongly suggests hypothyroidism.",
    "Consistent with Benign Paroxysmal Positional Vertigo (BPPV).",
    "Symptoms indicate an acute urinary tract infection.",
    "Presentation is highly suspicious for Influenza A or B.",
    "Contact dermatitis is the most probable diagnosis.",
    "Ocular symptoms require immediate ophthalmology intervention to rule out retinal detachment."
]

FINAL_REPORTS = [
    "Elevated troponin suspected based on textual description. Immediate ECG required.",
    "Recommend stepping up inhaled corticosteroid therapy and oral antihistamines.",
    "Prescribed triptans for acute management. Advised resting in a dark, quiet room.",
    "Scheduled MRI lumbar spine. Prescribed short course of oral steroids and NSAIDs.",
    "Surgical consult requested immediately. NPO implemented.",
    "Echocardiogram ordered. Adjusted diuretic dosage.",
    "Ordered HbA1c and fasting glucose. Recommended dietary modifications.",
    "Recommended physical therapy and prescribed NSAIDs as needed.",
    "Started on a daily proton pump inhibitor trial for 4 weeks.",
    "Checked TSH panel. Starting levothyroxine therapy pending lab results.",
    "Performed Epley maneuver in clinic. Patient reported significant improvement.",
    "Urine culture sent. Started on empiric antibiotic therapy.",
    "Rapid flu swab positive. Starting antiviral therapy. Advised rest and hydration.",
    "Prescribed topical hydrocortisone and over-the-counter antihistamines.",
    "Patient referred to emergency ophthalmology for a dilated fundus exam."
]

async def generate_bulk_data(num_patients=50, max_reports_per_patient=3):
    """
    Generates a large synthetic dataset of patients and their RAG reports.
    """
    await init_db()
    print(f"Generating bulk demo environment with {num_patients} patients...")
    async with AsyncSessionLocal() as session:
        # Create Demo Doctor if not exists
        from sqlalchemy.future import select
        result = await session.execute(select(User).filter_by(username="dr_alan_turing"))
        demo_doc = result.scalar_one_or_none()
        
        if not demo_doc:
            demo_doc = User(username="dr_alan_turing", email="alan@medrag.ai", hashed_password="hashed_secure_pbkdf2")
            session.add(demo_doc)
            await session.commit()
            await session.refresh(demo_doc)

        patients = []
        for i in range(num_patients):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            
            # Generate random birthday between 18 and 85 years ago
            days_old = random.randint(18 * 365, 85 * 365)
            dob = datetime.now() - timedelta(days=days_old)
            
            history = ", ".join(random.sample(CONDITIONS, random.randint(1, 3)))
            
            p = Patient(
                doctor_id=demo_doc.id,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                medical_history_summary=history
            )
            patients.append(p)
            
        session.add_all(patients)
        await session.commit()

        for p in patients:
            await session.refresh(p)

        reports = []
        for p in patients:
            num_reports = random.randint(1, max_reports_per_patient)
            for _ in range(num_reports):
                # Pick a random scenario
                idx = random.randint(0, len(CHIEF_COMPLAINTS) - 1)
                
                # Assign confidence and risk scores
                confidence = round(random.uniform(70.0, 99.0), 1)
                
                # Determine risk and emergency flag artificially based on keywords in complaint
                complaint = CHIEF_COMPLAINTS[idx]
                is_emergency = any(kw in complaint.lower() for kw in ["chest pain", "dyspnea", "shortness of breath", "abdominal pain", "blurry vision"])
                
                if is_emergency:
                    risk_score = round(random.uniform(75.0, 95.0), 1)
                else:
                    risk_score = round(random.uniform(10.0, 45.0), 1)
                    
                hallucination_score = round(random.uniform(0.01, 0.08), 2)
                
                r = Report(
                    patient_id=p.id,
                    chief_complaint=complaint,
                    diagnosis_reasoning=DIAGNOSIS_REASONING_POOL[idx],
                    retrieved_evidence=f"Source_MedicalDocs_{random.randint(100, 999)}",
                    final_report=FINAL_REPORTS[idx],
                    confidence_score=confidence,
                    risk_score=risk_score,
                    hallucination_score=hallucination_score,
                    emergency_flag=is_emergency
                )
                reports.append(r)
                
        session.add_all(reports)
        await session.commit()
        
        print(f"Successfully injected {len(patients)} Patients and {len(reports)} RAG Reports.")

if __name__ == "__main__":
    asyncio.run(generate_bulk_data(num_patients=50, max_reports_per_patient=3))
