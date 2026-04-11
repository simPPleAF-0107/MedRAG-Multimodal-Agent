import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Search, User, Settings, LogOut, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import ConfidenceBadge from './ConfidenceBadge';

const Navbar = () => {
    const navigate = useNavigate();
    const [isFocused, setIsFocused] = useState(false);
    const [showProfile, setShowProfile] = useState(false);
    const [user, setUser] = useState(null);
    const [lastConfidence, setLastConfidence] = useState(null);

    useEffect(() => {
        const stored = localStorage.getItem('user');
        if (stored) setUser(JSON.parse(stored));
        const lastReport = localStorage.getItem('lastReport');
        if (lastReport) {
            try {
                const r = JSON.parse(lastReport);
                const conf = r?.confidence_score ?? r?.confidence_calibration?.overall_confidence;
                if (conf != null) setLastConfidence(conf);
            } catch {}
        }
    }, []);

    const handleSignOut = () => { localStorage.removeItem('user'); setUser(null); navigate('/login'); };
    const userName = user?.name || 'User';
    const userEmail = user?.email || '';
    const userInitials = userName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

    return (
        <motion.header
            initial={{ y: -40, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className="h-16 flex items-center justify-between px-6 shrink-0"
            style={{
                background: 'var(--surface)',
                borderBottom: '1px solid var(--border)',
            }}
        >
            {/* Search */}
            <div className="flex items-center flex-1 max-w-sm">
                <motion.div className="relative w-full" animate={{ scale: isFocused ? 1.01 : 1 }} transition={{ type: 'spring', stiffness: 400, damping: 25 }}>
                    <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 transition-colors"
                        style={{ color: isFocused ? 'var(--primary)' : 'var(--text-muted)' }} />
                    <input
                        type="text"
                        onFocus={() => setIsFocused(true)}
                        onBlur={() => setIsFocused(false)}
                        placeholder="Search records, patients, metrics…"
                        className="glass-input pl-9 pr-4 py-2 text-sm"
                    />
                </motion.div>
            </div>

            {/* Right controls */}
            <div className="flex items-center gap-3">
                {lastConfidence != null && (
                    <div className="hidden lg:block"><ConfidenceBadge score={lastConfidence} size="sm" showShimmer={false} /></div>
                )}

                {/* Pipeline status */}
                <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs"
                    style={{ background: 'var(--success-bg)', border: '1px solid rgba(46,204,113,0.2)' }}>
                    <Activity size={10} className="animate-pulse" style={{ color: 'var(--success)' }} />
                    <span className="font-medium" style={{ color: 'var(--success)' }}>Pipeline Ready</span>
                </div>

                {/* Notifications */}
                <motion.button
                    whileHover={{ scale: 1.08 }}
                    whileTap={{ scale: 0.93 }}
                    onClick={() => toast('No new notifications', { icon: '🔔' })}
                    className="relative p-2 rounded-xl transition-colors"
                    style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}
                >
                    <Bell size={16} style={{ color: 'var(--text-muted)' }} />
                    <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: 'var(--error)' }} />
                </motion.button>

                {/* Profile */}
                <div className="relative">
                    <motion.button
                        whileHover={{ scale: 1.03 }}
                        whileTap={{ scale: 0.97 }}
                        onClick={() => setShowProfile(!showProfile)}
                        className="flex items-center gap-2 pl-1 pr-3 py-1 rounded-xl"
                        style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}
                    >
                        <div className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold text-white"
                            style={{ background: 'linear-gradient(135deg, var(--primary), var(--secondary))' }}>
                            {userInitials}
                        </div>
                        <span className="text-sm font-medium hidden md:block" style={{ color: 'var(--text-secondary)' }}>{userName}</span>
                    </motion.button>

                    <AnimatePresence>
                        {showProfile && (
                            <motion.div
                                initial={{ opacity: 0, y: 8, scale: 0.95 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                exit={{ opacity: 0, y: 8, scale: 0.95 }}
                                transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                                className="absolute right-0 mt-2 w-52 glass-panel-heavy py-2 overflow-hidden z-50"
                            >
                                <div className="px-4 py-3 mb-1" style={{ borderBottom: '1px solid var(--border)' }}>
                                    <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{userName}</p>
                                    <p className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>{userEmail}</p>
                                </div>
                                {[
                                    { icon: User, label: 'Profile', action: () => { setShowProfile(false); toast('Profile coming soon', { icon: '👤' }); } },
                                    { icon: Settings, label: 'Settings', action: () => { setShowProfile(false); toast('Settings coming soon', { icon: '⚙️' }); } },
                                ].map(({ icon: Icon, label, action }) => (
                                    <button key={label} onClick={action}
                                        className="flex items-center gap-3 w-full px-4 py-2 text-sm transition-colors hover:bg-[var(--surface-subtle)]"
                                        style={{ color: 'var(--text-secondary)' }}>
                                        <Icon size={14} />{label}
                                    </button>
                                ))}
                                <div className="mt-1 pt-1" style={{ borderTop: '1px solid var(--border)' }}>
                                    <button onClick={handleSignOut}
                                        className="flex items-center gap-3 w-full px-4 py-2 text-sm transition-colors hover:bg-red-50"
                                        style={{ color: 'var(--error)' }}>
                                        <LogOut size={14} />Sign out
                                    </button>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </motion.header>
    );
};

export default Navbar;
