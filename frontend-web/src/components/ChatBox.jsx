import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const ChatBox = ({ onSend, messages, isLoading }) => {
    const [input, setInput] = useState('');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    useEffect(() => { scrollToBottom(); }, [messages, isLoading]);

    const handleSend = (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;
        onSend(input);
        setInput('');
    };

    return (
        <div className="flex flex-col h-full overflow-hidden relative" style={{ background: 'var(--surface)', borderRadius: 16, border: '1px solid var(--border)' }}>
            {/* Header */}
            <div className="px-6 py-5 flex justify-between items-center z-10" style={{ borderBottom: '1px solid var(--border)', background: 'var(--surface-subtle)' }}>
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl" style={{ background: 'linear-gradient(135deg, var(--primary), var(--secondary))' }}>
                        <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h2 className="font-bold tracking-wide" style={{ color: 'var(--text-primary)' }}>Clinical AI Assistant</h2>
                        <p className="text-xs font-medium" style={{ color: 'var(--primary)' }}>Powered by MedRAG Engine</p>
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 relative z-0">
                {messages.length === 0 ? (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col items-center justify-center h-full text-center space-y-4">
                        <div className="w-20 h-20 rounded-full flex items-center justify-center" style={{ background: 'rgba(58,12,163,0.06)', border: '1px solid rgba(58,12,163,0.12)' }}>
                            <Bot size={40} style={{ color: 'var(--primary)', opacity: 0.6 }} />
                        </div>
                        <p className="text-sm max-w-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>Ask questions about the patient's record, diagnosis reasoning, or custom treatment plans.</p>
                    </motion.div>
                ) : (
                    <AnimatePresence>
                        {messages.map((msg, idx) => (
                            <motion.div key={idx} initial={{ opacity: 0, y: 10, scale: 0.95 }} animate={{ opacity: 1, y: 0, scale: 1 }}
                                transition={{ duration: 0.3, type: 'spring', stiffness: 300, damping: 25 }}
                                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} w-full group`}>
                                <div className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 flex gap-4 relative overflow-hidden ${
                                    msg.role === 'user'
                                        ? 'rounded-tr-sm text-white'
                                        : 'rounded-tl-sm'
                                }`} style={msg.role === 'user'
                                    ? { background: 'linear-gradient(135deg, var(--primary), var(--secondary))' }
                                    : { background: 'var(--surface-subtle)', border: '1px solid var(--border)' }
                                }>
                                    {msg.role !== 'user' && (
                                        <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0"
                                            style={{ background: 'rgba(58,12,163,0.08)', border: '1px solid rgba(58,12,163,0.15)' }}>
                                            <Bot className="w-4 h-4" style={{ color: 'var(--primary)' }} />
                                        </div>
                                    )}
                                    <div className={`text-sm leading-loose flex-1 ${msg.role === 'user' ? 'text-white font-medium' : ''}`}
                                        style={msg.role !== 'user' ? { color: 'var(--text-secondary)' } : {}}>
                                        {msg.content}
                                    </div>
                                    {msg.role === 'user' && <User className="w-5 h-5 text-white/70 shrink-0 mt-0.5" />}
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                )}
                {isLoading && (
                    <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="flex justify-start w-full">
                        <div className="rounded-2xl rounded-tl-sm p-4 flex items-center space-x-3"
                            style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}>
                            <Bot className="w-5 h-5" style={{ color: 'var(--primary)' }} />
                            <div className="flex space-x-1 items-center h-5">
                                <motion.div className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--primary)' }} animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0 }} />
                                <motion.div className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--primary)' }} animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }} />
                                <motion.div className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--primary)' }} animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }} />
                            </div>
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 z-10" style={{ borderTop: '1px solid var(--border)', background: 'var(--surface-subtle)' }}>
                <form onSubmit={handleSend} className="relative flex items-center">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={isLoading}
                        placeholder={isLoading ? 'Please wait...' : 'Ask MedRAG about this case...'}
                        className="glass-input pl-5 pr-14 py-4 text-sm disabled:opacity-50"
                    />
                    <motion.button
                        whileHover={{ scale: 1.05, rotate: input.trim() ? 10 : 0 }}
                        whileTap={{ scale: 0.95 }}
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className="absolute right-2 p-2.5 rounded-lg transition-all flex items-center justify-center"
                        style={input.trim() && !isLoading
                            ? { background: 'var(--primary)', cursor: 'pointer' }
                            : { background: 'var(--surface-subtle)', cursor: 'not-allowed' }
                        }
                    >
                        <Send size={18} className={input.trim() && !isLoading ? 'text-white' : ''} style={!(input.trim() && !isLoading) ? { color: 'var(--text-muted)' } : {}} />
                    </motion.button>
                </form>
            </div>
        </div>
    );
};

export default ChatBox;
