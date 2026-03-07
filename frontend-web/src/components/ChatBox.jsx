import React, { useState } from 'react';
import { Send, Bot, User } from 'lucide-react';

const ChatBox = ({ onSend, messages, isLoading }) => {
    const [input, setInput] = useState("");

    const handleSend = (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;
        onSend(input);
        setInput("");
    };

    return (
        <div className="flex flex-col h-full bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            {/* Header */}
            <div className="px-5 py-4 border-b border-slate-200 bg-slate-50/50 flex justify-between items-center">
                <div>
                    <h2 className="font-semibold text-slate-800 flex items-center">
                        <Bot className="w-5 h-5 mr-2 text-brand-500" />
                        Clinical AI Assistant
                    </h2>
                    <p className="text-xs text-slate-500 ml-7">Powered by MedRAG Engine</p>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-slate-50/30">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center text-slate-500 space-y-3">
                        <Bot size={40} className="text-slate-300" />
                        <p className="text-sm">Ask questions about the patient's record, diagnosis reasoning, or treatment plans.</p>
                    </div>
                ) : (
                    messages.map((msg, idx) => (
                        <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div
                                className={`max-w-[80%] rounded-2xl p-4 flex gap-3
                  ${msg.role === 'user'
                                        ? 'bg-brand-500 text-white rounded-tr-sm'
                                        : 'bg-white border border-slate-200 text-slate-800 rounded-tl-sm shadow-sm'
                                    }`}
                            >
                                {msg.role !== 'user' && <Bot className="w-5 h-5 text-brand-500 shrink-0 mt-0.5" />}
                                <div className={`text-sm leading-relaxed ${msg.role === 'user' ? 'text-white' : 'text-slate-700'}`}>
                                    {msg.content}
                                </div>
                                {msg.role === 'user' && <User className="w-5 h-5 text-brand-100 shrink-0 mt-0.5" />}
                            </div>
                        </div>
                    ))
                )}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-sm p-4 shadow-sm flex items-center space-x-2 text-slate-400">
                            <Bot className="w-4 h-4" />
                            <span className="text-xs italic">MedRAG is thinking...</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-slate-200">
                <form onSubmit={handleSend} className="relative flex items-center">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={isLoading}
                        placeholder="Ask MedRAG about this case..."
                        className="w-full pl-4 pr-12 py-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 disabled:opacity-50"
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className="absolute right-2 p-2 rounded-md bg-brand-500 text-white hover:bg-brand-600 disabled:bg-slate-300 disabled:text-slate-500 transition-colors"
                    >
                        <Send size={18} />
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChatBox;
