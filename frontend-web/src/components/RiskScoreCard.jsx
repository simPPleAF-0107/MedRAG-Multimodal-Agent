import React from 'react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';

const RiskScoreCard = ({ score, level }) => {
    // Determine gradient and colors based on Risk Level
    let bgGradient = "from-emerald-500/20 to-emerald-500/5";
    let textColor = "text-emerald-400";
    let ringColor = "border-emerald-500/30";
    let barColor = "bg-emerald-500";
    let Icon = CheckCircle2;

    if (level === "High") {
        bgGradient = "from-red-500/20 to-red-500/5";
        textColor = "text-red-400";
        ringColor = "border-red-500/30";
        barColor = "bg-red-500";
        Icon = AlertCircle;
    } else if (level === "Medium") {
        bgGradient = "from-amber-500/20 to-amber-500/5";
        textColor = "text-amber-400";
        ringColor = "border-amber-500/30";
        barColor = "bg-amber-500";
        Icon = AlertCircle;
    }

    return (
        <div className="glass-panel rounded-xl border border-white/5 shadow-lg p-6 relative overflow-hidden group hover:border-white/10 transition-all duration-500 hover:-translate-y-1">
            <div className={`absolute -right-8 -top-8 w-32 h-32 rounded-full bg-gradient-to-br ${bgGradient} blur-2xl opacity-70 group-hover:opacity-100 transition-opacity duration-500`}></div>

            <div className="flex justify-between items-start mb-6 relative z-10">
                <div>
                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Patient Risk Score</h3>
                    <p className="text-xs text-brand-500 mt-1 font-medium">Calculated by MedRAG Engine</p>
                </div>
                <div className={`p-2.5 rounded-xl bg-white/5 border shadow-inner ${ringColor} group-hover:scale-110 transition-transform`}>
                    <Icon className={`w-6 h-6 ${textColor}`} />
                </div>
            </div>

            <div className="flex items-end space-x-2 relative z-10 mb-5">
                <span className={`text-6xl font-black tracking-tighter drop-shadow-md ${textColor}`}>{score}</span>
                <span className="text-slate-500 font-bold mb-1.5 text-xl">/ 100</span>
            </div>

            <div className="mt-auto relative z-10">
                <div className="w-full bg-white/5 rounded-full h-2.5 border border-white/10 overflow-hidden shadow-inner">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${score}%` }}
                        transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
                        className={`h-full rounded-full ${barColor} shadow-[0_0_10px_currentColor]`}
                    />
                </div>
                <p className={`text-sm font-bold mt-4 ${textColor} flex items-center bg-white/5 inline-flex px-3 py-1 rounded-md border ${ringColor}`}>
                    {level} Risk Profile
                </p>
            </div>
        </div>
    );
};

export default RiskScoreCard;
