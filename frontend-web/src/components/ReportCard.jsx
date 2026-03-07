import React from 'react';
import { Activity, ShieldCheck, ShieldAlert, ChevronRight } from 'lucide-react';

const ReportCard = ({ report, onClick }) => {
    const isHighConfidence = report?.confidence_calibration?.overall_confidence > 70;

    return (
        <div
            className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer group"
            onClick={onClick}
        >
            <div className="p-5">
                <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center space-x-2">
                        <div className="p-1.5 bg-brand-50 rounded-lg">
                            <Activity className="w-5 h-5 text-brand-600" />
                        </div>
                        <h3 className="font-semibold text-slate-900 truncate pr-4">
                            Diagnostic Report
                        </h3>
                    </div>
                    <span className="text-xs font-medium text-slate-400 whitespace-nowrap">
                        {new Date().toLocaleDateString()}
                    </span>
                </div>

                <p className="text-sm text-slate-600 line-clamp-3 mb-4 leading-relaxed">
                    {report.final_report || report.diagnosis_reasoning || "No diagnosis logic available."}
                </p>

                <div className="flex items-center justify-between pt-4 border-t border-slate-100 mt-auto">
                    <div className="flex items-center space-x-1.5">
                        {isHighConfidence ? (
                            <ShieldCheck className="w-4 h-4 text-success" />
                        ) : (
                            <ShieldAlert className="w-4 h-4 text-warning" />
                        )}
                        <span className={`text-xs font-medium ${isHighConfidence ? 'text-success' : 'text-warning'}`}>
                            {report?.confidence_calibration?.overall_confidence?.toFixed(1) || 0}% Conf.
                        </span>
                    </div>
                    <div className="flex items-center text-xs font-medium text-brand-600 opacity-0 group-hover:opacity-100 transition-opacity">
                        View Details <ChevronRight className="w-4 h-4 ml-0.5" />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ReportCard;
