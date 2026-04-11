import React from 'react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';

const RiskScoreCard = ({ score, level }) => {
    let accentColor = 'var(--success)';
    let accentBg = 'var(--success-bg)';
    let Icon = CheckCircle2;

    if (level === 'High') {
        accentColor = 'var(--error)'; accentBg = 'var(--error-bg)'; Icon = AlertCircle;
    } else if (level === 'Medium') {
        accentColor = 'var(--warning)'; accentBg = 'var(--warning-bg)'; Icon = AlertCircle;
    }

    return (
        <div className="bento-card p-6 relative overflow-hidden group">
            {/* Accent glow */}
            <div className="absolute -right-8 -top-8 w-32 h-32 rounded-full blur-2xl opacity-30 group-hover:opacity-50 transition-opacity"
                style={{ background: accentColor }} />

            <div className="flex justify-between items-start mb-6 relative z-10">
                <div>
                    <h3 className="label-caps">Patient Risk Score</h3>
                    <p className="text-xs mt-1 font-medium" style={{ color: 'var(--primary)' }}>Calculated by MedRAG Engine</p>
                </div>
                <div className="p-2.5 rounded-xl border transition-transform group-hover:scale-110"
                    style={{ background: accentBg, borderColor: accentColor + '30' }}>
                    <Icon className="w-6 h-6" style={{ color: accentColor }} />
                </div>
            </div>

            <div className="flex items-end space-x-2 relative z-10 mb-5">
                <span className="text-6xl font-black tracking-tighter" style={{ color: accentColor }}>{score}</span>
                <span className="font-bold mb-1.5 text-xl" style={{ color: 'var(--text-muted)' }}>/ 100</span>
            </div>

            <div className="relative z-10">
                <div className="w-full rounded-full h-2.5 overflow-hidden" style={{ background: 'var(--surface-subtle)' }}>
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${score}%` }}
                        transition={{ duration: 1, delay: 0.2, ease: 'easeOut' }}
                        className="h-full rounded-full"
                        style={{ background: accentColor }}
                    />
                </div>
                <p className="text-sm font-bold mt-4 inline-flex items-center px-3 py-1 rounded-md border"
                    style={{ color: accentColor, background: accentBg, borderColor: accentColor + '30' }}>
                    {level} Risk Profile
                </p>
            </div>
        </div>
    );
};

export default RiskScoreCard;
