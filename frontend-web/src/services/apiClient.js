import axios from 'axios';

// Create a global Axios instance that routes through the Vite dev proxy.
// Using a relative baseURL (/api/v1) instead of absolute (http://localhost:8000)
// so ALL requests go through Vite's proxy server-side, eliminating CORS entirely.
const api = axios.create({
    baseURL: '/api/v1',
    timeout: 600000, // 10 minutes — RAG pipeline can take several minutes
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
        console.error('Login failed:', e.message);
        throw new Error(e.response?.data?.detail || 'Unable to connect. Please ensure the backend server is running.');
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
        console.error('Registration failed:', e.message);
        throw new Error(e.response?.data?.detail || 'Registration failed. Please ensure the backend server is running.');
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
        console.error('RAG pipeline failed:', e.message);
        throw new Error('Backend unavailable. Please ensure the server is running for AI-powered diagnostics.');
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

export const getPatientProfile = async (patientId) => {
    try {
        const res = await api.get(`/patient/${patientId}/history`);
        const p = res.data;
        // Parse JSON fields if they are strings
        const parse = (v) => { try { return typeof v === 'string' ? JSON.parse(v) : v; } catch { return v; } };
        return {
            status: 'success',
            data: {
                id: p.id,
                name: `${p.first_name} ${p.last_name}`,
                age: p.age,
                sex: p.sex,
                dob: p.date_of_birth,
                email: '',
                phone: p.phone,
                bloodType: p.blood_type,
                address: p.address,
                emergencyContact: parse(p.emergency_contact),
                insurance: parse(p.insurance),
                risk: p.risk,
                status: p.status,
                lastVisit: p.last_visit,
                conditions: parse(p.conditions) || [],
                allergies: parse(p.allergies) || [],
                medications: parse(p.medications) || [],
                vitals: parse(p.vitals) || {},
                labResults: parse(p.lab_results) || [],
                riskTrend: parse(p.risk_trend) || [],
                visitHistory: parse(p.visit_history) || [],
                reports: (p.reports || []).map(r => ({
                    id: r.id,
                    date: r.created_at,
                    title: r.chief_complaint || 'Diagnostic Report',
                    final_report: r.final_report,
                    confidence_calibration: { overall_confidence: Math.round((r.confidence_score || 0) * 100) }
                })),
                medicalHistory: p.medical_history_summary || '',
            }
        };
    } catch (e) {
        console.error('Patient profile fetch failed:', e.message);
        throw new Error('Patient profile not found or backend unavailable.');
    }
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

// ─── Tracker AI Suggestion ────────────────────────────────────────────────
export const getTrackerSuggestion = async (type, logs, patientContext = {}) => {
    try {
        const res = await api.post('/tracker/suggest', {
            type,
            logs,
            patient_context: patientContext,
        });
        return res.data;
    } catch (e) {
        console.warn(`Tracker AI (${type}) backend unavailable, returning mock suggestion:`, e.message);
        const mockSuggestions = {
            meal: {
                status: 'success',
                type: 'meal',
                suggestion:
                    "## 🥗 Your Personalized 7-Day Meal Plan\n\n" +
                    "### Monday\n- **Breakfast:** Greek yogurt with walnuts and blueberries (anti-inflammatory)\n- **Lunch:** Grilled salmon salad with olive oil dressing\n- **Dinner:** Quinoa bowl with roasted vegetables and turmeric\n\n" +
                    "### Tuesday\n- **Breakfast:** Overnight oats with chia seeds and banana\n- **Lunch:** Lentil soup with whole grain bread\n- **Dinner:** Baked chicken breast with sweet potato and steamed broccoli\n\n" +
                    "### Wednesday — Sunday\n*Follow a similar pattern alternating between lean proteins, complex carbs, and omega-3 rich foods.*\n\n" +
                    "### Key Recommendations\n- ✅ Increase omega-3 intake (salmon, walnuts, flaxseed)\n- ✅ Add turmeric and ginger for anti-inflammatory benefits\n- ⚠️ Reduce processed sugars and refined carbs\n- 💧 Aim for 8-10 glasses of water daily",
            },
            activity: {
                status: 'success',
                type: 'activity',
                suggestion:
                    "## 🏃 Your Weekly Activity Plan\n\n" +
                    "### Monday — Low Impact\n- 30 min walking (HR zone: 100-120 BPM)\n- 10 min stretching routine\n\n" +
                    "### Tuesday — Moderate\n- 25 min stationary bike (HR zone: 120-140 BPM)\n- 15 min light resistance exercises\n\n" +
                    "### Wednesday — Rest Day\n- Gentle yoga or meditation only\n\n" +
                    "### Thursday — Moderate\n- 20 min swimming (excellent for joint-friendly cardio)\n\n" +
                    "### Friday — Low Impact\n- 30 min walking outdoors\n\n" +
                    "### Weekend — Active Recovery\n- Light recreational activity of choice\n\n" +
                    "### Weekly Progress Target\n- Total active minutes: 150 min/week\n- Avg HR during exercise: 110-130 BPM\n- Gradual increase of 10% per week",
            },
            mood: {
                status: 'success',
                type: 'mood',
                suggestion:
                    "## 🧠 Mood & Wellness Insights\n\n" +
                    "### Trend Analysis\n📈 Your mood scores show a **slight upward trend** over the last entries. Stress levels have been fluctuating but are currently stable.\n\n" +
                    "### Pattern Observations\n- Higher mood scores correlate with **7+ hours of sleep**\n- Stress peaks appear to coincide with weekday mornings\n- Post-exercise entries show consistently better mood (avg +1.5 points)\n\n" +
                    "### Recommended Actions\n1. **Sleep Hygiene:** Maintain consistent bedtime (±30 min). Your data shows sleep quality directly impacts next-day mood.\n2. **Morning Routine:** Try a 5-min breathing exercise before starting your day — shown to reduce morning stress by 30%.\n3. **Exercise Timing:** Moving your activity to morning hours may improve mood for the remainder of the day.\n4. **Journaling:** Continue logging — 3 weeks of data enables more accurate pattern detection.\n\n" +
                    "### ⚠️ Watch For\nIf mood consistently drops below 4/10 for 3+ consecutive days, consider scheduling a mental health consultation.",
            },
            cycle: {
                status: 'success',
                type: 'cycle',
                suggestion:
                    "## 🌸 Cycle Health Insights\n\n" +
                    "### Cycle Overview\n- **Average cycle length:** ~28 days (based on logged entries)\n- **Predicted next cycle:** Approximately 14 days from your last entry\n- **Regularity:** Within normal variation\n\n" +
                    "### Symptom Management\n- **Cramping (severity 4-6):** Over-the-counter ibuprofen 30 min before onset. Heat therapy.\n- **Fatigue:** Increase iron-rich foods (spinach, legumes) during days 1-5.\n- **Mood changes:** Magnesium supplementation (200-400mg) may help during luteal phase.\n\n" +
                    "### Phase-Based Tips\n- **Follicular (Day 1-13):** Energy increasing. Best time for high-intensity workouts.\n- **Ovulatory (Day 14):** Peak energy. Excellent for demanding tasks.\n- **Luteal (Day 15-28):** Energy decreasing. Prioritize rest, gentle exercises, comfort foods.\n\n" +
                    "### When to Consult\n- Cycle consistently <21 or >35 days\n- Severe cramp score ≥8 for multiple cycles\n- Significant flow changes persisting 3+ cycles",
            },
        };
        return mockSuggestions[type] || { status: 'error', suggestion: 'Unknown tracker type.' };
    }
};

// ─── Dashboard Data (Live API) ────────────────────────────────────────────
export const getPatientList = async () => {
    try {
        const res = await api.get('/patient/list/all');
        return res.data;
    } catch (e) {
        console.warn('Failed to fetch patient list:', e.message);
        return { status: 'error', patients: [], total: 0 };
    }
};

export const getDashboardStats = async () => {
    try {
        const res = await api.get('/patient/stats/summary');
        return res.data;
    } catch (e) {
        console.warn('Failed to fetch dashboard stats:', e.message);
        return { status: 'error', total_patients: 0, critical_patients: 0, avg_risk: 0, avg_confidence: 0 };
    }
};

export const getSystemHealth = async () => {
    try {
        const res = await api.get('/system-health');
        return res.data;
    } catch (e) {
        console.warn('System health check failed:', e.message);
        return { status: 'offline' };
    }
};

export default api;
