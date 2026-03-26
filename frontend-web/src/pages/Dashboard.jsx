import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, FileText, AlertTriangle, Activity as ActivityIcon, UserSquare2, ShieldAlert } from 'lucide-react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer
} from 'recharts';
import RiskScoreCard from '../components/RiskScoreCard';
import ReportCard from '../components/ReportCard';
import { getPatientHistory } from '../services/apiClient';

const stubTrends = [
    { name: 'Mon', risk: 45 }, { name: 'Tue', risk: 48 }, { name: 'Wed', risk: 52 },
    { name: 'Thu', risk: 58 }, { name: 'Fri', risk: 65 }, { name: 'Sat', risk: 72 }, { name: 'Sun', risk: 68 },
];

const mockPatientList = [
    { id: 'p1', name: 'John Doe', risk: 68, lastVisit: '2026-03-20', status: 'High Risk' },
    { id: 'p2', name: 'Jane Smith', risk: 42, lastVisit: '2026-03-15', status: 'Stable' },
    { id: 'p3', name: 'Bob User', risk: 85, lastVisit: '2026-03-21', status: 'Critical' },
    { id: 'p4', name: 'Alice Wong', risk: 25, lastVisit: '2026-03-10', status: 'Stable' },
];

const Dashboard = () => {
    const navigate = useNavigate();
    const [patientData, setPatientData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState(null);

    useEffect(() => {
        const stored = localStorage.getItem('user');
        if (stored) {
            setUser(JSON.parse(stored));
        } else {
            navigate('/login');
            return;
        }

        const fetchDashboardData = async () => {
            try {
                // Mock fetching taking a second
                setTimeout(() => {
                    setPatientData({
                        first_name: JSON.parse(stored).name.split(' ')[0],
                        last_name: JSON.parse(stored).name.split(' ')[1] || '',
                        medical_history_summary: "History of hypertension and recent reports indicating elevated inflammatory markers.",
                        reports: [
                            {
                                id: 1,
                                final_report: "Elevated CRP and localized joint pain. Potential onset of rheumatoid arthritis. Recommend further serology.",
                                confidence_calibration: { overall_confidence: 85 }
                            }
                        ]
                    });
                    setLoading(false);
                }, 800);
            } catch (error) {
                console.error("Failed", error);
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, [navigate]);

    if (loading || !user) return <div className="p-8 text-center text-brand-500 animate-pulse font-bold">Encrypting & Loading Portal...</div>;

    // --- DOCTOR VIEW ---
    if (user.role === 'doctor') {
        return (
            <div className="space-y-6 animate-fade-in font-sans">
                <div className="flex justify-between items-end border-b border-slate-800 pb-4">
                    <div>
                        <div className="flex items-center space-x-3">
                            <ShieldAlert className="w-8 h-8 text-coral-500" />
                            <h1 className="text-3xl font-bold text-white tracking-tight">Clinical Command Center</h1>
                        </div>
                        <p className="text-slate-400 mt-2">Welcome back, {user.name}. Here is your patient triage queue.</p>
                    </div>
                    <button onClick={() => { localStorage.removeItem('user'); navigate('/login'); }} className="text-sm text-slate-500 hover:text-coral-500">Log Out</button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {mockPatientList.map(p => (
                        <div key={p.id} className="bg-surface rounded-xl border border-slate-800 p-5 shadow-lg hover:border-brand-500 transition-colors cursor-pointer">
                            <div className="flex justify-between items-start mb-4">
                                <div className="bg-slate-800 p-2 rounded-lg">
                                    <UserSquare2 className="w-6 h-6 text-brand-500" />
                                </div>
                                <span className={`text-xs font-bold px-2 py-1 rounded-full ${p.risk > 70 ? 'bg-danger/20 text-danger' : p.risk > 50 ? 'bg-warning/20 text-warning' : 'bg-success/20 text-success'}`}>
                                    {p.status}
                                </span>
                            </div>
                            <h3 className="text-lg font-bold text-white">{p.name}</h3>
                            <div className="mt-4 flex justify-between text-sm">
                                <span className="text-slate-500">Risk Score:</span>
                                <span className="text-white font-bold">{p.risk}/100</span>
                            </div>
                            <div className="mt-1 flex justify-between text-sm">
                                <span className="text-slate-500">Last Visit:</span>
                                <span className="text-slate-300">{p.lastVisit}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    // --- PATIENT VIEW ---
    return (
        <div className="space-y-6 animate-fade-in font-sans">
            <div className="flex justify-between items-end border-b border-slate-800 pb-4">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Patient Overview</h1>
                    <p className="text-slate-400 mt-2">Health telemetry for {patientData?.first_name} {patientData?.last_name}.</p>
                </div>
                <div className="flex items-center space-x-4">
                    <button onClick={() => { localStorage.removeItem('user'); navigate('/login'); }} className="text-sm text-slate-500 hover:text-coral-500">Log Out</button>
                    <button
                        onClick={() => navigate('/upload')}
                        className="bg-brand-500 hover:bg-brand-400 text-deepSpace px-4 py-2 rounded-lg text-sm font-bold shadow-neon transition-colors"
                    >
                        + New Diagnosis
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <RiskScoreCard score={68} level="High" />

                <div className="bg-surface rounded-xl border border-slate-800 shadow-lg p-5 flex flex-col justify-center">
                    <div className="flex items-center space-x-3 mb-2">
                        <div className="p-2 bg-brand-500/10 text-brand-500 rounded-lg"><FileText size={20} /></div>
                        <h3 className="font-semibold text-slate-300">Total Reports</h3>
                    </div>
                    <p className="text-4xl font-bold text-white">{patientData?.reports?.length || 0}</p>
                </div>

                <div className="bg-surface rounded-xl border border-slate-800 shadow-lg p-5 flex flex-col justify-center">
                    <div className="flex items-center space-x-3 mb-2">
                        <div className="p-2 bg-coral-500/10 text-coral-500 rounded-lg"><AlertTriangle size={20} /></div>
                        <h3 className="font-semibold text-slate-300">Active Alerts</h3>
                    </div>
                    <p className="text-4xl font-bold text-white">2</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-surface rounded-xl border border-slate-800 shadow-lg p-5">
                    <h3 className="font-semibold text-white mb-6 flex items-center">
                        <ActivityIcon className="w-5 h-5 mr-2 text-brand-500" />
                        Longitudinal Risk Trend (7 Days)
                    </h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={stubTrends} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1F2833" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} dx={-10} domain={[0, 100]} />
                                <RechartsTooltip
                                    contentStyle={{ backgroundColor: '#0B0C10', borderRadius: '8px', border: '1px solid #1F2833', color: '#fff' }}
                                    cursor={{ stroke: '#45F3FF', strokeWidth: 1, strokeDasharray: '4 4' }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="risk"
                                    stroke="#45F3FF"
                                    strokeWidth={3}
                                    dot={{ r: 4, fill: '#0B0C10', strokeWidth: 2, stroke: '#45F3FF' }}
                                    activeDot={{ r: 6, fill: '#45F3FF', stroke: '#fff', strokeWidth: 4 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="space-y-4">
                    <h3 className="font-semibold text-white px-1">Recent Consultations</h3>
                    {patientData?.reports && patientData.reports.length > 0 ? (
                        patientData.reports.slice(0, 3).map((report, idx) => (
                            <ReportCard
                                key={idx}
                                report={report}
                                onClick={() => navigate('/reports')}
                            />
                        ))
                    ) : (
                        <div className="text-sm text-slate-400 italic p-4 bg-surface rounded-lg border border-slate-800">
                            No recent reports found.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
