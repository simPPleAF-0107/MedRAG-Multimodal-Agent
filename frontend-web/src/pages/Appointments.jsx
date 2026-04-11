import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Search, UserSquare2 } from 'lucide-react';
import { getPatientAppointments, getDoctorsBySpecialty, bookAppointment } from '../services/apiClient';
import toast from 'react-hot-toast';

const Appointments = () => {
    const [user, setUser] = useState(null);
    const [appointments, setAppointments] = useState([]);
    const [doctors, setDoctors] = useState([]);
    const [specialty, setSpecialty] = useState('');
    const [loading, setLoading] = useState(false);
    const [selectedDoctor, setSelectedDoctor] = useState('');
    const [date, setDate] = useState('');
    const [reason, setReason] = useState('');

    useEffect(() => {
        const stored = localStorage.getItem('user');
        if (stored) { const parsed = JSON.parse(stored); setUser(parsed); fetchAppointments(parsed); }
    }, []);

    const fetchAppointments = async (userData) => {
        if (!userData || userData.role !== 'patient') return;
        setLoading(true);
        try { const res = await getPatientAppointments(userData.user_id); if (res.data) setAppointments(res.data); }
        catch (e) { console.error('Failed to fetch appointments', e); }
        finally { setLoading(false); }
    };

    const searchDoctors = async () => {
        if (!specialty) { toast.error('Please select a specialty'); return; }
        setLoading(true);
        try {
            const res = await getDoctorsBySpecialty(specialty);
            let docs = res.data || [];
            if (docs.length === 0) {
                docs = [
                    { id: 1, name: 'Dr. Smith', specialty: 'Cardiology' },
                    { id: 2, name: 'Dr. Jones', specialty: 'Neurology' },
                    { id: 3, name: 'Dr. Patel', specialty: 'Orthopaedic' },
                    { id: 4, name: 'Dr. Lee', specialty: 'Gynaecology' },
                    { id: 5, name: 'Dr. Evans', specialty: 'General' },
                ].filter(d => d.specialty === specialty);
            }
            setDoctors(docs);
        } catch (e) {
            const fallback = [
                { id: 1, name: 'Dr. Smith', specialty: 'Cardiology' },
                { id: 2, name: 'Dr. Jones', specialty: 'Neurology' },
                { id: 3, name: 'Dr. Patel', specialty: 'Orthopaedic' },
                { id: 4, name: 'Dr. Lee', specialty: 'Gynaecology' },
                { id: 5, name: 'Dr. Evans', specialty: 'General' },
            ].filter(d => d.specialty === specialty);
            setDoctors(fallback);
        } finally { setLoading(false); }
    };

    const handleBook = async (e) => {
        e.preventDefault();
        if (!selectedDoctor || !date) { toast.error('Doctor and Date are required'); return; }
        try {
            await bookAppointment({ patient_id: user.user_id, doctor_id: parseInt(selectedDoctor), appointment_date: new Date(date).toISOString(), reason });
            toast.success('Appointment booked successfully!');
            setSelectedDoctor(''); setReason('');
            fetchAppointments(user);
        } catch {
            toast.error('Backend unavailable — added mock appointment.');
            setAppointments(prev => [...prev, { appointment_date: new Date(date).toISOString(), doctor_id: selectedDoctor, reason, status: 'scheduled' }]);
            setSelectedDoctor(''); setReason('');
        }
    };

    const getStatusStyle = (status) => {
        switch (status) {
            case 'confirmed': return { bg: 'var(--success-bg)', color: 'var(--success)', border: 'rgba(46,204,113,0.2)' };
            case 'pending': return { bg: 'var(--warning-bg)', color: '#B8860B', border: 'rgba(241,196,15,0.3)' };
            case 'cancelled': return { bg: 'var(--error-bg)', color: 'var(--error)', border: 'rgba(231,76,60,0.2)' };
            default: return { bg: 'var(--info-bg)', color: 'var(--info)', border: 'rgba(52,152,219,0.2)' };
        }
    };

    return (
        <div className="space-y-6 animate-fade-up">
            <header className="mb-4">
                <h1 className="text-3xl font-extrabold tracking-tight" style={{ color: 'var(--text-primary)' }}>Appointments</h1>
                <p className="mt-2 text-lg" style={{ color: 'var(--text-muted)' }}>Manage your clinical visits.</p>
            </header>

            {user?.role === 'patient' ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Booking Panel */}
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bento-card p-6">
                        <h2 className="text-xl font-bold mb-4 flex items-center" style={{ color: 'var(--primary)' }}>
                            <Search className="w-5 h-5 mr-3" />Find a Specialist
                        </h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Speciality</label>
                                <select className="glass-input" value={specialty} onChange={(e) => setSpecialty(e.target.value)}>
                                    <option value="">Select Specialty</option>
                                    <option value="Cardiology">Cardiology</option>
                                    <option value="Neurology">Neurology</option>
                                    <option value="Orthopaedic">Orthopaedic</option>
                                    <option value="Gynaecology">Gynaecology</option>
                                    <option value="General">General Practice</option>
                                </select>
                            </div>
                            <button onClick={searchDoctors} className="btn-primary w-full">Search Doctors</button>
                        </div>

                        {doctors.length > 0 && (
                            <form onSubmit={handleBook} className="mt-8 space-y-4 pt-6" style={{ borderTop: '1px solid var(--border)' }}>
                                <h3 className="font-bold" style={{ color: 'var(--text-primary)' }}>Book Appointment</h3>
                                <div>
                                    <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Select Doctor</label>
                                    <select required className="glass-input" value={selectedDoctor} onChange={(e) => setSelectedDoctor(e.target.value)}>
                                        <option value="">Choose...</option>
                                        {doctors.map(d => <option key={d.id || d.username} value={d.id}>{d.name || d.username}</option>)}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Date & Time</label>
                                    <input type="datetime-local" required className="glass-input" value={date} onChange={(e) => setDate(e.target.value)} />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>Reason</label>
                                    <input type="text" placeholder="Brief reason for visit" className="glass-input" value={reason} onChange={(e) => setReason(e.target.value)} />
                                </div>
                                <button type="submit" className="btn-secondary w-full">Confirm Booking</button>
                            </form>
                        )}
                    </motion.div>

                    {/* Upcoming Appointments */}
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bento-card p-6">
                        <h2 className="text-xl font-bold mb-4 flex items-center" style={{ color: 'var(--primary)' }}>
                            <Calendar className="w-5 h-5 mr-3" />Your Appointments
                        </h2>
                        {appointments.length === 0 ? (
                            <div className="text-center p-8 rounded-xl" style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}>
                                <Calendar className="w-12 h-12 mx-auto mb-3" style={{ color: 'var(--text-muted)' }} />
                                <p style={{ color: 'var(--text-muted)' }}>No appointments scheduled yet.</p>
                                <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>Search for a specialist to book your first visit.</p>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {appointments.map((app, idx) => {
                                    const st = getStatusStyle(app.status);
                                    return (
                                        <div key={idx} className="p-4 rounded-xl transition flex justify-between items-center group"
                                            style={{ background: 'var(--surface-subtle)', border: '1px solid var(--border)' }}>
                                            <div>
                                                <p className="font-bold transition-colors" style={{ color: 'var(--text-primary)' }}>{new Date(app.appointment_date).toLocaleString()}</p>
                                                <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>Provider ID: {app.doctor_id}</p>
                                                <p className="text-xs mt-1 italic" style={{ color: 'var(--text-secondary)' }}>{app.reason}</p>
                                            </div>
                                            <span className="px-3 py-1 rounded-lg text-xs font-semibold" style={{ background: st.bg, color: st.color, border: `1px solid ${st.border}` }}>
                                                {app.status}
                                            </span>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </motion.div>
                </div>
            ) : (
                <div className="bento-card p-12 text-center flex flex-col items-center">
                    <UserSquare2 className="w-16 h-16 mb-6" style={{ color: 'var(--text-muted)' }} />
                    <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>Doctor View</h2>
                    <p className="max-w-md mx-auto" style={{ color: 'var(--text-muted)' }}>Appointment management for doctors is coming soon.</p>
                </div>
            )}
        </div>
    );
};

export default Appointments;
