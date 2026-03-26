import axios from 'axios';

// Create a global Axios instance to point to the FastAPI backend
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    timeout: 60000, 
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor for catching global errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error("API Error Response:", error.response);
        return Promise.reject(error);
    }
);

// --- MOCK DATABASE ---
const mockDoctors = [
    { identifier: 'dr.smith@medrag.com', password: 'password123', name: 'Dr. Smith', id: 'd1', role: 'doctor' },
    { identifier: 'dr.jones@medrag.com', password: 'password123', name: 'Dr. Jones', id: 'd2', role: 'doctor' },
    { identifier: '1234567890', password: 'password123', name: 'Dr. Patel', id: 'd3', role: 'doctor' },
];

const mockPatients = [
    { identifier: 'john.doe@email.com', password: 'password123', name: 'John Doe', id: 'JD123456', role: 'patient' },
    { identifier: 'jane.smith@email.com', password: 'password123', name: 'Jane Smith', id: 'JS654321', role: 'patient' },
    { identifier: '0987654321', password: 'password123', name: 'Bob User', id: 'BU112233', role: 'patient' },
    { identifier: 'alice.w@email.com', password: 'password123', name: 'Alice Wong', id: 'AW998877', role: 'patient' },
];

// --- AUTHENTICATION ---
export const loginUser = async (identifier, password, role) => {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (role === 'doctor') {
                const doc = mockDoctors.find(u => u.identifier === identifier);
                if (!doc) return reject(new Error('Doctor profile not found.'));
                if (doc.password !== password) return reject(new Error('Wrong credentials for Doctor.'));
                resolve({ status: 'success', user_id: doc.id, email: doc.identifier, name: doc.name, role });
            } else {
                const pat = mockPatients.find(u => u.identifier === identifier);
                if (!pat) return reject(new Error('Patient not found.'));
                if (pat.password !== password) return reject(new Error('Wrong credentials for Patient.'));
                resolve({ status: 'success', user_id: pat.id, email: pat.identifier, name: pat.name, role });
            }
        }, 800);
    });
};

export const registerPatient = async (patientData) => {
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
                role: 'patient'
            });
        }, 1500);
    });
};

// --- RAG PIPELINE ---
export const generateReport = async (formData) => {
    try {
        const res = await api.post('/rag/generate-report', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
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
    return await api.post('/upload/record', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
};

export const getPatientHistory = async (patientId) => {
    return await api.get(`/patient/${patientId}/history`);
};

export const chatWithAI = async (message, patientId) => {
    return await api.post(`/chat/?message=${encodeURIComponent(message)}&patient_id=${patientId}`);
};

export default api;
