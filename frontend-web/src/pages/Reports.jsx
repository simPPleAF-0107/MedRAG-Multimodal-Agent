import React, { useEffect, useState, useMemo } from 'react';
import {
    FileText, ShieldCheck, ShieldAlert, Activity, GitCommit, Search, List,
    AlertTriangle, Star, Stethoscope, BookOpen, ChevronDown, ChevronUp
} from 'lucide-react';
import RiskScoreCard from '../components/RiskScoreCard';

// Simple markdown-to-JSX renderer for medical reports
const MarkdownRenderer = ({ text }) => {
    if (!text) return null;

    const lines = text.split('\n');
    const elements = [];
    let i = 0;

    while (i < lines.length) {
        const line = lines[i];

        // Headers
        if (line.startsWith('### ')) {
            elements.push(<h4 key={i} className="text-base font-bold text-brand-400 mt-5 mb-2">{renderInline(line.slice(4))}</h4>);
        } else if (line.startsWith('## ')) {
            elements.push(<h3 key={i} className="text-lg font-bold text-white mt-6 mb-3 border-b border-white/10 pb-2">{renderInline(line.slice(3))}</h3>);
        } else if (line.startsWith('# ')) {
            elements.push(<h2 key={i} className="text-xl font-bold text-white mt-6 mb-3">{renderInline(line.slice(2))}</h2>);
        }
        // Horizontal rule
        else if (line.trim() === '---') {
            elements.push(<hr key={i} className="border-white/10 my-4" />);
        }
        // List items
        else if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
            const indent = line.search(/\S/);
            const content = line.trim().slice(2);
            elements.push(
                <div key={i} className={`flex items-start gap-2 mb-1 ${indent > 2 ? 'ml-6' : 'ml-2'}`}>
                    <span className="text-brand-500 mt-1.5 text-xs">●</span>
                    <span className="text-slate-300 leading-relaxed">{renderInline(content)}</span>
                </div>
            );
        }
        // Numbered items
        else if (/^\d+\.\s/.test(line.trim())) {
            const content = line.trim().replace(/^\d+\.\s/, '');
            const num = line.trim().match(/^(\d+)\./)?.[1];
            elements.push(
                <div key={i} className="flex items-start gap-3 mb-2 ml-2">
                    <span className="text-brand-400 font-bold text-sm min-w-[20px]">{num}.</span>
                    <span className="text-slate-300 leading-relaxed">{renderInline(content)}</span>
                </div>
            );
        }
        // Empty line = paragraph break
        else if (line.trim() === '') {
            elements.push(<div key={i} className="h-2" />);
        }
        // Regular paragraph
        else {
            elements.push(<p key={i} className="text-slate-300 leading-relaxed mb-2">{renderInline(line)}</p>);
        }
        i++;
    }
    return <>{elements}</>;
};

// Inline markdown (bold, italic, code)
function renderInline(text) {
    if (!text) return text;
    const parts = [];
    let remaining = text;
    let key = 0;

    while (remaining.length > 0) {
        // Bold
        const boldMatch = remaining.match(/\*\*(.+?)\*\*/);
        if (boldMatch && boldMatch.index !== undefined) {
            if (boldMatch.index > 0) parts.push(remaining.slice(0, boldMatch.index));
            parts.push(<strong key={key++} className="text-white font-semibold">{boldMatch[1]}</strong>);
            remaining = remaining.slice(boldMatch.index + boldMatch[0].length);
            continue;
        }
        parts.push(remaining);
        break;
    }
    return parts;
}

const Reports = () => {
    const [report, setReport] = useState(null);
    const [showEvidence, setShowEvidence] = useState(false);
    const [showDifferential, setShowDifferential] = useState(false);

    useEffect(() => {
        const stored = localStorage.getItem('lastReport');
        if (stored) {
            try {
                const parsed = JSON.parse(stored);
                setReport(parsed);
                console.log("Report data:", parsed);
            } catch (e) {
                console.error("Failed to parse report:", e);
            }
        }
    }, []);

    if (!report) {
        return (
            <div className="flex flex-col items-center justify-center p-16 text-center animate-fade-in">
                <div className="p-6 bg-white/5 rounded-full mb-4 border border-white/10">
                    <Search className="w-12 h-12 text-slate-500" />
                </div>
                <h2 className="text-xl font-semibold text-white">No Active Report Selected</h2>
                <p className="text-slate-400 mt-2">Run a new diagnosis through the Upload engine to view detailed RAG reasoning here.</p>
            </div>
        );
    }

    // Confidence
    const rawConf = report?.confidence_score ?? report?.confidence_calibration?.overall_confidence ?? 0;
    const confidencePercent = rawConf <= 1.0 ? rawConf * 100 : rawConf;
    const isHighConfidence = confidencePercent > 70;
    const isMediumConfidence = confidencePercent > 50;
    const confidenceScore = confidencePercent.toFixed(1);
    const confidenceColor = isHighConfidence ? 'text-success' : isMediumConfidence ? 'text-yellow-400' : 'text-warning';
    const confidenceBorder = isHighConfidence ? 'border-success/30' : isMediumConfidence ? 'border-yellow-400/30' : 'border-warning/30';
    const confidenceGlow = isHighConfidence ? 'bg-success' : isMediumConfidence ? 'bg-yellow-400' : 'bg-warning';

    // Risk
    const rawRisk = report?.risk_score ?? 0;
    const riskPercent = rawRisk <= 1.0 ? rawRisk * 100 : rawRisk;
    const riskLevel = report?.risk_level ?? report?.risk_assessment?.risk_level ?? (riskPercent > 70 ? 'High' : riskPercent > 40 ? 'Medium' : 'Low');

    // Emergency
    const emergencyFlag = report?.emergency_flag ?? false;

    // Hallucination
    const hallScore = report?.hallucination_score ?? 0;
    const hallPassed = hallScore < 0.5;

    // Specialty
    const specialty = report?.recommended_specialty ?? 'General';

    // Differential diagnosis
    const differentials = report?.differential_diagnosis ?? [];

    // Evidence
    const evidence = report?.evidence ?? '';

    // Diagnosis text (from final_report or diagnosis field)
    const diagnosisText = report?.final_report || report?.diagnosis || "No diagnosis generated.";

    return (
        <div className="space-y-6 animate-fade-in pb-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white tracking-tight flex items-center">
                        <FileText className="mr-3 text-brand-500" /> Diagnosis Inference Report
                    </h1>
                    <p className="text-slate-400 mt-1">Generated by MedRAG Orchestrator</p>
                </div>
                {/* Specialty Badge */}
                {specialty !== 'General' && (
                    <div className="flex items-center gap-2 px-4 py-2 bg-brand-500/10 border border-brand-500/30 rounded-xl">
                        <Stethoscope className="w-4 h-4 text-brand-400" />
                        <span className="text-sm font-semibold text-brand-400">{specialty}</span>
                    </div>
                )}
            </div>

            {/* Emergency Banner */}
            {emergencyFlag && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-center gap-3 animate-pulse">
                    <AlertTriangle className="w-6 h-6 text-red-400" />
                    <div>
                        <p className="text-red-400 font-bold">Emergency Flag Triggered</p>
                        <p className="text-red-400/70 text-sm">Critical symptoms detected. Seek immediate medical attention.</p>
                    </div>
                </div>
            )}

            {/* Top Banner Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Confidence */}
                <div className={`glass-panel border p-5 relative overflow-hidden ${confidenceBorder}`}>
                    <div className={`absolute -right-4 -top-4 w-24 h-24 rounded-full blur-2xl opacity-20 ${confidenceGlow}`}></div>
                    <div className="flex items-center space-x-3 mb-2 text-sm font-semibold uppercase tracking-wider text-slate-400">
                        {isHighConfidence ? <ShieldCheck className="text-success w-5 h-5" /> : <ShieldAlert className="text-warning w-5 h-5" />}
                        <span>Engine Confidence</span>
                    </div>
                    <div className="flex items-end space-x-2 mt-4">
                        <span className={`text-4xl font-bold tracking-tight ${confidenceColor}`}>{confidenceScore}</span>
                        <span className="text-slate-400 font-medium mb-1">%</span>
                    </div>
                    <div className="mt-3 w-full bg-white/5 rounded-full h-1.5">
                        <div className={`h-full rounded-full ${isHighConfidence ? 'bg-success' : isMediumConfidence ? 'bg-yellow-400' : 'bg-warning'}`}
                             style={{ width: `${Math.min(confidencePercent, 100)}%`, transition: 'width 1s ease' }}></div>
                    </div>
                </div>

                {/* Hallucination */}
                <div className="glass-panel border border-white/10 p-5 flex flex-col justify-center">
                    <div className="flex items-center space-x-3 mb-2 text-sm font-semibold uppercase tracking-wider text-slate-400">
                        <GitCommit className="text-brand-500 w-5 h-5" />
                        <span>Hallucination Audit</span>
                    </div>
                    <p className="mt-2 text-lg font-medium">
                        {hallPassed ? (
                            <span className="text-success flex items-center"><ShieldCheck size={18} className="mr-2" /> Verified ✓</span>
                        ) : (
                            <span className="text-yellow-400 flex items-center"><ShieldAlert size={18} className="mr-2" /> Review Suggested</span>
                        )}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                        Score: {(hallScore * 100).toFixed(1)}% — {hallPassed ? 'Evidence-grounded diagnosis' : 'Some claims beyond retrieved evidence'}
                    </p>
                </div>

                {/* Risk */}
                <RiskScoreCard score={riskPercent} level={riskLevel} />
            </div>

            {/* Differential Diagnosis Panel */}
            {differentials.length > 0 && (
                <div className="glass-panel border border-white/10 overflow-hidden">
                    <button
                        onClick={() => setShowDifferential(!showDifferential)}
                        className="w-full px-6 py-4 bg-white/5 border-b border-white/10 flex items-center justify-between hover:bg-white/[0.07] transition-colors"
                    >
                        <h3 className="font-bold text-white flex items-center">
                            <Star className="w-5 h-5 text-yellow-400 mr-3" />
                            Differential Diagnosis ({differentials.length} conditions)
                        </h3>
                        {showDifferential ? <ChevronUp className="text-slate-400" /> : <ChevronDown className="text-slate-400" />}
                    </button>
                    {showDifferential && (
                        <div className="p-6 space-y-3">
                            {differentials.map((diff, i) => (
                                <div key={i} className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/5">
                                    <div className="flex items-center gap-3">
                                        <span className="text-brand-400 font-bold text-sm w-6">{i + 1}.</span>
                                        <span className="text-slate-200 font-medium">{diff.condition || diff.name || JSON.stringify(diff)}</span>
                                    </div>
                                    {diff.probability != null && (
                                        <div className="flex items-center gap-2">
                                            <div className="w-20 bg-white/5 rounded-full h-2">
                                                <div className="h-full bg-brand-500 rounded-full" style={{ width: `${diff.probability * 100}%` }}></div>
                                            </div>
                                            <span className="text-xs text-slate-400 w-10 text-right">{(diff.probability * 100).toFixed(0)}%</span>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Core Body */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Main Diagnosis */}
                <div className="lg:col-span-8 glass-panel border border-white/10 overflow-hidden flex flex-col">
                    <div className="px-6 py-4 bg-white/5 border-b border-white/10 flex items-center justify-between">
                        <h3 className="font-bold border-l-4 border-brand-500 pl-3 leading-none text-white">
                            Synthesized Clinical Evaluation
                        </h3>
                        {specialty !== 'General' && (
                            <span className="text-xs bg-brand-500/10 text-brand-400 px-3 py-1 rounded-full font-medium">
                                {specialty}
                            </span>
                        )}
                    </div>
                    <div className="p-6 flex-1 overflow-y-auto max-h-[700px]">
                        <MarkdownRenderer text={
                            report?.diagnosis || report?.final_report || "No diagnosis generated."
                        } />
                    </div>
                </div>

                {/* Right Sidebar */}
                <div className="lg:col-span-4 space-y-6">
                    {/* Original Query */}
                    <div className="glass-panel border border-white/10 p-5">
                        <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Original Clinical Query</h4>
                        <p className="text-sm font-medium text-slate-300 italic">"{report?.query || '—'}"</p>
                    </div>

                    {/* Evidence Sources */}
                    <div className="glass-panel border border-white/10 overflow-hidden flex flex-col">
                        <button
                            onClick={() => setShowEvidence(!showEvidence)}
                            className="px-5 py-3 bg-white/5 border-b border-white/10 flex items-center justify-between hover:bg-white/[0.07] transition-colors"
                        >
                            <span className="font-semibold text-sm text-slate-300 flex items-center">
                                <BookOpen className="w-4 h-4 mr-2" /> Retrieved Evidence
                            </span>
                            {showEvidence ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                        </button>
                        {showEvidence && (
                            <div className="p-4 overflow-y-auto max-h-[400px] text-xs text-slate-400 space-y-3 whitespace-pre-wrap leading-relaxed font-mono">
                                {evidence && evidence.length > 10 ? (
                                    evidence.split('\n\n').map((chunk, i) => (
                                        <div key={i} className="p-3 bg-white/5 rounded-lg border border-white/5">
                                            <div className="text-[10px] text-brand-400 font-bold mb-1">Source {i + 1}</div>
                                            {chunk}
                                        </div>
                                    ))
                                ) : (
                                    <p className="text-slate-500 italic">Diagnosis based on LLM medical knowledge. No matching vector context was retrieved.</p>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Recommendations */}
                    {report?.recommendations && (
                        <div className="glass-panel border border-white/10 p-5">
                            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Recommendations</h4>
                            {report.recommendations.meal_plan && (
                                <div className="mb-3">
                                    <p className="text-xs text-brand-400 font-semibold mb-1">🍽️ Meal Plan</p>
                                    <p className="text-xs text-slate-400">
                                        {typeof report.recommendations.meal_plan === 'object'
                                            ? JSON.stringify(report.recommendations.meal_plan.day_1 || report.recommendations.meal_plan)
                                            : report.recommendations.meal_plan}
                                    </p>
                                </div>
                            )}
                            {report.recommendations.activity_plan && (
                                <div>
                                    <p className="text-xs text-brand-400 font-semibold mb-1">🏃 Activity Plan</p>
                                    <p className="text-xs text-slate-400">
                                        {typeof report.recommendations.activity_plan === 'object'
                                            ? report.recommendations.activity_plan.daily_goal || JSON.stringify(report.recommendations.activity_plan)
                                            : report.recommendations.activity_plan}
                                    </p>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Reports;
