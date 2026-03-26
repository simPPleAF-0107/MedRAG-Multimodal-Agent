import React, { useState, useEffect } from 'react';
import { Activity, Send } from 'lucide-react';
import { getPatientHistory } from '../services/apiClient';

const ActivityPage = () => {
    const [activityLogs, setActivityLogs] = useState([]);
    const [type, setType] = useState("Walking");
    const [duration, setDuration] = useState("");
    const [heartRate, setHeartRate] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchLogs();
    }, []);

    const fetchLogs = async () => {
        try {
            const response = await getPatientHistory(1);
            setActivityLogs(response.data.activity_logs || []);
        } catch (error) {
            setActivityLogs([
                { id: 1, activity_type: 'Physical Therapy', duration_minutes: 30, avg_bpm: 110, timestamp: '2026-02-21T08:00:00Z' },
                { id: 2, activity_type: 'Walking', duration_minutes: 15, avg_bpm: 95, timestamp: '2026-02-20T16:00:00Z' }
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleLogSubmit = (e) => {
        e.preventDefault();
        if (!duration) return;
        const newLog = {
            id: Date.now(),
            activity_type: type,
            duration_minutes: parseInt(duration),
            avg_bpm: heartRate ? parseInt(heartRate) : null,
            timestamp: new Date().toISOString()
        };
        setActivityLogs([newLog, ...activityLogs]);
        setDuration(""); setHeartRate("");
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6 animate-fade-in font-sans">
            <div className="flex items-center space-x-3 mb-8">
                <div className="p-3 bg-brand-500/20 text-brand-500 rounded-xl shadow-neon">
                    <Activity size={28} />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-white tracking-tight">Activity Therapy Routing</h1>
                    <p className="text-slate-400 mt-1">Logs physical rehabilitation output based on engine-directed limits.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-surface rounded-xl border border-slate-800 shadow-xl p-6">
                    <h3 className="font-semibold text-white mb-4">Log Output</h3>
                    <form onSubmit={handleLogSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Activity Type</label>
                            <select value={type} onChange={(e) => setType(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:border-brand-500 outline-none">
                                <option>Walking</option><option>Physical Therapy</option><option>Stationary Bike</option><option>Swimming</option><option>Stretching</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Duration (minutes)</label>
                            <input type="number" min="1" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:border-brand-500 outline-none" placeholder="e.g. 30" value={duration} onChange={(e) => setDuration(e.target.value)} />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Avg Heart Rate (BPM)</label>
                            <input type="number" min="40" max="220" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:border-brand-500 outline-none" placeholder="Optional" value={heartRate} onChange={(e) => setHeartRate(e.target.value)} />
                        </div>
                        <button type="submit" disabled={!duration} className="w-full bg-brand-500 hover:bg-brand-400 text-deepSpace font-bold py-2.5 rounded-lg transition flex justify-center items-center disabled:opacity-50">
                            Save Log <Send className="ml-2 w-4 h-4" />
                        </button>
                    </form>
                </div>

                <div className="md:col-span-2 bg-surface rounded-xl border border-slate-800 shadow-xl p-6 overflow-hidden flex flex-col h-[400px]">
                    <h3 className="font-semibold text-white mb-4 border-b border-slate-800 pb-2">Recent Activities</h3>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-hide">
                        {loading ? <p className="text-brand-500 animate-pulse text-sm">Translating records...</p> : activityLogs.map(log => (
                            <div key={log.id} className="p-4 bg-deepSpace border border-slate-800 rounded-lg flex justify-between items-center">
                                <div>
                                    <span className="text-sm font-bold text-white block">{log.activity_type}</span>
                                    <span className="text-xs text-slate-500">{new Date(log.timestamp).toLocaleString()}</span>
                                    {log.avg_bpm && <span className="ml-3 text-xs text-coral-500 border border-coral-500/30 bg-coral-500/10 px-2 py-0.5 rounded">♥ {log.avg_bpm} BPM</span>}
                                </div>
                                <div className="text-sm font-bold text-brand-500 bg-brand-500/10 px-3 py-1 rounded-md border border-brand-500/30 shadow-neon">
                                    {log.duration_minutes} min
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ActivityPage;
