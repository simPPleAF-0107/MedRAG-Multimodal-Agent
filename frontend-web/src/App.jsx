import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Layout
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Reports from './pages/Reports';
import Chat from './pages/Chat';
import MealPlanner from './pages/MealPlanner';
import Activity from './pages/Activity';
import MoodTracker from './pages/MoodTracker';
import CycleTracker from './pages/CycleTracker';

const Layout = ({ children }) => {
    return (
        <div className="flex h-screen bg-slate-50 overflow-hidden">
            <Sidebar />
            <div className="flex-1 flex flex-col h-full overflow-hidden">
                <Navbar />
                <main className="flex-1 overflow-y-auto p-4 md:p-8">
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

                {/* Protected layout wraps the main application */}
                <Route path="/" element={<Layout><Dashboard /></Layout>} />
                <Route path="/upload" element={<Layout><Upload /></Layout>} />
                <Route path="/reports" element={<Layout><Reports /></Layout>} />
                <Route path="/chat" element={<Layout><Chat /></Layout>} />
                <Route path="/meal-planner" element={<Layout><MealPlanner /></Layout>} />
                <Route path="/activity" element={<Layout><Activity /></Layout>} />
                <Route path="/mood-tracker" element={<Layout><MoodTracker /></Layout>} />
                <Route path="/cycle-tracker" element={<Layout><CycleTracker /></Layout>} />

                {/* Fallback route */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </Router>
    );
}

export default App;
