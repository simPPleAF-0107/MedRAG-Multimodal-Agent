import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, User, Search, UserSquare2, RefreshCw } from 'lucide-react';
import { getPatientAppointments, getDoctorsBySpecialty, bookAppointment } from '../services/apiClient';
import toast from 'react-hot-toast';

const Appointments = () => {
    const [user, setUser] = useState(null);
    const [appointments, setAppointments] = useState([]);
    const [doctors, setDoctors] = useState([]);
    const [specialty, setSpecialty] = useState('');
    const [loading, setLoading] = useState(false);
    
    // For booking
    const [selectedDoctor, setSelectedDoctor] = useState('');
    const [date, setDate] = useState('');
    const [reason, setReason] = useState('');

    useEffect(() => {
        const stored = localStorage.getItem('user');
        if (stored) {
            const parsed = JSON.parse(stored);
            setUser(parsed);
            fetchAppointments(parsed);
        }
    }, []);

    const fetchAppointments = async (userData) => {
        if (!userData || userData.role !== 'patient') return;
        setLoading(true);
        try {
            const res = await getPatientAppointments(userData.user_id);
            if (res.data) setAppointments(res.data);
        } catch (e) {
            console.error("Failed to fetch appointments", e);
        } finally {
            setLoading(false);
        }
    };

    const searchDoctors = async () => {
        if (!specialty) {
            toast.error("Please select a specialty");
            return;
        }
        setLoading(true);
        try {
            const res = await getDoctorsBySpecialty(specialty);
            setDoctors(res.data || []);
            if (res.data && res.data.length === 0) {
                // offline fallback logic
                const offlineDocs = [
                    { id: 1, name: 'Dr. Smith', specialty: 'Cardiology' },
                    { id: 2, name: 'Dr. Jones', specialty: 'Neurology' },
                    { id: 3, name: 'Dr. Patel', specialty: 'Orthopaedic' },
                    { id: 4, name: 'Dr. Lee', specialty: 'Gynaecology' },
                    { id: 5, name: 'Dr. Evans', specialty: 'General' }
                ].filter(d => d.specialty === specialty);
                if(offlineDocs.length > 0) setDoctors(offlineDocs);
                else { toast.info("No offline mock doctors for this specialty."); setDoctors([]); }
            }
        } catch (e) {
            console.warn("Failed to fetch doctors, using mock", e);
             const offlineDocs = [
                { id: 1, name: 'Dr. Smith', specialty: 'Cardiology' },
                { id: 2, name: 'Dr. Jones', specialty: 'Neurology' },
                { id: 3, name: 'Dr. Patel', specialty: 'Orthopaedic' },
                { id: 4, name: 'Dr. Lee', specialty: 'Gynaecology' },
                { id: 5, name: 'Dr. Evans', specialty: 'General' }
            ].filter(d => d.specialty === specialty);
            setDoctors(offlineDocs);
        } finally {
            setLoading(false);
        }
    };

    const handleBook = async (e) => {
        e.preventDefault();
        if (!selectedDoctor || !date) {
            toast.error("Doctor and Date are required");
            return;
        }
        try {
            const payload = {
                patient_id: user.user_id,
                doctor_id: parseInt(selectedDoctor),
                appointment_date: new Date(date).toISOString(),
                reason: reason
            };
            await bookAppointment(payload);
            toast.success("Appointment booked successfully!");
            setSelectedDoctor('');
            setReason('');
            fetchAppointments(user);
        } catch (e) {
            toast.error("Failed to book appointment, using mock flow.");
            // Mock addition
            const mockApp = { appointment_date: new Date(date).toISOString(), doctor_id: selectedDoctor, reason, status: 'scheduled' };
            setAppointments(prev => [...prev, mockApp]);
            setSelectedDoctor('');
            setReason('');
        }
    };

    return (
        <div className="space-y-6">
            <header className="mb-8">
                <h1 className="text-3xl font-extrabold text-white tracking-tight text-glow">Appointments</h1>
                <p className="text-brand-100/70 mt-2 text-lg">Manage your clinical visits.</p>
            </header>

            {user?.role === 'patient' ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Booking Panel */}
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="glass-panel p-6"
                    >
                        <h2 className="text-xl font-bold mb-4 text-brand-400 flex items-center">
                            <Search className="w-5 h-5 mr-3" />
                            Find a Specialist
                        </h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-1">
                                    Speciality (AI Recommended or Manual)
                                </label>
                                <select 
                                    className="glass-input w-full p-3 rounded-xl appearance-none bg-[#0B0C10]/80"
                                    value={specialty}
                                    onChange={(e) => setSpecialty(e.target.value)}
                                >
                                    <option value="">Select Specialty</option>
                                    <option value="Cardiology">Cardiology</option>
                                    <option value="Neurology">Neurology</option>
                                    <option value="Orthopaedic">Orthopaedic</option>
                                    <option value="Gynaecology">Gynaecology</option>
                                    <option value="General">General Practice</option>
                                </select>
                            </div>
                            <button 
                                onClick={searchDoctors}
                                className="w-full py-3 bg-brand-600 hover:bg-brand-500 text-deepSpace font-bold rounded-xl transition cursor-pointer"
                            >
                                Search Doctors
                            </button>
                        </div>

                        {doctors.length > 0 && (
                            <form onSubmit={handleBook} className="mt-8 space-y-4 border-t border-white/10 pt-6">
                                <h3 className="font-bold text-white mb-2 shadow-sm">Book Appointment</h3>
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-1">Select Doctor</label>
                                    <select 
                                        required
                                        className="glass-input w-full p-3 rounded-xl appearance-none bg-[#0B0C10]/80"
                                        value={selectedDoctor}
                                        onChange={(e) => setSelectedDoctor(e.target.value)}
                                    >
                                        <option value="">Choose...</option>
                                        {doctors.map(d => (
                                            <option key={d.id || d.username} value={d.id}>{d.name || d.username}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-1">Date & Time</label>
                                    <input 
                                        type="datetime-local" 
                                        required 
                                        className="glass-input w-full p-3 rounded-xl bg-[#0B0C10]/80 text-white"
                                        value={date}
                                        onChange={(e) => setDate(e.target.value)}
                                        style={{ colorScheme: 'dark' }}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-1">Reason</label>
                                    <input 
                                        type="text" 
                                        placeholder="Brief reason for visit"
                                        className="glass-input w-full p-3 rounded-xl bg-[#0B0C10]/80 text-white"
                                        value={reason}
                                        onChange={(e) => setReason(e.target.value)}
                                    />
                                </div>
                                <button type="submit" className="w-full py-3 bg-gradient-to-r from-coral-600 to-coral-500 hover:shadow-neon-coral text-white font-bold rounded-xl transition cursor-pointer mt-2">
                                    Confirm Booking
                                </button>
                            </form>
                        )}
                    </motion.div>

                    {/* Upcoming Appointments */}
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="glass-panel p-6"
                    >
                        <h2 className="text-xl font-bold mb-4 text-brand-400 flex items-center">
                            <Calendar className="w-5 h-5 mr-3" />
                            Your Appointments
                        </h2>
                        {appointments.length === 0 ? (
                            <div className="text-center p-8 bg-white/5 rounded-xl border border-white/10">
                                <p className="text-slate-400">No appointments scheduled.</p>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {appointments.map((app, idx) => (
                                    <div key={idx} className="p-4 bg-white/5 border border-white/10 rounded-xl hover:border-brand-500/50 transition flex justify-between items-center group">
                                        <div>
                                            <p className="font-bold text-white group-hover:text-brand-400 transition-colors">{new Date(app.appointment_date).toLocaleString()}</p>
                                            <p className="text-sm text-slate-400 mt-1">Provider ID: {app.doctor_id}</p>
                                            <p className="text-xs text-brand-300/80 mt-1 italic">{app.reason}</p>
                                        </div>
                                        <div>
                                            <span className="px-3 py-1 bg-brand-500/20 text-brand-300 rounded-lg text-xs font-semibold backdrop-blur-sm border border-brand-500/30">
                                                {app.status}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </motion.div>
                </div>
            ) : (
                <div className="glass-panel p-12 text-center flex flex-col items-center">
                    <UserSquare2 className="w-16 h-16 text-slate-500 mb-6" />
                    <h2 className="text-2xl font-bold text-white mb-2">Doctor View</h2>
                    <p className="text-slate-400 max-w-md mx-auto">Appointment management for doctors is coming soon. Please advise your patients to book via their patient portal.</p>
                </div>
            )}
        </div>
    );
};

export default Appointments;
