import React, { useState, useEffect } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    LayoutDashboard, UploadCloud, FileText, MessageSquare,
    Utensils, Activity, Smile, CalendarHeart, ChevronRight,
    LogOut, CalendarCheck, Cpu, Database, Wifi, WifiOff
} from 'lucide-react';

const Sidebar = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [backendStatus, setBackendStatus] = useState('checking');

    useEffect(() => {
        const stored = localStorage.getItem('user');
        if (stored) setUser(JSON.parse(stored));
    }, []);

    useEffect(() => {
        const check = async () => {
            try {
                await fetch('/api/v1/health', { signal: AbortSignal.timeout(3000) });
                setBackendStatus('online');
            } catch { setBackendStatus('offline'); }
        };
        check();
        const interval = setInterval(check, 30000);
        return () => clearInterval(interval);
    }, []);

    const handleSignOut = () => { localStorage.removeItem('user'); navigate('/login'); };

    const isDoctor = user?.role === 'doctor';
    const userName = user?.name || 'User';
    const userRole = user?.role === 'doctor' ? 'Clinician' : 'Patient';
    const userInitials = userName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

    const links = [
        { to: '/',             icon: LayoutDashboard, label: 'Overview' },
        { to: '/upload',       icon: UploadCloud,     label: 'Diagnostics' },
        { to: '/reports',      icon: FileText,        label: 'Reports' },
        { to: '/chat',         icon: MessageSquare,   label: 'AI Assistant' },
        { to: '/appointments', icon: CalendarCheck,   label: 'Appointments' },
        ...(!isDoctor ? [
            { to: '/meal-planner', icon: Utensils,      label: 'Meal Planner' },
            { to: '/activity',     icon: Activity,       label: 'Activity' },
            { to: '/mood-tracker', icon: Smile,          label: 'Mood Tracker' },
            ...(user?.sex === 'Female' ? [{ to: '/cycle-tracker', icon: CalendarHeart, label: 'Cycle Tracker' }] : [])
        ] : []),
    ];

    return (
        <motion.aside
            initial={{ x: -80, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="w-64 hidden md:flex flex-col h-screen shrink-0"
            style={{
                background: 'var(--surface)',
                borderRight: '1px solid var(--border)',
            }}
        >
            {/* Logo */}
            <div className="h-16 flex items-center px-5 shrink-0" style={{ borderBottom: '1px solid var(--border)' }}>
                <div className="p-2 rounded-xl mr-3" style={{ background: 'rgba(58,12,163,0.08)' }}>
                    <Cpu size={18} style={{ color: 'var(--primary)' }} />
                </div>
                <div>
                    <span className="font-black text-lg tracking-tight" style={{ color: 'var(--text-primary)' }}>MedRAG</span>
                    <span className="block text-[10px] font-medium tracking-widest uppercase" style={{ color: 'var(--text-muted)' }}>Clinical AI</span>
                </div>
            </div>

            {/* Nav links */}
            <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-0.5">
                <p className="label-caps px-3 pb-2 pt-1">Navigation</p>
                {links.map((link) => {
                    const isActive = location.pathname === link.to;
                    return (
                        <NavLink key={link.to} to={link.to} className="block">
                            <motion.div whileTap={{ scale: 0.97 }} className={`nav-link ${isActive ? 'active' : ''}`}>
                                <link.icon size={16} style={{ color: isActive ? 'var(--primary)' : 'var(--text-muted)' }} />
                                <span className="flex-1">{link.label}</span>
                                {isActive && <ChevronRight size={13} style={{ color: 'var(--primary)', opacity: 0.6 }} />}
                            </motion.div>
                        </NavLink>
                    );
                })}
            </nav>

            {/* System status */}
            <div className="px-3 pb-2">
                <div className="rounded-xl p-3 space-y-2" style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}>
                    <p className="label-caps mb-2">System Status</p>
                    <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2" style={{ color: 'var(--text-muted)' }}>
                            {backendStatus === 'online'
                                ? <Wifi size={11} style={{ color: 'var(--success)' }} />
                                : <WifiOff size={11} style={{ color: 'var(--error)' }} />}
                            <span>Backend API</span>
                        </div>
                        <span className="font-medium text-[10px]" style={{ color: backendStatus === 'online' ? 'var(--success)' : backendStatus === 'offline' ? 'var(--error)' : 'var(--warning)' }}>
                            {backendStatus === 'checking' ? 'Checking…' : backendStatus === 'online' ? 'Online' : 'Offline'}
                        </span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2" style={{ color: 'var(--text-muted)' }}>
                            <Database size={11} style={{ color: 'var(--info)' }} />
                            <span>Vector DB</span>
                        </div>
                        <span className="font-medium text-[10px]" style={{ color: 'var(--info)' }}>31K docs</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2" style={{ color: 'var(--text-muted)' }}>
                            <Cpu size={11} style={{ color: 'var(--warning)' }} />
                            <span>LLM Model</span>
                        </div>
                        <span className="font-medium text-[10px]" style={{ color: '#B8860B' }}>gpt-5.4-mini</span>
                    </div>
                </div>
            </div>

            {/* User card */}
            <div className="p-3 shrink-0" style={{ borderTop: '1px solid var(--border)' }}>
                <motion.div
                    whileHover={{ y: -1 }}
                    className="flex items-center gap-3 p-3 rounded-xl cursor-pointer"
                    style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}
                >
                    <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0 relative"
                        style={{ background: 'linear-gradient(135deg, var(--primary), var(--secondary))' }}>
                        {userInitials}
                        <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2"
                            style={{ background: 'var(--success)', borderColor: 'var(--surface)' }} />
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold truncate" style={{ color: 'var(--text-primary)' }}>{userName}</p>
                        <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{userRole}</p>
                    </div>
                    <button onClick={handleSignOut} title="Sign out"
                        className="p-1.5 rounded-lg transition-colors group" style={{ ':hover': { background: 'var(--error-bg)' } }}>
                        <LogOut size={13} className="group-hover:text-red-500 transition-colors" style={{ color: 'var(--text-muted)' }} />
                    </button>
                </motion.div>
            </div>
        </motion.aside>
    );
};

export default Sidebar;
