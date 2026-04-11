import React, { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Network } from 'lucide-react';

const KnowledgeGraphOverlay = ({ visible, onClose, query = '', diagnosis = '', evidence = '' }) => {
    const graph = useMemo(() => {
        const stopWords = new Set(['the','a','an','is','are','was','were','with','and','or','of','in','to','for','at','by','from']);
        const extractTerms = (text, limit) =>
            text.toLowerCase().replace(/[^a-z\s]/g, ' ').split(/\s+/)
                .filter(w => w.length > 4 && !stopWords.has(w)).slice(0, limit);

        const symptomTerms = extractTerms(query, 4);
        const evidenceTerms = extractTerms(evidence, 6);
        const diagTerms = extractTerms(diagnosis, 3);

        const nodes = [
            ...symptomTerms.map((term, i) => ({ id: `s-${i}`, label: term, type: 'symptom', x: 80, y: 80 + i * 80 })),
            ...evidenceTerms.map((term, i) => ({ id: `e-${i}`, label: term, type: 'evidence', x: 260, y: 40 + i * 65 })),
            { id: 'diag', label: diagTerms[0] || 'Diagnosis', type: 'diagnosis', x: 460, y: 170 },
        ];

        const edges = [];
        symptomTerms.forEach((_, si) => {
            evidenceTerms.slice(0, 3).forEach((_, ei) => edges.push({ from: `s-${si}`, to: `e-${ei}` }));
        });
        evidenceTerms.slice(0, 5).forEach((_, ei) => { edges.push({ from: `e-${ei}`, to: 'diag' }); });

        return { nodes, edges };
    }, [query, diagnosis, evidence]);

    const getNode = id => graph.nodes.find(n => n.id === id);

    return (
        <AnimatePresence>
            {visible && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    className="fixed inset-0 z-50 flex items-center justify-center p-6"
                    style={{ background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(8px)' }} onClick={onClose}>
                    <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }} transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                        className="glass-panel-heavy w-full max-w-2xl p-6 relative" onClick={e => e.stopPropagation()}>

                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-xl" style={{ background: 'rgba(58,12,163,0.08)', border: '1px solid rgba(58,12,163,0.15)' }}>
                                    <Network size={18} style={{ color: 'var(--primary)' }} />
                                </div>
                                <div>
                                    <p className="font-bold text-sm" style={{ color: 'var(--text-primary)' }}>Knowledge Graph Reasoning Path</p>
                                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Symptom → Evidence → Diagnosis</p>
                                </div>
                            </div>
                            <button onClick={onClose} className="btn-ghost p-2 rounded-lg">
                                <X size={16} style={{ color: 'var(--text-muted)' }} />
                            </button>
                        </div>

                        <div className="flex items-center gap-5 mb-4">
                            {[
                                { color: 'var(--secondary)', label: 'Symptom' },
                                { color: 'var(--text-muted)', label: 'Evidence' },
                                { color: 'var(--success)', label: 'Diagnosis' },
                            ].map(({ color, label }) => (
                                <div key={label} className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
                                    <span className="w-2.5 h-2.5 rounded-full" style={{ background: color }} />{label}
                                </div>
                            ))}
                        </div>

                        <svg viewBox="0 0 560 420" className="w-full rounded-xl"
                            style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}>
                            <defs>
                                <marker id="arrowhead" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
                                    <path d="M0,0 L0,6 L8,3 z" fill="var(--border)" />
                                </marker>
                            </defs>
                            {graph.edges.map((edge, i) => {
                                const from = getNode(edge.from);
                                const to = getNode(edge.to);
                                if (!from || !to) return null;
                                return (
                                    <motion.line key={i} x1={from.x} y1={from.y} x2={to.x} y2={to.y}
                                        stroke="var(--border)" strokeWidth="1" strokeDasharray="4 4"
                                        markerEnd="url(#arrowhead)"
                                        initial={{ pathLength: 0, opacity: 0 }}
                                        animate={{ pathLength: 1, opacity: 1 }}
                                        transition={{ delay: i * 0.04, duration: 0.5 }} />
                                );
                            })}
                            {graph.nodes.map((node, i) => {
                                const color = node.type === 'symptom' ? 'var(--secondary)' : node.type === 'diagnosis' ? 'var(--success)' : 'var(--text-muted)';
                                const r = node.type === 'diagnosis' ? 28 : 22;
                                return (
                                    <motion.g key={node.id} initial={{ scale: 0, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
                                        transition={{ delay: i * 0.06 + 0.1, type: 'spring', stiffness: 300 }}
                                        style={{ transformOrigin: `${node.x}px ${node.y}px` }}>
                                        <circle cx={node.x} cy={node.y} r={r + 6} fill="none" stroke={color} strokeWidth="0.5" opacity="0.3" />
                                        <circle cx={node.x} cy={node.y} r={r} fill={`${color}18`} stroke={color} strokeWidth="1" />
                                        <text x={node.x} y={node.y + 4} textAnchor="middle" fill={color}
                                            fontSize={node.type === 'diagnosis' ? '8' : '7'} fontWeight="600" fontFamily="Inter, sans-serif">
                                            {node.label.slice(0, 10)}
                                        </text>
                                    </motion.g>
                                );
                            })}
                        </svg>

                        <p className="text-xs mt-3 text-center" style={{ color: 'var(--text-muted)' }}>
                            Nodes represent entities extracted from the clinical query, retrieved evidence, and generated diagnosis.
                        </p>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default KnowledgeGraphOverlay;
