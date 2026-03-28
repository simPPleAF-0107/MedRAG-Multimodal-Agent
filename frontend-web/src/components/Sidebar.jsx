import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    LayoutDashboard,
    UploadCloud,
    FileText,
    MessageSquare,
    Utensils,
    Activity,
    Smile,
    CalendarHeart,
    ChevronRight,
    Settings
} from 'lucide-react';

const Sidebar = () => {
    const location = useLocation();
    const links = [
        { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { to: '/upload', icon: UploadCloud, label: 'Upload Record' },
        { to: '/reports', icon: FileText, label: 'Diagnosis Reports' },
        { to: '/chat', icon: MessageSquare, label: 'AI Assistant' },
        { to: '/meal-planner', icon: Utensils, label: 'Meal Planner' },
        { to: '/activity', icon: Activity, label: 'Activity Tracker' },
        { to: '/mood-tracker', icon: Smile, label: 'Mood Tracker' },
        { to: '/cycle-tracker', icon: CalendarHeart, label: 'Cycle Tracker' },
    ];

    return (
        <motion.aside 
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="w-72 glass-panel hidden md:flex flex-col h-[calc(100vh-2rem)] m-4 shadow-2xl relative overflow-hidden"
        >
            {/* Ambient Background Glow */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-brand-500/10 blur-[50px] rounded-full pointer-events-none" />
            
            <div className="h-20 flex items-center justify-center border-b border-white/5 mx-4 z-10">
                <div className="bg-gradient-to-tr from-brand-600 to-brand-400 text-deepSpace p-2 rounded-xl mr-3 shadow-neon">
                    <Activity size={24} className="animate-pulse-glow" />
                </div>
                <span className="font-extrabold text-2xl text-white tracking-wider text-glow mt-1 bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">MedRAG</span>
            </div>

            <nav className="flex-1 overflow-y-auto py-6 px-4 space-y-2 z-10 custom-scrollbar">
                {links.map((link, idx) => {
                    const isActive = location.pathname === link.to;
                    return (
                        <NavLink
                            key={link.to}
                            to={link.to}
                            className="block"
                        >
                            <motion.div
                                whileHover={{ scale: 1.02, x: 5 }}
                                whileTap={{ scale: 0.98 }}
                                className={`group flex items-center justify-between px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-300 relative overflow-hidden ${
                                    isActive
                                        ? 'bg-gradient-to-r from-brand-500/20 to-transparent text-brand-500 border-l-4 border-brand-500 shadow-[inset_0px_0px_20px_rgba(69,243,255,0.05)]'
                                        : 'text-slate-400 hover:text-white hover:bg-white/5'
                                }`}
                            >
                                <div className="flex items-center">
                                    <link.icon className={`mr-4 h-5 w-5 transition-transform duration-300 ${isActive ? 'animate-pulse scale-110' : 'group-hover:scale-110 group-hover:text-brand-400'}`} />
                                    <span className="z-10">{link.label}</span>
                                </div>
                                {isActive && (
                                    <motion.div
                                        layoutId="activeTab"
                                        className="absolute inset-0 bg-brand-500/5 z-0"
                                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                    />
                                )}
                                <ChevronRight size={16} className={`transition-opacity duration-300 ${isActive ? 'opacity-100 text-brand-500' : 'opacity-0 group-hover:opacity-100 group-hover:text-white'}`} />
                            </motion.div>
                        </NavLink>
                    );
                })}
            </nav>

            <motion.div 
                whileHover={{ y: -2 }}
                className="p-4 mx-4 mb-4 rounded-xl bg-gradient-to-b from-white/10 to-white/5 border border-white/10 hover:border-brand-500/30 transition-all duration-300 cursor-pointer shadow-lg z-10"
            >
                <div className="flex items-center">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-coral-500 to-brand-500 flex items-center justify-center text-white font-bold shadow-md relative group">
                        DR
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-[#0B0C10]"></div>
                    </div>
                    <div className="ml-3 flex-1 flex justify-between items-center">
                        <div>
                            <p className="text-sm font-bold text-slate-100">Dr. Smith</p>
                            <p className="text-xs text-brand-400 font-medium">Cardiologist</p>
                        </div>
                        <Settings size={16} className="text-slate-400 hover:text-white transition-colors" />
                    </div>
                </div>
            </motion.div>
        </motion.aside>
    );
};

export default Sidebar;
