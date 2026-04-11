import React, { useState, useEffect } from 'react';
import { CalendarHeart, Send, Sparkles, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { getPatientHistory, getTrackerSuggestion } from '../services/apiClient';
import toast from 'react-hot-toast';

const CycleTracker = () => {
    const [cycleLogs, setCycleLogs] = useState([]);
    const [flow, setFlow] = useState('Medium');
    const [cramps, setCramps] = useState(3);
    const [symptoms, setSymptoms] = useState('');
    const [loading, setLoading] = useState(true);
    const [aiSuggestion, setAiSuggestion] = useState('');
    const [aiLoading, setAiLoading] = useState(false);

    useEffect(() => { fetchLogs(); }, []);

    const fetchLogs = async () => {
        try {
            const response = await getPatientHistory(1);
            setCycleLogs(response.data.cycle_logs || []);
        } catch {
            setCycleLogs([
                { id: 1, flow_intensity: 'Medium', cramps_severity: 4, symptoms: 'Mild cramping', timestamp: '2026-02-15T00:00:00Z' },
                { id: 2, flow_intensity: 'Heavy', cramps_severity: 8, symptoms: 'Fatigue, lower back pain', timestamp: '2026-02-16T00:00:00Z' },
            ]);
        } finally { setLoading(false); }
    };

    const handleLogSubmit = (e) => {
        e.preventDefault();
        const newLog = { id: Date.now(), flow_intensity: flow, cramps_severity: parseInt(cramps), symptoms, timestamp: new Date().toISOString() };
        setCycleLogs([newLog, ...cycleLogs]);
        setSymptoms(''); setCramps(3); setFlow('Medium');
        toast.success('Cycle event logged!');
    };

    const handleAISuggest = async () => {
        setAiLoading(true);
        try {
            const result = await getTrackerSuggestion('cycle', cycleLogs.slice(0, 10));
            setAiSuggestion(result.suggestion || 'No insight available.');
        } catch { setAiSuggestion('Failed to generate insight.'); }
        setAiLoading(false);
    };

    const getFlowColor = (f) => {
        if (f === 'Heavy') return 'var(--error)';
        if (f === 'Medium') return 'var(--warning)';
        return 'var(--info)';
    };

    const getCrampBg = (s) => {
        if (s >= 7) return { bg: 'var(--error-bg)', color: 'var(--error)' };
        if (s >= 4) return { bg: 'var(--warning-bg)', color: '#B8860B' };
        return { bg: 'var(--success-bg)', color: 'var(--success)' };
    };

    return (
        <div className="max-w-6xl mx-auto space-y-6 animate-fade-up">
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                    <div className="p-3 rounded-xl" style={{ background: 'rgba(231,76,60,0.08)' }}>
                        <CalendarHeart size={24} style={{ color: 'var(--error)' }} />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Cycle Tracker</h1>
                        <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>Track your cycle and get AI-powered health insights</p>
                    </div>
                </div>
                <button onClick={handleAISuggest} disabled={aiLoading} className="btn-primary flex items-center gap-2 text-sm disabled:opacity-50">
                    {aiLoading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                    {aiLoading ? 'Analyzing...' : 'Cycle Insights'}
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Log Form */}
                <div className="bento-card p-6">
                    <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Log Cycle Event</h3>
                    <form onSubmit={handleLogSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Flow Intensity</label>
                            <select value={flow} onChange={(e) => setFlow(e.target.value)} className="glass-input">
                                <option>None (Spotting)</option><option>Light</option><option>Medium</option><option>Heavy</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Cramp Severity</label>
                            <input type="range" min="1" max="10" value={cramps} onChange={(e) => setCramps(e.target.value)} className="w-full" style={{ accentColor: getCrampBg(cramps).color }} />
                            <div className="text-center text-sm font-bold mt-1" style={{ color: getCrampBg(cramps).color }}>{cramps}/10</div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Symptoms</label>
                            <textarea rows="2" className="glass-input resize-none" placeholder="e.g., cramping, fatigue, mood changes" value={symptoms} onChange={(e) => setSymptoms(e.target.value)} />
                        </div>
                        <button type="submit" className="btn-primary w-full flex justify-center items-center">
                            Add Log <Send className="ml-2 w-4 h-4" />
                        </button>
                    </form>
                </div>

                {/* Cycle Log History */}
                <div className="lg:col-span-2 bento-card p-6 flex flex-col" style={{ maxHeight: 520 }}>
                    <h3 className="font-semibold mb-4 pb-2" style={{ color: 'var(--text-primary)', borderBottom: '1px solid var(--border)' }}>Cycle History</h3>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-1">
                        {loading ? (
                            <p className="text-sm animate-pulse" style={{ color: 'var(--error)' }}>Loading logs...</p>
                        ) : cycleLogs.map(log => (
                            <div key={log.id} className="p-4 rounded-xl flex justify-between items-start"
                                style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}>
                                <div>
                                    <span className="text-xs font-semibold block mb-1" style={{ color: 'var(--text-muted)' }}>{new Date(log.timestamp).toLocaleDateString()}</span>
                                    <div className="flex flex-wrap gap-2 mb-2">
                                        {log.cramps_severity !== undefined && (
                                            <span className="text-xs px-2 py-0.5 rounded" style={{ background: getCrampBg(log.cramps_severity).bg, color: getCrampBg(log.cramps_severity).color }}>
                                                Cramps: {log.cramps_severity}/10
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Symptoms: {log.symptoms || 'None reported'}</p>
                                </div>
                                <div className="text-xs font-bold px-2 py-1 rounded" style={{ color: getFlowColor(log.flow_intensity), background: getFlowColor(log.flow_intensity) + '12', border: `1px solid ${getFlowColor(log.flow_intensity)}30` }}>
                                    {log.flow_intensity} Flow
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* AI Panel */}
            <AnimatePresence>
                {aiSuggestion && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="ai-panel">
                        <div className="ai-panel-header"><Sparkles size={16} /> AI Cycle Insights</div>
                        <div className="prose prose-sm max-w-none" style={{ color: 'var(--text-secondary)' }}>
                            {aiSuggestion.split('\n').map((line, i) => {
                                if (line.startsWith('## ')) return <h2 key={i} className="text-lg font-bold mt-4 mb-2" style={{ color: 'var(--text-primary)' }}>{line.replace('## ', '')}</h2>;
                                if (line.startsWith('### ')) return <h3 key={i} className="text-base font-semibold mt-3 mb-1" style={{ color: 'var(--primary)' }}>{line.replace('### ', '')}</h3>;
                                if (line.startsWith('- ')) return <p key={i} className="ml-4 mb-0.5">• {line.replace('- ', '')}</p>;
                                if (line.trim() === '') return <br key={i} />;
                                return <p key={i} className="mb-1">{line}</p>;
                            })}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default CycleTracker;
