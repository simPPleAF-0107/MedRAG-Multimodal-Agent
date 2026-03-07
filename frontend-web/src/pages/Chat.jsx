import React, { useState } from 'react';
import ChatBox from '../components/ChatBox';
import { chatWithAI } from '../services/apiClient';

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [isTyping, setIsTyping] = useState(false);

    // Hardcoded Patient 1 context interaction snippet
    const handleSendMessage = async (rawMessage) => {
        // User message
        const newMsg = { role: 'user', content: rawMessage };
        setMessages(prev => [...prev, newMsg]);
        setIsTyping(true);

        try {
            // Connect to the specific new Conversational RAG Endpoint we made in backend
            const res = await chatWithAI(rawMessage, 1);

            const aiReply = { role: 'assistant', content: res.data.reply };
            setMessages(prev => [...prev, aiReply]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: 'Connection error communicating with MemoryAgent endpoints.' }]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="h-[calc(100vh-8rem)] animate-fade-in flex flex-col max-w-4xl mx-auto">
            <div className="mb-6 shrink-0">
                <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Conversational AI Probe</h1>
                <p className="text-slate-500 mt-1">Directly query the MemoryAgent regarding Patient History or Medical Vector Graph.</p>
            </div>

            <div className="flex-1 overflow-hidden shadow-lg border-slate-200/60 border rounded-2xl ring-1 ring-slate-900/5">
                <ChatBox
                    messages={messages}
                    isLoading={isTyping}
                    onSend={handleSendMessage}
                />
            </div>
        </div>
    );
};

export default Chat;
