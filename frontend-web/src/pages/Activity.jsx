import React, { useState, useEffect } from 'react';
import { Activity, Send } from 'lucide-react';
import { getPatientHistory } from '../services/apiClient';

const ActivityPage = () => {
    const [activityLogs, setActivityLogs] = useState([]);
    const [type, setType] = useState("Walking");
    const [duration, setDuration] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchLogs();
    }, []);

    const fetchLogs = async () => {
        try {
            const response = await getPatientHistory(1);
            setActivityLogs(response.data.activity_logs || []);
        } catch (error) {
            console.error("Failed to fetch activity logs", error);
            setActivityLogs([
                { id: 1, activity_type: 'Physical Therapy', duration_minutes: 30, timestamp: '2026-02-21T08:00:00Z' },
                { id: 2, activity_type: 'Walking', duration_minutes: 15, timestamp: '2026-02-20T16:00:00Z' }
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
            timestamp: new Date().toISOString()
        };
        setActivityLogs([newLog, ...activityLogs]);
        setDuration("");
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
            <div className="flex items-center space-x-3 mb-8">
                <div className="p-3 bg-blue-100 text-blue-600 rounded-xl">
                    <Activity size={28} />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Activity Therapy Routing</h1>
                    <p className="text-slate-500 mt-1">Logs physical rehabilitation output based on engine-directed limits.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                    <h3 className="font-semibold text-slate-800 mb-4">Log Rehabilitation</h3>
                    <form onSubmit={handleLogSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Activity Type</label>
                            <select
                                value={type} onChange={(e) => setType(e.target.value)}
                                className="w-full border border-slate-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none bg-white"
                            >
                                <option>Walking</option>
                                <option>Physical Therapy</option>
                                <option>Stationary Bike</option>
                                <option>Swimming</option>
                                <option>Stretching</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Duration (minutes)</label>
                            <input
                                type="number" min="1"
                                className="w-full border border-slate-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                                placeholder="e.g. 30"
                                value={duration} onChange={(e) => setDuration(e.target.value)}
                            />
                        </div>
                        <button type="submit" disabled={!duration} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition flex justify-center items-center disabled:opacity-50">
                            Save Log <Send className="ml-2 w-4 h-4" />
                        </button>
                    </form>
                </div>

                <div className="md:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm p-6 overflow-hidden flex flex-col h-[400px]">
                    <h3 className="font-semibold text-slate-800 mb-4 border-b pb-2">Recent Activities</h3>
                    <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                        {loading ? (
                            <p className="text-slate-500 animate-pulse text-sm">Loading logs...</p>
                        ) : activityLogs.length > 0 ? (
                            activityLogs.map(log => (
                                <div key={log.id} className="p-4 bg-slate-50 border border-slate-100 rounded-lg flex justify-between items-center">
                                    <div>
                                        <span className="text-sm font-semibold text-slate-800 block">{log.activity_type}</span>
                                        <span className="text-xs text-slate-400">
                                            {new Date(log.timestamp).toLocaleString()}
                                        </span>
                                    </div>
                                    <div className="text-sm font-bold text-blue-600 bg-blue-50 px-3 py-1 rounded-md border border-blue-100">
                                        {log.duration_minutes} min
                                    </div>
                                </div>
                            ))
                        ) : (
                            <p className="text-slate-500 text-sm">No activities logged yet.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ActivityPage;
