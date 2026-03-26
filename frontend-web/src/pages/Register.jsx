import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Activity, ArrowRight, ArrowLeft } from 'lucide-react';
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

    return (
        <div className="min-h-screen bg-deepSpace flex flex-col justify-center py-12 sm:px-6 lg:px-8 font-sans">
            <div className="sm:mx-auto sm:w-full sm:max-w-2xl">
                <div className="flex justify-center mb-6">
                    <div className="bg-brand-500 p-3 rounded-xl shadow-neon">
                        <Activity className="w-10 h-10 text-deepSpace" />
                    </div>
                </div>
                <h2 className="text-center text-3xl font-extrabold text-white">Patient Onboarding</h2>
            </div>

            <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-2xl">
                <div className="bg-surface py-8 px-6 shadow-xl sm:rounded-2xl border border-slate-800">
                    
                    {/* Stepper Header */}
                    <div className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
                        {[1, 2, 3].map(s => (
                            <div key={s} className="flex items-center">
                                <div className={`w-8 h-8 flex items-center justify-center rounded-full text-sm font-bold ${step >= s ? 'bg-brand-500 text-deepSpace shadow-neon' : 'bg-slate-800 text-slate-500'}`}>
                                    {s}
                                </div>
                                {s < 3 && <div className={`h-1 w-12 sm:w-24 mx-2 rounded ${step > s ? 'bg-brand-500' : 'bg-slate-800'}`} />}
                            </div>
                        ))}
                    </div>

                    <form onSubmit={handleRegister} className="space-y-6">
                        {error && <div className="p-3 bg-danger/20 text-danger rounded-lg text-sm">{error}</div>}

                        {/* STEP 1: Personal Details */}
                        {step === 1 && (
                            <div className="space-y-4 animate-fade-in">
                                <h3 className="text-xl font-bold text-white mb-4">Personal Identification</h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm text-slate-400">First Name</label>
                                        <input required name="firstName" value={formData.firstName} onChange={handleChange} className="w-full mt-1 p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:border-brand-500" />
                                    </div>
                                    <div>
                                        <label className="block text-sm text-slate-400">Last Name</label>
                                        <input required name="lastName" value={formData.lastName} onChange={handleChange} className="w-full mt-1 p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:border-brand-500" />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm text-slate-400">Email Address</label>
                                    <input required type="email" name="email" value={formData.email} onChange={handleChange} className="w-full mt-1 p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:border-brand-500" />
                                </div>
                                <div>
                                    <label className="block text-sm text-slate-400">Password</label>
                                    <input required type="password" name="password" value={formData.password} onChange={handleChange} className="w-full mt-1 p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:border-brand-500" />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm text-slate-400">Date of Birth</label>
                                        <input required type="date" name="dob" value={formData.dob} onChange={handleChange} className="w-full mt-1 p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:border-brand-500" />
                                    </div>
                                    <div>
                                        <label className="block text-sm text-slate-400">Sex / Gender</label>
                                        <select name="gender" value={formData.gender} onChange={handleChange} className="w-full mt-1 p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:border-brand-500">
                                            <option value="">Select...</option><option value="Male">Male</option><option value="Female">Female</option><option value="Other">Other</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* STEP 2: Vitals & Lifestyle */}
                        {step === 2 && (
                            <div className="space-y-4 animate-fade-in">
                                <h3 className="text-xl font-bold text-white mb-4">Vitals & Lifestyle</h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm text-slate-400">Height (cm)</label>
                                        <input required type="number" name="height" value={formData.height} onChange={handleChange} className="w-full mt-1 p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:border-brand-500" />
                                    </div>
                                    <div>
                                        <label className="block text-sm text-slate-400">Weight (kg)</label>
                                        <input required type="number" name="weight" value={formData.weight} onChange={handleChange} className="w-full mt-1 p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:border-brand-500" />
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm text-slate-400">Smoking Status</label>
                                        <select name="smokingStatus" value={formData.smokingStatus} onChange={handleChange} className="w-full mt-1 p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:border-brand-500">
                                            <option value="">Select...</option><option value="Never">Never</option><option value="Occasional">Occasional</option><option value="Regular">Regular</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm text-slate-400">Drinking Status</label>
                                        <select name="drinkingStatus" value={formData.drinkingStatus} onChange={handleChange} className="w-full mt-1 p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:border-brand-500">
                                            <option value="">Select...</option><option value="Never">Never</option><option value="Occasional">Occasional</option><option value="Regular">Regular</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* STEP 3: Medical History */}
                        {step === 3 && (
                            <div className="space-y-4 animate-fade-in">
                                <h3 className="text-xl font-bold text-white mb-4">Medical History</h3>
                                <input name="conditions" placeholder="Past Medical Conditions" value={formData.conditions} onChange={handleChange} className="w-full p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:border-brand-500" />
                                <input name="surgeries" placeholder="Surgical History" value={formData.surgeries} onChange={handleChange} className="w-full p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:border-brand-500" />
                                <input name="allergies" placeholder="Allergies (Drug, Food, Environmental)" value={formData.allergies} onChange={handleChange} className="w-full p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:border-brand-500" />
                                <input name="physicianName" placeholder="Primary Attending Physician" value={formData.physicianName} onChange={handleChange} className="w-full p-2.5 bg-slate-900 border border-slate-700 rounded text-white focus:border-brand-500" />
                            </div>
                        )}

                        {/* Controller buttons */}
                        <div className="flex justify-between items-center mt-8 pt-4 border-t border-slate-800">
                            {step > 1 ? (
                                <button type="button" onClick={() => setStep(step - 1)} className="flex items-center text-slate-400 hover:text-white transition-colors px-4 py-2">
                                    <ArrowLeft className="w-4 h-4 mr-2" /> Back
                                </button>
                            ) : (
                                <Link to="/login" className="text-sm text-slate-500 hover:text-brand-500">Cancel</Link>
                            )}
                            
                            <button type="submit" disabled={loading} className="flex items-center bg-brand-500 hover:bg-brand-400 text-deepSpace font-bold py-2.5 px-6 rounded-lg transition-colors">
                                {loading && <div className="w-4 h-4 rounded-full border-2 border-deepSpace border-t-transparent animate-spin mr-2" />}
                                {step < 3 ? 'Next Phase' : 'Complete Registration'}
                                {step < 3 && <ArrowRight className="w-4 h-4 ml-2" />}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Register;
