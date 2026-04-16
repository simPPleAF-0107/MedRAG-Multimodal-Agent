import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

// Layout
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';

// Pages
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Reports from './pages/Reports';
import Chat from './pages/Chat';
import PatientProfile from './pages/PatientProfile';
import Appointments from './pages/Appointments';
import Settings from './pages/Settings';

// Route guard — redirects to /login when no user session exists
const ProtectedRoute = ({ children }) => {
    const user = localStorage.getItem('user');
    if (!user) {
        return <Navigate to="/login" replace />;
    }
    return children;
};

const Layout = ({ children }) => {
    return (
        <div className="flex h-screen overflow-hidden relative" style={{ background: 'var(--background)', color: 'var(--text-primary)' }}>
            {/* Ambient Background blobs */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-brand-500/20 rounded-full mix-blend-screen filter blur-[100px] animate-blob pointer-events-none z-0"></div>
            <div className="absolute top-[20%] right-[-10%] w-[35%] h-[35%] bg-blue-600/20 rounded-full mix-blend-screen filter blur-[120px] animate-blob animation-delay-2000 pointer-events-none z-0"></div>
            <div className="absolute bottom-[-20%] left-[20%] w-[50%] h-[50%] bg-emerald-500/10 rounded-full mix-blend-screen filter blur-[140px] animate-blob animation-delay-4000 pointer-events-none z-0"></div>
            
            {/* Sidebar layer */}
            <div className="z-10 bg-surface/50 backdrop-blur-xl border-r border-white/5">
                <Sidebar />
            </div>
            
            <div className="flex-1 flex flex-col h-full overflow-hidden z-10 relative bg-surface/30 backdrop-blur-3xl">
                <Navbar />
                <main className="flex-1 overflow-y-auto p-4 md:p-8 animate-slide-up-fade">
                    {children}
                </main>
            </div>
        </div>
    );
};

function App() {
    return (
        <Router>
            <Routes>
                {/* Public routes */}
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Protected layout wraps the main application */}
                <Route path="/dashboard" element={<ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>} />
                <Route path="/upload" element={<ProtectedRoute><Layout><Upload /></Layout></ProtectedRoute>} />
                <Route path="/reports" element={<ProtectedRoute><Layout><Reports /></Layout></ProtectedRoute>} />
                <Route path="/chat" element={<ProtectedRoute><Layout><Chat /></Layout></ProtectedRoute>} />
                <Route path="/patient/:patientId" element={<ProtectedRoute><Layout><PatientProfile /></Layout></ProtectedRoute>} />
                <Route path="/appointments" element={<ProtectedRoute><Layout><Appointments /></Layout></ProtectedRoute>} />
                <Route path="/settings" element={<ProtectedRoute><Layout><Settings /></Layout></ProtectedRoute>} />

                {/* Fallback route */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
            <Toaster 
                position="top-right" 
                toastOptions={{
                    style: {
                        background: '#111',
                        color: '#F8F9FF',
                        border: '1px solid rgba(255,255,255,0.08)',
                        borderRadius: '16px',
                        boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
                        fontWeight: 500,
                    },
                }}
            />
        </Router>
    );
}

export default App;
