import React, { useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const ScanningCard = ({ icon, title, subtitle, accept, accentColor = 'var(--primary)', onFile, multiple = false }) => {
    const inputRef = useRef(null);
    const [scanning, setScanning] = useState(false);
    const [entities, setEntities] = useState([]);

    const handleClick = () => inputRef.current?.click();

    const handleChange = (e) => {
        const files = Array.from(e.target.files);
        if (files.length === 0) return;
        setScanning(true);
        setEntities([]);
        setTimeout(() => {
            const chips = files.map(f => f.name.split('.')[0].replace(/[_-]/g, ' '));
            setEntities(chips);
            setScanning(false);
            if (onFile) onFile(multiple ? files : files[0]);
        }, 1200);
    };

    return (
        <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="bento-card p-6 scan-container cursor-pointer flex flex-col items-center text-center gap-4"
            onClick={handleClick}
            style={{ borderColor: scanning ? accentColor : undefined }}
        >
            <input ref={inputRef} type="file" accept={accept} className="hidden" onChange={handleChange} multiple={multiple} />

            {/* Icon container */}
            <div className="p-4 rounded-2xl" style={{ background: accentColor + '10', border: `1px solid ${accentColor}25` }}>
                <div style={{ color: accentColor }}>
                    {React.cloneElement(icon, { size: 28 })}
                </div>
            </div>

            <div>
                <p className="font-bold text-sm" style={{ color: 'var(--text-primary)' }}>{title}</p>
                <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{subtitle}</p>
            </div>

            {/* Browse button */}
            <div className="text-xs font-medium px-4 py-2 rounded-lg" style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                Browse files
            </div>

            {/* Scan line */}
            <AnimatePresence>
                {scanning && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="scan-line animate-scan-line"
                        style={{ background: `linear-gradient(90deg, transparent, ${accentColor}, transparent)`, boxShadow: `0 0 8px ${accentColor}80` }}
                    />
                )}
            </AnimatePresence>

            {/* Entity chips */}
            {entities.length > 0 && (
                <div className="flex flex-wrap gap-1.5 justify-center">
                    {entities.map((e, i) => (
                        <motion.span key={i} initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: i * 0.1 }} className="entity-chip text-[10px]">{e}</motion.span>
                    ))}
                </div>
            )}
        </motion.div>
    );
};

export default ScanningCard;
