import React from 'react';
import { Activity, ShieldCheck, ShieldAlert, ChevronRight } from 'lucide-react';

const ReportCard = ({ report, onClick }) => {
    const isHighConfidence = report?.confidence_calibration?.overall_confidence > 70;

    return (
        <div
            className="glass-panel border border-white/5 hover:border-brand-500/50 shadow-lg hover:shadow-[0_0_20px_rgba(69,243,255,0.15)] transition-all duration-300 cursor-pointer group rounded-xl overflow-hidden relative"
            onClick={onClick}
        >
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <div className="p-5 relative z-10">
                <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-brand-500/10 rounded-xl border border-brand-500/20 group-hover:bg-brand-500/20 transition-colors">
                            <Activity className="w-5 h-5 text-brand-400" />
                        </div>
                        <h3 className="font-bold text-white tracking-wide truncate pr-4 group-hover:text-brand-300 transition-colors">
                            Diagnostic Report
                        </h3>
                    </div>
                    <span className="text-xs font-medium text-slate-500 whitespace-nowrap bg-white/5 px-2 py-1 rounded-md">
                        {new Date().toLocaleDateString()}
                    </span>
                </div>

                <p className="text-sm text-slate-400 line-clamp-3 mb-5 leading-relaxed">
                    {report.final_report || report.diagnosis_reasoning || "No diagnosis logic available."}
                </p>

                <div className="flex items-center justify-between pt-4 border-t border-white/5 mt-auto">
                    <div className="flex items-center space-x-2 bg-white/5 px-2 py-1 rounded-md">
                        {isHighConfidence ? (
                            <ShieldCheck className="w-4 h-4 text-emerald-400" />
                        ) : (
                            <ShieldAlert className="w-4 h-4 text-amber-400" />
                        )}
                        <span className={`text-xs font-bold ${isHighConfidence ? 'text-emerald-400' : 'text-amber-400'}`}>
                            {report?.confidence_calibration?.overall_confidence?.toFixed(1) || 0}% Conf.
                        </span>
                    </div>
                    <div className="flex items-center text-xs font-bold text-brand-400 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-x-2 group-hover:translate-x-0">
                        View Details <ChevronRight className="w-4 h-4 ml-1" />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ReportCard;
