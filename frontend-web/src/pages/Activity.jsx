import React, { useState, useEffect } from 'react';
import { Activity as ActivityIcon, Send, Sparkles, Loader2, Heart } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { getPatientHistory, getTrackerSuggestion } from '../services/apiClient';
import toast from 'react-hot-toast';

const ActivityPage = () => {
    const [activityLogs, setActivityLogs] = useState([]);
    const [type, setType] = useState('Walking');
    const [duration, setDuration] = useState('');
    const [heartRate, setHeartRate] = useState('');
    const [loading, setLoading] = useState(true);
    const [aiSuggestion, setAiSuggestion] = useState('');
    const [aiLoading, setAiLoading] = useState(false);

    useEffect(() => { fetchLogs(); }, []);

    const fetchLogs = async () => {
        try {
            const response = await getPatientHistory(1);
            setActivityLogs(response.data.activity_logs || []);
        } catch {
            setActivityLogs([
                { id: 1, activity_type: 'Physical Therapy', duration_minutes: 30, avg_bpm: 110, timestamp: '2026-02-21T08:00:00Z' },
                { id: 2, activity_type: 'Walking', duration_minutes: 15, avg_bpm: 95, timestamp: '2026-02-20T16:00:00Z' },
            ]);
        } finally { setLoading(false); }
    };

    const handleLogSubmit = (e) => {
        e.preventDefault();
        if (!duration) return;
        const newLog = { id: Date.now(), activity_type: type, duration_minutes: parseInt(duration), avg_bpm: heartRate ? parseInt(heartRate) : null, timestamp: new Date().toISOString() };
        setActivityLogs([newLog, ...activityLogs]);
        setDuration(''); setHeartRate('');
        toast.success('Activity logged!');
    };

    const handleAISuggest = async () => {
        setAiLoading(true);
        try {
            const result = await getTrackerSuggestion('activity', activityLogs.slice(0, 10));
            setAiSuggestion(result.suggestion || 'No suggestion available.');
        } catch { setAiSuggestion('Failed to generate suggestion.'); }
        setAiLoading(false);
    };

    // Weekly summary
    const totalMin = activityLogs.reduce((s, l) => s + (l.duration_minutes || 0), 0);
    const avgBpm = activityLogs.filter(l => l.avg_bpm).reduce((s, l, _, a) => s + l.avg_bpm / a.length, 0);

    return (
        <div className="max-w-6xl mx-auto space-y-6 animate-fade-up">
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                    <div className="p-3 rounded-xl" style={{ background: 'rgba(46,204,113,0.1)' }}>
                        <ActivityIcon size={24} style={{ color: 'var(--success)' }} />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>Activity Tracker</h1>
                        <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>Log workouts and get AI-powered activity plans</p>
                    </div>
                </div>
                <button onClick={handleAISuggest} disabled={aiLoading} className="btn-secondary flex items-center gap-2 text-sm disabled:opacity-50">
                    {aiLoading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                    {aiLoading ? 'Planning...' : 'Plan My Week'}
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
                <div className="bento-card p-4 text-center">
                    <p className="label-caps mb-1">Total Minutes</p>
                    <p className="text-2xl font-bold" style={{ color: 'var(--success)' }}>{totalMin}</p>
                </div>
                <div className="bento-card p-4 text-center">
                    <p className="label-caps mb-1">Sessions</p>
                    <p className="text-2xl font-bold" style={{ color: 'var(--secondary)' }}>{activityLogs.length}</p>
                </div>
                <div className="bento-card p-4 text-center">
                    <p className="label-caps mb-1">Avg HR</p>
                    <p className="text-2xl font-bold" style={{ color: 'var(--error)' }}>{avgBpm ? Math.round(avgBpm) : '—'}<span className="text-sm font-normal ml-1" style={{ color: 'var(--text-muted)' }}>BPM</span></p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Log Form */}
                <div className="bento-card p-6">
                    <h3 className="font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Log Activity</h3>
                    <form onSubmit={handleLogSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Activity Type</label>
                            <select value={type} onChange={(e) => setType(e.target.value)} className="glass-input">
                                <option>Walking</option><option>Physical Therapy</option><option>Stationary Bike</option><option>Swimming</option><option>Stretching</option><option>Yoga</option><option>Running</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Duration (minutes)</label>
                            <input type="number" min="1" className="glass-input" placeholder="e.g. 30" value={duration} onChange={(e) => setDuration(e.target.value)} />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Avg Heart Rate (BPM)</label>
                            <input type="number" min="40" max="220" className="glass-input" placeholder="Optional" value={heartRate} onChange={(e) => setHeartRate(e.target.value)} />
                        </div>
                        <button type="submit" disabled={!duration} className="btn-success w-full flex justify-center items-center text-white disabled:opacity-50">
                            Save Log <Send className="ml-2 w-4 h-4" />
                        </button>
                    </form>
                </div>

                {/* Activity History */}
                <div className="lg:col-span-2 bento-card p-6 flex flex-col" style={{ maxHeight: 480 }}>
                    <h3 className="font-semibold mb-4 pb-2" style={{ color: 'var(--text-primary)', borderBottom: '1px solid var(--border)' }}>Recent Activities</h3>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-1">
                        {loading ? (
                            <p className="text-sm animate-pulse" style={{ color: 'var(--success)' }}>Loading logs...</p>
                        ) : activityLogs.map(log => (
                            <div key={log.id} className="p-4 rounded-xl flex justify-between items-center"
                                style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}>
                                <div>
                                    <span className="text-sm font-bold block" style={{ color: 'var(--text-primary)' }}>{log.activity_type}</span>
                                    <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{new Date(log.timestamp).toLocaleString()}</span>
                                    {log.avg_bpm && (
                                        <span className="ml-3 text-xs px-2 py-0.5 rounded inline-flex items-center gap-1"
                                            style={{ background: 'var(--error-bg)', color: 'var(--error)', border: '1px solid rgba(231,76,60,0.2)' }}>
                                            <Heart size={10} /> {log.avg_bpm} BPM
                                        </span>
                                    )}
                                </div>
                                <div className="text-sm font-bold px-3 py-1 rounded-md" style={{ color: 'var(--success)', background: 'var(--success-bg)', border: '1px solid rgba(46,204,113,0.2)' }}>
                                    {log.duration_minutes} min
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
                        <div className="ai-panel-header"><Sparkles size={16} /> AI-Generated Weekly Plan</div>
                        <div className="prose prose-sm max-w-none" style={{ color: 'var(--text-secondary)' }}>
                            {aiSuggestion.split('\n').map((line, i) => {
                                if (line.startsWith('## ')) return <h2 key={i} className="text-lg font-bold mt-4 mb-2" style={{ color: 'var(--text-primary)' }}>{line.replace('## ', '')}</h2>;
                                if (line.startsWith('### ')) return <h3 key={i} className="text-base font-semibold mt-3 mb-1" style={{ color: 'var(--success)' }}>{line.replace('### ', '')}</h3>;
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

export default ActivityPage;
