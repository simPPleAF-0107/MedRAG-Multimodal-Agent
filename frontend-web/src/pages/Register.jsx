import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Activity, ArrowRight, ArrowLeft } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { registerPatient } from '../services/apiClient';

const generateId = (first, last) => {
    const f = first ? first[0].toUpperCase() : 'X';
    const l = last ? last[0].toUpperCase() : 'X';
    const num = Math.floor(100000 + Math.random() * 900000);
    return `${f}${l}${num}`;
};

const Register = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const [formData, setFormData] = useState({
        firstName: '', lastName: '', email: '', contactNumber: '', password: '', dob: '', gender: '',
        height: '', weight: '', smokingStatus: '', drinkingStatus: '', lifestyleOther: '',
        pastConditions: '', surgeries: '', familyHistory: '', allergies: '', medications: '', physicianName: ''
    });

    const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

    const handleRegister = async (e) => {
        e.preventDefault();
        if (step < 3) return setStep(step + 1);

        setLoading(true);
        setError('');
        
        const patientId = generateId(formData.firstName, formData.lastName);
        const payload = { ...formData, patientId };

        try {
            const res = await registerPatient(payload);
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

    const variants = {
        enter: (direction) => {
            return {
                x: direction > 0 ? 50 : -50,
                opacity: 0
            };
        },
        center: {
            zIndex: 1,
            x: 0,
            opacity: 1
        },
        exit: (direction) => {
            return {
                zIndex: 0,
                x: direction < 0 ? 50 : -50,
                opacity: 0
            };
        }
    };

    const [direction, setDirection] = useState(1);
    
    const nextStep = () => {
        setDirection(1);
        setStep(step + 1);
    };
    
    const prevStep = () => {
        setDirection(-1);
        setStep(step - 1);
    };

    return (
        <div className="min-h-screen bg-transparent flex flex-col justify-center py-12 sm:px-6 lg:px-8 font-sans relative overflow-x-hidden">
            {/* Ambient Background Glow */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-500/20 rounded-full blur-[100px] pointer-events-none animate-float"></div>
            <div className="absolute bottom-1/4 right-1/4 w-[30rem] h-[30rem] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none animate-float-delayed"></div>

            <motion.div 
                initial={{ y: -20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="sm:mx-auto sm:w-full sm:max-w-2xl relative z-10"
            >
                <div className="flex justify-center mb-6">
                    <motion.div 
                        whileHover={{ scale: 1.05 }}
                        className="bg-gradient-to-tr from-brand-600 to-brand-400 p-4 rounded-2xl shadow-neon animate-pulse-glow"
                    >
                        <Activity className="w-12 h-12 text-deepSpace" />
                    </motion.div>
                </div>
                <h2 className="text-center text-4xl font-extrabold text-white text-glow tracking-wide">Patient Portal Setup</h2>
            </motion.div>

            <motion.div 
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.1 }}
                className="mt-8 sm:mx-auto sm:w-full sm:max-w-2xl relative z-10"
            >
                <div className="glass-panel-heavy py-8 px-6 sm:px-10">
                    
                    {/* Stepper Header */}
                    <div className="flex justify-between items-center mb-8 border-b border-white/10 pb-6 relative">
                        {[1, 2, 3].map(s => (
                            <div key={s} className="flex items-center z-10">
                                <motion.div 
                                    animate={step === s ? { scale: 1.1 } : { scale: 1 }}
                                    className={`w-10 h-10 flex items-center justify-center rounded-full text-base font-bold transition-all duration-300 ${step >= s ? 'bg-gradient-to-br from-brand-500 to-brand-400 text-deepSpace shadow-neon' : 'bg-white/10 text-slate-400 border border-white/10'}`}
                                >
                                    {s}
                                </motion.div>
                                {s < 3 && <div className={`h-1 w-16 sm:w-32 mx-3 rounded transition-all duration-500 ${step > s ? 'bg-brand-500 shadow-[0_0_10px_rgba(69,243,255,0.5)]' : 'bg-white/10'}`} />}
                            </div>
                        ))}
                    </div>

                    <form onSubmit={(e) => {
                        e.preventDefault();
                        if (step < 3) nextStep();
                        else handleRegister(e);
                    }} className="space-y-6">
                        {error && (
                            <motion.div 
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="p-3 bg-red-500/10 text-red-400 rounded-xl border border-red-500/30 text-sm"
                            >
                                {error}
                            </motion.div>
                        )}

                        <div className="relative min-h-[350px]">
                            <AnimatePresence custom={direction} mode="wait">
                                {/* STEP 1: Personal Details */}
                                {step === 1 && (
                                    <motion.div 
                                        key="step1"
                                        custom={direction}
                                        variants={variants}
                                        initial="enter"
                                        animate="center"
                                        exit="exit"
                                        transition={{ duration: 0.3 }}
                                        className="space-y-5"
                                    >
                                        <h3 className="text-2xl font-bold text-white mb-6">Personal Identification</h3>
                                        <div className="grid grid-cols-2 gap-5">
                                            <div>
                                                <label className="block text-sm text-slate-400 ml-1 mb-1">First Name</label>
                                                <input required name="firstName" value={formData.firstName} onChange={handleChange} className="glass-input" />
                                            </div>
                                            <div>
                                                <label className="block text-sm text-slate-400 ml-1 mb-1">Last Name</label>
                                                <input required name="lastName" value={formData.lastName} onChange={handleChange} className="glass-input" />
                                            </div>
                                        </div>
                                        <div>
                                            <label className="block text-sm text-slate-400 ml-1 mb-1">Email Address</label>
                                            <input required type="email" name="email" value={formData.email} onChange={handleChange} className="glass-input" />
                                        </div>
                                        <div>
                                            <label className="block text-sm text-slate-400 ml-1 mb-1">Password</label>
                                            <input required type="password" name="password" value={formData.password} onChange={handleChange} className="glass-input" />
                                        </div>
                                        <div className="grid grid-cols-2 gap-5">
                                            <div>
                                                <label className="block text-sm text-slate-400 ml-1 mb-1">Date of Birth</label>
                                                <input required type="date" name="dob" value={formData.dob} onChange={handleChange} className="glass-input [&::-webkit-calendar-picker-indicator]:filter-invert" />
                                            </div>
                                            <div>
                                                <label className="block text-sm text-slate-400 ml-1 mb-1">Sex / Gender</label>
                                                <select name="gender" value={formData.gender} onChange={handleChange} className="glass-input appearance-none">
                                                    <option value="" className="bg-slate-900">Select...</option>
                                                    <option value="Male" className="bg-slate-900">Male</option>
                                                    <option value="Female" className="bg-slate-900">Female</option>
                                                    <option value="Other" className="bg-slate-900">Other</option>
                                                </select>
                                            </div>
                                        </div>
                                    </motion.div>
                                )}

                                {/* STEP 2: Vitals & Lifestyle */}
                                {step === 2 && (
                                    <motion.div 
                                        key="step2"
                                        custom={direction}
                                        variants={variants}
                                        initial="enter"
                                        animate="center"
                                        exit="exit"
                                        transition={{ duration: 0.3 }}
                                        className="space-y-5"
                                    >
                                        <h3 className="text-2xl font-bold text-white mb-6">Vitals & Lifestyle</h3>
                                        <div className="grid grid-cols-2 gap-5">
                                            <div>
                                                <label className="block text-sm text-slate-400 ml-1 mb-1">Height (cm)</label>
                                                <input required type="number" name="height" value={formData.height} onChange={handleChange} className="glass-input" />
                                            </div>
                                            <div>
                                                <label className="block text-sm text-slate-400 ml-1 mb-1">Weight (kg)</label>
                                                <input required type="number" name="weight" value={formData.weight} onChange={handleChange} className="glass-input" />
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-2 gap-5">
                                            <div>
                                                <label className="block text-sm text-slate-400 ml-1 mb-1">Smoking Status</label>
                                                <select name="smokingStatus" value={formData.smokingStatus} onChange={handleChange} className="glass-input appearance-none">
                                                    <option value="" className="bg-slate-900">Select...</option>
                                                    <option value="Never" className="bg-slate-900">Never</option>
                                                    <option value="Occasional" className="bg-slate-900">Occasional</option>
                                                    <option value="Regular" className="bg-slate-900">Regular</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-sm text-slate-400 ml-1 mb-1">Drinking Status</label>
                                                <select name="drinkingStatus" value={formData.drinkingStatus} onChange={handleChange} className="glass-input appearance-none">
                                                    <option value="" className="bg-slate-900">Select...</option>
                                                    <option value="Never" className="bg-slate-900">Never</option>
                                                    <option value="Occasional" className="bg-slate-900">Occasional</option>
                                                    <option value="Regular" className="bg-slate-900">Regular</option>
                                                </select>
                                            </div>
                                        </div>
                                    </motion.div>
                                )}

                                {/* STEP 3: Medical History */}
                                {step === 3 && (
                                    <motion.div 
                                        key="step3"
                                        custom={direction}
                                        variants={variants}
                                        initial="enter"
                                        animate="center"
                                        exit="exit"
                                        transition={{ duration: 0.3 }}
                                        className="space-y-6"
                                    >
                                        <h3 className="text-2xl font-bold text-white mb-6">Medical History</h3>
                                        <div>
                                            <label className="block text-sm text-slate-400 ml-1 mb-1">Past Medical Conditions</label>
                                            <input name="conditions" placeholder="e.g. Asthma, Hypertension" value={formData.conditions} onChange={handleChange} className="glass-input" />
                                        </div>
                                        <div>
                                            <label className="block text-sm text-slate-400 ml-1 mb-1">Surgical History</label>
                                            <input name="surgeries" placeholder="e.g. Appendectomy" value={formData.surgeries} onChange={handleChange} className="glass-input" />
                                        </div>
                                        <div>
                                            <label className="block text-sm text-slate-400 ml-1 mb-1">Allergies</label>
                                            <input name="allergies" placeholder="Drug, Food, Environmental" value={formData.allergies} onChange={handleChange} className="glass-input" />
                                        </div>
                                        <div>
                                            <label className="block text-sm text-slate-400 ml-1 mb-1">Primary Physician</label>
                                            <input name="physicianName" placeholder="Dr. First Last" value={formData.physicianName} onChange={handleChange} className="glass-input" />
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>

                        {/* Controller buttons */}
                        <div className="flex justify-between items-center mt-8 pt-6 border-t border-white/10 relative z-20">
                            {step > 1 ? (
                                <button type="button" onClick={prevStep} className="flex items-center text-slate-400 hover:text-white transition-colors px-4 py-2 hover:bg-white/5 rounded-lg">
                                    <ArrowLeft className="w-4 h-4 mr-2" /> Back
                                </button>
                            ) : (
                                <Link to="/login" className="text-sm text-slate-400 hover:text-brand-500 transition-colors px-4 py-2 hover:bg-white/5 rounded-lg font-medium">Cancel</Link>
                            )}
                            
                            <motion.button 
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                type="submit" 
                                disabled={loading} 
                                className="flex items-center btn-primary"
                            >
                                {loading ? (
                                    <div className="w-5 h-5 rounded-full border-2 border-deepSpace border-t-transparent animate-spin mr-2" />
                                ) : null}
                                {step < 3 ? 'Next Phase' : 'Complete Registration'}
                                {step < 3 && <ArrowRight className="w-4 h-4 ml-2" />}
                            </motion.button>
                        </div>
                    </form>
                </div>
            </motion.div>
        </div>
    );
};

export default Register;
