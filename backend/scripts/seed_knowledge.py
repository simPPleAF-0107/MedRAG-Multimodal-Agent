"""
MedRAG Medical Knowledge Seeder — Expanded Edition
====================================================
Downloads open-source medical datasets from Hugging Face and ingests them
into the Qdrant vector store so the RAG engine has comprehensive medical knowledge
spanning ALL major clinical specialties.

Datasets used:
  1. PubMedQA       —  1,000 labelled biomedical Q&A entries from PubMed abstracts
  2. MedQA-USMLE    — ~12,000 USMLE-style clinical reasoning questions
  3. MedMCQA        — 20,000 sampled from 194k medical MCQs across 2,400+ topics
  4. WikiDoc Corpus — Curated clinical encyclopedia entries covering every specialty

Run:  python -m backend.scripts.seed_knowledge  (from the Prototype directory)

Requirements:
  pip install datasets
"""
import asyncio
import sys
import os
import time
import hashlib
import uuid as _uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.vector_store import vector_store
from backend.rag.text.embedder import text_embedder
from backend.rag.graph_store import graph_store
from backend.utils.logger import logger


# ── Helper: deterministic UUID from a string ──
def _stable_uuid(text: str) -> str:
    return str(_uuid.UUID(hashlib.md5(text.encode()).hexdigest()))


async def _embed_and_store(doc_id: str, text: str, metadata: dict):
    embedding = await text_embedder.embed_text(text)
    await vector_store.store_text_embedding(
        doc_id=doc_id,
        embedding=embedding,
        text=text,
        metadata=metadata,
    )


# ═══════════════════════════════════════════════════════════
# 1. PubMedQA (labelled split — 1,000 expert QA pairs)
# ═══════════════════════════════════════════════════════════
async def seed_pubmedqa():
    from datasets import load_dataset

    print("\n📚 [1/4] Loading PubMedQA (labelled)…")
    ds = load_dataset("qiaojin/PubMedQA", "pqa_labeled", split="train")

    count = 0
    for row in ds:
        question = row.get("question", "")
        contexts = row.get("context", {})
        long_answer = row.get("long_answer", "")

        context_strs = contexts.get("contexts", []) if isinstance(contexts, dict) else []
        context_text = " ".join(context_strs) if context_strs else ""

        chunk = f"Question: {question}\nContext: {context_text}\nAnswer: {long_answer}"
        if len(chunk.strip()) < 30:
            continue

        doc_id = _stable_uuid(f"pubmedqa_{count}")
        await _embed_and_store(doc_id, chunk, {
            "source": "PubMedQA",
            "type": "biomedical_qa",
            "question": question[:200],
        })

        if question and long_answer:
            short_answer = " ".join(long_answer.split()[:8])
            graph_store.add_relationship(question[:80], "ANSWERED_BY", short_answer)

        count += 1
        if count % 100 == 0:
            print(f"   ✅ PubMedQA: {count} entries ingested")

    print(f"   ✅ PubMedQA complete — {count} entries")
    return count


# ═══════════════════════════════════════════════════════════
# 2. MedQA-USMLE (US clinical board questions)
# ═══════════════════════════════════════════════════════════
async def seed_medqa():
    from datasets import load_dataset

    print("\n📚 [2/4] Loading MedQA-USMLE…")
    ds = load_dataset("GBaker/MedQA-USMLE-4-options", split="train")

    count = 0
    for row in ds:
        question = row.get("question", "")
        options = row.get("options", {})
        answer = row.get("answer", "")

        if isinstance(options, dict):
            opts_str = " | ".join([f"{k}: {v}" for k, v in options.items()])
        elif isinstance(options, list):
            opts_str = " | ".join([str(o) for o in options])
        else:
            opts_str = str(options)

        chunk = f"Clinical Question: {question}\nOptions: {opts_str}\nCorrect Answer: {answer}"
        if len(chunk.strip()) < 30:
            continue

        doc_id = _stable_uuid(f"medqa_{count}")
        await _embed_and_store(doc_id, chunk, {
            "source": "MedQA-USMLE",
            "type": "clinical_reasoning",
            "question": question[:200],
        })

        count += 1
        if count % 500 == 0:
            print(f"   ✅ MedQA: {count} entries ingested")

    print(f"   ✅ MedQA complete — {count} entries")
    return count


# ═══════════════════════════════════════════════════════════
# 3. MedMCQA (massive — 20k sampled from 194k)
# ═══════════════════════════════════════════════════════════
async def seed_medmcqa(max_entries: int = 20000):
    from datasets import load_dataset

    print(f"\n📚 [3/4] Loading MedMCQA (sampling {max_entries:,} from train)…")
    ds = load_dataset("openlifescienceai/medmcqa", split="train", trust_remote_code=True)

    count = 0
    label_map = {0: "A", 1: "B", 2: "C", 3: "D"}
    for row in ds:
        if count >= max_entries:
            break

        question = row.get("question", "")
        opa = row.get("opa", "")
        opb = row.get("opb", "")
        opc = row.get("opc", "")
        opd = row.get("opd", "")
        correct = label_map.get(row.get("cop", -1), "?")
        subject = row.get("subject_name", "General")
        explanation = row.get("exp", "")

        chunk = f"[{subject}] Q: {question}\nA) {opa}  B) {opb}  C) {opc}  D) {opd}\nCorrect: {correct}"
        if explanation:
            chunk += f"\nExplanation: {explanation}"

        if len(chunk.strip()) < 30:
            continue

        doc_id = _stable_uuid(f"medmcqa_{count}")
        await _embed_and_store(doc_id, chunk, {
            "source": "MedMCQA",
            "type": "medical_mcq",
            "subject": subject,
            "question": question[:200],
        })

        if subject and question:
            graph_store.add_relationship(subject, "COVERS_TOPIC", question[:60])

        count += 1
        if count % 1000 == 0:
            print(f"   ✅ MedMCQA: {count:,} entries ingested")

    print(f"   ✅ MedMCQA complete — {count:,} entries")
    return count


# ═══════════════════════════════════════════════════════════
# 4. Curated Specialty Knowledge Base
#    Handwritten clinical reference paragraphs covering
#    every major medical specialty — ensures the RAG engine
#    has foundational knowledge even for rare specialties
#    that may be underrepresented in the MCQ datasets.
# ═══════════════════════════════════════════════════════════
SPECIALTY_KNOWLEDGE = {
    "Oncology": [
        "Cancer staging uses the TNM system: Tumor size (T), Node involvement (N), Metastasis (M). Staging guides treatment decisions including surgery, chemotherapy, radiation, immunotherapy, and targeted therapy. Common cancers include lung, breast, colorectal, prostate, and pancreatic carcinoma.",
        "Chemotherapy agents are classified by mechanism: alkylating agents (cyclophosphamide), antimetabolites (methotrexate, 5-FU), plant alkaloids (vincristine, paclitaxel), antibiotics (doxorubicin), and topoisomerase inhibitors. Side effects include myelosuppression, nausea, alopecia, and mucositis.",
        "Immunotherapy has revolutionized oncology. Checkpoint inhibitors (PD-1/PD-L1 blockers like pembrolizumab, nivolumab) and CTLA-4 inhibitors (ipilimumab) enhance immune-mediated tumor killing. CAR-T cell therapy is approved for certain B-cell lymphomas and ALL.",
        "Breast cancer subtypes guide therapy: ER+/PR+ (hormonal therapy with tamoxifen or aromatase inhibitors), HER2+ (trastuzumab), Triple-negative (chemotherapy). Screening with mammography is recommended starting at age 40-50 depending on guidelines.",
    ],
    "Hematology": [
        "Anemia is classified by MCV: microcytic (iron deficiency, thalassemia), normocytic (chronic disease, acute blood loss), macrocytic (B12/folate deficiency, MDS). Iron studies include serum iron, TIBC, ferritin, and transferrin saturation.",
        "Leukemias are classified as acute (ALL, AML) or chronic (CLL, CML). AML is common in adults with Auer rods on smear. CML shows the Philadelphia chromosome t(9;22) BCR-ABL fusion treated with imatinib (tyrosine kinase inhibitor).",
        "Coagulation cascade: intrinsic pathway (XII→XI→IX→VIII→X), extrinsic pathway (TF→VII→X), common pathway (X→V→thrombin→fibrin). PT/INR measures extrinsic, PTT measures intrinsic. Heparin affects PTT; warfarin affects PT/INR.",
        "Deep vein thrombosis (DVT) presents with unilateral leg swelling, pain, and warmth. Diagnosis by D-dimer and compression ultrasonography. Treatment: anticoagulation with LMWH bridging to warfarin or DOACs (rivaroxaban, apixaban).",
    ],
    "Nephrology": [
        "Chronic kidney disease (CKD) is staged by GFR: Stage 1 (≥90), Stage 2 (60-89), Stage 3a (45-59), 3b (30-44), Stage 4 (15-29), Stage 5 (<15, dialysis). Complications include anemia, hyperkalemia, metabolic acidosis, renal osteodystrophy, and uremia.",
        "Nephrotic syndrome: proteinuria >3.5g/day, hypoalbuminemia, edema, hyperlipidemia. Causes: minimal change disease (children), FSGS, membranous nephropathy, diabetic nephropathy. Treatment includes corticosteroids and ACE inhibitors.",
        "Acute kidney injury (AKI): pre-renal (hypoperfusion), intrinsic (ATN, glomerulonephritis), post-renal (obstruction). FENa <1% suggests pre-renal, >2% suggests intrinsic. Muddy brown casts indicate ATN.",
        "Glomerulonephritis: IgA nephropathy (mesangial IgA deposits, most common worldwide), post-streptococcal GN (children, low C3), Goodpasture syndrome (anti-GBM antibodies, pulmonary-renal), lupus nephritis (WHO classification I-V).",
    ],
    "Pulmonology": [
        "Asthma is characterized by reversible airway obstruction, bronchial hyperresponsiveness, and inflammation. Diagnosed by spirometry showing FEV1/FVC <0.70 with >12% reversibility. Step therapy: SABA → low-dose ICS → add LABA → medium/high ICS-LABA → biologics (omalizumab, mepolizumab).",
        "COPD includes emphysema (destruction of alveoli, decreased DLCO) and chronic bronchitis (productive cough ≥3 months/year for 2 years). Primarily caused by smoking. Treatment: bronchodilators (tiotropium, salmeterol), ICS for exacerbations, oxygen therapy if PaO2 <55.",
        "Pulmonary embolism: acute dyspnea, pleuritic chest pain, tachycardia. Wells score guides workup. D-dimer for low-probability; CT pulmonary angiography (CTPA) is gold standard. Treatment: anticoagulation, thrombolytics for massive PE with hemodynamic instability.",
        "Pneumonia: community-acquired (S. pneumoniae, H. influenzae, Mycoplasma), hospital-acquired (Pseudomonas, MRSA, Klebsiella). Chest X-ray shows consolidation. Empiric therapy: outpatient (amoxicillin or azithromycin), inpatient (ceftriaxone + azithromycin).",
        "Interstitial lung diseases include idiopathic pulmonary fibrosis (IPF), sarcoidosis, hypersensitivity pneumonitis, and pneumoconioses (asbestosis, silicosis). IPF shows UIP pattern on HRCT (honeycombing, traction bronchiectasis). Treatment: pirfenidone, nintedanib.",
    ],
    "Endocrinology": [
        "Diabetes mellitus: Type 1 (autoimmune beta-cell destruction, insulin-dependent), Type 2 (insulin resistance). Diagnosis: fasting glucose ≥126, HbA1c ≥6.5%, random glucose ≥200 with symptoms. Complications: retinopathy, nephropathy, neuropathy, cardiovascular disease.",
        "Thyroid disorders: hypothyroidism (fatigue, weight gain, cold intolerance — TSH elevated, free T4 low — treat with levothyroxine), hyperthyroidism (weight loss, tremor, heat intolerance — TSH low, free T4 high — Graves disease, toxic nodule). Thyroid storm is a medical emergency.",
        "Adrenal insufficiency: primary (Addison disease — cortisol and aldosterone deficient, elevated ACTH, hyperpigmentation) vs secondary (pituitary failure — low ACTH). Treatment: hydrocortisone + fludrocortisone. Stress dosing during illness/surgery.",
        "Cushing syndrome: excess cortisol. Features: central obesity, moon facies, striae, buffalo hump, hyperglycemia, hypertension. Workup: 24hr urine cortisol, overnight dexamethasone suppression test, midnight salivary cortisol.",
        "Pituitary adenomas: prolactinoma (galactorrhea, amenorrhea — treat with cabergoline), growth hormone-secreting (acromegaly), ACTH-secreting (Cushing disease), non-functioning (visual field defects from chiasmal compression).",
    ],
    "Rheumatology": [
        "Rheumatoid arthritis: symmetric polyarthritis of small joints (MCPs, PIPs, wrists). RF and anti-CCP antibodies. Erosive disease on X-ray. Treatment: DMARDs (methotrexate first-line), biologics (TNF inhibitors like adalimumab, etanercept).",
        "Systemic lupus erythematosus (SLE): multisystem autoimmune disease. Malar rash, arthritis, serositis, nephritis, cytopenias, anti-dsDNA and anti-Smith antibodies, low complement. Treatment: hydroxychloroquine (all patients), steroids, mycophenolate for nephritis.",
        "Gout: monosodium urate crystal deposition. Acute: podagra (first MTP), intense inflammation. Negatively birefringent crystals on polarized microscopy. Acute treatment: NSAIDs, colchicine, steroids. Prophylaxis: allopurinol, febuxostat.",
        "Ankylosing spondylitis: inflammatory back pain improving with exercise, sacroiliitis, HLA-B27 association. Bamboo spine on X-ray. Treatment: NSAIDs, TNF inhibitors, physical therapy.",
    ],
    "Gastroenterology": [
        "Inflammatory bowel disease: Crohn disease (transmural, skip lesions, any GI segment, fistulas, granulomas) vs Ulcerative colitis (mucosal only, continuous from rectum, bloody diarrhea, pseudopolyps). Treatment: 5-ASA, steroids, azathioprine, biologics (infliximab).",
        "Hepatitis: A (fecal-oral, self-limited), B (blood/sexual, chronic in 5-10% adults, HBsAg/anti-HBc, treat with tenofovir/entecavir), C (blood, chronic in 75%, direct-acting antivirals cure >95%). Cirrhosis complications: varices, ascites, hepatic encephalopathy, HCC.",
        "Peptic ulcer disease: gastric and duodenal ulcers. H. pylori (urea breath test, stool antigen) or NSAID-induced. Treatment: PPI + amoxicillin + clarithromycin (triple therapy). Complications: bleeding, perforation, obstruction.",
        "Celiac disease: autoimmune response to gluten. Villous atrophy in small bowel. Anti-tTG IgA antibodies. Treatment: strict gluten-free diet. Associated with dermatitis herpetiformis, iron deficiency anemia, osteoporosis.",
        "Pancreatitis: acute (gallstones, alcohol — lipase elevated >3x ULN, epigastric pain radiating to back) vs chronic (calcifications, exocrine/endocrine insufficiency). Treatment: NPO, IV fluids, pain control, ERCP for gallstone pancreatitis.",
    ],
    "Infectious Disease": [
        "HIV/AIDS: CD4 count staging, viral load monitoring. Opportunistic infections: PCP (CD4 <200, TMP-SMX prophylaxis), toxoplasmosis (CD4 <100), MAC (CD4 <50), CMV retinitis (CD4 <50). ART: 2 NRTIs + integrase inhibitor (dolutegravir).",
        "Tuberculosis: Mycobacterium tuberculosis. Pulmonary TB: cough, hemoptysis, night sweats, weight loss, upper lobe cavitary lesion. Diagnosis: sputum AFB smear/culture, GeneXpert. Treatment: RIPE (rifampin, isoniazid, pyrazinamide, ethambutol) for 2 months then RI for 4 months.",
        "Sepsis: systemic inflammatory response to infection. qSOFA ≥2, lactate >2. Management: early antibiotics (<1 hour), IV fluid resuscitation (30 mL/kg crystalloid), vasopressors (norepinephrine first-line), source control. Septic shock: sepsis + vasopressors + lactate >2.",
        "Meningitis: bacterial (N. meningitidis, S. pneumoniae — high protein, low glucose, PMN predominance in CSF), viral (enterovirus — normal glucose, lymphocytes), fungal (Cryptococcus in HIV — India ink, crypto antigen). Empiric: ceftriaxone + vancomycin + dexamethasone.",
    ],
    "Dermatology": [
        "Psoriasis: silvery scales on extensor surfaces, Auspitz sign, nail pitting. Treatment ladder: topical steroids → vitamin D analogs → phototherapy → methotrexate → biologics (secukinumab IL-17, ustekinumab IL-12/23).",
        "Melanoma: ABCDE criteria (Asymmetry, Border irregularity, Color variation, Diameter >6mm, Evolution). Breslow depth determines prognosis. Sentinel lymph node biopsy for staging. Treatment: wide local excision, immunotherapy (pembrolizumab) for advanced disease.",
        "Eczema (atopic dermatitis): chronic relapsing pruritic dermatitis. Flexural distribution in children/adults. Treatment: emollients, topical corticosteroids, calcineurin inhibitors (tacrolimus), dupilumab for moderate-severe. Part of the atopic triad with asthma and allergic rhinitis.",
        "Stevens-Johnson syndrome (SJS) and toxic epidermal necrolysis (TEN): severe drug reactions. Mucocutaneous sloughing, Nikolsky sign positive. Common culprits: allopurinol, sulfonamides, carbamazepine, phenytoin. Treatment: stop offending drug, supportive ICU care, IVIG controversial.",
    ],
    "Ophthalmology": [
        "Glaucoma: open-angle (gradual peripheral vision loss, elevated IOP, optic disc cupping — treat with prostaglandin analogs like latanoprost) vs angle-closure (acute red eye, mid-dilated pupil, halos — emergency with pilocarpine and laser iridotomy).",
        "Diabetic retinopathy: non-proliferative (microaneurysms, cotton wool spots, hard exudates) → proliferative (neovascularization, vitreous hemorrhage). Treatment: glycemic control, anti-VEGF injections (ranibizumab, bevacizumab), laser photocoagulation.",
        "Age-related macular degeneration (AMD): dry (drusen, geographic atrophy) vs wet (choroidal neovascularization, sudden vision loss). Wet AMD treated with anti-VEGF injections. Amsler grid for monitoring. Central vision loss with preserved peripheral vision.",
        "Retinal detachment: flashes, floaters, curtain-like visual field defect. Emergent ophthalmology referral. Types: rhegmatogenous (retinal tear), tractional (diabetic), exudative (inflammatory). Treatment: pneumatic retinopexy, scleral buckle, or vitrectomy.",
    ],
    "ENT / Otolaryngology": [
        "Otitis media: middle ear infection in children. S. pneumoniae, H. influenzae, M. catarrhalis. Bulging TM, ear pain, fever. Treatment: amoxicillin first-line, amoxicillin-clavulanate for resistant cases. Complications: TM perforation, mastoiditis, cholesteatoma.",
        "Sinusitis: acute (<4 weeks) vs chronic (>12 weeks). Viral (common cold) vs bacterial (≥10 days symptoms or biphasic illness). Treatment: saline irrigation, intranasal steroids, amoxicillin-clavulanate for bacterial.",
        "Head and neck cancers: squamous cell carcinoma of oral cavity, oropharynx, larynx, hypopharynx. Risk factors: smoking, alcohol, HPV (oropharynx). Presents with persistent hoarseness, dysphagia, neck mass. Treatment: surgery, radiation, chemoradiation.",
        "Hearing loss: conductive (middle ear pathology — otosclerosis, effusion, perforation, Weber lateralizes to affected ear, Rinne BC>AC) vs sensorineural (inner ear/CN VIII — presbycusis, noise, Meniere, Weber lateralizes away, Rinne AC>BC).",
    ],
    "Urology": [
        "Benign prostatic hyperplasia (BPH): lower urinary tract symptoms (frequency, urgency, nocturia, hesitancy, weak stream). PSA may be mildly elevated. Treatment: alpha-blockers (tamsulosin), 5-alpha reductase inhibitors (finasteride), TURP for refractory cases.",
        "Kidney stones (nephrolithiasis): calcium oxalate (most common), uric acid (radiolucent), struvite (infection stones, staghorn), cystine (hexagonal crystals). Colicky flank pain, hematuria. CT non-contrast for diagnosis. Treatment: hydration, NSAIDs, alpha-blockers, lithotripsy, ureteroscopy.",
        "Prostate cancer: most common cancer in men. Screening with PSA controversial. Gleason score for grading. Treatment depends on stage: active surveillance, radical prostatectomy, radiation, androgen deprivation therapy (leuprolide, enzalutamide).",
        "Urinary tract infection: cystitis (dysuria, frequency, urgency) vs pyelonephritis (flank pain, fever, CVA tenderness). E. coli most common. Uncomplicated cystitis: nitrofurantoin or TMP-SMX. Pyelonephritis: fluoroquinolone or ceftriaxone.",
    ],
    "Obstetrics": [
        "Preeclampsia: hypertension (≥140/90) + proteinuria after 20 weeks gestation. Severe features: BP ≥160/110, thrombocytopenia, liver enzymes elevated, renal insufficiency, pulmonary edema. Treatment: magnesium sulfate (seizure prophylaxis), antihypertensives, delivery is definitive.",
        "Gestational diabetes: glucose intolerance first recognized in pregnancy. Screening at 24-28 weeks with oral glucose tolerance test. Risks: macrosomia, shoulder dystocia, neonatal hypoglycemia. Management: diet, exercise, insulin if needed.",
        "Ectopic pregnancy: implantation outside uterine cavity (95% tubal). Triad: amenorrhea, vaginal bleeding, abdominal pain. Beta-hCG rising slowly, no IUP on ultrasound. Treatment: methotrexate (if stable, <3.5cm, no fetal heartbeat) or surgery.",
        "Placental abruption: premature separation of placenta. Painful vaginal bleeding, rigid abdomen, fetal distress. Risk factors: hypertension, cocaine, trauma. Management: emergent delivery if at term or fetal distress.",
    ],
    "Pediatrics": [
        "Common childhood exanthems: measles (Koplik spots, maculopapular rash, cough-coryza-conjunctivitis), rubella (postauricular lymphadenopathy), roseola (HHV-6, high fever then rash), fifth disease (parvovirus B19, slapped-cheek rash), chickenpox (vesicular rash in different stages).",
        "Kawasaki disease: fever ≥5 days + 4 of 5: bilateral conjunctivitis, oral changes (strawberry tongue), rash, extremity changes (desquamation), cervical lymphadenopathy. Risk: coronary artery aneurysms. Treatment: IVIG + aspirin.",
        "Neonatal jaundice: physiologic (day 2-3, unconjugated, resolves by day 7) vs pathologic (first 24 hours, prolonged, conjugated). Kernicterus risk with very high bilirubin. Treatment: phototherapy, exchange transfusion if severe.",
        "Intussusception: most common cause of intestinal obstruction in children 6-36 months. Currant jelly stool, colicky pain, sausage-shaped mass. Diagnosis and treatment: air or contrast enema reduction. Surgery if not reducible.",
    ],
    "Psychiatry": [
        "Major depressive disorder: ≥5 symptoms for ≥2 weeks including depressed mood or anhedonia. SIG E CAPS mnemonic. First-line treatment: SSRIs (sertraline, escitalopram). CBT is effective. Treatment-resistant: augmentation with atypical antipsychotics, ketamine/esketamine, ECT.",
        "Schizophrenia: positive symptoms (hallucinations, delusions, disorganized speech), negative symptoms (flat affect, avolition, alogia), cognitive symptoms. Treatment: first-generation (haloperidol) and second-generation (risperidone, olanzapine, clozapine for refractory). Clozapine requires ANC monitoring.",
        "Bipolar disorder: Type I (mania + depression), Type II (hypomania + depression). Mania: elevated mood, decreased sleep, grandiosity, pressured speech, risky behavior. Treatment: mood stabilizers (lithium, valproate), atypical antipsychotics. Lithium requires renal and thyroid monitoring.",
        "Anxiety disorders: GAD (excessive worry ≥6 months), panic disorder (recurrent panic attacks), social anxiety, specific phobias, PTSD, OCD. Treatment: SSRIs first-line, buspirone for GAD, benzodiazepines short-term only. CBT is evidence-based for all anxiety disorders.",
    ],
    "Emergency Medicine": [
        "ACLS: cardiac arrest algorithm — shockable rhythms (VF/pVT: defibrillation, epinephrine q3-5min, amiodarone) vs non-shockable (PEA/asystole: epinephrine, identify/treat reversible causes — Hs and Ts). High-quality CPR: rate 100-120/min, depth ≥2 inches, full recoil.",
        "Trauma: ATLS primary survey (ABCDE): Airway, Breathing, Circulation, Disability, Exposure. Massive transfusion protocol: 1:1:1 ratio of pRBCs:FFP:platelets. FAST exam for abdominal free fluid. Tension pneumothorax: tracheal deviation, absent breath sounds — needle decompression at 2nd ICS.",
        "Stroke: ischemic (85%) vs hemorrhagic (15%). NIHSS for severity. CT head to rule out hemorrhage. tPA (alteplase) within 4.5 hours of symptom onset for ischemic stroke. Thrombectomy for large vessel occlusion within 24 hours. BP management differs for ischemic vs hemorrhagic.",
        "Anaphylaxis: rapid-onset systemic allergic reaction. Urticaria, angioedema, bronchospasm, hypotension. Treatment: IM epinephrine (0.3-0.5mg of 1:1000) to anterolateral thigh — repeat q5-15min. Adjuncts: IV fluids, antihistamines, steroids, nebulized albuterol.",
    ],
    "Dental / Oral Surgery": [
        "Impacted third molars (wisdom teeth): horizontally, vertically, mesio-angularly, or disto-angularly impacted. Complications: pericoronitis (gum tissue inflammation), dental caries in adjacent teeth, cyst formation, root resorption. Treatment: surgical extraction under local or general anesthesia.",
        "Dental caries: demineralization of tooth enamel by acid-producing bacteria (S. mutans). Classification: incipient, moderate, advanced, severe. Treatment: fluoride, composites, crowns, root canal therapy for pulp involvement. Prevention: fluoride, sealants, oral hygiene.",
        "Temporomandibular joint (TMJ) disorders: pain, clicking, limited jaw opening. Causes: bruxism, arthritis, disc displacement, trauma. Treatment: NSAIDs, physical therapy, occlusal splints, arthrocentesis for refractory cases.",
        "Oral cancers: squamous cell carcinoma of tongue, floor of mouth, buccal mucosa. Risk factors: tobacco, alcohol, betel nut, HPV. Presents as non-healing ulcer, leukoplakia, erythroplakia. Treatment: surgical resection with margins, radiation, chemoradiation.",
        "Periapical abscess: infection at tooth root apex from untreated caries or trauma. Presents with severe throbbing toothache, swelling, fever, percussion sensitivity. Treatment: drainage, antibiotics (amoxicillin or clindamycin), root canal therapy or extraction.",
    ],
    "Orthopedics": [
        "Fracture classification: open vs closed, displaced vs non-displaced. Common fractures: Colles (distal radius), hip (femoral neck — intracapsular, intertrochanteric), ankle (Weber classification). Treatment: reduction, immobilization (casting, splinting), ORIF for displaced/unstable.",
        "Osteoarthritis: degenerative joint disease. Weight-bearing joints (knees, hips), DIP and PIP joints (Heberden and Bouchard nodes). X-ray: joint space narrowing, osteophytes, subchondral sclerosis. Treatment: weight loss, physical therapy, NSAIDs, intra-articular steroids/hyaluronic acid, joint replacement.",
        "ACL tear: pivot injury, pop sound, knee swelling. Lachman test (most sensitive), anterior drawer test. MRI for confirmation. Treatment: rehabilitation for low-demand patients, ACL reconstruction for active patients.",
        "Spine disorders: herniated disc (radiculopathy — L4-5 most common lumbar), spinal stenosis (neurogenic claudication), spondylolisthesis. Red flags: cauda equina syndrome (urinary retention, saddle anesthesia — surgical emergency).",
    ],
    "Radiology": [
        "Chest X-ray interpretation: systematic approach — ABCDE (Airway, Bones, Cardiac, Diaphragm, Everything else). Key findings: cardiomegaly (CTR >0.5), pleural effusion (meniscus sign), pneumothorax (absent lung markings), consolidation (air bronchograms).",
        "CT imaging: uses X-rays and computer reconstruction. Contrast-enhanced for vascular studies. Key indications: trauma (CT head, CT abdomen), PE (CTPA), stroke (CT head non-contrast), cancer staging. Radiation dose considerations, especially in children and pregnant women.",
        "MRI: uses magnetic fields and radiofrequency pulses. Superior soft tissue contrast. T1 (anatomy — fat bright), T2 (pathology — fluid bright), FLAIR (T2 with CSF suppressed). Key uses: brain, spine, joints, soft tissues. Contraindicated with some metallic implants and pacemakers.",
        "Ultrasound: real-time, no radiation. Key uses: obstetric (fetal assessment), FAST exam (trauma — free fluid), echocardiography (cardiac function), hepatobiliary (gallstones, liver lesions), DVT (compression ultrasonography).",
    ],
    "Anesthesiology": [
        "General anesthesia: induction (propofol, etomidate), maintenance (inhaled agents — sevoflurane, desflurane; IV — propofol infusion), emergence. Airway management: endotracheal intubation, laryngeal mask airway (LMA). Complications: aspiration, malignant hyperthermia (treat with dantrolene).",
        "Regional anesthesia: neuraxial (epidural — labor, post-op; spinal — C-section, lower extremity surgery) and peripheral nerve blocks (brachial plexus, femoral nerve). Local anesthetics: lidocaine (short-acting), bupivacaine (long-acting). LAST toxicity: seizures, cardiac arrest — treat with intralipid.",
        "Perioperative pain management: multimodal approach — NSAIDs, acetaminophen, regional techniques, opioids (morphine, fentanyl, hydromorphone). Patient-controlled analgesia (PCA). Enhanced recovery after surgery (ERAS) protocols minimize opioid use.",
    ],
    "Pathology": [
        "Inflammation: acute (neutrophils, vascular changes, cardinal signs — rubor, calor, dolor, tumor, functio laesa) vs chronic (lymphocytes, macrophages, granulomas — TB, sarcoidosis, Crohn). Chemical mediators: histamine, prostaglandins, leukotrienes, cytokines.",
        "Neoplasia: benign (encapsulated, well-differentiated, slow growth, no metastasis) vs malignant (invasive, poorly differentiated, rapid growth, metastasis via hematogenous, lymphatic, or seeding). Tumor markers: PSA (prostate), AFP (liver, germ cell), CA-125 (ovarian), CEA (colorectal).",
        "Cell injury and death: reversible (cellular swelling, fatty change) vs irreversible (coagulative necrosis, liquefactive necrosis, caseous necrosis, fat necrosis, fibrinoid necrosis). Apoptosis: programmed cell death via caspase cascade. Autophagy: cellular self-digestion.",
    ],
    "Neurosurgery": [
        "Intracranial hemorrhage: epidural hematoma (middle meningeal artery, biconvex/lens shape on CT, lucid interval), subdural hematoma (bridging veins, crescent shape, acute vs chronic), subarachnoid hemorrhage (thunderclap headache, berry aneurysm, CT then LP if negative).",
        "Brain tumors: glioblastoma (GBM — most common malignant primary, butterfly pattern crossing midline), meningioma (benign, dural-based, enhancing), schwannoma (CN VIII, cerebellopontine angle), pituitary adenoma. Treatment: surgery, temozolomide + radiation for GBM.",
        "Hydrocephalus: obstructive (non-communicating — tumor, stenosis) vs communicating (impaired CSF absorption). Normal pressure hydrocephalus (NPH): triad of wet (urinary incontinence), wacky (dementia), wobbly (gait apraxia). Treatment: VP shunt.",
    ],
}


async def seed_specialty_knowledge():
    print("\n📚 [4/4] Embedding curated specialty knowledge base…")
    count = 0
    for specialty, paragraphs in SPECIALTY_KNOWLEDGE.items():
        for i, text in enumerate(paragraphs):
            doc_id = _stable_uuid(f"specialty_{specialty}_{i}")
            await _embed_and_store(doc_id, text, {
                "source": "MedRAG_Curated",
                "type": "specialty_reference",
                "specialty": specialty,
            })
            graph_store.add_relationship(specialty, "HAS_KNOWLEDGE", text[:60])
            count += 1

        print(f"   ✅ {specialty}: {len(paragraphs)} entries")

    print(f"   ✅ Specialty knowledge complete — {count} entries across {len(SPECIALTY_KNOWLEDGE)} specialties")
    return count


# ═══════════════════════════════════════════════════════════
# Main Runner
# ═══════════════════════════════════════════════════════════
async def main():
    print("=" * 60)
    print("  MedRAG Knowledge Base Seeder — Expanded Edition")
    print("  Downloading & embedding open-source medical datasets")
    print("=" * 60)

    start = time.time()

    total = 0
    total += await seed_pubmedqa()
    total += await seed_medqa()
    total += await seed_medmcqa(max_entries=20000)
    total += await seed_specialty_knowledge()

    graph_store.save_graph()

    elapsed = time.time() - start
    print("\n" + "=" * 60)
    print(f"  🎉 Seeding complete!")
    print(f"  Total documents ingested: {total:,}")
    print(f"  Time elapsed: {elapsed / 60:.1f} minutes")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
