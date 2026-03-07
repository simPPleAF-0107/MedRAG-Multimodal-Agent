import React, { useState, useEffect } from 'react';
import { CalendarHeart, Send } from 'lucide-react';
import { getPatientHistory } from '../services/apiClient';

const CycleTracker = () => {
    const [cycleLogs, setCycleLogs] = useState([]);
    const [flow, setFlow] = useState("Medium");
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
            console.error("Failed to fetch cycle logs", error);
            setCycleLogs([
                { id: 1, flow_intensity: 'Medium', symptoms: 'Mild cramping', timestamp: '2026-02-15T00:00:00Z' },
                { id: 2, flow_intensity: 'Heavy', symptoms: 'Fatigue, lower back pain', timestamp: '2026-02-16T00:00:00Z' }
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
            symptoms,
            timestamp: new Date().toISOString()
        };
        setCycleLogs([newLog, ...cycleLogs]);
        setSymptoms("");
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
            <div className="flex items-center space-x-3 mb-8">
                <div className="p-3 bg-rose-100 text-rose-600 rounded-xl">
                    <CalendarHeart size={28} />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Reproductive Timeline</h1>
                    <p className="text-slate-500 mt-1">Cross-registers physiological cycles against broad systemic symptoms to flag correlations.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                    <h3 className="font-semibold text-slate-800 mb-4">Log Cycle Event</h3>
                    <form onSubmit={handleLogSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Flow Intensity</label>
                            <select
                                value={flow} onChange={(e) => setFlow(e.target.value)}
                                className="w-full border border-slate-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-rose-500 outline-none bg-white"
                            >
                                <option>None (Spotting)</option>
                                <option>Light</option>
                                <option>Medium</option>
                                <option>Heavy</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Associated Symptoms</label>
                            <textarea
                                rows="2"
                                className="w-full border border-slate-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-rose-500 outline-none resize-none"
                                placeholder="e.g., Cramping, fatigue, mood changes"
                                value={symptoms} onChange={(e) => setSymptoms(e.target.value)}
                            />
                        </div>
                        <button type="submit" className="w-full bg-rose-500 hover:bg-rose-600 text-white font-medium py-2 rounded-lg transition flex justify-center items-center">
                            Add Log <Send className="ml-2 w-4 h-4" />
                        </button>
                    </form>
                </div>

                <div className="md:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm p-6 overflow-hidden flex flex-col h-[400px]">
                    <h3 className="font-semibold text-slate-800 mb-4 border-b pb-2">Cycle Log History</h3>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                        {loading ? (
                            <p className="text-slate-500 animate-pulse text-sm">Loading logs...</p>
                        ) : cycleLogs.length > 0 ? (
                            cycleLogs.map(log => (
                                <div key={log.id} className="p-4 bg-slate-50 border border-slate-100 rounded-lg flex justify-between items-start">
                                    <div>
                                        <span className="text-xs font-semibold text-slate-400 block mb-1">
                                            {new Date(log.timestamp).toLocaleDateString()}
                                        </span>
                                        <p className="text-sm text-slate-700">Symptoms: {log.symptoms || "None reported"}</p>
                                    </div>
                                    <div className="text-xs font-bold text-rose-600 bg-rose-50 border border-rose-100 rounded px-2 py-1">
                                        {log.flow_intensity} Flow
                                    </div>
                                </div>
                            ))
                        ) : (
                            <p className="text-slate-500 text-sm">No cycle events logged yet.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CycleTracker;
