import React from 'react';
import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    UploadCloud,
    FileText,
    MessageSquare,
    Utensils,
    Activity,
    Smile,
    CalendarHeart
} from 'lucide-react';

const Sidebar = () => {
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
        <aside className="w-64 bg-white border-r border-slate-200 hidden md:flex flex-col h-full shadow-sm">
            <div className="h-16 flex items-center px-6 border-b border-slate-200">
                <div className="bg-brand-500 text-white p-1.5 rounded mr-3">
                    <Activity size={20} />
                </div>
                <span className="font-bold text-xl text-slate-800 tracking-tight">MedRAG</span>
            </div>

            <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
                {links.map((link) => (
                    <NavLink
                        key={link.to}
                        to={link.to}
                        className={({ isActive }) =>
                            `flex items-center px-3 py-2.5 text-sm font-medium rounded-md transition-colors ${isActive
                                ? 'bg-brand-50 text-brand-700'
                                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                            }`
                        }
                    >
                        <link.icon className="mr-3 h-5 w-5" />
                        {link.label}
                    </NavLink>
                ))}
            </nav>

            <div className="p-4 border-t border-slate-200">
                <div className="flex items-center">
                    <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-bold">
                        DR
                    </div>
                    <div className="ml-3">
                        <p className="text-sm font-medium text-slate-700">Dr. Smith</p>
                        <p className="text-xs text-slate-500">View Profile</p>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
