import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Activity, Lock, Mail, ArrowRight, UserSquare2, Stethoscope } from 'lucide-react';
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
        <div className="min-h-screen bg-deepSpace flex flex-col justify-center py-12 sm:px-6 lg:px-8 font-sans">
            <div className="sm:mx-auto sm:w-full sm:max-w-md">
                <div className="flex justify-center">
                    <div className="bg-brand-500 p-4 rounded-xl shadow-neon">
                        <Activity className="w-12 h-12 text-deepSpace" />
                    </div>
                </div>
                <h2 className="mt-6 text-center text-4xl font-extrabold text-white tracking-tight">
                    MedRAG
                </h2>
                <p className="mt-2 text-center text-md text-brand-100">
                    Clinical Intelligence Platform
                </p>
            </div>

            <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
                <div className="bg-surface py-8 px-4 shadow-xl sm:rounded-2xl sm:px-10 border border-slate-800">
                    
                    {/* Role Toggle */}
                    <div className="flex bg-slate-800 p-1 rounded-lg mb-8">
                        <button
                            type="button"
                            onClick={() => setRole('patient')}
                            className={`flex flex-1 justify-center items-center py-2.5 rounded-md text-sm font-semibold transition-all ${
                                role === 'patient' ? 'bg-brand-500 text-deepSpace shadow-neon' : 'text-slate-400 hover:text-white'
                            }`}
                        >
                            <UserSquare2 className="w-4 h-4 mr-2" />
                            Patient
                        </button>
                        <button
                            type="button"
                            onClick={() => setRole('doctor')}
                            className={`flex flex-1 justify-center items-center py-2.5 rounded-md text-sm font-semibold transition-all ${
                                role === 'doctor' ? 'bg-coral-500 text-white shadow-neon-coral' : 'text-slate-400 hover:text-white'
                            }`}
                        >
                            <Stethoscope className="w-4 h-4 mr-2" />
                            Doctor
                        </button>
                    </div>

                    <form className="space-y-6" onSubmit={handleLogin}>
                        {error && (
                            <div className="p-3 bg-danger/20 border border-danger/50 rounded-lg text-danger text-sm text-center">
                                {error}
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1">
                                {role === 'doctor' ? 'Provider Email' : 'Email or Phone Number'}
                            </label>
                            <div className="relative rounded-md shadow-sm">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Mail className="h-5 w-5 text-slate-500" />
                                </div>
                                <input
                                    type="text"
                                    required
                                    value={identifier}
                                    onChange={(e) => setIdentifier(e.target.value)}
                                    className="block w-full pl-10 pr-3 py-3 bg-slate-900 border border-slate-700 rounded-lg text-white focus:ring-brand-500 focus:border-brand-500 sm:text-sm transition-colors placeholder-slate-600"
                                    placeholder={role === 'doctor' ? 'dr.smith@medrag.com' : 'john.doe@email.com'}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-1">
                                Password
                            </label>
                            <div className="relative rounded-md shadow-sm">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Lock className="h-5 w-5 text-slate-500" />
                                </div>
                                <input
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="block w-full pl-10 pr-3 py-3 bg-slate-900 border border-slate-700 rounded-lg text-white focus:ring-brand-500 focus:border-brand-500 sm:text-sm transition-colors placeholder-slate-600"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        <div>
                            <button
                                type="submit"
                                disabled={loading || !identifier || !password}
                                className={`w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-deepSpace focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-deepSpace disabled:opacity-50 transition-all ${
                                    role === 'doctor' ? 'bg-coral-500 focus:ring-coral-500 text-white hover:bg-coral-400' : 'bg-brand-500 focus:ring-brand-500 hover:bg-brand-400'
                                }`}
                            >
                                {loading ? 'Authenticating...' : 'Secure Sign In'}
                                {!loading && <ArrowRight className="ml-2 w-4 h-4" />}
                            </button>
                        </div>
                    </form>

                    {role === 'patient' && (
                        <div className="mt-6 text-center text-sm text-slate-400">
                            New patient?{' '}
                            <Link to="/register" className="font-medium text-brand-500 hover:text-brand-400 transition-colors">
                                Create your portal account
                            </Link>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Login;
