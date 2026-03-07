import React from 'react';
import { Bell, Search, Menu } from 'lucide-react';

const Navbar = () => {
    return (
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 md:px-8 shadow-sm">
            <div className="flex items-center">
                <button className="md:hidden text-slate-500 hover:text-slate-700 mr-4">
                    <Menu size={24} />
                </button>
                <div className="relative hidden sm:block">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Search className="h-4 w-4 text-slate-400" />
                    </div>
                    <input
                        type="text"
                        className="block w-full pl-10 pr-3 py-2 border border-slate-200 rounded-md leading-5 bg-slate-50 placeholder-slate-400 focus:outline-none focus:bg-white focus:ring-1 focus:ring-brand-500 focus:border-brand-500 sm:text-sm transition-colors"
                        placeholder="Search patient records..."
                    />
                </div>
            </div>

            <div className="flex items-center space-x-4">
                <button className="relative p-2 text-slate-400 hover:text-slate-500 transition-colors">
                    <Bell size={20} />
                    <span className="absolute top-1.5 right-1.5 block h-2 w-2 rounded-full bg-danger ring-2 ring-white"></span>
                </button>
            </div>
        </header>
    );
};

export default Navbar;
