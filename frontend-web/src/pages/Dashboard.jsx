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

const stubTrends = [
    { name: 'Mon', risk: 45 }, { name: 'Tue', risk: 48 }, { name: 'Wed', risk: 52 },
    { name: 'Thu', risk: 58 }, { name: 'Fri', risk: 65 }, { name: 'Sat', risk: 72 }, { name: 'Sun', risk: 68 },
];

const mockPatientList = [
    { id: 'JD123456', name: 'John Doe',    risk: 68, lastVisit: '2026-03-20', status: 'High Risk',  confidence: 82 },
    { id: 'JS654321', name: 'Jane Smith',  risk: 42, lastVisit: '2026-03-15', status: 'Stable',     confidence: 91 },
    { id: 'BU112233', name: 'Bob User',    risk: 85, lastVisit: '2026-03-21', status: 'Critical',   confidence: 54 },
    { id: 'AW998877', name: 'Alice Wong',  risk: 25, lastVisit: '2026-03-10', status: 'Stable',     confidence: 95 },
];

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
    <motion.div variants={itemVariants} className="bento-card p-5 flex flex-col gap-3">
        <div className="flex items-center justify-between">
            <div className="p-2 rounded-xl" style={{ background: accent + '10', border: `1px solid ${accent}25` }}>
                <Icon size={16} style={{ color: accent }} />
            </div>
            <span className="label-caps">{label}</span>
        </div>
        <p className="text-4xl font-black tracking-tighter" style={{ color: 'var(--text-primary)' }}>{value}</p>
        {sub && <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{sub}</p>}
    </motion.div>
);

// ── Quick Action card ────────────────────────────────────────────────────────
const QuickAction = ({ icon: Icon, label, description, accent, onClick }) => (
    <motion.div variants={itemVariants} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
        onClick={onClick} className="bento-card p-4 cursor-pointer flex items-center gap-4 group">
        <div className="p-3 rounded-xl transition-all group-hover:scale-110" style={{ background: accent + '10', border: `1px solid ${accent}20` }}>
            <Icon size={20} style={{ color: accent }} />
        </div>
        <div className="flex-1">
            <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{label}</p>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{description}</p>
        </div>
        <ArrowRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" style={{ color: accent }} />
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
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState(null);

    useEffect(() => {
        const stored = localStorage.getItem('user');
        if (stored) { setUser(JSON.parse(stored)); }
        else { navigate('/login'); return; }
        setTimeout(() => {
            setPatientData({
                first_name: JSON.parse(stored).name?.split(' ')[0] || 'Patient',
                last_name:  JSON.parse(stored).name?.split(' ')[1] || '',
                reports: [{
                    id: 1,
                    final_report: 'Elevated CRP and localized joint pain. Potential onset of rheumatoid arthritis. Recommend further serology.',
                    confidence_calibration: { overall_confidence: 85 }
                }]
            });
            setLoading(false);
        }, 600);
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
            <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-6 pb-8">
                <motion.div variants={itemVariants} className="flex items-end justify-between">
                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <div className="p-2 rounded-xl" style={{ background: 'rgba(231,76,60,0.08)', border: '1px solid rgba(231,76,60,0.15)' }}>
                                <Zap size={18} style={{ color: 'var(--error)' }} />
                            </div>
                            <h1 className="heading-xl">Clinical Command</h1>
                        </div>
                        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{user.name} · Active Triage Queue</p>
                    </div>
                    <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                        onClick={() => navigate('/upload')} className="btn-primary flex items-center gap-2 text-sm">
                        <Sparkles size={14} /> New Assessment
                    </motion.button>
                </motion.div>

                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <StatCard icon={Users}         label="Patients"       value={mockPatientList.length} accent="var(--primary)" sub="Active records" />
                    <StatCard icon={AlertTriangle} label="Critical"       value={1} accent="var(--error)" sub="Needs immediate review" />
                    <StatCard icon={ShieldCheck}   label="Avg Confidence" value="78%" accent="var(--success)" sub="Cross-cohort average" />
                    <StatCard icon={ActivityIcon}  label="Avg Risk"       value="55" accent="var(--warning)" sub="Population risk index" />
                </div>

                <motion.div variants={itemVariants}>
                    <p className="label-caps mb-3">Patient Queue</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        {mockPatientList.map(p => (
                            <PatientBentoCard key={p.id} patient={p} onClick={() => navigate(`/patient/${p.id}`)} />
                        ))}
                    </div>
                </motion.div>
            </motion.div>
        );
    }

    // ── PATIENT VIEW ─────────────────────────────────────────────────────────
    return (
        <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-5 pb-8">
            {/* Header */}
            <motion.div variants={itemVariants} className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <h1 className="heading-xl flex items-center gap-3">
                        <Sparkles size={30} style={{ color: 'var(--primary)' }} /> Health Overview
                    </h1>
                    <p className="mt-1 text-sm" style={{ color: 'var(--text-muted)' }}>
                        Intelligent telemetry for <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>{patientData?.first_name} {patientData?.last_name}</span>
                    </p>
                </div>
                <div className="flex gap-3">
                    {user?.user_id && (
                        <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
                            onClick={() => navigate(`/patient/${user.user_id}`)} className="btn-ghost text-sm">My Profile</motion.button>
                    )}
                    <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
                        onClick={() => navigate('/upload')} className="btn-primary flex items-center gap-2 text-sm">
                        <Sparkles size={13} /> New Assessment
                    </motion.button>
                </div>
            </motion.div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <motion.div variants={itemVariants} className="lg:col-span-2 bento-card p-6">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-2">
                            <TrendingUp size={16} style={{ color: 'var(--primary)' }} />
                            <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Longitudinal Risk Trend</h3>
                            <span className="label-caps">7 Days</span>
                        </div>
                        <ConfidenceBadge score={72} size="sm" showShimmer={false} />
                    </div>
                    <div className="h-52">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={stubTrends} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%"  stopColor="var(--primary)" stopOpacity={0.15} />
                                        <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
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

                <motion.div variants={itemVariants} className="flex flex-col gap-3">
                    <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Recent Consultations</h3>
                        <button onClick={() => navigate('/reports')}
                            className="text-xs flex items-center gap-1 transition-colors hover:underline underline-offset-2"
                            style={{ color: 'var(--primary)' }}>
                            View all <ArrowRight size={11} />
                        </button>
                    </div>
                    {patientData?.reports?.length > 0 ? (
                        patientData.reports.slice(0, 3).map((report, idx) => (
                            <ReportCard key={idx} report={report} onClick={() => navigate('/reports')} />
                        ))
                    ) : (
                        <div className="bento-card p-8 flex flex-col items-center justify-center text-center flex-1">
                            <FileText size={28} style={{ color: 'var(--text-muted)' }} className="mb-2" />
                            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>No reports yet</p>
                            <button onClick={() => navigate('/upload')}
                                className="mt-3 text-xs hover:underline" style={{ color: 'var(--primary)' }}>Start a diagnosis →</button>
                        </div>
                    )}
                </motion.div>
            </div>
        </motion.div>
    );
};

export default Dashboard;
