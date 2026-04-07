import axios from 'axios';

// Create a global Axios instance to point to the FastAPI backend
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    timeout: 600000, // 10 minutes — RAG pipeline can take several minutes
    headers: {
        'Content-Type': 'application/json',
    },
});

// ── AUTH TOKEN INTERCEPTOR ──
// Automatically attach JWT token to every request if available
api.interceptors.request.use(
    (config) => {
        const user = localStorage.getItem('user');
        if (user) {
            try {
                const parsed = JSON.parse(user);
                if (parsed.access_token) {
                    config.headers.Authorization = `Bearer ${parsed.access_token}`;
                }
            } catch (e) {
                // Invalid JSON in localStorage, ignore
            }
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Interceptor for catching global errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error("API Error Response:", error.response);
        // If 401 Unauthorized, clear session and redirect to login.
        // This covers both expired real tokens AND stale mock-auth sessions.
        if (error.response && error.response.status === 401) {
            const user = localStorage.getItem('user');
            if (user) {
                try {
                    const parsed = JSON.parse(user);
                    if (!parsed.access_token) {
                        console.warn('Session has no real JWT token. Redirecting to login for proper authentication.');
                    }
                } catch (e) { /* ignore */ }
            }
            localStorage.removeItem('user');
            if (!window.location.pathname.includes('/login')) {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

// --- MOCK DATABASE (kept as fallback for offline demo) ---
const mockDoctors = [
    { identifier: 'dr.smith@medrag.com', password: 'password123', name: 'Dr. Smith', id: '1', role: 'doctor', specialty: 'Cardiology' },
    { identifier: 'dr.jones@medrag.com', password: 'password123', name: 'Dr. Jones', id: '2', role: 'doctor', specialty: 'Neurology' },
    { identifier: '1234567890', password: 'password123', name: 'Dr. Patel', id: '3', role: 'doctor', specialty: 'Orthopaedic' },
];

const mockPatients = [
    { identifier: 'john.doe@email.com', password: 'password123', name: 'John Doe', id: '4', role: 'patient', sex: 'Male' },
    { identifier: 'jane.smith@email.com', password: 'password123', name: 'Jane Smith', id: '5', role: 'patient', sex: 'Female' },
    { identifier: '0987654321', password: 'password123', name: 'Bob User', id: '6', role: 'patient', sex: 'Male' },
    { identifier: 'alice.w@email.com', password: 'password123', name: 'Alice Wong', id: '7', role: 'patient', sex: 'Female' },
];

// --- AUTHENTICATION ---
export const loginUser = async (identifier, password, role) => {
    try {
        // Real backend OAuth2 login (form-encoded)
        const formData = new URLSearchParams();
        formData.append('username', identifier);
        formData.append('password', password);
        
        const res = await api.post('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        
        const data = res.data;
        return {
            status: 'success',
            user_id: data.user_id,
            email: data.email,
            name: data.username,
            role: data.role,
            specialty: data.specialty,
            sex: data.sex,
            access_token: data.access_token
        };
    } catch (e) {
        console.warn('Backend login failed, falling back to mock auth:', e.message);
        // Fallback to mock auth for offline demo
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (role === 'doctor') {
                    const doc = mockDoctors.find(u => u.identifier === identifier);
                    if (!doc) return reject(new Error('Doctor profile not found.'));
                    if (doc.password !== password) return reject(new Error('Wrong credentials for Doctor.'));
                    resolve({ status: 'success', user_id: doc.id, email: doc.identifier, name: doc.name, role, specialty: doc.specialty, access_token: null });
                } else {
                    const pat = mockPatients.find(u => u.identifier === identifier);
                    if (!pat) return reject(new Error('Patient not found.'));
                    if (pat.password !== password) return reject(new Error('Wrong credentials for Patient.'));
                    resolve({ status: 'success', user_id: pat.id, email: pat.identifier, name: pat.name, role, sex: pat.sex, access_token: null });
                }
            }, 300);
        });
    }
};

export const registerPatient = async (patientData) => {
    try {
        // Real backend registration
        const res = await api.post('/auth/register', {
            username: patientData.email || patientData.contactNumber,
            email: patientData.email,
            password: patientData.password,
            role: 'patient'
        });
        
        const data = res.data;
        return {
            status: 'success',
            user_id: data.user_id,
            email: data.email,
            name: data.username,
            role: data.role,
            access_token: data.access_token
        };
    } catch (e) {
        console.warn('Backend registration failed, falling back to mock:', e.message);
        // Fallback mock registration
        return new Promise((resolve) => {
            setTimeout(() => {
                mockPatients.push({
                    identifier: patientData.email || patientData.contactNumber,
                    password: patientData.password,
                    name: `${patientData.firstName} ${patientData.lastName}`,
                    id: patientData.patientId,
                    role: 'patient'
                });
                resolve({
                    status: 'success',
                    user_id: patientData.patientId,
                    email: patientData.email,
                    name: `${patientData.firstName} ${patientData.lastName}`,
                    role: 'patient',
                    access_token: null
                });
            }, 1500);
        });
    }
};

export const logoutUser = () => {
    localStorage.removeItem('user');
    window.location.href = '/login';
};

// --- RAG PIPELINE ---
export const generateReport = async (formData) => {
    try {
        const res = await api.post('/rag/generate-report', formData);
        return res;
    } catch (e) {
        // Mock Fallback
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    data: {
                        status: "success",
                        diagnosis: "Mock Fallback Diagnosis: Potential localized inflammation or muscular strain based on observed patient metrics. Recommended rest, hydration, and NSAIDs as needed.",
                        evidences: [
                            "Clinical Trial 1032 indicates 85% efficacy for standard NSAID protocol in similar strain patterns.",
                            "Image analysis (simulated): No apparent fractures. Soft tissue slightly elevated."
                        ]
                    }
                });
            }, 2000);
        });
    }
};

export const uploadFile = async (formData) => {
    return await api.post('/upload/record', formData);
};

export const getPatientHistory = async (patientId) => {
    try {
        return await api.get(`/patient/${patientId}/history`);
    } catch (e) {
        console.warn('Backend patient history failed:', e.message);
        return { data: null };
    }
};

// --- APPOINTMENTS ---
export const bookAppointment = async (appointmentData) => {
    return await api.post('/appointments/book', appointmentData);
};

export const getPatientAppointments = async (patientId) => {
    return await api.get(`/appointments/patient/${patientId}`);
};

export const getDoctorsBySpecialty = async (specialty) => {
    return await api.get(`/doctors/specialty/${specialty}`);
};

// --- DETAILED MOCK PATIENT PROFILES ---
const mockPatientProfiles = {
    'JD123456': {
        id: 'JD123456', name: 'John Doe', age: 58, sex: 'Male', dob: '1968-05-14',
        email: 'john.doe@email.com', phone: '+1 (555) 123-4567', bloodType: 'O+',
        address: '142 Maple Ave, Springfield, IL 62704',
        emergencyContact: { name: 'Mary Doe', relation: 'Spouse', phone: '+1 (555) 123-4568' },
        insurance: { provider: 'BlueCross BlueShield', policyNo: 'BC-8827341', group: 'GRP-44021' },
        risk: 68, status: 'High Risk', lastVisit: '2026-03-20',
        conditions: ['Hypertension (Stage 2)', 'Type 2 Diabetes', 'Hyperlipidemia', 'Suspected Rheumatoid Arthritis'],
        allergies: ['Penicillin', 'Sulfa Drugs'],
        medications: [
            { name: 'Lisinopril', dose: '20mg', freq: 'Once daily', purpose: 'Blood Pressure' },
            { name: 'Metformin', dose: '500mg', freq: 'Twice daily', purpose: 'Blood Sugar' },
            { name: 'Atorvastatin', dose: '40mg', freq: 'Once daily (evening)', purpose: 'Cholesterol' },
            { name: 'Aspirin', dose: '81mg', freq: 'Once daily', purpose: 'Cardiac Prevention' },
        ],
        vitals: { bp: '148/92', heartRate: 82, temp: '98.6°F', weight: '198 lbs', height: '5\'10"', bmi: 28.4, spO2: '96%' },
        labResults: [
            { test: 'HbA1c', value: '7.2%', range: '< 5.7%', status: 'high', date: '2026-03-18' },
            { test: 'Fasting Glucose', value: '142 mg/dL', range: '70-100 mg/dL', status: 'high', date: '2026-03-18' },
            { test: 'Total Cholesterol', value: '224 mg/dL', range: '< 200 mg/dL', status: 'high', date: '2026-03-18' },
            { test: 'LDL Cholesterol', value: '148 mg/dL', range: '< 100 mg/dL', status: 'high', date: '2026-03-18' },
            { test: 'HDL Cholesterol', value: '42 mg/dL', range: '> 40 mg/dL', status: 'normal', date: '2026-03-18' },
            { test: 'CRP (C-Reactive Protein)', value: '8.4 mg/L', range: '< 3 mg/L', status: 'high', date: '2026-03-18' },
            { test: 'ESR', value: '38 mm/hr', range: '0-22 mm/hr', status: 'high', date: '2026-03-18' },
            { test: 'Creatinine', value: '1.1 mg/dL', range: '0.7-1.3 mg/dL', status: 'normal', date: '2026-03-18' },
        ],
        riskTrend: [
            { name: 'Jan', risk: 42 }, { name: 'Feb', risk: 48 }, { name: 'Mar', risk: 55 },
            { name: 'Apr', risk: 52 }, { name: 'May', risk: 58 }, { name: 'Jun', risk: 62 }, { name: 'Jul', risk: 68 },
        ],
        visitHistory: [
            { date: '2026-03-20', type: 'Follow-up', doctor: 'Dr. Smith', summary: 'Elevated CRP and joint pain reviewed. Rheumatology referral initiated.' },
            { date: '2026-02-12', type: 'Lab Review', doctor: 'Dr. Smith', summary: 'HbA1c rising; Metformin dosage adjusted from 250 to 500mg BID.' },
            { date: '2026-01-05', type: 'Annual Physical', doctor: 'Dr. Smith', summary: 'Baseline labs drawn. Weight gain of 8 lbs noted. Diet counseling provided.' },
            { date: '2025-10-18', type: 'Urgent Visit', doctor: 'Dr. Jones', summary: 'Acute knee swelling and pain. X-ray showed no fractures. NSAID prescribed.' },
        ],
        reports: [
            { id: 1, date: '2026-03-20', title: 'Rheumatology Screening Panel', final_report: 'Elevated CRP (8.4) and ESR (38) with localized joint pain in bilateral knees and hands. Recommend anti-CCP antibody testing and rheumatology consultation. Early RA cannot be ruled out.', confidence_calibration: { overall_confidence: 85 } },
            { id: 2, date: '2026-02-12', title: 'Metabolic Panel Review', final_report: 'HbA1c 7.2% (up from 6.8%). Fasting glucose 142. Diabetes control is deteriorating. Metformin increased. Consider adding GLP-1 agonist if no improvement in 3 months.', confidence_calibration: { overall_confidence: 92 } },
            { id: 3, date: '2026-01-05', title: 'Cardiovascular Risk Assessment', final_report: 'Framingham 10-year CVD risk: 18%. LDL remains above target at 148. Statin therapy continued. Lifestyle modification counseled. BP target of <130/80 not met.', confidence_calibration: { overall_confidence: 88 } },
        ],
        medicalHistory: 'John Doe is a 58-year-old male with a 12-year history of hypertension and a 6-year history of Type 2 Diabetes Mellitus. Recently presenting with bilateral joint stiffness predominantly in the mornings lasting >45 minutes. Family history significant for coronary artery disease (father, MI at age 62) and rheumatoid arthritis (mother). Former smoker (quit 2019, 15 pack-year history). Moderate alcohol use (2-3 drinks/week).',
    },
    'JS654321': {
        id: 'JS654321', name: 'Jane Smith', age: 34, sex: 'Female', dob: '1992-08-22',
        email: 'jane.smith@email.com', phone: '+1 (555) 234-5678', bloodType: 'A+',
        address: '88 Oak Street, Apt 4B, Chicago, IL 60614',
        emergencyContact: { name: 'Robert Smith', relation: 'Brother', phone: '+1 (555) 234-5679' },
        insurance: { provider: 'Aetna', policyNo: 'AE-5519882', group: 'GRP-77103' },
        risk: 42, status: 'Stable', lastVisit: '2026-03-15',
        conditions: ['Generalized Anxiety Disorder', 'Iron Deficiency Anemia (resolved)', 'Seasonal Allergies'],
        allergies: ['Latex', 'Ibuprofen'],
        medications: [
            { name: 'Sertraline', dose: '50mg', freq: 'Once daily', purpose: 'Anxiety' },
            { name: 'Cetirizine', dose: '10mg', freq: 'As needed', purpose: 'Allergies' },
            { name: 'Vitamin D3', dose: '2000 IU', freq: 'Once daily', purpose: 'Supplement' },
        ],
        vitals: { bp: '118/74', heartRate: 72, temp: '98.4°F', weight: '138 lbs', height: '5\'6"', bmi: 22.3, spO2: '99%' },
        labResults: [
            { test: 'CBC - Hemoglobin', value: '13.2 g/dL', range: '12.0-15.5 g/dL', status: 'normal', date: '2026-03-10' },
            { test: 'Ferritin', value: '42 ng/mL', range: '12-150 ng/mL', status: 'normal', date: '2026-03-10' },
            { test: 'TSH', value: '2.1 mIU/L', range: '0.4-4.0 mIU/L', status: 'normal', date: '2026-03-10' },
            { test: 'Vitamin D', value: '34 ng/mL', range: '30-100 ng/mL', status: 'normal', date: '2026-03-10' },
            { test: 'Total Cholesterol', value: '182 mg/dL', range: '< 200 mg/dL', status: 'normal', date: '2026-03-10' },
        ],
        riskTrend: [
            { name: 'Jan', risk: 50 }, { name: 'Feb', risk: 48 }, { name: 'Mar', risk: 45 },
            { name: 'Apr', risk: 43 }, { name: 'May', risk: 44 }, { name: 'Jun', risk: 43 }, { name: 'Jul', risk: 42 },
        ],
        visitHistory: [
            { date: '2026-03-15', type: 'Follow-up', doctor: 'Dr. Smith', summary: 'Anxiety well-managed on current dose. Continue Sertraline 50mg.' },
            { date: '2025-12-02', type: 'Lab Review', doctor: 'Dr. Smith', summary: 'Iron stores normalized. Discontinued Ferrous Sulfate supplement.' },
            { date: '2025-09-14', type: 'Annual Physical', doctor: 'Dr. Jones', summary: 'Healthy exam. Mild Vitamin D deficiency, supplementation started.' },
        ],
        reports: [
            { id: 1, date: '2026-03-15', title: 'Mental Health Follow-up', final_report: 'GAD-7 score improved from 14 to 8 over 6 months on Sertraline. Patient reports significant improvement in daily functioning. No side effects. Continue current regimen, follow up in 3 months.', confidence_calibration: { overall_confidence: 90 } },
            { id: 2, date: '2025-12-02', title: 'Anemia Resolution Panel', final_report: 'Hemoglobin 13.2 (previously 10.8). Ferritin 42 (previously 8). Iron deficiency anemia resolved after 6 months of supplementation. Discontinue Ferrous Sulfate.', confidence_calibration: { overall_confidence: 95 } },
        ],
        medicalHistory: 'Jane Smith is a 34-year-old female diagnosed with Generalized Anxiety Disorder in 2024, well-managed on Sertraline. Resolved iron deficiency anemia in 2025 after 6 months of supplementation. No surgical history. No family history of significant chronic disease. Non-smoker, occasional alcohol (1-2 drinks/month). Regular exercise routine (yoga 3x/week, jogging 2x/week).',
    },
    'BU112233': {
        id: 'BU112233', name: 'Bob User', age: 71, sex: 'Male', dob: '1955-11-03',
        email: 'bob.user@email.com', phone: '+1 (555) 345-6789', bloodType: 'B-',
        address: '305 Pine Lane, Evanston, IL 60201',
        emergencyContact: { name: 'Susan User', relation: 'Daughter', phone: '+1 (555) 345-6790' },
        insurance: { provider: 'Medicare', policyNo: 'MC-1128374', group: 'N/A' },
        risk: 85, status: 'Critical', lastVisit: '2026-03-21',
        conditions: ['Congestive Heart Failure (NYHA Class III)', 'Atrial Fibrillation', 'Chronic Kidney Disease (Stage 3a)', 'COPD (Moderate)', 'Osteoarthritis'],
        allergies: ['ACE Inhibitors (cough)', 'Codeine'],
        medications: [
            { name: 'Losartan', dose: '100mg', freq: 'Once daily', purpose: 'Heart Failure / BP' },
            { name: 'Carvedilol', dose: '25mg', freq: 'Twice daily', purpose: 'Heart Failure' },
            { name: 'Furosemide', dose: '40mg', freq: 'Once daily', purpose: 'Fluid Retention' },
            { name: 'Apixaban', dose: '5mg', freq: 'Twice daily', purpose: 'AFib Anticoagulation' },
            { name: 'Tiotropium', dose: '18mcg', freq: 'Once daily (inhaler)', purpose: 'COPD' },
            { name: 'Albuterol', dose: '90mcg', freq: 'As needed', purpose: 'COPD Rescue Inhaler' },
        ],
        vitals: { bp: '156/96', heartRate: 98, temp: '98.8°F', weight: '215 lbs', height: '5\'8"', bmi: 32.7, spO2: '91%' },
        labResults: [
            { test: 'BNP', value: '820 pg/mL', range: '< 100 pg/mL', status: 'high', date: '2026-03-21' },
            { test: 'eGFR', value: '48 mL/min', range: '> 60 mL/min', status: 'high', date: '2026-03-21' },
            { test: 'Creatinine', value: '1.8 mg/dL', range: '0.7-1.3 mg/dL', status: 'high', date: '2026-03-21' },
            { test: 'Potassium', value: '5.2 mEq/L', range: '3.5-5.0 mEq/L', status: 'high', date: '2026-03-21' },
            { test: 'Sodium', value: '134 mEq/L', range: '136-145 mEq/L', status: 'high', date: '2026-03-21' },
            { test: 'Hemoglobin', value: '11.8 g/dL', range: '13.5-17.5 g/dL', status: 'high', date: '2026-03-21' },
            { test: 'INR', value: '2.4', range: '2.0-3.0', status: 'normal', date: '2026-03-21' },
        ],
        riskTrend: [
            { name: 'Jan', risk: 70 }, { name: 'Feb', risk: 72 }, { name: 'Mar', risk: 75 },
            { name: 'Apr', risk: 78 }, { name: 'May', risk: 80 }, { name: 'Jun', risk: 82 }, { name: 'Jul', risk: 85 },
        ],
        visitHistory: [
            { date: '2026-03-21', type: 'Urgent Visit', doctor: 'Dr. Smith', summary: 'Acute dyspnea and lower extremity edema. BNP significantly elevated. Furosemide IV bolus administered. Hospital admission discussed.' },
            { date: '2026-03-05', type: 'Follow-up', doctor: 'Dr. Smith', summary: 'Heart failure stable. Weight up 4 lbs. Diuretic adjusted.' },
            { date: '2026-01-22', type: 'Cardiology Consult', doctor: 'Dr. Jones', summary: 'Echo: EF 30%. Moderate mitral regurgitation. Discussed ICD placement.' },
            { date: '2025-11-10', type: 'ER Visit', doctor: 'Dr. Patel', summary: 'Presented with palpitations and SOB. Cardioverted from rapid AFib. Rate-control optimized.' },
        ],
        reports: [
            { id: 1, date: '2026-03-21', title: 'Acute Heart Failure Exacerbation', final_report: 'BNP 820, SpO2 91%, bilateral LE edema 3+. Acute-on-chronic HF exacerbation likely precipitated by dietary indiscretion and medication non-adherence. IV diuresis initiated. Monitor I&O, daily weights. Consider hospital admission if no improvement in 24h.', confidence_calibration: { overall_confidence: 91 } },
            { id: 2, date: '2026-01-22', title: 'Cardiac Function Review', final_report: 'Echocardiogram: LVEF 30% (previously 35%). Progressive systolic dysfunction. Moderate MR with dilated LA. Recommend cardiology referral for ICD evaluation and possible CRT-D.', confidence_calibration: { overall_confidence: 88 } },
            { id: 3, date: '2025-11-10', title: 'Atrial Fibrillation Episode', final_report: 'Presented with rapid AFib (ventricular rate 142). Successfully cardioverted to NSR. CHA₂DS₂-VASc score: 5. High stroke risk. Apixaban started. Amiodarone considered but deferred due to COPD.', confidence_calibration: { overall_confidence: 86 } },
        ],
        medicalHistory: 'Bob User is a 71-year-old male with complex multi-morbidity: CHF NYHA III (EF 30%), persistent AFib on anticoagulation, CKD 3a, moderate COPD (former smoker, 40 pack-year history, quit 2010). Extensive surgical history including CABG x3 (2018) and right knee replacement (2020). Family history: father died of stroke at 65, mother had diabetes. Currently lives alone; daughter checks in daily.',
    },
    'AW998877': {
        id: 'AW998877', name: 'Alice Wong', age: 28, sex: 'Female', dob: '1998-02-17',
        email: 'alice.w@email.com', phone: '+1 (555) 456-7890', bloodType: 'AB+',
        address: '1200 Lakeshore Dr, Unit 12C, Chicago, IL 60611',
        emergencyContact: { name: 'David Wong', relation: 'Father', phone: '+1 (555) 456-7891' },
        insurance: { provider: 'United Healthcare', policyNo: 'UH-7721599', group: 'GRP-33520' },
        risk: 25, status: 'Stable', lastVisit: '2026-03-10',
        conditions: ['Migraine with Aura', 'Mild Asthma (well-controlled)'],
        allergies: ['Shellfish'],
        medications: [
            { name: 'Sumatriptan', dose: '50mg', freq: 'As needed (onset of migraine)', purpose: 'Migraine Relief' },
            { name: 'Topiramate', dose: '25mg', freq: 'Once daily', purpose: 'Migraine Prevention' },
            { name: 'Montelukast', dose: '10mg', freq: 'Once daily', purpose: 'Asthma Maintenance' },
        ],
        vitals: { bp: '112/68', heartRate: 66, temp: '98.2°F', weight: '125 lbs', height: '5\'4"', bmi: 21.5, spO2: '99%' },
        labResults: [
            { test: 'CBC - WBC', value: '6.8 K/uL', range: '4.5-11.0 K/uL', status: 'normal', date: '2026-03-08' },
            { test: 'Hemoglobin', value: '14.0 g/dL', range: '12.0-15.5 g/dL', status: 'normal', date: '2026-03-08' },
            { test: 'TSH', value: '1.8 mIU/L', range: '0.4-4.0 mIU/L', status: 'normal', date: '2026-03-08' },
            { test: 'CMP - Glucose', value: '88 mg/dL', range: '70-100 mg/dL', status: 'normal', date: '2026-03-08' },
            { test: 'Magnesium', value: '2.0 mg/dL', range: '1.7-2.2 mg/dL', status: 'normal', date: '2026-03-08' },
        ],
        riskTrend: [
            { name: 'Jan', risk: 28 }, { name: 'Feb', risk: 30 }, { name: 'Mar', risk: 27 },
            { name: 'Apr', risk: 26 }, { name: 'May', risk: 25 }, { name: 'Jun', risk: 24 }, { name: 'Jul', risk: 25 },
        ],
        visitHistory: [
            { date: '2026-03-10', type: 'Follow-up', doctor: 'Dr. Jones', summary: 'Migraine frequency reduced from 8/month to 2/month on Topiramate. Excellent response.' },
            { date: '2025-11-20', type: 'Annual Physical', doctor: 'Dr. Jones', summary: 'Healthy exam. Asthma well-controlled, no exacerbations in 12 months. Migraine prophylaxis discussed.' },
        ],
        reports: [
            { id: 1, date: '2026-03-10', title: 'Migraine Management Review', final_report: 'Significant improvement with Topiramate 25mg daily. Migraine frequency reduced from 8 to 2 episodes per month. No visual aura episodes in 6 weeks. Mild paresthesias in fingertips (known side effect), tolerable. Continue current regimen.', confidence_calibration: { overall_confidence: 94 } },
        ],
        medicalHistory: 'Alice Wong is a 28-year-old female with migraine with aura (diagnosed 2022) and mild persistent asthma (diagnosed childhood). Migraine triggers identified: stress, menstrual cycle, bright lights. Asthma well-controlled with daily Montelukast; no ER visits or hospitalizations. No surgical history. Family history: mother has migraines. Non-smoker, social alcohol only. Active lifestyle (cycling, swimming).',
    },
};

export const getPatientProfile = async (patientId) => {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            const profile = mockPatientProfiles[patientId];
            if (profile) {
                resolve({ status: 'success', data: profile });
            } else {
                reject(new Error('Patient profile not found.'));
            }
        }, 600);
    });
};

export const chatWithAI = async (message, patientId) => {
    try {
        // Send as JSON body instead of query params
        const res = await api.post('/chat/', {
            message: message,
            patient_id: patientId ? parseInt(patientId) : null
        });
        return res;
    } catch (e) {
        console.warn('Chat API failed, returning error:', e.message);
        return {
            data: {
                reply: "I'm having trouble connecting to the AI backend. Please ensure the server is running.",
                route: "error"
            }
        };
    }
};

export default api;
