import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Activity, Lock, Mail, ArrowRight, UserSquare2, Stethoscope } from 'lucide-react';
import { motion } from 'framer-motion';
import { loginUser } from '../services/apiClient';

const Login = () => {
    const navigate = useNavigate();
    const [role, setRole] = useState('patient');
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
        } catch (err) { setError(err.message); }
        finally { setLoading(false); }
    };

    return (
        <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden"
            style={{ background: 'linear-gradient(135deg, #F8F9FF 0%, #E8EAFF 50%, #F0F8FF 100%)' }}>

            {/* Soft floating orbs */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full blur-[120px] pointer-events-none animate-float"
                style={{ background: 'rgba(58,12,163,0.08)' }} />
            <div className="absolute bottom-1/4 right-1/4 w-[30rem] h-[30rem] rounded-full blur-[140px] pointer-events-none animate-float-delayed"
                style={{ background: 'rgba(67,97,238,0.06)' }} />

            <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, ease: 'easeOut' }} className="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
                <motion.div whileHover={{ scale: 1.05 }} className="flex justify-center mb-4">
                    <div className="p-4 rounded-2xl" style={{ background: 'linear-gradient(135deg, var(--primary), var(--secondary))' }}>
                        <Activity className="w-14 h-14 text-white" />
                    </div>
                </motion.div>
                <h2 className="mt-2 text-center text-5xl font-black tracking-widest" style={{ color: 'var(--text-primary)' }}>MedRAG</h2>
                <p className="mt-3 text-center text-lg font-medium tracking-wide" style={{ color: 'var(--text-muted)' }}>Next-Gen Clinical Intelligence</p>
            </motion.div>

            <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.1, ease: 'easeOut' }}
                className="mt-10 sm:mx-auto sm:w-full sm:max-w-md relative z-10">
                <div className="glass-panel-heavy py-10 px-6 sm:px-12">

                    {/* Role Toggle */}
                    <div className="flex p-1 rounded-xl mb-8 relative overflow-hidden" style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}>
                        <button type="button" onClick={() => setRole('patient')}
                            className={`flex flex-1 justify-center items-center py-2.5 rounded-lg text-sm font-semibold transition-all z-10 ${role === 'patient' ? 'text-white' : ''}`}
                            style={role !== 'patient' ? { color: 'var(--text-muted)' } : {}}>
                            <UserSquare2 className="w-4 h-4 mr-2" />Patient
                        </button>
                        <button type="button" onClick={() => setRole('doctor')}
                            className={`flex flex-1 justify-center items-center py-2.5 rounded-lg text-sm font-semibold transition-all z-10 ${role === 'doctor' ? 'text-white' : ''}`}
                            style={role !== 'doctor' ? { color: 'var(--text-muted)' } : {}}>
                            <Stethoscope className="w-4 h-4 mr-2" />Doctor
                        </button>
                        <motion.div
                            className="absolute top-1 bottom-1 w-[calc(50%-4px)] rounded-lg"
                            initial={false}
                            animate={{ x: role === 'patient' ? '0%' : '100%', left: role === 'patient' ? '4px' : '0px' }}
                            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                            style={{ background: role === 'patient' ? 'var(--primary)' : 'var(--secondary)' }}
                        />
                    </div>

                    <form className="space-y-6" onSubmit={handleLogin}>
                        {error && (
                            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
                                className="p-3 rounded-xl text-sm text-center"
                                style={{ background: 'var(--error-bg)', border: '1px solid rgba(231,76,60,0.3)', color: 'var(--error)' }}>
                                {error}
                            </motion.div>
                        )}

                        <div>
                            <label className="block text-sm font-medium mb-1 ml-1" style={{ color: 'var(--text-secondary)' }}>
                                {role === 'doctor' ? 'Provider Email' : 'Email or Phone Number'}
                            </label>
                            <div className="relative rounded-xl group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none transition-colors" style={{ color: 'var(--text-muted)' }}>
                                    <Mail className="h-5 w-5" />
                                </div>
                                <input type="text" required value={identifier} onChange={(e) => setIdentifier(e.target.value)}
                                    className="glass-input pl-11"
                                    placeholder={role === 'doctor' ? 'dr.smith@medrag.com' : 'john.doe@email.com'} />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-1 ml-1" style={{ color: 'var(--text-secondary)' }}>Password</label>
                            <div className="relative rounded-xl group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none" style={{ color: 'var(--text-muted)' }}>
                                    <Lock className="h-5 w-5" />
                                </div>
                                <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
                                    className="glass-input pl-11" placeholder="••••••••" />
                            </div>
                        </div>

                        <div className="pt-2">
                            <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                                type="submit" disabled={loading || !identifier || !password}
                                className="w-full flex justify-center items-center py-3 px-4 rounded-xl text-sm font-bold text-white disabled:opacity-50 transition-all"
                                style={{ background: role === 'doctor' ? 'var(--secondary)' : 'var(--primary)' }}>
                                {loading ? 'Authenticating...' : 'Secure Sign In'}
                                {!loading && <ArrowRight className="ml-2 w-4 h-4" />}
                            </motion.button>
                        </div>
                    </form>

                    {role === 'patient' && (
                        <div className="mt-8 text-center text-sm" style={{ color: 'var(--text-muted)' }}>
                            New patient?{' '}
                            <Link to="/register" className="font-semibold transition-colors hover:underline underline-offset-4" style={{ color: 'var(--primary)' }}>
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
