import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, FileText, AlertTriangle, Activity as ActivityIcon } from 'lucide-react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer
} from 'recharts';
import RiskScoreCard from '../components/RiskScoreCard';
import ReportCard from '../components/ReportCard';
import { getPatientHistory } from '../services/apiClient';

// Stub Data for initial render before API connects
const stubTrends = [
    { name: 'Mon', risk: 45 },
    { name: 'Tue', risk: 48 },
    { name: 'Wed', risk: 52 },
    { name: 'Thu', risk: 58 },
    { name: 'Fri', risk: 65 },
    { name: 'Sat', risk: 72 },
    { name: 'Sun', risk: 68 },
];

const Dashboard = () => {
    const navigate = useNavigate();
    const [patientData, setPatientData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                // Assume patient ID 1 for prototype
                const response = await getPatientHistory(1);
                setPatientData(response.data);
            } catch (error) {
                console.error("Failed to fetch dashboard data", error);
                // Fallback stub
                setPatientData({
                    first_name: "Jane",
                    last_name: "Doe",
                    medical_history_summary: "History of hypertension and recent reports indicating elevated inflammatory markers.",
                    reports: [
                        {
                            id: 1,
                            final_report: "Elevated CRP and localized joint pain. Potential onset of rheumatoid arthritis. Recommend further serology.",
                            confidence_calibration: { overall_confidence: 85 }
                        }
                    ]
                });
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    if (loading) return <div className="p-8 text-center text-slate-500 animate-pulse">Loading Patient Data...</div>;

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Patient Dashboard</h1>
                    <p className="text-slate-500 mt-1">Overview of {patientData?.first_name} {patientData?.last_name}'s clinical status.</p>
                </div>
                <button
                    onClick={() => navigate('/upload')}
                    className="bg-brand-600 hover:bg-brand-700 text-white px-4 py-2 rounded-lg text-sm font-medium shadow-sm transition-colors"
                >
                    + New Diagnosis
                </button>
            </div>

            {/* Top Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <RiskScoreCard
                    score={68} // Hardcoded stub, would come from risk engine API in prod
                    level="High"
                />

                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 flex flex-col justify-center">
                    <div className="flex items-center space-x-3 mb-2">
                        <div className="p-2 bg-blue-50 text-blue-600 rounded-lg"><FileText size={20} /></div>
                        <h3 className="font-semibold text-slate-700">Total Reports</h3>
                    </div>
                    <p className="text-3xl font-bold text-slate-900">{patientData?.reports?.length || 0}</p>
                </div>

                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 flex flex-col justify-center">
                    <div className="flex items-center space-x-3 mb-2">
                        <div className="p-2 bg-amber-50 text-amber-600 rounded-lg"><AlertTriangle size={20} /></div>
                        <h3 className="font-semibold text-slate-700">Active Alerts</h3>
                    </div>
                    <p className="text-3xl font-bold text-slate-900">2</p>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Left Column: Trend Graph */}
                <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm p-5">
                    <h3 className="font-semibold text-slate-800 mb-6 flex items-center">
                        <ActivityIcon className="w-5 h-5 mr-2 text-brand-500" />
                        Longitudinal Risk Trend (7 Days)
                    </h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={stubTrends} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dx={-10} domain={[0, 100]} />
                                <RechartsTooltip
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)' }}
                                    cursor={{ stroke: '#cbd5e1', strokeWidth: 1, strokeDasharray: '4 4' }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="risk"
                                    stroke="#14b8a6"
                                    strokeWidth={3}
                                    dot={{ r: 4, fill: '#14b8a6', strokeWidth: 2, stroke: '#fff' }}
                                    activeDot={{ r: 6, fill: '#14b8a6', stroke: '#ccfbf1', strokeWidth: 4 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Right Column: Recent Reports */}
                <div className="space-y-4">
                    <h3 className="font-semibold text-slate-800 px-1">Recent Consultations</h3>
                    {patientData?.reports && patientData.reports.length > 0 ? (
                        patientData.reports.slice(0, 3).map((report, idx) => (
                            <ReportCard
                                key={idx}
                                report={report}
                                onClick={() => navigate('/reports')}
                            />
                        ))
                    ) : (
                        <div className="text-sm text-slate-500 italic p-4 bg-slate-50 rounded-lg border border-slate-200">
                            No recent reports found.
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};

export default Dashboard;
