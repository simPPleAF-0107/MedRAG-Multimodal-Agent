import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Users, FileText, AlertTriangle, Activity as ActivityIcon,
    UserSquare2, Sparkles, TrendingUp, Calendar, ArrowRight,
    ShieldCheck, Zap, UploadCloud, MessageSquare
} from 'lucide-react';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid,
    Tooltip as RechartsTooltip, ResponsiveContainer
} from 'recharts';
import { motion } from 'framer-motion';
import RiskScoreCard from '../components/RiskScoreCard';
import ReportCard from '../components/ReportCard';
import ConfidenceBadge from '../components/ConfidenceBadge';
import { getPatientList, getDashboardStats } from '../services/apiClient';

// Risk trend data is generated dynamically from patient risk scores
const generateTrends = (patients) => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    if (!patients || patients.length === 0) {
        return days.map(d => ({ name: d, risk: 0 }));
    }
    const avgRisk = Math.round(patients.reduce((s, p) => s + (p.risk || 0), 0) / patients.length);
    return days.map((d, i) => ({ name: d, risk: Math.max(5, avgRisk + Math.round(Math.sin(i) * 12)) }));
};

const containerVariants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.07 } }
};
const itemVariants = {
    hidden: { opacity: 0, y: 16 },
    show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 28 } }
};

// ── Stat mini-card ──────────────────────────────────────────────────────────
const StatCard = ({ icon: Icon, label, value, accent = 'var(--primary)', sub }) => (
    <motion.div variants={itemVariants} className="bg-surface-2/40 backdrop-blur-heavy border border-white/5 rounded-3xl p-6 flex flex-col gap-3 hover:border-brand-500/30 transition-all duration-500 shadow-bento group">
        <div className="flex items-center justify-between">
            <div className="p-3 rounded-2xl transition-transform group-hover:scale-110" style={{ background: accent + '15', border: `1px solid ${accent}30` }}>
                <Icon size={20} style={{ color: accent }} />
            </div>
            <span className="label-caps text-slate-500">{label}</span>
        </div>
        <p className="text-5xl font-black tracking-tighter text-white drop-shadow-md">{value}</p>
        {sub && <p className="text-xs text-slate-400 font-medium">{sub}</p>}
    </motion.div>
);

// ── Quick Action card ────────────────────────────────────────────────────────
const QuickAction = ({ icon: Icon, label, description, accent, onClick }) => (
    <motion.div variants={itemVariants} whileHover={{ y: -4 }} whileTap={{ scale: 0.98 }}
        onClick={onClick} className="bg-surface-3/50 backdrop-blur-glass border border-white/5 rounded-2xl p-5 cursor-pointer flex items-center gap-4 group hover:shadow-neon transition-all duration-300">
        <div className="p-3.5 rounded-xl transition-all duration-300 group-hover:scale-110 group-hover:shadow-neon" style={{ background: accent + '20', border: `1px solid ${accent}40` }}>
            <Icon size={22} style={{ color: accent }} />
        </div>
        <div className="flex-1">
            <p className="font-bold text-md text-white group-hover:text-brand-400 transition-colors">{label}</p>
            <p className="text-xs text-slate-400 mt-0.5">{description}</p>
        </div>
        <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all transform group-hover:translate-x-1">
            <ArrowRight size={16} style={{ color: accent }} />
        </div>
    </motion.div>
);

// ── Patient row card for doctor view ────────────────────────────────────────
const PatientBentoCard = ({ patient, onClick }) => {
    const riskColor = patient.risk > 70 ? 'var(--error)' : patient.risk > 50 ? 'var(--warning)' : 'var(--success)';
    return (
        <motion.div variants={itemVariants} onClick={onClick} className="bento-card p-5 cursor-pointer"
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <div className="flex items-start justify-between mb-4">
                <div className="p-2.5 rounded-xl" style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}>
                    <UserSquare2 size={20} style={{ color: 'var(--text-muted)' }} />
                </div>
                <ConfidenceBadge score={patient.confidence} size="sm" showShimmer={false} />
            </div>
            <h3 className="font-bold mb-1" style={{ color: 'var(--text-primary)' }}>{patient.name}</h3>
            <div className="space-y-2 mt-3 pt-3" style={{ borderTop: '1px solid var(--border)' }}>
                <div className="flex justify-between items-center text-xs">
                    <span className="flex items-center gap-1.5" style={{ color: 'var(--text-muted)' }}>
                        <ActivityIcon size={11} />Risk
                    </span>
                    <div className="flex items-center gap-2">
                        <div className="w-16 h-1 rounded-full" style={{ background: 'var(--surface-subtle)' }}>
                            <div className="h-full rounded-full" style={{ width: `${patient.risk}%`, background: riskColor }} />
                        </div>
                        <span className="font-bold font-mono" style={{ color: 'var(--text-primary)' }}>{patient.risk}</span>
                    </div>
                </div>
                <div className="flex justify-between items-center text-xs">
                    <span className="flex items-center gap-1.5" style={{ color: 'var(--text-muted)' }}>
                        <Calendar size={11} />Last Visit
                    </span>
                    <span className="font-medium" style={{ color: 'var(--text-secondary)' }}>{patient.lastVisit}</span>
                </div>
            </div>
        </motion.div>
    );
};

// ── Main Dashboard ──────────────────────────────────────────────────────────
const Dashboard = () => {
    const navigate = useNavigate();
    const [patientData, setPatientData] = useState(null);
    const [patients, setPatients] = useState([]);
    const [stats, setStats] = useState({ total_patients: 0, critical_patients: 0, avg_risk: 0, avg_confidence: 0 });
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState(null);

    useEffect(() => {
        const stored = localStorage.getItem('user');
        if (stored) { setUser(JSON.parse(stored)); }
        else { navigate('/login'); return; }

        const fetchData = async () => {
            try {
                const [patientRes, statsRes] = await Promise.all([
                    getPatientList(),
                    getDashboardStats(),
                ]);
                if (patientRes.patients) setPatients(patientRes.patients);
                if (statsRes.status === 'success') setStats(statsRes);
                
                const parsed = JSON.parse(stored);
                setPatientData({
                    first_name: parsed.name?.split(' ')[0] || 'Patient',
                    last_name:  parsed.name?.split(' ')[1] || '',
                    reports: []
                });
            } catch (e) {
                console.warn('Dashboard data fetch failed:', e);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [navigate]);

    if (loading || !user) return (
        <div className="h-full flex items-center justify-center">
            <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 rounded-full border-2 animate-spin"
                    style={{ borderColor: 'var(--border)', borderTopColor: 'var(--primary)' }} />
                <p className="text-xs tracking-widest uppercase animate-pulse" style={{ color: 'var(--text-muted)' }}>Syncing Data</p>
            </div>
        </div>
    );

    // ── DOCTOR VIEW ──────────────────────────────────────────────────────────
    if (user.role === 'doctor') {
        return (
            <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-8 pb-12 relative z-10 w-full max-w-7xl mx-auto">
                <motion.div variants={itemVariants} className="flex items-end justify-between bg-surface-2/30 p-8 rounded-3xl backdrop-blur-glass border border-white/5 shadow-bento">
                    <div>
                        <div className="flex items-center gap-4 mb-2">
                            <div className="p-3 rounded-2xl bg-brand-500/20 border border-brand-500/30 shadow-neon">
                                <Zap size={24} className="text-brand-400" />
                            </div>
                            <h1 className="text-5xl font-black tracking-tighter text-white drop-shadow-md">Clinical Command</h1>
                        </div>
                        <p className="text-lg text-slate-400 ml-16">{user.name} <span className="text-brand-500 ml-2">●</span> Active Triage Queue</p>
                    </div>
                    <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                        onClick={() => navigate('/upload')} className="bg-brand-500 hover:bg-brand-400 text-obsidian px-6 py-3 rounded-xl font-bold shadow-neon transition-all flex items-center gap-2">
                        <Sparkles size={18} /> New Assessment
                    </motion.button>
                </motion.div>

                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <StatCard icon={Users}         label="Patients"       value={stats.total_patients} accent="var(--primary)" sub="Active records" />
                    <StatCard icon={AlertTriangle} label="Critical"       value={stats.critical_patients} accent="var(--error)" sub="Needs immediate review" />
                    <StatCard icon={ShieldCheck}   label="Avg Confidence" value={`${stats.avg_confidence}%`} accent="var(--success)" sub="Cross-cohort average" />
                    <StatCard icon={ActivityIcon}  label="Avg Risk"       value={stats.avg_risk} accent="var(--warning)" sub="Population risk index" />
                </div>

                <motion.div variants={itemVariants}>
                    <p className="label-caps mb-3">Patient Queue ({patients.length})</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        {patients.slice(0, 12).map(p => (
                            <PatientBentoCard key={p.id} patient={p} onClick={() => navigate(`/patient/${p.id}`)} />
                        ))}
                    </div>
                </motion.div>
            </motion.div>
        );
    }

    // ── PATIENT VIEW ─────────────────────────────────────────────────────────
    return (
        <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-8 pb-12 relative z-10 w-full max-w-7xl mx-auto">
            {/* Header */}
            <motion.div variants={itemVariants} className="flex flex-col md:flex-row md:items-end justify-between bg-surface-2/30 p-8 rounded-3xl backdrop-blur-glass border border-white/5 shadow-bento group">
                <div>
                    <h1 className="text-5xl font-black tracking-tighter text-white drop-shadow-md flex items-center gap-4">
                        <div className="p-3 rounded-2xl bg-brand-500/20 border border-brand-500/30 shadow-neon group-hover:shadow-[0_0_30px_rgba(0,212,255,0.6)] transition-all duration-500">
                            <Sparkles size={28} className="text-brand-400" />
                        </div>
                        Health Overview
                    </h1>
                    <p className="mt-3 text-lg text-slate-400 ml-16">
                        Intelligent telemetry for <span className="font-bold text-white ml-2">{patientData?.first_name} {patientData?.last_name}</span>
                    </p>
                </div>
                <div className="flex gap-4 mt-6 md:mt-0">
                    {user?.user_id && (
                        <motion.button whileHover={{ y: -2 }} whileTap={{ scale: 0.97 }}
                            onClick={() => navigate(`/patient/${user.user_id}`)} className="px-6 py-3 rounded-xl border border-white/10 text-slate-300 font-semibold hover:border-brand-500 hover:text-brand-400 transition-all bg-surface-3/50 backdrop-blur-glass">
                            My Profile
                        </motion.button>
                    )}
                    <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                        onClick={() => navigate('/upload')} className="bg-brand-500 hover:bg-brand-400 text-obsidian px-6 py-3 rounded-xl font-bold shadow-neon transition-all flex items-center gap-2">
                        <Sparkles size={16} /> New Assessment
                    </motion.button>
                </div>
            </motion.div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <QuickAction icon={UploadCloud} label="New Diagnosis" description="Upload files and run the RAG pipeline"
                    accent="var(--primary)" onClick={() => navigate('/upload')} />
                <QuickAction icon={MessageSquare} label="AI Chat" description="Ask the clinical assistant anything"
                    accent="var(--secondary)" onClick={() => navigate('/chat')} />
                <QuickAction icon={Calendar} label="Book Appointment" description="Find a specialist and schedule a visit"
                    accent="var(--success)" onClick={() => navigate('/appointments')} />
            </div>

            {/* KPI Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <motion.div variants={itemVariants}>
                    <RiskScoreCard score={68} level="High" />
                </motion.div>
                <StatCard icon={FileText}      label="Reports"      value={patientData?.reports?.length || 0} accent="var(--secondary)" sub="Total diagnoses generated" />
                <StatCard icon={AlertTriangle} label="Active Alerts" value="2" accent="var(--error)" sub="Require clinical review" />
            </div>

            {/* Chart + Reports */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <motion.div variants={itemVariants} className="lg:col-span-2 bg-surface-2/40 backdrop-blur-glass border border-white/5 rounded-3xl p-8 hover:border-brand-500/30 transition-all duration-500 shadow-bento group">
                    <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-xl bg-brand-500/10 border border-brand-500/20 group-hover:scale-110 transition-transform">
                                <TrendingUp size={18} className="text-brand-400" />
                            </div>
                            <h3 className="font-bold text-lg text-white">Longitudinal Risk Trend</h3>
                            <span className="label-caps text-slate-500 ml-2">7 Days</span>
                        </div>
                        <ConfidenceBadge score={72} size="sm" showShimmer={false} />
                    </div>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={generateTrends(patients)} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%"  stopColor="#00D4FF" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#00D4FF" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false}
                                    tick={{ fill: 'var(--text-muted)', fontSize: 11, fontFamily: 'Inter' }} dy={8} />
                                <YAxis axisLine={false} tickLine={false}
                                    tick={{ fill: 'var(--text-muted)', fontSize: 11, fontFamily: 'Inter' }} domain={[0, 100]} />
                                <RechartsTooltip
                                    contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, color: 'var(--text-primary)', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}
                                    itemStyle={{ color: 'var(--primary)', fontWeight: 600 }}
                                />
                                <Area type="monotone" dataKey="risk" stroke="var(--primary)" strokeWidth={2.5}
                                    fillOpacity={1} fill="url(#riskGrad)"
                                    activeDot={{ r: 6, fill: 'var(--primary)', stroke: 'var(--surface)', strokeWidth: 2 }} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>

                <motion.div variants={itemVariants} className="flex flex-col gap-4 bg-surface-2/20 backdrop-blur-glass border border-white/5 rounded-3xl p-6 shadow-bento">
                    <div className="flex items-center justify-between px-2">
                        <h3 className="font-bold text-lg text-white">Recent Consultations</h3>
                        <button onClick={() => navigate('/reports')}
                            className="text-sm font-semibold flex items-center gap-1 transition-colors hover:text-brand-400 group text-slate-400">
                            View all <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
                        </button>
                    </div>
                    {patientData?.reports?.length > 0 ? (
                        patientData.reports.slice(0, 3).map((report, idx) => (
                            <ReportCard key={idx} report={report} onClick={() => navigate('/reports')} />
                        ))
                    ) : (
                        <div className="bg-surface-3/30 border border-white/5 rounded-2xl p-8 flex flex-col items-center justify-center text-center flex-1 h-full">
                            <FileText size={32} className="text-slate-600 mb-3" />
                            <p className="text-sm text-slate-500 font-medium">No diagnostic reports available</p>
                            <button onClick={() => navigate('/upload')}
                                className="mt-4 text-sm font-bold text-brand-500 flex items-center gap-2 hover:text-brand-400 transition-colors">
                                Start a diagnosis <ArrowRight size={14} />
                            </button>
                        </div>
                    )}
                </motion.div>
            </div>
        </motion.div>
    );
};

export default Dashboard;
