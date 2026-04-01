import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

// Layout
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Reports from './pages/Reports';
import Chat from './pages/Chat';
import MealPlanner from './pages/MealPlanner';
import Activity from './pages/Activity';
import MoodTracker from './pages/MoodTracker';
import CycleTracker from './pages/CycleTracker';
import PatientProfile from './pages/PatientProfile';
import Appointments from './pages/Appointments';

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
        <div className="flex h-screen bg-transparent overflow-hidden text-slate-100">
            <Sidebar />
            <div className="flex-1 flex flex-col h-full overflow-hidden">
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
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Protected layout wraps the main application */}
                <Route path="/" element={<ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>} />
                <Route path="/upload" element={<ProtectedRoute><Layout><Upload /></Layout></ProtectedRoute>} />
                <Route path="/reports" element={<ProtectedRoute><Layout><Reports /></Layout></ProtectedRoute>} />
                <Route path="/chat" element={<ProtectedRoute><Layout><Chat /></Layout></ProtectedRoute>} />
                <Route path="/meal-planner" element={<ProtectedRoute><Layout><MealPlanner /></Layout></ProtectedRoute>} />
                <Route path="/activity" element={<ProtectedRoute><Layout><Activity /></Layout></ProtectedRoute>} />
                <Route path="/mood-tracker" element={<ProtectedRoute><Layout><MoodTracker /></Layout></ProtectedRoute>} />
                <Route path="/cycle-tracker" element={<ProtectedRoute><Layout><CycleTracker /></Layout></ProtectedRoute>} />
                <Route path="/patient/:patientId" element={<ProtectedRoute><Layout><PatientProfile /></Layout></ProtectedRoute>} />
                <Route path="/appointments" element={<ProtectedRoute><Layout><Appointments /></Layout></ProtectedRoute>} />

                {/* Fallback route */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
            <Toaster 
                position="top-right" 
                toastOptions={{
                    style: {
                        background: 'rgba(15, 23, 42, 0.9)',
                        color: '#e2e8f0',
                        border: '1px solid rgba(255,255,255,0.1)',
                        backdropFilter: 'blur(10px)',
                        borderRadius: '12px',
                    },
                }}
            />
        </Router>
    );
}

export default App;

