import React, { useEffect, useState } from 'react';
import {
    FileText, ShieldCheck, ShieldAlert, Activity, Search,
    AlertTriangle, Star, Stethoscope, BookOpen,
    ChevronDown, ChevronUp, Network, Download
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import RiskScoreCard from '../components/RiskScoreCard';
import ConfidenceBadge from '../components/ConfidenceBadge';
import KnowledgeGraphOverlay from '../components/KnowledgeGraphOverlay';
import toast from 'react-hot-toast';

// ── Inline markdown renderer (light theme) ────────────────────────────────
const MarkdownRenderer = ({ text }) => {
    if (!text) return null;
    const lines = text.split('\n');
    const renderInline = (t) => {
        if (!t) return t;
        const parts = []; let rem = t, k = 0;
        while (rem.length > 0) {
            const b = rem.match(/\*\*(.+?)\*\*/);
            if (b && b.index !== undefined) {
                if (b.index > 0) parts.push(rem.slice(0, b.index));
                parts.push(<strong key={k++} className="font-semibold" style={{ color: 'var(--text-primary)' }}>{b[1]}</strong>);
                rem = rem.slice(b.index + b[0].length); continue;
            }
            parts.push(rem); break;
        }
        return parts;
    };
    return (
        <>
            {lines.map((line, i) => {
                if (line.startsWith('### ')) return <h4 key={i} className="text-sm font-bold mt-4 mb-1.5" style={{ color: 'var(--primary)' }}>{renderInline(line.slice(4))}</h4>;
                if (line.startsWith('## '))  return <h3 key={i} className="text-base font-bold mt-5 mb-2 pb-1.5" style={{ color: 'var(--text-primary)', borderBottom: '1px solid var(--border)' }}>{renderInline(line.slice(3))}</h3>;
                if (line.startsWith('# '))   return <h2 key={i} className="text-lg font-bold mt-5 mb-2" style={{ color: 'var(--text-primary)' }}>{renderInline(line.slice(2))}</h2>;
                if (line.trim() === '---')   return <hr key={i} className="my-4" style={{ borderColor: 'var(--border)' }} />;
                if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
                    return (
                        <div key={i} className="flex items-start gap-2 mb-1 ml-2">
                            <span className="mt-1.5 text-[10px] shrink-0" style={{ color: 'var(--primary)' }}>◆</span>
                            <span className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{renderInline(line.trim().slice(2))}</span>
                        </div>
                    );
                }
                if (/^\d+\.\s/.test(line.trim())) {
                    const num = line.trim().match(/^(\d+)\./)?.[1];
                    const ct  = line.trim().replace(/^\d+\.\s/, '');
                    return (
                        <div key={i} className="flex items-start gap-2.5 mb-1.5 ml-2">
                            <span className="font-bold text-xs min-w-[18px] font-mono" style={{ color: 'var(--primary)' }}>{num}.</span>
                            <span className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{renderInline(ct)}</span>
                        </div>
                    );
                }
                if (line.trim() === '') return <div key={i} className="h-2" />;
                return <p key={i} className="text-sm leading-relaxed mb-1.5" style={{ color: 'var(--text-secondary)' }}>{renderInline(line)}</p>;
            })}
        </>
    );
};

// ── Evidence chunk card ───────────────────────────────────────────────────
const EvidenceChunk = ({ chunk, index }) => {
    const [open, setOpen] = useState(false);
    return (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.05 }}
            className="rounded-xl overflow-hidden" style={{ border: '1px solid var(--border)', background: 'var(--surface-subtle)' }}>
            <button onClick={() => setOpen(!open)}
                className="w-full flex items-center justify-between px-4 py-3 transition-colors text-left hover:bg-[var(--surface-subtle)]">
                <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded-full"
                        style={{ color: 'var(--primary)', background: 'rgba(58,12,163,0.08)' }}>SRC {index + 1}</span>
                    <span className="text-xs truncate max-w-[200px]" style={{ color: 'var(--text-muted)' }}>{chunk.slice(0, 60)}…</span>
                </div>
                {open ? <ChevronUp size={13} style={{ color: 'var(--text-muted)' }} /> : <ChevronDown size={13} style={{ color: 'var(--text-muted)' }} />}
            </button>
            <AnimatePresence>
                {open && (
                    <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.2 }}
                        className="px-4 pb-4 text-xs font-mono leading-relaxed" style={{ borderTop: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                        <div className="pt-3">{chunk}</div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

// ── Reports page ─────────────────────────────────────────────────────────
const Reports = () => {
    const [report, setReport] = useState(null);
    const [showDifferential, setShowDifferential] = useState(true);
    const [showKG, setShowKG] = useState(false);

    useEffect(() => {
        const stored = localStorage.getItem('lastReport');
        if (stored) { try { setReport(JSON.parse(stored)); } catch {} }
    }, []);

    const handleExport = () => {
        toast.success('Export feature coming soon — PDF generation in progress.');
    };

    if (!report) return (
        <div className="flex flex-col items-center justify-center py-24 text-center animate-fade-up">
            <div className="w-20 h-20 rounded-full flex items-center justify-center mb-5"
                style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}>
                <Search size={28} style={{ color: 'var(--text-muted)' }} />
            </div>
            <h2 className="heading-lg mb-2">No Report Active</h2>
            <p className="text-sm max-w-xs" style={{ color: 'var(--text-muted)' }}>
                Run a diagnosis through the Upload engine to view the RAG reasoning report here.
            </p>
        </div>
    );

    const rawConf = report?.confidence_score ?? report?.confidence_calibration?.overall_confidence ?? 0;
    const confPct = rawConf <= 1.0 ? rawConf * 100 : rawConf;
    const rawRisk = report?.risk_score ?? 0;
    const riskPct = rawRisk <= 1.0 ? rawRisk * 100 : rawRisk;
    const riskLevel = report?.risk_level ?? (riskPct > 70 ? 'High' : riskPct > 40 ? 'Medium' : 'Low');
    const hallScore = report?.hallucination_score ?? 0;
    const hallPassed = hallScore < 0.5;
    const specialty = report?.recommended_specialty ?? 'General';
    const differentials = report?.differential_diagnosis ?? [];
    const evidence = report?.evidence ?? '';
    const evidenceChunks = evidence.split('\n\n').filter(c => c.trim().length > 10);
    const diagnosisText = report?.final_report || report?.diagnosis || 'No diagnosis generated.';
    const emergencyFlag = report?.emergency_flag ?? false;

    const confColor = confPct >= 75 ? 'var(--success)' : confPct >= 50 ? 'var(--warning)' : 'var(--error)';

    return (
        <>
            <KnowledgeGraphOverlay visible={showKG} onClose={() => setShowKG(false)}
                query={report?.query || ''} diagnosis={diagnosisText} evidence={evidence} />

            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }} className="space-y-5 pb-12">

                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-xl" style={{ background: 'rgba(58,12,163,0.08)', border: '1px solid rgba(58,12,163,0.15)' }}>
                                <FileText size={18} style={{ color: 'var(--primary)' }} />
                            </div>
                            <h1 className="heading-lg">Diagnosis Report</h1>
                        </div>
                        <p className="text-xs mt-1 ml-12" style={{ color: 'var(--text-muted)' }}>Generated by MedRAG Orchestrator · gpt-5.4-mini</p>
                    </div>
                    <div className="flex items-center gap-2 flex-wrap">
                        {specialty !== 'General' && (
                            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs"
                                style={{ background: 'var(--info-bg)', border: '1px solid rgba(52,152,219,0.2)' }}>
                                <Stethoscope size={11} style={{ color: 'var(--info)' }} />
                                <span className="font-medium" style={{ color: 'var(--info)' }}>{specialty}</span>
                            </div>
                        )}
                        <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                            onClick={() => setShowKG(true)} className="btn-ghost flex items-center gap-1.5 text-xs">
                            <Network size={11} style={{ color: 'var(--primary)' }} /> Knowledge Graph
                        </motion.button>
                        <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                            onClick={handleExport} className="btn-ghost flex items-center gap-1.5 text-xs">
                            <Download size={11} /> Export PDF
                        </motion.button>
                    </div>
                </div>

                {/* Emergency banner */}
                {emergencyFlag && (
                    <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }}
                        className="rounded-xl p-4 flex items-center gap-3"
                        style={{ background: 'var(--error-bg)', border: '1px solid rgba(231,76,60,0.3)' }}>
                        <AlertTriangle size={20} className="animate-pulse shrink-0" style={{ color: 'var(--error)' }} />
                        <div>
                            <p className="font-bold text-sm" style={{ color: 'var(--error)' }}>Emergency Flag Triggered</p>
                            <p className="text-xs mt-0.5" style={{ color: 'var(--error)', opacity: 0.8 }}>Critical symptoms detected. Seek immediate medical attention.</p>
                        </div>
                    </motion.div>
                )}

                {/* KPI cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bento-card p-5">
                        <p className="label-caps mb-4">Engine Confidence</p>
                        <div className="flex items-end gap-2 mb-3">
                            <span className="text-5xl font-black tracking-tighter" style={{ color: confColor }}>{confPct.toFixed(0)}</span>
                            <span className="text-lg mb-1" style={{ color: 'var(--text-muted)' }}>%</span>
                        </div>
                        <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--surface-subtle)' }}>
                            <motion.div className="h-full rounded-full" initial={{ width: 0 }}
                                animate={{ width: `${Math.min(confPct, 100)}%` }}
                                transition={{ duration: 1, ease: 'easeOut', delay: 0.3 }} style={{ background: confColor }} />
                        </div>
                        <div className="mt-3"><ConfidenceBadge score={confPct} size="sm" /></div>
                    </div>

                    <div className="bento-card p-5">
                        <p className="label-caps mb-4">Hallucination Audit</p>
                        <div className="flex items-center gap-3 mb-3">
                            {hallPassed ? <ShieldCheck size={28} style={{ color: 'var(--success)' }} /> : <ShieldAlert size={28} style={{ color: 'var(--warning)' }} />}
                            <div>
                                <p className="font-bold text-sm" style={{ color: hallPassed ? 'var(--success)' : '#B8860B' }}>
                                    {hallPassed ? 'Verified ✓' : 'Review Suggested'}
                                </p>
                                <p className="text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>Score: {(hallScore * 100).toFixed(1)}%</p>
                            </div>
                        </div>
                        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                            {hallPassed ? 'All claims grounded in retrieved evidence.' : 'Some claims extend beyond retrieved context.'}
                        </p>
                    </div>

                    <RiskScoreCard score={riskPct} level={riskLevel} />
                </div>

                {/* Diagnosis + Evidence sidebar */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
                    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }} className="lg:col-span-8 bento-card flex flex-col">
                        <div className="flex items-center justify-between px-6 py-4" style={{ borderBottom: '1px solid var(--border)' }}>
                            <div className="flex items-center gap-3">
                                <div className="w-1 h-5 rounded-full" style={{ background: 'var(--primary)' }} />
                                <h2 className="font-bold text-sm" style={{ color: 'var(--text-primary)' }}>Synthesized Clinical Evaluation</h2>
                            </div>
                            <ConfidenceBadge score={confPct} size="sm" />
                        </div>
                        <div className="p-6 flex-1 overflow-y-auto max-h-[600px]">
                            <MarkdownRenderer text={diagnosisText} />
                        </div>
                    </motion.div>

                    <div className="lg:col-span-4 space-y-4">
                        {report?.query && (
                            <div className="bento-card p-4">
                                <p className="label-caps mb-2">Clinical Query</p>
                                <p className="text-sm italic leading-relaxed" style={{ color: 'var(--text-secondary)' }}>"{report.query}"</p>
                            </div>
                        )}

                        {evidenceChunks.length > 0 && (
                            <div className="bento-card overflow-hidden">
                                <div className="flex items-center gap-2 px-4 py-3" style={{ borderBottom: '1px solid var(--border)' }}>
                                    <BookOpen size={13} style={{ color: 'var(--primary)' }} />
                                    <span className="text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>Retrieved Evidence</span>
                                    <span className="ml-auto text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>{evidenceChunks.length} sources</span>
                                </div>
                                <div className="p-3 space-y-2 max-h-72 overflow-y-auto">
                                    {evidenceChunks.map((chunk, i) => (<EvidenceChunk key={i} chunk={chunk} index={i} />))}
                                </div>
                            </div>
                        )}

                        {report?.recommendations && (
                            <div className="bento-card p-4">
                                <p className="label-caps mb-3">Recommendations</p>
                                {report.recommendations.meal_plan && (
                                    <div className="mb-3">
                                        <p className="text-xs font-semibold mb-1" style={{ color: 'var(--success)' }}>🍽️ Meal Plan</p>
                                        <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                                            {typeof report.recommendations.meal_plan === 'object' ? JSON.stringify(report.recommendations.meal_plan.day_1 || report.recommendations.meal_plan) : report.recommendations.meal_plan}
                                        </p>
                                    </div>
                                )}
                                {report.recommendations.activity_plan && (
                                    <div>
                                        <p className="text-xs font-semibold mb-1" style={{ color: 'var(--primary)' }}>🏃 Activity Plan</p>
                                        <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                                            {typeof report.recommendations.activity_plan === 'object' ? report.recommendations.activity_plan.daily_goal || JSON.stringify(report.recommendations.activity_plan) : report.recommendations.activity_plan}
                                        </p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {/* Differential Diagnosis */}
                {differentials.length > 0 && (
                    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }} className="bento-card overflow-hidden">
                        <button onClick={() => setShowDifferential(!showDifferential)}
                            className="w-full flex items-center justify-between px-6 py-4 transition-colors hover:bg-[var(--surface-subtle)]"
                            style={{ borderBottom: showDifferential ? '1px solid var(--border)' : 'none' }}>
                            <div className="flex items-center gap-3">
                                <Star size={15} style={{ color: 'var(--warning)' }} />
                                <span className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Differential Diagnosis</span>
                                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full" style={{ color: 'var(--text-muted)', background: 'var(--surface-subtle)' }}>
                                    {differentials.length} conditions
                                </span>
                            </div>
                            <motion.div animate={{ rotate: showDifferential ? 180 : 0 }} transition={{ duration: 0.2 }}>
                                <ChevronDown size={14} style={{ color: 'var(--text-muted)' }} />
                            </motion.div>
                        </button>
                        <AnimatePresence>
                            {showDifferential && (
                                <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.25 }}
                                    className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 p-4">
                                    {differentials.map((diff, i) => {
                                        const prob = (diff.probability ?? 0) * 100;
                                        const color = prob >= 60 ? 'var(--success)' : prob >= 35 ? 'var(--warning)' : 'var(--text-muted)';
                                        return (
                                            <motion.div key={i} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
                                                transition={{ delay: i * 0.05, type: 'spring', stiffness: 300 }}
                                                className="rounded-xl p-4" style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}>
                                                <div className="flex items-start justify-between mb-3">
                                                    <span className="text-xs font-bold font-mono" style={{ color: 'var(--text-muted)' }}>#{i + 1}</span>
                                                    <span className="text-xs font-bold font-mono" style={{ color }}>{prob.toFixed(0)}%</span>
                                                </div>
                                                <p className="text-sm font-semibold leading-snug mb-3" style={{ color: 'var(--text-primary)' }}>
                                                    {diff.condition || diff.name || JSON.stringify(diff)}
                                                </p>
                                                <div className="w-full h-1 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
                                                    <motion.div className="h-full rounded-full" initial={{ width: 0 }}
                                                        animate={{ width: `${prob}%` }}
                                                        transition={{ duration: 0.8, delay: i * 0.1, ease: 'easeOut' }} style={{ background: color }} />
                                                </div>
                                            </motion.div>
                                        );
                                    })}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.div>
                )}
            </motion.div>
        </>
    );
};

export default Reports;
