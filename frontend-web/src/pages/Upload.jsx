import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Image as ImageIcon, FileText, Mic, Brain, ChevronRight, Stethoscope
} from 'lucide-react';
import { generateReport } from '../services/apiClient';
import ScanningCard from '../components/ScanningCard';
import { motion, AnimatePresence } from 'framer-motion';

// ── Step indicator ────────────────────────────────────────────────────────
const Step = ({ n, label, active, done }) => (
    <div className="flex items-center gap-2" style={{ color: active || done ? 'var(--text-primary)' : 'var(--text-muted)' }}>
        <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
            style={done
                ? { background: 'var(--success)', color: '#fff' }
                : active
                    ? { color: 'var(--primary)', border: '2px solid var(--primary)' }
                    : { border: '1px solid var(--border)', color: 'var(--text-muted)' }}>
            {done ? '✓' : n}
        </div>
        <span className={`text-xs font-medium hidden sm:block`}
            style={{ color: active ? 'var(--text-primary)' : done ? 'var(--success)' : 'var(--text-muted)' }}>{label}</span>
    </div>
);

const Divider = ({ active }) => (
    <div className="flex-1 h-px mx-2" style={{ background: active ? 'var(--primary)' : 'var(--border)' }} />
);

// ── Upload page ───────────────────────────────────────────────────────────
const Upload = () => {
    const navigate = useNavigate();
    const [files, setFiles]       = useState([]);
    const [symptoms, setSymptoms] = useState('');
    const [loading, setLoading]   = useState(false);
    const [step, setStep]         = useState(1);

    const addFile = (f) => {
        if (!f) return;
        const arr = Array.isArray(f) ? f : [f];
        setFiles(prev => [...prev, ...arr]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!symptoms.trim() && files.length === 0) return;
        setLoading(true);
        setStep(2);
        try {
            const formData = new FormData();
            formData.append('query', symptoms || 'Analyze the provided clinical context.');
            files.forEach(f => formData.append('files', f));
            const res = await generateReport(formData);
            localStorage.setItem('lastReport', JSON.stringify(res.data));
            setStep(3);
            setTimeout(() => navigate('/reports'), 1200);
        } catch (err) {
            console.error('Pipeline failed:', err);
            alert('Pipeline execution failed. Ensure the backend is running.');
            setLoading(false);
            setStep(1);
        }
    };

    return (
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }} className="max-w-4xl mx-auto pb-12">

            {/* Header */}
            <div className="mb-8">
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2.5 rounded-xl" style={{ background: 'rgba(58,12,163,0.08)', border: '1px solid rgba(58,12,163,0.15)' }}>
                        <Stethoscope size={20} style={{ color: 'var(--primary)' }} />
                    </div>
                    <h1 className="heading-lg">Diagnostic Inference Engine</h1>
                </div>
                <p className="text-sm ml-14" style={{ color: 'var(--text-muted)' }}>
                    Upload multimodal clinical evidence to trigger the MedRAG pipeline.
                </p>
            </div>

            {/* Step tracker */}
            <div className="flex items-center mb-8 px-1">
                <Step n={1} label="Input Evidence" active={step === 1} done={step > 1} />
                <Divider active={step >= 2} />
                <Step n={2} label="Engine Analysis" active={step === 2} done={step > 2} />
                <Divider active={step >= 3} />
                <Step n={3} label="Diagnosis" active={step === 3} done={step > 3} />
            </div>

            <AnimatePresence mode="wait">
                {step === 1 && (
                    <motion.form key="step1" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }} transition={{ type: 'spring', stiffness: 300, damping: 28 }}
                        onSubmit={handleSubmit} className="space-y-6">

                        <div>
                            <p className="label-caps mb-3">Multimodal Evidence Input</p>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <ScanningCard icon={<ImageIcon />} title="Medical Imaging" subtitle="X-Ray, MRI, CT scans"
                                    accept="image/*" accentColor="var(--primary)" onFile={addFile} multiple />
                                <ScanningCard icon={<FileText />} title="EHR / Lab Reports" subtitle="PDF, lab results, notes"
                                    accept=".pdf,.txt,.doc,.docx" accentColor="var(--success)" onFile={addFile} multiple />
                                <ScanningCard icon={<Mic />} title="Voice Consultation" subtitle="MP3, WAV audio notes"
                                    accept=".mp3,.wav,.ogg,.m4a" accentColor="var(--warning)" onFile={addFile} />
                            </div>
                        </div>

                        <div>
                            <p className="label-caps mb-2">Clinical Observations</p>
                            <div className="relative">
                                <textarea required={files.length === 0} rows={4}
                                    placeholder="e.g. Patient presents with sharp lower right quadrant pain, fever of 101.2°F, elevated WBC..."
                                    className="glass-input resize-none w-full text-sm leading-relaxed"
                                    value={symptoms} onChange={e => setSymptoms(e.target.value)} />
                                <span className="absolute bottom-3 right-3 text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>
                                    {symptoms.length} chars
                                </span>
                            </div>
                            <p className="text-xs mt-1.5" style={{ color: 'var(--text-muted)' }}>
                                Include vitals, chief complaint, relevant physician notes, or lab values.
                            </p>
                        </div>

                        {files.length > 0 && (
                            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="flex flex-wrap gap-2">
                                <span className="label-caps w-full mb-1">Attached ({files.length})</span>
                                {files.map((f, i) => (<span key={i} className="entity-chip text-[11px]">{f.name}</span>))}
                            </motion.div>
                        )}

                        <div className="flex justify-end pt-2">
                            <motion.button type="submit" disabled={loading || (!symptoms.trim() && files.length === 0)}
                                whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                                className="btn-primary flex items-center gap-2 disabled:opacity-40 disabled:pointer-events-none">
                                <Brain size={16} /> Execute Pipeline <ChevronRight size={15} />
                            </motion.button>
                        </div>
                    </motion.form>
                )}

                {step === 2 && (
                    <motion.div key="step2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        className="flex flex-col items-center justify-center py-24 gap-6">
                        <div className="relative w-24 h-24">
                            <div className="absolute inset-0 rounded-full animate-ping opacity-20" style={{ background: 'var(--primary)' }} />
                            <div className="absolute inset-2 rounded-full animate-spin"
                                style={{ border: '2px solid transparent', borderTopColor: 'var(--primary)', borderRightColor: 'var(--success)' }} />
                            <div className="absolute inset-0 flex items-center justify-center">
                                <Brain size={32} className="animate-pulse" style={{ color: 'var(--primary)' }} />
                            </div>
                        </div>
                        <div className="text-center">
                            <h3 className="font-bold text-xl mb-2" style={{ color: 'var(--text-primary)' }}>Analyzing Evidence…</h3>
                            <p className="text-sm max-w-xs" style={{ color: 'var(--text-muted)' }}>
                                MedRAG is retrieving knowledge graph relations, embedding vectors, and synthesizing the clinical report.
                            </p>
                        </div>
                        <div className="space-y-2 text-left w-64">
                            {['Hybrid retrieval (dense + BM25)', 'LLM reranking & deduplication', 'GraphRAG subgraph fusion', 'Reasoning agent synthesis', 'Hallucination verification'].map((s, i) => (
                                <motion.div key={s} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: i * 0.4 }} className="flex items-center gap-2 text-xs" style={{ color: 'var(--text-muted)' }}>
                                    <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: 'var(--primary)', animationDelay: `${i * 0.1}s` }} />
                                    {s}
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                )}

                {step === 3 && (
                    <motion.div key="step3" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
                        transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                        className="flex flex-col items-center py-24 gap-4">
                        <div className="w-16 h-16 rounded-full flex items-center justify-center"
                            style={{ background: 'var(--success-bg)', border: '2px solid var(--success)' }}>
                            <span className="text-2xl">✓</span>
                        </div>
                        <p className="font-bold text-lg" style={{ color: 'var(--success)' }}>Diagnosis Complete</p>
                        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Redirecting to your report…</p>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

export default Upload;
