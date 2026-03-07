import axios from 'axios';

// Create a global Axios instance to point to the FastAPI backend
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    timeout: 60000, // 60 seconds (Large latency expected from heavy LLM calls)
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

// Specific API Functions as requested

export const generateReport = async (formData) => {
    return await api.post('/rag/generate-report', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
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
