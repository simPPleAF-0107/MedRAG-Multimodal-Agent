import React from 'react';
import { Activity, ShieldCheck, ShieldAlert, ChevronRight } from 'lucide-react';

const ReportCard = ({ report, onClick }) => {
    const isHighConfidence = report?.confidence_calibration?.overall_confidence > 70;

    return (
        <div
            className="bento-card cursor-pointer group"
            onClick={onClick}
        >
            <div className="p-5 relative z-10">
                <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 rounded-xl transition-colors"
                            style={{ background: 'rgba(58,12,163,0.06)', border: '1px solid rgba(58,12,163,0.12)' }}>
                            <Activity className="w-5 h-5" style={{ color: 'var(--primary)' }} />
                        </div>
                        <h3 className="font-bold tracking-wide truncate pr-4 transition-colors"
                            style={{ color: 'var(--text-primary)' }}>
                            Diagnostic Report
                        </h3>
                    </div>
                    <span className="text-xs font-medium whitespace-nowrap px-2 py-1 rounded-md"
                        style={{ color: 'var(--text-muted)', background: 'var(--surface-subtle)' }}>
                        {new Date().toLocaleDateString()}
                    </span>
                </div>

                <p className="text-sm line-clamp-3 mb-5 leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                    {report.final_report || report.diagnosis_reasoning || 'No diagnosis logic available.'}
                </p>

                <div className="flex items-center justify-between pt-4 mt-auto" style={{ borderTop: '1px solid var(--border)' }}>
                    <div className="flex items-center space-x-2 px-2 py-1 rounded-md" style={{ background: isHighConfidence ? 'var(--success-bg)' : 'var(--warning-bg)' }}>
                        {isHighConfidence
                            ? <ShieldCheck className="w-4 h-4" style={{ color: 'var(--success)' }} />
                            : <ShieldAlert className="w-4 h-4" style={{ color: 'var(--warning)' }} />}
                        <span className="text-xs font-bold" style={{ color: isHighConfidence ? 'var(--success)' : '#B8860B' }}>
                            {report?.confidence_calibration?.overall_confidence?.toFixed(1) || 0}% Conf.
                        </span>
                    </div>
                    <div className="flex items-center text-xs font-bold opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-x-2 group-hover:translate-x-0"
                        style={{ color: 'var(--primary)' }}>
                        View Details <ChevronRight className="w-4 h-4 ml-1" />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ReportCard;
