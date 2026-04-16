import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
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
        <div className="flex flex-col h-full overflow-hidden relative bg-surface-2/30 backdrop-blur-glass border border-white/5 rounded-3xl shadow-bento group">
            {/* Header */}
            <div className="px-8 py-6 flex justify-between items-center z-10 border-b border-white/5 bg-surface-3/50 backdrop-blur-heavy">
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-2xl bg-brand-500/20 border border-brand-500/30 shadow-neon">
                        <Sparkles className="w-6 h-6 text-brand-400" />
                    </div>
                    <div>
                        <h2 className="font-bold text-xl tracking-tight text-white drop-shadow-md">Clinical AI Engine</h2>
                        <p className="text-xs font-semibold text-brand-500 tracking-widest uppercase mt-1">Live Multimodal RAG</p>
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-8 space-y-6 relative z-0">
                {messages.length === 0 ? (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col items-center justify-center h-full text-center space-y-5">
                        <div className="w-24 h-24 rounded-full flex items-center justify-center bg-brand-500/10 border border-brand-500/20 shadow-neon">
                            <Bot size={48} className="text-brand-400 opacity-80" />
                        </div>
                        <p className="text-base max-w-sm leading-relaxed text-slate-400 font-medium">Ask questions about the patient's record, diagnostic reasoning, or custom treatment plans.</p>
                    </motion.div>
                ) : (
                    <AnimatePresence>
                        {messages.map((msg, idx) => (
                            <motion.div key={idx} initial={{ opacity: 0, y: 10, scale: 0.95 }} animate={{ opacity: 1, y: 0, scale: 1 }}
                                transition={{ duration: 0.3, type: 'spring', stiffness: 300, damping: 25 }}
                                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} w-full group`}>
                                <div className={`max-w-[85%] sm:max-w-[75%] rounded-3xl p-5 flex gap-5 relative overflow-hidden shadow-bento ${
                                    msg.role === 'user'
                                        ? 'rounded-tr-sm bg-gradient-to-br from-brand-500 to-blue-600 text-white'
                                        : 'rounded-tl-sm bg-surface-3/50 backdrop-blur-glass border border-white/5'
                                }`}>
                                    {msg.role !== 'user' && (
                                        <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 bg-brand-500/10 border border-brand-500/20 shadow-neon">
                                            <Bot className="w-5 h-5 text-brand-400" />
                                        </div>
                                    )}
                                    <div className={`text-base flex-1 ${msg.role === 'user' ? 'text-white font-medium leading-relaxed' : 'markdown-body text-slate-300'}`}>
                                        {msg.role === 'user' ? msg.content : (
                                            <ReactMarkdown 
                                                remarkPlugins={[remarkGfm]}
                                                components={{
                                                    p: ({node, ...props}) => <p className="mb-4 leading-relaxed" {...props} />,
                                                    ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-4 space-y-2 marker:text-brand-500" {...props} />,
                                                    ol: ({node, ...props}) => <ol className="list-decimal pl-5 mb-4 space-y-2 marker:text-brand-500 font-semibold" {...props} />,
                                                    li: ({node, ...props}) => <li className="pl-1" {...props} />,
                                                    strong: ({node, ...props}) => <strong className="font-bold text-white shadow-neon" {...props} />,
                                                    h1: ({node, ...props}) => <h1 className="text-xl font-black mb-4 mt-8 text-brand-400" {...props} />,
                                                    h2: ({node, ...props}) => <h2 className="text-lg font-bold mb-3 mt-6 text-brand-400" {...props} />,
                                                    h3: ({node, ...props}) => <h3 className="text-md font-bold mb-2 mt-4 text-brand-400" {...props} />
                                                }}
                                            >
                                                {msg.content.replace(/""/g, '"').replace(/\[Evidence\]/g, '🔬 **[Evidence]**').replace(/\[Clinical Reasoning\]/g, '🧠 **[Clinical Reasoning]**').replace(/\[No Evidence Available\]/g, '⚠️ **[No Evidence Available]**')}
                                            </ReactMarkdown>
                                        )}
                                    </div>
                                    {msg.role === 'user' && <User className="w-6 h-6 text-white/70 shrink-0 mt-0.5" />}
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                )}
                {isLoading && (
                    <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="flex justify-start w-full">
                        <div className="rounded-3xl rounded-tl-sm p-5 flex items-center space-x-4 bg-surface-3/50 backdrop-blur-glass border border-white/5 shadow-bento">
                            <Bot className="w-6 h-6 text-brand-400 opacity-80" />
                            <div className="flex space-x-2 items-center h-6">
                                <motion.div className="w-2 h-2 rounded-full bg-brand-500 shadow-neon" animate={{ y: [0, -6, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0 }} />
                                <motion.div className="w-2 h-2 rounded-full bg-brand-500 shadow-neon" animate={{ y: [0, -6, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }} />
                                <motion.div className="w-2 h-2 rounded-full bg-brand-500 shadow-neon" animate={{ y: [0, -6, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }} />
                            </div>
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-6 z-10 border-t border-white/5 bg-surface-3/50 backdrop-blur-heavy rounded-b-3xl">
                <form onSubmit={handleSend} className="relative flex items-center">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={isLoading}
                        placeholder={isLoading ? 'Please wait...' : 'Ask MedRAG about this case...'}
                        className="w-full bg-surface-2/60 border border-white/10 rounded-2xl px-6 py-4 text-base text-white focus:outline-none focus:border-brand-500/50 focus:shadow-neon disabled:opacity-50 transition-all placeholder:text-slate-500"
                    />
                    <motion.button
                        whileHover={{ scale: 1.05, rotate: input.trim() ? 10 : 0 }}
                        whileTap={{ scale: 0.95 }}
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className={`absolute right-3 p-3 rounded-xl transition-all flex items-center justify-center ${input.trim() && !isLoading ? 'bg-brand-500 hover:bg-brand-400 shadow-neon text-obsidian' : 'bg-surface-3/50 text-slate-500 cursor-not-allowed border border-white/5'}`}
                    >
                        <Send size={20} className={input.trim() && !isLoading ? 'text-obsidian' : ''} />
                    </motion.button>
                </form>
            </div>
        </div>
    );
};

export default ChatBox;
