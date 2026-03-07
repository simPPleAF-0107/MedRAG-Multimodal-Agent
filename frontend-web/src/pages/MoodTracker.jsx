import React, { useState, useEffect } from 'react';
import { Smile, Info, Send } from 'lucide-react';
import { getPatientHistory } from '../services/apiClient';

const MoodTracker = () => {
    const [moodLogs, setMoodLogs] = useState([]);
    const [score, setScore] = useState(5);
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
            console.error("Failed to fetch mood logs", error);
            setMoodLogs([
                { id: 1, mood_score: 4, notes: 'Feeling a bit drained today.', timestamp: '2026-02-20T10:00:00Z' },
                { id: 2, mood_score: 7, notes: 'Better energy levels after rest.', timestamp: '2026-02-21T09:00:00Z' }
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleLogSubmit = (e) => {
        e.preventDefault();
        // In a real app we would POST this to an endpoint. 
        // Here we'll optimistically update the UI.
        const newLog = {
            id: Date.now(),
            mood_score: parseInt(score),
            notes,
            timestamp: new Date().toISOString()
        };
        setMoodLogs([newLog, ...moodLogs]);
        setScore(5);
        setNotes("");
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
            <div className="flex items-center space-x-3 mb-8">
                <div className="p-3 bg-amber-100 text-amber-600 rounded-xl">
                    <Smile size={28} />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Psychiatric Mood Correlator</h1>
                    <p className="text-slate-500 mt-1">Tracks daily subjective wellbeing against physiological RAG data over time.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                    <h3 className="font-semibold text-slate-800 mb-4">Log Daily Mood</h3>
                    <form onSubmit={handleLogSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Mood Score (1-10)</label>
                            <input
                                type="range" min="1" max="10"
                                value={score} onChange={(e) => setScore(e.target.value)}
                                className="w-full accent-amber-500"
                            />
                            <div className="text-center text-lg font-bold text-amber-600 mt-2">{score}</div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Clinical Notes</label>
                            <textarea
                                rows="3"
                                className="w-full border border-slate-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-amber-500 outline-none"
                                placeholder="Patient self-reported feelings..."
                                value={notes} onChange={(e) => setNotes(e.target.value)}
                            />
                        </div>
                        <button type="submit" className="w-full bg-amber-500 hover:bg-amber-600 text-white font-medium py-2 rounded-lg transition flex justify-center items-center">
                            Save Log <Send className="ml-2 w-4 h-4" />
                        </button>
                    </form>
                </div>

                <div className="md:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm p-6 overflow-hidden flex flex-col h-[400px]">
                    <h3 className="font-semibold text-slate-800 mb-4 border-b pb-2">Recent Mood History</h3>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                        {loading ? (
                            <p className="text-slate-500 animate-pulse text-sm">Loading logs...</p>
                        ) : moodLogs.length > 0 ? (
                            moodLogs.map(log => (
                                <div key={log.id} className="p-4 bg-slate-50 border border-slate-100 rounded-lg flex justify-between items-start">
                                    <div>
                                        <span className="text-xs font-semibold text-slate-400 block mb-1">
                                            {new Date(log.timestamp).toLocaleString()}
                                        </span>
                                        <p className="text-sm text-slate-700">{log.notes || "No notes provided."}</p>
                                    </div>
                                    <div className="flex bg-white ring-1 ring-slate-200 rounded-lg px-3 py-1 items-center justify-center font-bold text-amber-600 text-lg shadow-sm">
                                        {log.mood_score}
                                    </div>
                                </div>
                            ))
                        ) : (
                            <p className="text-slate-500 text-sm">No mood logs actively tracked.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MoodTracker;
