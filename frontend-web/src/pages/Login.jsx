import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Activity, Lock, Mail, ArrowRight, UserSquare2, Stethoscope } from 'lucide-react';
import { motion } from 'framer-motion';
import { loginUser } from '../services/apiClient';

const Login = () => {
    const navigate = useNavigate();
    const [role, setRole] = useState('patient'); // 'patient' or 'doctor'
    const [identifier, setIdentifier] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        
        try {
            const res = await loginUser(identifier, password, role);
            if (res.status === 'success') {
                localStorage.setItem('user', JSON.stringify(res));
                navigate('/');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-transparent flex flex-col justify-center py-12 sm:px-6 lg:px-8 font-sans relative overflow-hidden">
            {/* Animated floating orbs background elements */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-500/20 rounded-full blur-[100px] pointer-events-none animate-float"></div>
            <div className="absolute bottom-1/4 right-1/4 w-[30rem] h-[30rem] bg-coral-500/10 rounded-full blur-[120px] pointer-events-none animate-float-delayed"></div>

            <motion.div 
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
                className="sm:mx-auto sm:w-full sm:max-w-md relative z-10"
            >
                <motion.div 
                    whileHover={{ scale: 1.05 }}
                    className="flex justify-center mb-4"
                >
                    <div className="bg-gradient-to-tr from-brand-600 to-brand-400 p-4 rounded-2xl shadow-neon animate-pulse-glow">
                        <Activity className="w-14 h-14 text-deepSpace" />
                    </div>
                </motion.div>
                <h2 className="mt-2 text-center text-5xl font-black text-white tracking-widest text-glow">
                    MedRAG
                </h2>
                <p className="mt-3 text-center text-lg text-brand-100/70 font-medium tracking-wide">
                    Next-Gen Clinical Intelligence
                </p>
            </motion.div>

            <motion.div 
                initial={{ y: 30, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
                className="mt-10 sm:mx-auto sm:w-full sm:max-w-md relative z-10"
            >
                <div className="glass-panel-heavy py-10 px-6 sm:px-12">
                    
                    {/* Role Toggle */}
                    <div className="flex bg-white/5 p-1 rounded-xl mb-8 border border-white/10 relative overflow-hidden">
                        <button
                            type="button"
                            onClick={() => setRole('patient')}
                            className={`flex flex-1 justify-center items-center py-2.5 rounded-lg text-sm font-semibold transition-all duration-300 z-10 ${
                                role === 'patient' ? 'text-deepSpace shadow-neon' : 'text-slate-400 hover:text-white'
                            }`}
                        >
                            <UserSquare2 className="w-4 h-4 mr-2" />
                            Patient
                        </button>
                        <button
                            type="button"
                            onClick={() => setRole('doctor')}
                            className={`flex flex-1 justify-center items-center py-2.5 rounded-lg text-sm font-semibold transition-all duration-300 z-10 ${
                                role === 'doctor' ? 'text-white shadow-neon-coral' : 'text-slate-400 hover:text-white'
                            }`}
                        >
                            <Stethoscope className="w-4 h-4 mr-2" />
                            Doctor
                        </button>
                        
                        {/* Animated background pill for toggle */}
                        <motion.div
                            className={`absolute top-1 bottom-1 w-[calc(50%-4px)] rounded-lg transition-colors ${role === 'patient' ? 'bg-brand-500' : 'bg-coral-500'}`}
                            initial={false}
                            animate={{ 
                                x: role === 'patient' ? '0%' : '100%',
                                left: role === 'patient' ? '4px' : '0px',
                                right: role === 'patient' ? 'auto' : '4px'
                            }}
                            transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        />
                    </div>

                    <form className="space-y-6" onSubmit={handleLogin}>
                        {error && (
                            <motion.div 
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                className="p-3 bg-red-500/10 border border-red-500/50 rounded-xl text-red-400 text-sm text-center"
                            >
                                {error}
                            </motion.div>
                        )}

                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1 ml-1">
                                {role === 'doctor' ? 'Provider Email' : 'Email or Phone Number'}
                            </label>
                            <div className="relative rounded-xl shadow-sm group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none transition-colors group-focus-within:text-brand-500 text-slate-500">
                                    <Mail className="h-5 w-5" />
                                </div>
                                <input
                                    type="text"
                                    required
                                    value={identifier}
                                    onChange={(e) => setIdentifier(e.target.value)}
                                    className="glass-input pl-11"
                                    placeholder={role === 'doctor' ? 'dr.smith@medrag.com' : 'john.doe@email.com'}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1 ml-1">
                                Password
                            </label>
                            <div className="relative rounded-xl shadow-sm group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none transition-colors group-focus-within:text-brand-500 text-slate-500">
                                    <Lock className="h-5 w-5" />
                                </div>
                                <input
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="glass-input pl-11"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        <div className="pt-2">
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                type="submit"
                                disabled={loading || !identifier || !password}
                                className={`w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-xl shadow-lg text-sm font-bold focus:outline-none disabled:opacity-50 transition-all ${
                                    role === 'doctor' ? 'bg-gradient-to-r from-coral-600 to-coral-500 text-white hover:shadow-neon-coral' : 'bg-gradient-to-r from-brand-600 to-brand-500 text-deepSpace hover:shadow-neon'
                                }`}
                            >
                                {loading ? 'Authenticating...' : 'Secure Sign In'}
                                {!loading && <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />}
                            </motion.button>
                        </div>
                    </form>

                    {role === 'patient' && (
                        <div className="mt-8 text-center text-sm text-slate-400">
                            New patient?{' '}
                            <Link to="/register" className="font-semibold text-brand-500 hover:text-brand-400 transition-colors hover:underline underline-offset-4">
                                Create your portal account
                            </Link>
                        </div>
                    )}
                </div>
            </motion.div>
        </div>
    );
};

export default Login;
