import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    ArrowLeft, User, Phone, Mail, MapPin, Shield, Heart, Activity,
    Pill, FlaskConical, FileText, Calendar, Clock, AlertTriangle,
    Droplets, Thermometer, Weight, Ruler, Wind, ChevronRight,
    ShieldAlert, TrendingUp, Stethoscope, ClipboardList, UserSquare2
} from 'lucide-react';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer
} from 'recharts';
import { getPatientProfile } from '../services/apiClient';

const containerVariants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.08 } }
};
const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

// --- Sub-components ---

const SectionTitle = ({ icon: Icon, title, iconColor = 'text-brand-500', children }) => (
    <div className="flex items-center justify-between mb-5">
        <h3 className="text-lg font-bold text-white flex items-center gap-2.5">
            <div className={`p-2 rounded-xl bg-white/5 border border-white/10 ${iconColor}`}>
                <Icon size={18} />
            </div>
            {title}
        </h3>
        {children}
    </div>
);

const StatusBadge = ({ status, risk }) => {
    let classes = 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
    if (risk > 70) classes = 'bg-red-500/20 text-red-400 border-red-500/30';
    else if (risk > 50) classes = 'bg-orange-500/20 text-orange-400 border-orange-500/30';
    return (
        <span className={`text-xs font-black px-3 py-1.5 rounded-full uppercase tracking-wider border ${classes}`}>
            {status}
        </span>
    );
};

const VitalCard = ({ icon: Icon, label, value, alert }) => (
    <div className={`p-3.5 rounded-xl bg-white/5 border transition-all duration-300 hover:bg-white/10 hover:-translate-y-0.5 ${alert ? 'border-red-500/30' : 'border-white/5'}`}>
        <div className="flex items-center gap-2 mb-1">
            <Icon size={14} className={alert ? 'text-red-400' : 'text-brand-400'} />
            <span className="text-xs text-slate-400 font-medium">{label}</span>
        </div>
        <p className={`text-lg font-bold ${alert ? 'text-red-400' : 'text-white'}`}>{value}</p>
    </div>
);

// --- Main Component ---

const PatientProfile = () => {
    const { patientId } = useParams();
    const navigate = useNavigate();
    const [patient, setPatient] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('overview');
    const [error, setError] = useState('');

    useEffect(() => {
        const load = async () => {
            try {
                const res = await getPatientProfile(patientId);
                setPatient(res.data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [patientId]);

    if (loading) return (
        <div className="h-[calc(100vh-8rem)] flex items-center justify-center">
            <div className="flex flex-col items-center space-y-4">
                <div className="w-16 h-16 border-4 border-white/10 border-t-brand-500 rounded-full animate-spin shadow-[0_0_15px_rgba(69,243,255,0.5)]"></div>
                <p className="text-brand-400 font-bold tracking-widest text-glow animate-pulse">LOADING PATIENT DATA</p>
            </div>
        </div>
    );

    if (error) return (
        <div className="h-[calc(100vh-8rem)] flex items-center justify-center">
            <div className="glass-panel p-8 text-center max-w-md">
                <AlertTriangle className="w-12 h-12 text-coral-500 mx-auto mb-4" />
                <p className="text-white font-bold text-lg mb-2">Patient Not Found</p>
                <p className="text-slate-400 mb-6">{error}</p>
                <button onClick={() => navigate('/')} className="btn-primary">Return to Dashboard</button>
            </div>
        </div>
    );

    const p = patient;
    const initials = p.name.split(' ').map(n => n[0]).join('').toUpperCase();
    const tabs = [
        { id: 'overview', label: 'Overview' },
        { id: 'labs', label: 'Lab Results' },
        { id: 'visits', label: 'Visit History' },
        { id: 'reports', label: 'Diagnostic Reports' },
    ];

    return (
        <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className="space-y-6 font-sans pb-8"
        >
            {/* --- BACK BUTTON & HEADER --- */}
            <motion.div variants={itemVariants}>
                <button
                    onClick={() => navigate('/')}
                    className="flex items-center gap-2 text-slate-400 hover:text-brand-400 transition-colors mb-4 group"
                >
                    <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
                    <span className="text-sm font-medium">Back to Command Center</span>
                </button>

                <div className="glass-panel p-6 md:p-8 relative overflow-hidden">
                    {/* ambient glow */}
                    <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 rounded-full blur-[80px] pointer-events-none" />
                    <div className="absolute bottom-0 left-1/4 w-48 h-48 bg-coral-500/8 rounded-full blur-[60px] pointer-events-none" />

                    <div className="flex flex-col md:flex-row gap-6 items-start relative z-10">
                        {/* Avatar */}
                        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-brand-500 to-coral-500 flex items-center justify-center text-white text-2xl font-black shadow-lg shadow-brand-500/20 shrink-0">
                            {initials}
                        </div>

                        {/* Info */}
                        <div className="flex-1 min-w-0">
                            <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-3">
                                <h1 className="text-3xl font-black text-white tracking-tight">{p.name}</h1>
                                <StatusBadge status={p.status} risk={p.risk} />
                            </div>
                            <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-400">
                                <span className="flex items-center gap-1.5"><User size={14} className="text-slate-500" /> {p.age}y • {p.sex}</span>
                                <span className="flex items-center gap-1.5"><Calendar size={14} className="text-slate-500" /> DOB: {p.dob}</span>
                                <span className="flex items-center gap-1.5"><Droplets size={14} className="text-red-400" /> {p.bloodType}</span>
                                <span className="flex items-center gap-1.5"><Phone size={14} className="text-slate-500" /> {p.phone}</span>
                                <span className="flex items-center gap-1.5"><Mail size={14} className="text-slate-500" /> {p.email}</span>
                            </div>
                            <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-500 mt-2">
                                <span className="flex items-center gap-1.5"><MapPin size={14} /> {p.address}</span>
                            </div>
                        </div>

                        {/* Quick risk score */}
                        <div className="glass-panel p-4 text-center shrink-0 min-w-[120px] border border-white/10">
                            <p className="text-xs text-slate-400 font-bold uppercase tracking-widest mb-1">Risk Score</p>
                            <p className={`text-4xl font-black ${p.risk > 70 ? 'text-red-400' : p.risk > 50 ? 'text-orange-400' : 'text-emerald-400'}`}>
                                {p.risk}
                            </p>
                            <p className="text-xs text-slate-500 mt-0.5">/ 100</p>
                        </div>
                    </div>
                </div>
            </motion.div>

            {/* --- TAB NAVIGATION --- */}
            <motion.div variants={itemVariants} className="flex bg-white/5 p-1 rounded-xl border border-white/10 overflow-x-auto">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-semibold transition-all duration-300 whitespace-nowrap ${
                            activeTab === tab.id
                                ? 'bg-brand-500 text-deepSpace shadow-neon'
                                : 'text-slate-400 hover:text-white hover:bg-white/5'
                        }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </motion.div>

            {/* === TAB: OVERVIEW === */}
            {activeTab === 'overview' && (
                <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-6">
                    {/* Vitals Grid */}
                    <motion.div variants={itemVariants} className="glass-panel p-6">
                        <SectionTitle icon={Heart} title="Current Vitals" iconColor="text-coral-400" />
                        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3">
                            <VitalCard icon={Activity} label="Blood Pressure" value={p.vitals.bp} alert={parseInt(p.vitals.bp) > 140} />
                            <VitalCard icon={Heart} label="Heart Rate" value={`${p.vitals.heartRate} bpm`} alert={p.vitals.heartRate > 100} />
                            <VitalCard icon={Thermometer} label="Temperature" value={p.vitals.temp} />
                            <VitalCard icon={Weight} label="Weight" value={p.vitals.weight} />
                            <VitalCard icon={Ruler} label="Height" value={p.vitals.height} />
                            <VitalCard icon={Activity} label="BMI" value={p.vitals.bmi} alert={p.vitals.bmi > 30} />
                            <VitalCard icon={Wind} label="SpO₂" value={p.vitals.spO2} alert={parseInt(p.vitals.spO2) < 95} />
                        </div>
                    </motion.div>

                    {/* Two-column: Conditions & Medications */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Conditions & Allergies */}
                        <motion.div variants={itemVariants} className="glass-panel p-6">
                            <SectionTitle icon={ClipboardList} title="Conditions" iconColor="text-orange-400" />
                            <div className="space-y-2 mb-6">
                                {p.conditions.map((c, i) => (
                                    <div key={i} className="flex items-center gap-2.5 p-2.5 rounded-lg bg-white/5 border border-white/5">
                                        <div className="w-2 h-2 rounded-full bg-orange-400 shrink-0" />
                                        <span className="text-sm text-slate-200 font-medium">{c}</span>
                                    </div>
                                ))}
                            </div>
                            <h4 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                                <AlertTriangle size={14} className="text-red-400" /> Known Allergies
                            </h4>
                            <div className="flex flex-wrap gap-2">
                                {p.allergies.map((a, i) => (
                                    <span key={i} className="text-xs font-bold px-3 py-1.5 bg-red-500/15 text-red-400 border border-red-500/30 rounded-full">
                                        {a}
                                    </span>
                                ))}
                            </div>
                        </motion.div>

                        {/* Medications */}
                        <motion.div variants={itemVariants} className="glass-panel p-6">
                            <SectionTitle icon={Pill} title="Active Medications" iconColor="text-emerald-400" />
                            <div className="space-y-3">
                                {p.medications.map((med, i) => (
                                    <div key={i} className="p-3.5 rounded-xl bg-white/5 border border-white/5 hover:border-brand-500/30 transition-all group">
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <p className="text-sm text-white font-bold group-hover:text-brand-300 transition-colors">{med.name}</p>
                                                <p className="text-xs text-slate-400 mt-1">{med.dose} • {med.freq}</p>
                                            </div>
                                            <span className="text-xs text-brand-400 bg-brand-500/10 px-2.5 py-1 rounded-md border border-brand-500/20 font-medium shrink-0 ml-2">
                                                {med.purpose}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    </div>

                    {/* Risk Trend Chart */}
                    <motion.div variants={itemVariants} className="glass-panel p-6 relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-full h-full bg-gradient-to-br from-brand-500/5 via-transparent to-transparent opacity-50 pointer-events-none" />
                        <SectionTitle icon={TrendingUp} title="Risk Score Trend" />
                        <div className="h-[280px] w-full relative z-10">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={p.riskTrend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="colorPatientRisk" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#45F3FF" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#45F3FF" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ffffff15" />
                                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 13, fontWeight: 500 }} dy={10} />
                                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 13, fontWeight: 500 }} dx={-10} domain={[0, 100]} />
                                    <RechartsTooltip
                                        contentStyle={{ backgroundColor: 'rgba(11, 12, 16, 0.8)', backdropFilter: 'blur(10px)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', boxShadow: '0 10px 25px rgba(0,0,0,0.5)' }}
                                        itemStyle={{ color: '#45F3FF', fontWeight: 'bold' }}
                                    />
                                    <Area type="monotone" dataKey="risk" stroke="#45F3FF" strokeWidth={3} fillOpacity={1} fill="url(#colorPatientRisk)"
                                        activeDot={{ r: 7, fill: '#45F3FF', stroke: '#0B0C10', strokeWidth: 3 }}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </motion.div>

                    {/* Medical History */}
                    <motion.div variants={itemVariants} className="glass-panel p-6">
                        <SectionTitle icon={Stethoscope} title="Medical History Summary" iconColor="text-purple-400" />
                        <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-line">{p.medicalHistory}</p>
                    </motion.div>

                    {/* Insurance & Emergency */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <motion.div variants={itemVariants} className="glass-panel p-6">
                            <SectionTitle icon={Shield} title="Insurance" iconColor="text-blue-400" />
                            <div className="space-y-3 text-sm">
                                <div className="flex justify-between"><span className="text-slate-400">Provider</span><span className="text-white font-medium">{p.insurance.provider}</span></div>
                                <div className="flex justify-between"><span className="text-slate-400">Policy #</span><span className="text-white font-medium">{p.insurance.policyNo}</span></div>
                                <div className="flex justify-between"><span className="text-slate-400">Group</span><span className="text-white font-medium">{p.insurance.group}</span></div>
                            </div>
                        </motion.div>
                        <motion.div variants={itemVariants} className="glass-panel p-6">
                            <SectionTitle icon={Phone} title="Emergency Contact" iconColor="text-coral-400" />
                            <div className="space-y-3 text-sm">
                                <div className="flex justify-between"><span className="text-slate-400">Name</span><span className="text-white font-medium">{p.emergencyContact.name}</span></div>
                                <div className="flex justify-between"><span className="text-slate-400">Relation</span><span className="text-white font-medium">{p.emergencyContact.relation}</span></div>
                                <div className="flex justify-between"><span className="text-slate-400">Phone</span><span className="text-white font-medium">{p.emergencyContact.phone}</span></div>
                            </div>
                        </motion.div>
                    </div>
                </motion.div>
            )}

            {/* === TAB: LAB RESULTS === */}
            {activeTab === 'labs' && (
                <motion.div variants={containerVariants} initial="hidden" animate="show">
                    <motion.div variants={itemVariants} className="glass-panel p-6">
                        <SectionTitle icon={FlaskConical} title="Laboratory Results" iconColor="text-purple-400">
                            <span className="text-xs text-slate-500 bg-white/5 px-3 py-1.5 rounded-md border border-white/5 font-medium">
                                Last updated: {p.labResults[0]?.date}
                            </span>
                        </SectionTitle>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b border-white/10">
                                        <th className="text-left py-3 px-4 text-slate-400 font-bold uppercase tracking-wider text-xs">Test</th>
                                        <th className="text-left py-3 px-4 text-slate-400 font-bold uppercase tracking-wider text-xs">Result</th>
                                        <th className="text-left py-3 px-4 text-slate-400 font-bold uppercase tracking-wider text-xs">Reference Range</th>
                                        <th className="text-left py-3 px-4 text-slate-400 font-bold uppercase tracking-wider text-xs">Status</th>
                                        <th className="text-left py-3 px-4 text-slate-400 font-bold uppercase tracking-wider text-xs">Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {p.labResults.map((lab, i) => (
                                        <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                                            <td className="py-3.5 px-4 text-white font-medium">{lab.test}</td>
                                            <td className={`py-3.5 px-4 font-bold ${lab.status === 'high' ? 'text-red-400' : 'text-emerald-400'}`}>{lab.value}</td>
                                            <td className="py-3.5 px-4 text-slate-400">{lab.range}</td>
                                            <td className="py-3.5 px-4">
                                                <span className={`text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wider ${
                                                    lab.status === 'high'
                                                        ? 'bg-red-500/15 text-red-400 border border-red-500/30'
                                                        : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                                                }`}>
                                                    {lab.status === 'high' ? 'Abnormal' : 'Normal'}
                                                </span>
                                            </td>
                                            <td className="py-3.5 px-4 text-slate-500">{lab.date}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </motion.div>
                </motion.div>
            )}

            {/* === TAB: VISIT HISTORY === */}
            {activeTab === 'visits' && (
                <motion.div variants={containerVariants} initial="hidden" animate="show">
                    <motion.div variants={itemVariants} className="glass-panel p-6">
                        <SectionTitle icon={Calendar} title="Visit History" iconColor="text-blue-400" />
                        <div className="space-y-4">
                            {p.visitHistory.map((visit, i) => (
                                <motion.div
                                    key={i}
                                    variants={itemVariants}
                                    className="relative pl-8 pb-6 last:pb-0 group"
                                >
                                    {/* Timeline line */}
                                    {i < p.visitHistory.length - 1 && (
                                        <div className="absolute left-[11px] top-6 bottom-0 w-px bg-gradient-to-b from-brand-500/40 to-transparent" />
                                    )}
                                    {/* Timeline dot */}
                                    <div className="absolute left-0 top-1 w-6 h-6 rounded-full bg-brand-500/20 border-2 border-brand-500 flex items-center justify-center">
                                        <div className="w-2 h-2 rounded-full bg-brand-500" />
                                    </div>

                                    <div className="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-brand-500/30 transition-all group-hover:bg-white/[0.07]">
                                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                                            <div className="flex items-center gap-3">
                                                <span className={`text-xs font-bold px-2.5 py-1 rounded-md border ${
                                                    visit.type === 'Urgent Visit' || visit.type === 'ER Visit'
                                                        ? 'bg-red-500/15 text-red-400 border-red-500/30'
                                                        : visit.type === 'Cardiology Consult'
                                                            ? 'bg-purple-500/15 text-purple-400 border-purple-500/30'
                                                            : 'bg-brand-500/15 text-brand-400 border-brand-500/30'
                                                }`}>
                                                    {visit.type}
                                                </span>
                                                <span className="text-sm text-white font-semibold">{visit.doctor}</span>
                                            </div>
                                            <span className="text-xs text-slate-500 flex items-center gap-1.5">
                                                <Clock size={12} /> {visit.date}
                                            </span>
                                        </div>
                                        <p className="text-sm text-slate-300 leading-relaxed">{visit.summary}</p>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                </motion.div>
            )}

            {/* === TAB: DIAGNOSTIC REPORTS === */}
            {activeTab === 'reports' && (
                <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-4">
                    {p.reports.map((report, i) => (
                        <motion.div key={report.id} variants={itemVariants} className="glass-panel p-6 relative overflow-hidden group hover:border-brand-500/30 transition-all duration-300">
                            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                            <div className="relative z-10">
                                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2.5 bg-brand-500/10 rounded-xl border border-brand-500/20">
                                            <FileText size={18} className="text-brand-400" />
                                        </div>
                                        <div>
                                            <h4 className="text-white font-bold group-hover:text-brand-300 transition-colors">{report.title}</h4>
                                            <span className="text-xs text-slate-500">{report.date}</span>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2 bg-white/5 px-3 py-1.5 rounded-md border border-white/10 shrink-0">
                                        {report.confidence_calibration.overall_confidence > 70 ? (
                                            <Shield size={14} className="text-emerald-400" />
                                        ) : (
                                            <ShieldAlert size={14} className="text-amber-400" />
                                        )}
                                        <span className={`text-xs font-bold ${report.confidence_calibration.overall_confidence > 70 ? 'text-emerald-400' : 'text-amber-400'}`}>
                                            {report.confidence_calibration.overall_confidence}% Confidence
                                        </span>
                                    </div>
                                </div>
                                <p className="text-sm text-slate-300 leading-relaxed">{report.final_report}</p>
                            </div>
                        </motion.div>
                    ))}
                </motion.div>
            )}
        </motion.div>
    );
};

export default PatientProfile;
