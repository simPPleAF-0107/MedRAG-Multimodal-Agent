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
        <div className="h-[calc(100vh-8rem)] animate-slide-up-fade flex flex-col max-w-4xl mx-auto relative z-10">
            <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 rounded-full blur-[100px] animate-pulse-glow pointer-events-none"></div>
            
            <div className="mb-8 shrink-0 relative z-20 text-center">
                <h1 className="text-4xl font-extrabold text-white tracking-widest text-glow mb-2">Neurological NLP Core</h1>
                <p className="text-brand-100/70 font-medium">Securely query the MemoryAgent Vector Graph</p>
            </div>

            <div className="flex-1 overflow-hidden glass-panel-heavy p-1 shadow-neon mb-4">
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
