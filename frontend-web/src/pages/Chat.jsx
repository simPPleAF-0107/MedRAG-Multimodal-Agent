import React, { useState, useEffect } from 'react';
import { chatWithAI } from '../services/apiClient';
import ChatBox from '../components/ChatBox';

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [isTyping, setIsTyping] = useState(false);

    const getPatientId = () => {
        try {
            const stored = localStorage.getItem('user');
            if (!stored) return null;
            const u = JSON.parse(stored);
            return u.role === 'patient' ? (u.user_id || null) : null;
        } catch { return null; }
    };

    const handleSendMessage = async (rawMessage) => {
        setMessages(prev => [...prev, { role: 'user', content: rawMessage }]);
        setIsTyping(true);
        try {
            const res = await chatWithAI(rawMessage, getPatientId());
            setMessages(prev => [...prev, { role: 'assistant', content: res.data.reply }]);
        } catch {
            setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please check the backend connection.' }]);
        }
        setIsTyping(false);
    };

    return (
        <div className="h-[calc(100vh-5rem)] animate-fade-up">
            <ChatBox messages={messages} onSend={handleSendMessage} isLoading={isTyping} />
        </div>
    );
};

export default Chat;
