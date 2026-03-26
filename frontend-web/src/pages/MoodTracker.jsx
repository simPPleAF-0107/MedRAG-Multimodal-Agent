import React, { useState, useEffect } from 'react';
import { Smile, Send } from 'lucide-react';
import { getPatientHistory } from '../services/apiClient';

const MoodTracker = () => {
    const [moodLogs, setMoodLogs] = useState([]);
    const [score, setScore] = useState(5);
    const [stress, setStress] = useState(5);
    const [sleep, setSleep] = useState("");
    const [notes, setNotes] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchLogs();
    }, []);

    const fetchLogs = async () => {
        try {
            const response = await getPatientHistory(1);
            setMoodLogs(response.data.mood_logs || []);
        } catch (error) {
            setMoodLogs([
                { id: 1, mood_score: 4, stress_level: 8, sleep_hours: 5, notes: 'Feeling a bit drained today.', timestamp: '2026-02-20T10:00:00Z' },
                { id: 2, mood_score: 7, stress_level: 3, sleep_hours: 8, notes: 'Better energy levels after rest.', timestamp: '2026-02-21T09:00:00Z' }
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleLogSubmit = (e) => {
        e.preventDefault();
        const newLog = {
            id: Date.now(),
            mood_score: parseInt(score),
            stress_level: parseInt(stress),
            sleep_hours: parseFloat(sleep || 0),
            notes,
            timestamp: new Date().toISOString()
        };
        setMoodLogs([newLog, ...moodLogs]);
        setScore(5); setStress(5); setSleep(""); setNotes("");
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6 animate-fade-in font-sans">
            <div className="flex items-center space-x-3 mb-8">
                <div className="p-3 bg-amber-500/20 text-amber-500 rounded-xl shadow-lg">
                    <Smile size={28} />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-white tracking-tight">Psychiatric Mood Correlator</h1>
                    <p className="text-slate-400 mt-1">Tracks subjective wellbeing against physiological data over time.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-surface rounded-xl border border-slate-800 shadow-xl p-6">
                    <h3 className="font-semibold text-white mb-4">Log Daily Metrics</h3>
                    <form onSubmit={handleLogSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Mood Score (1-10)</label>
                            <input type="range" min="1" max="10" value={score} onChange={(e) => setScore(e.target.value)} className="w-full accent-amber-500" />
                            <div className="text-center text-sm font-bold text-amber-500 mt-1">{score}/10</div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Stress Level (1-10)</label>
                            <input type="range" min="1" max="10" value={stress} onChange={(e) => setStress(e.target.value)} className="w-full accent-danger" />
                            <div className="text-center text-sm font-bold text-danger mt-1">{stress}/10</div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Sleep (Hours)</label>
                            <input type="number" step="0.5" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:border-amber-500 outline-none" placeholder="e.g. 7.5" value={sleep} onChange={(e) => setSleep(e.target.value)} />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Clinical Notes</label>
                            <textarea rows="2" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white focus:border-amber-500 outline-none resize-none" placeholder="Patient self-reported feelings..." value={notes} onChange={(e) => setNotes(e.target.value)} />
                        </div>
                        <button type="submit" className="w-full bg-amber-500 hover:bg-amber-400 text-deepSpace font-bold py-2.5 rounded-lg transition-colors flex justify-center items-center">
                            Save Log <Send className="ml-2 w-4 h-4" />
                        </button>
                    </form>
                </div>

                <div className="md:col-span-2 bg-surface rounded-xl border border-slate-800 shadow-xl p-6 overflow-hidden flex flex-col h-[480px]">
                    <h3 className="font-semibold text-white mb-4 border-b border-slate-800 pb-2">Recent Mood History</h3>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-hide">
                        {loading ? <p className="text-brand-500 animate-pulse text-sm">Translating records...</p> : moodLogs.map(log => (
                            <div key={log.id} className="p-4 bg-deepSpace border border-slate-800 rounded-lg flex justify-between items-start">
                                <div>
                                    <span className="text-xs font-semibold text-slate-500 block mb-1">{new Date(log.timestamp).toLocaleString()}</span>
                                    <div className="flex space-x-3 mb-2 text-xs">
                                        <span className="bg-amber-500/10 text-amber-500 px-2 py-1 rounded">Mood: {log.mood_score}/10</span>
                                        {log.stress_level && <span className="bg-danger/10 text-danger px-2 py-1 rounded">Stress: {log.stress_level}/10</span>}
                                        {log.sleep_hours && <span className="bg-brand-500/10 text-brand-500 px-2 py-1 rounded">Sleep: {log.sleep_hours}h</span>}
                                    </div>
                                    <p className="text-sm text-slate-300">{log.notes || "No notes provided."}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MoodTracker;
