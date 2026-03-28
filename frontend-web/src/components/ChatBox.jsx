import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const ChatBox = ({ onSend, messages, isLoading }) => {
    const [input, setInput] = useState("");
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleSend = (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;
        onSend(input);
        setInput("");
    };

    return (
        <div className="flex flex-col h-full glass-panel border border-white/10 shadow-2xl overflow-hidden relative">
            {/* Header */}
            <div className="px-6 py-5 border-b border-white/10 bg-white/5 flex justify-between items-center backdrop-blur-md z-10">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-gradient-to-tr from-brand-600 to-brand-400 rounded-xl shadow-neon">
                        <Sparkles className="w-5 h-5 text-deepSpace" />
                    </div>
                    <div>
                        <h2 className="font-bold text-white tracking-wide">
                            Clinical AI Assistant
                        </h2>
                        <p className="text-xs text-brand-400 font-medium">Powered by MedRAG Engine</p>
                    </div>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-transparent custom-scrollbar relative z-0">
                {messages.length === 0 ? (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex flex-col items-center justify-center h-full text-center space-y-4"
                    >
                        <div className="w-20 h-20 bg-brand-500/10 rounded-full flex items-center justify-center border border-brand-500/20 shadow-[0_0_30px_rgba(69,243,255,0.1)]">
                            <Bot size={40} className="text-brand-500 opacity-80" />
                        </div>
                        <p className="text-sm text-slate-400 max-w-xs leading-relaxed">Ask questions about the patient's record, diagnosis reasoning, or custom treatment plans.</p>
                    </motion.div>
                ) : (
                    <AnimatePresence>
                        {messages.map((msg, idx) => (
                            <motion.div 
                                key={idx} 
                                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                transition={{ duration: 0.3, type: "spring", stiffness: 300, damping: 25 }}
                                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} w-full group`}
                            >
                                <div
                                    className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 flex gap-4 relative overflow-hidden
                                        ${msg.role === 'user'
                                            ? 'bg-gradient-to-br from-brand-600 to-brand-500 text-deepSpace rounded-tr-sm shadow-neon'
                                            : 'bg-white/5 border border-white/10 text-slate-200 rounded-tl-sm shadow-lg backdrop-blur-sm'
                                        }`}
                                >
                                    {msg.role !== 'user' && (
                                        <div className="w-8 h-8 rounded-full bg-brand-500/20 flex items-center justify-center shrink-0 border border-brand-500/30">
                                            <Bot className="w-4 h-4 text-brand-400" />
                                        </div>
                                    )}
                                    <div className={`text-sm leading-loose ${msg.role === 'user' ? 'text-deepSpace font-medium' : 'text-slate-300'} flex-1`}>
                                        {msg.content}
                                    </div>
                                    {msg.role === 'user' && (
                                        <User className="w-5 h-5 text-deepSpace/70 shrink-0 mt-0.5" />
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                )}
                
                {isLoading && (
                    <motion.div 
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex justify-start w-full"
                    >
                        <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-sm p-4 shadow-lg flex items-center space-x-3 text-brand-400 backdrop-blur-sm">
                            <Bot className="w-5 h-5" />
                            <div className="flex space-x-1 items-center h-5">
                                <motion.div className="w-1.5 h-1.5 bg-brand-400 rounded-full" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0 }} />
                                <motion.div className="w-1.5 h-1.5 bg-brand-400 rounded-full" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }} />
                                <motion.div className="w-1.5 h-1.5 bg-brand-400 rounded-full" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }} />
                            </div>
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white/5 border-t border-white/10 backdrop-blur-md z-10">
                <form onSubmit={handleSend} className="relative flex items-center group">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={isLoading}
                        placeholder={isLoading ? "Please wait..." : "Ask MedRAG about this case..."}
                        className="w-full pl-5 pr-14 py-4 bg-deepSpace/50 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 focus:shadow-[0_0_15px_rgba(69,243,255,0.1)] disabled:opacity-50 transition-all duration-300"
                    />
                    <motion.button
                        whileHover={{ scale: 1.05, rotate: input.trim() ? 10 : 0 }}
                        whileTap={{ scale: 0.95 }}
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className={`absolute right-2 p-2.5 rounded-lg transition-all duration-300 flex items-center justify-center ${
                            input.trim() && !isLoading 
                                ? 'bg-gradient-to-r from-brand-600 to-brand-500 text-deepSpace shadow-md cursor-pointer' 
                                : 'bg-white/10 text-slate-500 cursor-not-allowed'
                        }`}
                    >
                        <Send size={18} className={input.trim() && !isLoading ? 'opacity-100' : 'opacity-50'} />
                    </motion.button>
                </form>
            </div>
        </div>
    );
};

export default ChatBox;
