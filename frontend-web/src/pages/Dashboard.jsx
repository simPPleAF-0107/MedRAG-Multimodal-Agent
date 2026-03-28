import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, FileText, AlertTriangle, Activity as ActivityIcon, UserSquare2, ShieldAlert, Sparkles, TrendingUp, Calendar } from 'lucide-react';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer
} from 'recharts';
import { motion } from 'framer-motion';
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

const containerVariants = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: { staggerChildren: 0.1 }
    }
};

const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

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

    if (loading || !user) return (
        <div className="h-[calc(100vh-8rem)] flex items-center justify-center">
            <div className="flex flex-col items-center space-y-4">
                <div className="w-16 h-16 border-4 border-white/10 border-t-brand-500 rounded-full animate-spin shadow-[0_0_15px_rgba(69,243,255,0.5)]"></div>
                <p className="text-brand-400 font-bold tracking-widest text-glow animate-pulse">SYNCING SECURE DATA</p>
            </div>
        </div>
    );

    // --- DOCTOR VIEW ---
    if (user.role === 'doctor') {
        return (
            <motion.div 
                variants={containerVariants}
                initial="hidden"
                animate="show"
                className="space-y-8 font-sans"
            >
                <div className="flex justify-between items-end border-b border-white/10 pb-6 relative">
                    <div className="absolute top-0 right-1/4 w-96 h-32 bg-coral-500/10 rounded-full blur-[80px] pointer-events-none"></div>
                    <div>
                        <div className="flex items-center space-x-3">
                            <motion.div 
                                animate={{ rotate: 360 }} 
                                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                            >
                                <ShieldAlert className="w-10 h-10 text-coral-500 drop-shadow-[0_0_10px_rgba(255,42,122,0.6)]" />
                            </motion.div>
                            <h1 className="text-4xl font-black text-white tracking-tight drop-shadow-md">Clinical Command Center</h1>
                        </div>
                        <p className="text-slate-400 mt-2 text-lg">Dr. {user.name} • Active Triage Queue</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {mockPatientList.map(p => (
                        <motion.div variants={itemVariants} key={p.id} className="relative group">
                            <div className="absolute inset-0 bg-gradient-to-br from-brand-500/0 to-brand-500/5 rounded-2xl blur-xl group-hover:from-brand-500/20 transition-all duration-500" />
                            <div className="glass-panel p-6 h-full relative border border-white/5 group-hover:border-brand-500/50 hover:shadow-[0_0_30px_rgba(69,243,255,0.15)] transition-all duration-300 transform group-hover:-translate-y-1 cursor-pointer overflow-hidden backdrop-blur-xl">
                                
                                <div className="flex justify-between items-start mb-6">
                                    <div className="bg-white/5 p-3 rounded-xl border border-white/10 shadow-inner">
                                        <UserSquare2 className="w-6 h-6 text-brand-400" />
                                    </div>
                                    <span className={`text-xs font-black px-3 py-1.5 rounded-full uppercase tracking-wider ${p.risk > 70 ? 'bg-red-500/20 text-red-400 border border-red-500/30' : p.risk > 50 ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'}`}>
                                        {p.status}
                                    </span>
                                </div>

                                <h3 className="text-xl font-bold text-white mb-1 group-hover:text-brand-300 transition-colors">{p.name}</h3>
                                
                                <div className="space-y-3 mt-5 border-t border-white/5 pt-4">
                                    <div className="flex justify-between text-sm items-center">
                                        <span className="text-slate-400 flex items-center"><ActivityIcon size={14} className="mr-1.5"/> Risk Score</span>
                                        <span className="text-white font-bold bg-white/5 px-2 py-0.5 rounded-md">{p.risk}/100</span>
                                    </div>
                                    <div className="flex justify-between text-sm items-center">
                                        <span className="text-slate-400 flex items-center"><Calendar size={14} className="mr-1.5"/> Last Visit</span>
                                        <span className="text-slate-300 font-medium">{p.lastVisit}</span>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </motion.div>
        );
    }

    // --- PATIENT VIEW ---
    return (
        <motion.div 
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className="space-y-8 font-sans pb-8"
        >
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/10 pb-6 relative gap-4">
                <div className="absolute top-0 right-1/4 w-96 h-32 bg-brand-500/10 rounded-full blur-[80px] pointer-events-none"></div>
                <div className="relative z-10">
                    <h1 className="text-4xl font-black text-white tracking-tight flex items-center gap-3">
                        <Sparkles className="w-8 h-8 text-brand-500" /> Health Overview
                    </h1>
                    <p className="text-slate-400 mt-2 text-lg">Intelligent telemetry for <span className="text-white font-semibold">{patientData?.first_name} {patientData?.last_name}</span></p>
                </div>
                <div className="flex items-center space-x-4 relative z-10 w-full md:w-auto">
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => navigate('/upload')}
                        className="btn-primary w-full md:w-auto"
                    >
                        + New Assessment
                    </motion.button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <motion.div variants={itemVariants}>
                    <RiskScoreCard score={68} level="High" />
                </motion.div>

                <motion.div variants={itemVariants} className="glass-panel p-6 flex flex-col justify-center relative overflow-hidden group hover:shadow-[0_0_30px_rgba(69,243,255,0.1)] transition-all duration-500 hover:-translate-y-1">
                    <div className="absolute -right-8 -top-8 w-32 h-32 bg-brand-500/10 rounded-full blur-2xl group-hover:bg-brand-500/20 transition-all duration-500"></div>
                    <div className="flex items-center space-x-3 mb-4 relative z-10">
                        <div className="p-2.5 bg-gradient-to-br from-white/10 to-brand-500/10 text-brand-400 rounded-xl border border-brand-500/20 shadow-inner group-hover:scale-110 transition-transform">
                            <FileText size={22} />
                        </div>
                        <h3 className="font-semibold text-slate-300 text-lg">Total Reports</h3>
                    </div>
                    <p className="text-5xl font-black text-white tracking-tighter ml-1">
                        {patientData?.reports?.length || 0}
                    </p>
                </motion.div>

                <motion.div variants={itemVariants} className="glass-panel p-6 flex flex-col justify-center relative overflow-hidden group hover:shadow-[0_0_30px_rgba(255,42,122,0.1)] transition-all duration-500 hover:-translate-y-1">
                    <div className="absolute -right-8 -top-8 w-32 h-32 bg-coral-500/10 rounded-full blur-2xl group-hover:bg-coral-500/20 transition-all duration-500"></div>
                    <div className="flex items-center space-x-3 mb-4 relative z-10">
                        <div className="p-2.5 bg-gradient-to-br from-white/10 to-coral-500/10 text-coral-400 rounded-xl border border-coral-500/20 shadow-inner group-hover:scale-110 transition-transform">
                            <AlertTriangle size={22} />
                        </div>
                        <h3 className="font-semibold text-slate-300 text-lg">Active Alerts</h3>
                    </div>
                    <p className="text-5xl font-black text-coral-400 tracking-tighter drop-shadow-[0_0_10px_rgba(255,42,122,0.5)] ml-1">
                        2
                    </p>
                </motion.div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <motion.div variants={itemVariants} className="lg:col-span-2 glass-panel p-6 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-full h-full bg-gradient-to-br from-brand-500/5 via-transparent to-transparent opacity-50 pointer-events-none"></div>
                    <h3 className="text-xl font-bold text-white mb-8 flex items-center relative z-10">
                        <TrendingUp className="w-6 h-6 mr-3 text-brand-500" />
                        Longitudinal Risk Trend <span className="text-slate-500 text-sm font-medium ml-3 mt-1">(Last 7 Days)</span>
                    </h3>
                    <div className="h-[320px] w-full relative z-10">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={stubTrends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#45F3FF" stopOpacity={0.3}/>
                                        <stop offset="95%" stopColor="#45F3FF" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ffffff15" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 13, fontWeight: 500 }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 13, fontWeight: 500 }} dx={-10} domain={[0, 100]} />
                                <RechartsTooltip
                                    contentStyle={{ backgroundColor: 'rgba(11, 12, 16, 0.8)', backdropFilter: 'blur(10px)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', boxShadow: '0 10px 25px rgba(0,0,0,0.5)' }}
                                    itemStyle={{ color: '#45F3FF', fontWeight: 'bold' }}
                                    cursor={{ stroke: 'rgba(69,243,255,0.3)', strokeWidth: 2, strokeDasharray: '4 4' }}
                                />
                                <Area 
                                    type="monotone" 
                                    dataKey="risk" 
                                    stroke="#45F3FF" 
                                    strokeWidth={4}
                                    fillOpacity={1} 
                                    fill="url(#colorRisk)" 
                                    activeDot={{ r: 8, fill: '#45F3FF', stroke: '#0B0C10', strokeWidth: 3, shadow: '0 0 10px #45F3FF' }}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>

                <motion.div variants={itemVariants} className="space-y-5">
                    <h3 className="text-xl font-bold text-white px-1 border-b border-white/5 pb-3">Recent Consultations</h3>
                    {patientData?.reports && patientData.reports.length > 0 ? (
                        <div className="space-y-4">
                            {patientData.reports.slice(0, 3).map((report, idx) => (
                                <ReportCard
                                    key={idx}
                                    report={report}
                                    onClick={() => navigate('/reports')}
                                />
                            ))}
                        </div>
                    ) : (
                        <div className="text-sm text-slate-400 italic p-6 glass-panel border border-white/5 text-center flex flex-col items-center justify-center">
                            <FileText size={32} className="mb-3 opacity-20" />
                            No recent reports found.
                        </div>
                    )}
                </motion.div>
            </div>
        </motion.div>
    );
};

export default Dashboard;
