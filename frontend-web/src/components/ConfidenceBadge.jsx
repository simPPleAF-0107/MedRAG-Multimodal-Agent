import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle } from 'lucide-react';

const ConfidenceBadge = ({ score, size = 'md', showShimmer = true }) => {
    const pct = score <= 1 ? score * 100 : score;

    let badgeClass, Icon, label;
    if (pct >= 75) {
        badgeClass = 'badge-success';
        Icon = ShieldCheck;
        label = 'High Confidence';
    } else if (pct >= 50) {
        badgeClass = 'badge-warning';
        Icon = ShieldAlert;
        label = 'Follow-up Needed';
    } else {
        badgeClass = 'badge-error';
        Icon = AlertTriangle;
        label = 'Low Confidence';
    }

    const sizeClasses = size === 'sm' ? 'text-[11px] px-2.5 py-0.5' : 'text-xs px-3 py-1';

    return (
        <span className={`${badgeClass} ${sizeClasses}`}>
            <Icon size={size === 'sm' ? 11 : 13} />
            <span>{pct.toFixed(1)}%</span>
            {size !== 'sm' && <span className="hidden sm:inline">· {label}</span>}
        </span>
    );
};

export default ConfidenceBadge;
