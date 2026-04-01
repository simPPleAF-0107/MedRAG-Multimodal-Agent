import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Search, Menu, User, Settings, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';

const Navbar = () => {
    const navigate = useNavigate();
    const [isFocused, setIsFocused] = useState(false);
    const [showProfile, setShowProfile] = useState(false);
    const [user, setUser] = useState(null);

    useEffect(() => {
        const stored = localStorage.getItem('user');
        if (stored) {
            setUser(JSON.parse(stored));
        }
    }, []);

    const handleSignOut = () => {
        localStorage.removeItem('user');
        setUser(null);
        setShowProfile(false);
        navigate('/login');
    };

    // Derive initials and display name from user data
    const userName = user?.name || 'User';
    const userEmail = user?.email || '';
    const userInitials = userName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

    return (
        <motion.header 
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="h-20 glass-panel border-b border-white/10 flex items-center justify-between px-6 md:px-10 m-4 shadow-lg sticky top-0 z-40"
        >
            <div className="flex items-center w-full max-w-xl">
                <button 
                    className="md:hidden text-slate-300 hover:text-brand-500 mr-4 transition-colors"
                    onClick={() => window.dispatchEvent(new CustomEvent('toggle-sidebar'))}
                >
                    <Menu size={24} />
                </button>
                <motion.div 
                    className="relative hidden w-full sm:block"
                    animate={{ scale: isFocused ? 1.02 : 1 }}
                    transition={{ type: "spring", stiffness: 300, damping: 20 }}
                >
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none transition-colors text-slate-400">
                        <Search className={`h-4 w-4 ${isFocused ? 'text-brand-500' : 'text-slate-400'}`} />
                    </div>
                    <input
                        type="text"
                        onFocus={() => setIsFocused(true)}
                        onBlur={() => setIsFocused(false)}
                        className="block w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl leading-5 text-white placeholder-slate-400 focus:outline-none focus:bg-white/10 focus:ring-1 focus:ring-brand-500 focus:border-brand-500 sm:text-sm transition-all shadow-inner"
                        placeholder="Search patient records, metrics, or insights..."
                    />
                </motion.div>
            </div>

            <div className="flex items-center space-x-4 md:space-x-6">
                <motion.button 
                    whileHover={{ scale: 1.1, rotate: 10 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => toast('No new notifications', { icon: '🔔' })}
                    className="relative p-3 text-slate-300 hover:text-brand-500 transition-colors bg-white/5 rounded-full border border-white/10 hover:shadow-neon"
                >
                    <Bell size={20} />
                    <span className="absolute top-1 right-1 block h-2.5 w-2.5 rounded-full bg-coral-500 ring-2 ring-deepSpace animate-pulse"></span>
                </motion.button>
                
                {/* Profile Dropdown */}
                <div className="relative">
                    <motion.button 
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setShowProfile(!showProfile)}
                        className="flex items-center gap-2 p-1.5 pr-4 bg-white/5 border border-white/10 rounded-full hover:bg-white/10 transition-colors"
                    >
                        <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-brand-600 to-coral-500 flex items-center justify-center text-white font-bold shadow-md">
                            {userInitials}
                        </div>
                        <span className="text-sm font-semibold text-slate-200 hidden md:block">{userName}</span>
                    </motion.button>

                    <AnimatePresence>
                        {showProfile && (
                            <motion.div 
                                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                                transition={{ duration: 0.2 }}
                                className="absolute right-0 mt-3 w-48 glass-panel border border-white/10 shadow-xl overflow-hidden py-2"
                            >
                                <div className="px-4 py-3 border-b border-white/10 mb-2">
                                    <p className="text-sm text-white font-medium">{userName}</p>
                                    <p className="text-xs text-slate-400 truncate">{userEmail}</p>
                                </div>
                                <button 
                                    onClick={() => { setShowProfile(false); toast('Profile page coming soon!', { icon: '👤' }); }}
                                    className="flex items-center w-full px-4 py-2 text-sm text-slate-300 hover:bg-white/10 hover:text-brand-500 transition-colors"
                                >
                                    <User size={16} className="mr-3" /> Profile
                                </button>
                                <button 
                                    onClick={() => { setShowProfile(false); toast('Settings page coming soon!', { icon: '⚙️' }); }}
                                    className="flex items-center w-full px-4 py-2 text-sm text-slate-300 hover:bg-white/10 hover:text-brand-500 transition-colors"
                                >
                                    <Settings size={16} className="mr-3" /> Settings
                                </button>
                                <button 
                                    onClick={handleSignOut}
                                    className="flex items-center w-full px-4 py-2 text-sm text-coral-400 hover:bg-white/10 hover:text-coral-300 transition-colors mt-1 border-t border-white/10 pt-3"
                                >
                                    <LogOut size={16} className="mr-3" /> Sign out
                                </button>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </motion.header>
    );
};

export default Navbar;
