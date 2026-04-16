import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Activity, Lock, Mail, ArrowRight, UserSquare2, Stethoscope, Eye, EyeOff, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { loginUser } from '../services/apiClient';

const Login = () => {
    const navigate = useNavigate();
    const [role, setRole] = useState('patient');
    const [identifier, setIdentifier] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
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
                navigate('/dashboard');
            }
        } catch (err) { setError(err.message); }
        finally { setLoading(false); }
    };

    return (
        <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-[#04060C]">

            {/* Ambient background effects */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-1/3 left-1/4 w-[500px] h-[500px] bg-cyan-500/8 rounded-full blur-[150px] animate-pulse" />
                <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-blue-600/6 rounded-full blur-[180px] animate-pulse" style={{ animationDelay: '3s' }} />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/4 rounded-full blur-[200px]" />
                {/* Subtle grid */}
                <div className="absolute inset-0" style={{
                    backgroundImage: 'linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px)',
                    backgroundSize: '50px 50px',
                }} />
            </div>

            <div className="relative z-10 w-full max-w-md px-6">
                {/* Logo & Brand */}
                <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.6, ease: 'easeOut' }} className="text-center mb-10">

                    <motion.div whileHover={{ scale: 1.05 }} className="inline-flex mb-6">
                        <div className="p-4 rounded-3xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-[0_8px_40px_rgba(0,212,255,0.2)]">
                            <Activity className="w-10 h-10 text-white" />
                        </div>
                    </motion.div>

                    <h1 className="text-4xl font-black tracking-wider text-white mb-2">MedRAG</h1>
                    <p className="text-sm font-medium text-gray-500 tracking-widest uppercase">Welcome Back</p>
                </motion.div>

                {/* Auth Card */}
                <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.6, delay: 0.1, ease: 'easeOut' }}
                    className="bg-white/[0.03] backdrop-blur-2xl border border-white/[0.06] rounded-3xl p-8 sm:p-10 shadow-[0_24px_80px_rgba(0,0,0,0.4)]">

                    {/* Role Toggle */}
                    <div className="flex p-1 rounded-2xl mb-8 bg-white/[0.04] border border-white/[0.06] relative overflow-hidden">
                        <button type="button" onClick={() => setRole('patient')}
                            className={`flex flex-1 justify-center items-center py-3 rounded-xl text-sm font-bold transition-all z-10 ${role === 'patient' ? 'text-[#04060C]' : 'text-gray-500 hover:text-gray-300'}`}>
                            <UserSquare2 className="w-4 h-4 mr-2" />Patient
                        </button>
                        <button type="button" onClick={() => setRole('doctor')}
                            className={`flex flex-1 justify-center items-center py-3 rounded-xl text-sm font-bold transition-all z-10 ${role === 'doctor' ? 'text-[#04060C]' : 'text-gray-500 hover:text-gray-300'}`}>
                            <Stethoscope className="w-4 h-4 mr-2" />Doctor
                        </button>
                        <motion.div
                            className="absolute top-1 bottom-1 w-[calc(50%-4px)] rounded-xl"
                            initial={false}
                            animate={{ x: role === 'patient' ? '0%' : '100%', left: role === 'patient' ? '4px' : '0px' }}
                            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                            style={{ background: 'linear-gradient(135deg, #00D4FF, #3B82F6)' }}
                        />
                    </div>

                    <form className="space-y-5" onSubmit={handleLogin}>
                        {error && (
                            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
                                className="p-4 rounded-2xl text-sm text-center bg-red-500/10 border border-red-500/20 text-red-400 font-medium">
                                {error}
                            </motion.div>
                        )}

                        {/* Email Input */}
                        <div>
                            <label className="block text-xs font-bold text-gray-400 mb-2 ml-1 tracking-wider uppercase">
                                {role === 'doctor' ? 'Provider Email' : 'Email Address'}
                            </label>
                            <div className="relative group">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-600 group-focus-within:text-cyan-400 transition-colors" />
                                <input type="text" required value={identifier} onChange={(e) => setIdentifier(e.target.value)}
                                    className="w-full bg-white/[0.04] border border-white/[0.08] rounded-2xl pl-12 pr-5 py-4 text-white text-sm font-medium placeholder:text-gray-600 focus:outline-none focus:border-cyan-500/50 focus:shadow-[0_0_20px_rgba(0,212,255,0.1)] transition-all"
                                    placeholder={role === 'doctor' ? 'dr.arjun.sharma@medrag.com' : 'john.smith@email.com'} />
                            </div>
                        </div>

                        {/* Password Input */}
                        <div>
                            <label className="block text-xs font-bold text-gray-400 mb-2 ml-1 tracking-wider uppercase">Password</label>
                            <div className="relative group">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-600 group-focus-within:text-cyan-400 transition-colors" />
                                <input type={showPassword ? 'text' : 'password'} required value={password} onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-white/[0.04] border border-white/[0.08] rounded-2xl pl-12 pr-12 py-4 text-white text-sm font-medium placeholder:text-gray-600 focus:outline-none focus:border-cyan-500/50 focus:shadow-[0_0_20px_rgba(0,212,255,0.1)] transition-all"
                                    placeholder="••••••••" />
                                <button type="button" onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-400 transition-colors">
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                        </div>

                        {/* Submit */}
                        <div className="pt-3">
                            <motion.button whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}
                                type="submit" disabled={loading || !identifier || !password}
                                className="w-full flex justify-center items-center py-4 px-6 rounded-2xl text-sm font-black text-[#04060C] disabled:opacity-40 transition-all tracking-wide"
                                style={{ background: 'linear-gradient(135deg, #00D4FF, #3B82F6)' }}>
                                {loading ? (
                                    <span className="flex items-center gap-2">
                                        <Sparkles className="w-4 h-4 animate-spin" /> Authenticating...
                                    </span>
                                ) : (
                                    <span className="flex items-center gap-2">
                                        Secure Sign In <ArrowRight className="w-4 h-4" />
                                    </span>
                                )}
                            </motion.button>
                        </div>
                    </form>

                    {/* Register Link */}
                    {role === 'patient' && (
                        <div className="mt-8 text-center text-sm text-gray-500">
                            New patient?{' '}
                            <Link to="/register" className="font-bold text-cyan-400 hover:text-cyan-300 transition-colors">
                                Create your account
                            </Link>
                        </div>
                    )}
                </motion.div>

                {/* Back to home */}
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
                    className="mt-8 text-center">
                    <Link to="/" className="text-xs text-gray-600 hover:text-gray-400 transition-colors font-medium tracking-wider uppercase">
                        ← Back to Home
                    </Link>
                </motion.div>
            </div>
        </div>
    );
};

export default Login;
