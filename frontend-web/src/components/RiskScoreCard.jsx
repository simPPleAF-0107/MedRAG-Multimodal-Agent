import React from 'react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

const RiskScoreCard = ({ score, level }) => {
    // Determine gradient and colors based on Risk Level
    let bgGradient = "from-success/10 to-success/5";
    let textColor = "text-success";
    let ringColor = "ring-success/20";
    let Icon = CheckCircle2;

    if (level === "High") {
        bgGradient = "from-danger/10 to-danger/5";
        textColor = "text-danger";
        ringColor = "ring-danger/20";
        Icon = AlertCircle;
    } else if (level === "Medium") {
        bgGradient = "from-warning/10 to-warning/5";
        textColor = "text-warning";
        ringColor = "ring-warning/20";
        Icon = AlertCircle;
    }

    return (
        <div className={`bg-white rounded-xl border border-slate-200 shadow-sm p-5 relative overflow-hidden`}>
            <div className={`absolute -right-4 -top-4 w-24 h-24 rounded-full bg-gradient-to-br ${bgGradient} blur-2xl opacity-50`}></div>

            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Patient Risk Score</h3>
                    <p className="text-xs text-slate-400 mt-0.5">Calculated by MedRAG Engine</p>
                </div>
                <div className={`p-2 rounded-lg bg-white ring-1 ring-inset ${ringColor}`}>
                    <Icon className={`w-5 h-5 ${textColor}`} />
                </div>
            </div>

            <div className="flex items-end space-x-2">
                <span className={`text-4xl font-bold tracking-tight ${textColor}`}>{score}</span>
                <span className="text-slate-500 font-medium mb-1">/ 100</span>
            </div>

            <div className="mt-4">
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                        className={`h-2 rounded-full ${textColor.replace('text-', 'bg-')}`}
                        style={{ width: `${score}%` }}
                    ></div>
                </div>
                <p className={`text-sm font-medium mt-2 ${textColor} flex items-center`}>
                    {level} Risk Profile
                </p>
            </div>
        </div>
    );
};

export default RiskScoreCard;
