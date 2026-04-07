import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stethoscope, FileText, CheckCircle2, ChevronRight, Activity } from 'lucide-react';
import { generateReport } from '../services/apiClient';
import UploadBox from '../components/UploadBox';
import { motion } from 'framer-motion';

const Upload = () => {
    const navigate = useNavigate();
    const [files, setFiles] = useState([]);
    const [symptoms, setSymptoms] = useState("");
    const [loading, setLoading] = useState(false);
    const [step, setStep] = useState(1);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!symptoms.trim() && files.length === 0) return;

        setLoading(true);
        setStep(2); // Analyzing State

        try {
            const formData = new FormData();
            formData.append('query', symptoms || "Analyze the provided image context.");
            
            // Append multiple files natively
            files.forEach(f => {
                formData.append('files', f);
            });

            // Real API call to trigger report generation
            const res = await generateReport(formData);

            // Pass data to reports page via local storage or state management (using simple localStorage for prototype)
            localStorage.setItem('lastReport', JSON.stringify(res.data));

            setStep(3); // Complete State
            setTimeout(() => {
                navigate('/reports');
            }, 1000);

        } catch (error) {
            console.error("Pipeline Failed:", error);
            alert("Pipeline Execution Failed. Ensure backend is running.");
            setLoading(false);
            setStep(1);
        }
    };

    return (
        <div className="max-w-3xl mx-auto py-8 animate-fade-in">
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-white tracking-tight">Diagnostic Inference Engine</h1>
                <p className="text-slate-400 mt-2">Trigger the Multimodal RAG pipeline by providing clinical context below.</p>
            </div>

            <div className="glass-panel border border-white/10 overflow-hidden">

                {/* Progress Tracker */}
                <div className="bg-white/5 px-8 py-4 border-b border-white/10 flex items-center justify-between">
                    <div className={`flex items-center ${step >= 1 ? 'text-brand-500' : 'text-slate-500'}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${step >= 1 ? 'bg-brand-500/20 text-brand-400' : 'bg-white/10 text-slate-500'} mr-3`}>1</div>
                        <span className="font-medium text-sm">Input Pipeline</span>
                    </div>
                    <div className="flex-1 h-0.5 bg-white/10 mx-4">
                        <div className={`h-full bg-brand-500 transition-all ${step >= 2 ? 'w-full' : 'w-0'}`}></div>
                    </div>
                    <div className={`flex items-center ${step >= 2 ? 'text-brand-500' : 'text-slate-500'}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${step >= 2 ? 'bg-brand-500/20 text-brand-400' : 'bg-white/10 text-slate-500'} mr-3`}>2</div>
                        <span className="font-medium text-sm">Engine Analysis</span>
                    </div>
                    <div className="flex-1 h-0.5 bg-white/10 mx-4">
                        <div className={`h-full bg-brand-500 transition-all ${step >= 3 ? 'w-full' : 'w-0'}`}></div>
                    </div>
                    <div className={`flex items-center ${step >= 3 ? 'text-brand-500' : 'text-slate-500'}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${step >= 3 ? 'bg-brand-500/20 text-brand-400' : 'bg-white/10 text-slate-500'} mr-3`}>
                            {step >= 3 ? <CheckCircle2 size={16} /> : '3'}
                        </div>
                        <span className="font-medium text-sm">Diagnosis</span>
                    </div>
                </div>

                {step === 1 && (
                    <form onSubmit={handleSubmit} className="p-8 space-y-8">
                        {/* Symptom Text Input */}
                        <div>
                            <label className="flex flex-col">
                                <span className="text-sm font-semibold text-slate-300 flex items-center mb-1">
                                    <FileText className="w-4 h-4 mr-2 text-slate-500" />
                                    Clinical Observations
                                </span>
                                <span className="text-xs text-slate-500 mb-3">Include vitals, chief complaint, or relevant physician notes.</span>
                                <textarea
                                    required={files.length === 0}
                                    rows={4}
                                    placeholder="e.g. Patient presents with sharp lower right quadrant abdominal pain, fever of 101.2F, and elevated WBC."
                                    className="w-full p-3 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-brand-500 focus:border-brand-500 text-white placeholder-slate-500 transition-colors resize-none"
                                    value={symptoms}
                                    onChange={(e) => setSymptoms(e.target.value)}
                                />
                            </label>
                        </div>

                        {/* Media Upload */}
                        <div>
                            <span className="text-sm font-semibold text-slate-300 flex items-center mb-1">
                                <Stethoscope className="w-4 h-4 mr-2 text-slate-500" />
                                Multimodal Evidence (Optional)
                            </span>
                            <span className="text-xs text-slate-500 mb-3 block">Attach X-Rays, MRI scans, or PDF lab results.</span>
                            <UploadBox onFilesSelect={setFiles} />
                        </div>

                        <div className="pt-4 flex justify-end">
                            <button
                                type="submit"
                                disabled={loading || (files.length === 0 && !symptoms.trim())}
                                className="flex items-center px-6 py-3 bg-brand-600 hover:bg-brand-700 text-white rounded-xl font-medium shadow-md shadow-brand-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Execute Pipeline <ChevronRight className="ml-2 w-5 h-5" />
                            </button>
                        </div>
                    </form>
                )}

                {step === 2 && (
                    <div className="p-16 flex flex-col items-center justify-center text-center">
                        <div className="relative w-24 h-24 mb-8">
                            {/* Engine Pulse Animation */}
                            <div className="absolute inset-0 border-4 border-brand-500/20 rounded-full animate-ping opacity-75"></div>
                            <div className="absolute inset-2 border-4 border-brand-400 rounded-full animate-spin border-t-transparent shadow-lg shadow-brand-500/30"></div>
                            <div className="absolute inset-0 flex items-center justify-center text-brand-500">
                                <Activity size={32} />
                            </div>
                        </div>
                        <h3 className="text-xl font-bold text-white mb-2">Analyzing Vectors...</h3>
                        <p className="text-slate-400 max-w-sm">
                            MedRAG is concurrently compiling memory graph, retrieving evidence, and generating risk projections.
                        </p>
                    </div>
                )}

            </div>
        </div>
    );
};

export default Upload;
