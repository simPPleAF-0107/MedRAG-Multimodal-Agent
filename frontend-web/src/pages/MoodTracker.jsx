import React, { useState, useEffect } from 'react';
import { Smile, Send, Sparkles, Loader2, Moon, Brain } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { getPatientHistory, getTrackerSuggestion } from '../services/apiClient';
import toast from 'react-hot-toast';

const MoodTracker = () => {
    const [moodLogs, setMoodLogs] = useState([]);
    const [score, setScore] = useState(5);
    const [stress, setStress] = useState(5);
    const [sleep, setSleep] = useState('');
    const [notes, setNotes] = useState('');
    const [loading, setLoading] = useState(true);
    const [aiSuggestion, setAiSuggestion] = useState('');
    const [aiLoading, setAiLoading] = useState(false);

    useEffect(() => { fetchLogs(); }, []);

    const fetchLogs = async () => {
        try {
            const response = await getPatientHistory(1);
            setMoodLogs(response.data.mood_logs || []);
        } catch {
            setMoodLogs([
                { id: 1, mood_score: 4, stress_level: 8, sleep_hours: 5, notes: 'Feeling a bit drained today.', timestamp: '2026-02-20T10:00:00Z' },
                { id: 2, mood_score: 7, stress_level: 3, sleep_hours: 8, notes: 'Better energy levels after rest.', timestamp: '2026-02-21T09:00:00Z' },
            ]);
        } finally { setLoading(false); }
    };

    const handleLogSubmit = (e) => {
        e.preventDefault();
        const newLog = { id: Date.now(), mood_score: parseInt(score), stress_level: parseInt(stress), sleep_hours: parseFloat(sleep || 0), notes, timestamp: new Date().toISOString() };
        setMoodLogs([newLog, ...moodLogs]);
        setScore(5); setStress(5); setSleep(''); setNotes('');
        toast.success('Mood logged!');
    };

    const handleAISuggest = async () => {
        setAiLoading(true);
        try {
            const result = await getTrackerSuggestion('mood', moodLogs.slice(0, 10));
            setAiSuggestion(result.suggestion || 'No insight available.');
        } catch { setAiSuggestion('Failed to generate insight.'); }
        setAiLoading(false);
    };

    const getMoodEmoji = (s) => {
        if (s >= 8) return '😄';
        if (s >= 6) return '🙂';
        if (s >= 4) return '😐';
        if (s >= 2) return '😔';
        return '😢';
    };

    const getMoodColor = (s) => {
        if (s >= 7) return 'var(--success)';
        if (s >= 4) return 'var(--warning)';
        return 'var(--error)';
    };

    return (
        <div className="max-w-6xl mx-auto space-y-6 animate-fade-up">
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                    <div className="p-3 rounded-xl" style={{ background: 'rgba(241,196,15,0.1)' }}>
                        <Brain size={24} style={{ color: 'var(--warning)' }} />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Mood & Wellness</h1>
                        <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>Track wellbeing and get AI-powered insights</p>
                    </div>
                </div>
                <button onClick={handleAISuggest} disabled={aiLoading} className="btn-primary flex items-center gap-2 text-sm disabled:opacity-50">
                    {aiLoading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                    {aiLoading ? 'Analyzing...' : 'Get AI Insights'}
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Log Form */}
                <div className="bento-card p-6">
                    <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Log Daily Metrics</h3>
                    <form onSubmit={handleLogSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Mood Score</label>
                            <input type="range" min="1" max="10" value={score} onChange={(e) => setScore(e.target.value)} className="w-full" style={{ accentColor: getMoodColor(score) }} />
                            <div className="text-center text-sm font-bold mt-1" style={{ color: getMoodColor(score) }}>{getMoodEmoji(score)} {score}/10</div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Stress Level</label>
                            <input type="range" min="1" max="10" value={stress} onChange={(e) => setStress(e.target.value)} className="w-full" style={{ accentColor: 'var(--error)' }} />
                            <div className="text-center text-sm font-bold mt-1" style={{ color: 'var(--error)' }}>{stress}/10</div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Sleep (Hours)</label>
                            <input type="number" step="0.5" className="glass-input" placeholder="e.g. 7.5" value={sleep} onChange={(e) => setSleep(e.target.value)} />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Notes</label>
                            <textarea rows="2" className="glass-input resize-none" placeholder="How are you feeling today?" value={notes} onChange={(e) => setNotes(e.target.value)} />
                        </div>
                        <button type="submit" className="btn-primary w-full flex justify-center items-center">
                            Save Log <Send className="ml-2 w-4 h-4" />
                        </button>
                    </form>
                </div>

                {/* Mood History */}
                <div className="lg:col-span-2 bento-card p-6 flex flex-col" style={{ maxHeight: 560 }}>
                    <h3 className="font-semibold mb-4 pb-2" style={{ color: 'var(--text-primary)', borderBottom: '1px solid var(--border)' }}>Mood History</h3>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-1">
                        {loading ? (
                            <p className="text-sm animate-pulse" style={{ color: 'var(--primary)' }}>Loading logs...</p>
                        ) : moodLogs.map(log => (
                            <div key={log.id} className="p-4 rounded-xl" style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}>
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-xs font-semibold" style={{ color: 'var(--text-muted)' }}>{new Date(log.timestamp).toLocaleString()}</span>
                                    <span className="text-lg">{getMoodEmoji(log.mood_score)}</span>
                                </div>
                                <div className="flex flex-wrap gap-2 mb-2">
                                    <span className="text-xs px-2 py-1 rounded" style={{ background: 'var(--warning-bg)', color: '#B8860B' }}>Mood: {log.mood_score}/10</span>
                                    {log.stress_level && <span className="text-xs px-2 py-1 rounded" style={{ background: 'var(--error-bg)', color: 'var(--error)' }}>Stress: {log.stress_level}/10</span>}
                                    {log.sleep_hours > 0 && (
                                        <span className="text-xs px-2 py-1 rounded inline-flex items-center gap-1" style={{ background: 'var(--info-bg)', color: 'var(--info)' }}>
                                            <Moon size={10} /> {log.sleep_hours}h
                                        </span>
                                    )}
                                </div>
                                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{log.notes || 'No notes provided.'}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* AI Panel */}
            <AnimatePresence>
                {aiSuggestion && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="ai-panel">
                        <div className="ai-panel-header"><Sparkles size={16} /> AI Wellness Insights</div>
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

export default MoodTracker;
