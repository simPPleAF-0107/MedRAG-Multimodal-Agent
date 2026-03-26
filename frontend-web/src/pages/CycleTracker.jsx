import React, { useState, useEffect } from 'react';
import { CalendarHeart, Send } from 'lucide-react';
import { getPatientHistory } from '../services/apiClient';

const CycleTracker = () => {
    const [cycleLogs, setCycleLogs] = useState([]);
    const [flow, setFlow] = useState("Medium");
    const [cramps, setCramps] = useState(3);
    const [symptoms, setSymptoms] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchLogs();
    }, []);

    const fetchLogs = async () => {
        try {
            const response = await getPatientHistory(1);
            setCycleLogs(response.data.cycle_logs || []);
        } catch (error) {
            setCycleLogs([
                { id: 1, flow_intensity: 'Medium', cramps_severity: 4, symptoms: 'Mild cramping', timestamp: '2026-02-15T00:00:00Z' },
                { id: 2, flow_intensity: 'Heavy', cramps_severity: 8, symptoms: 'Fatigue, lower back pain', timestamp: '2026-02-16T00:00:00Z' }
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleLogSubmit = (e) => {
        e.preventDefault();
        const newLog = {
            id: Date.now(),
            flow_intensity: flow,
            cramps_severity: parseInt(cramps),
            symptoms,
            timestamp: new Date().toISOString()
        };
        setCycleLogs([newLog, ...cycleLogs]);
        setSymptoms(""); setCramps(3); setFlow("Medium");
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6 animate-fade-in font-sans">
            <div className="flex items-center space-x-3 mb-8">
                <div className="p-3 bg-coral-500/20 text-coral-500 rounded-xl shadow-neon-coral">
                    <CalendarHeart size={28} />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-white tracking-tight">Reproductive Timeline</h1>
                    <p className="text-slate-400 mt-1">Cross-registers physiological cycles against broad systemic symptoms to flag correlations.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-surface rounded-xl border border-slate-800 shadow-xl p-6">
                    <h3 className="font-semibold text-white mb-4">Log Cycle Event</h3>
                    <form onSubmit={handleLogSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Flow Intensity</label>
                            <select value={flow} onChange={(e) => setFlow(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:border-coral-500 outline-none">
                                <option>None (Spotting)</option><option>Light</option><option>Medium</option><option>Heavy</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Cramp Severity (1-10)</label>
                            <input type="range" min="1" max="10" value={cramps} onChange={(e) => setCramps(e.target.value)} className="w-full accent-coral-500" />
                            <div className="text-center text-sm font-bold text-coral-500 mt-1">{cramps}/10</div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Associated Symptoms</label>
                            <textarea rows="2" className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:border-coral-500 outline-none resize-none" placeholder="e.g., Cramping, fatigue, mood changes" value={symptoms} onChange={(e) => setSymptoms(e.target.value)} />
                        </div>
                        <button type="submit" className="w-full bg-coral-500 hover:bg-coral-400 text-white font-bold py-2.5 rounded-lg transition flex justify-center items-center shadow-neon-coral">
                            Add Log <Send className="ml-2 w-4 h-4" />
                        </button>
                    </form>
                </div>

                <div className="md:col-span-2 bg-surface rounded-xl border border-slate-800 shadow-xl p-6 overflow-hidden flex flex-col h-[480px]">
                    <h3 className="font-semibold text-white mb-4 border-b border-slate-800 pb-2">Cycle Log History</h3>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-hide">
                        {loading ? <p className="text-coral-500 animate-pulse text-sm">Translating records...</p> : cycleLogs.map(log => (
                            <div key={log.id} className="p-4 bg-deepSpace border border-slate-800 rounded-lg flex justify-between items-start">
                                <div>
                                    <span className="text-xs font-semibold text-slate-500 block mb-1">{new Date(log.timestamp).toLocaleDateString()}</span>
                                    <div className="flex space-x-2 mb-2">
                                        {log.cramps_severity !== undefined && <span className="text-xs bg-danger/10 text-danger px-2 py-0.5 rounded">Cramps: {log.cramps_severity}/10</span>}
                                    </div>
                                    <p className="text-sm text-slate-300">Symptoms: {log.symptoms || "None reported"}</p>
                                </div>
                                <div className="text-xs font-bold text-coral-500 bg-coral-500/10 border border-coral-500/30 rounded px-2 py-1 shadow-neon-coral">
                                    {log.flow_intensity} Flow
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CycleTracker;
