import { useState } from 'react';
import Navbar from './components/layout/Navbar';
import Background from './components/layout/Background';
import Toast from './components/ui/Toast';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import { ToastContext } from './contexts/ToastContext';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('login');
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('voicekey_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  const handleAuthSuccess = (authData) => {
    const nextUser = { name: authData.username };
    setUser(nextUser);
    localStorage.setItem('voicekey_user', JSON.stringify(nextUser));
    localStorage.setItem('voicekey_token', authData.access_token || '');
    showToast('Authentication successful!', 'success');
    setCurrentPage('dashboard');
  };

  const handleSignOut = () => {
    setUser(null);
    localStorage.removeItem('voicekey_user');
    localStorage.removeItem('voicekey_token');
    setCurrentPage('login');
    showToast('Signed out successfully.', 'success');
  };

  return (
    <ToastContext.Provider value={showToast}>
      <div className="app">
        <Background />
        <Navbar onNav={setCurrentPage} currentPage={currentPage} user={user} onSignOut={handleSignOut} />

        <main className="main-content">
          {currentPage === 'login' && (
            <Login
              onSuccess={handleAuthSuccess}
              onSwitch={() => setCurrentPage('register')}
            />
          )}

          {currentPage === 'register' && (
            <Register
              onSuccess={() => {
                showToast('Voice profile created!', 'success');
                setCurrentPage('login');
              }}
              onSwitch={() => setCurrentPage('login')}
            />
          )}

          {currentPage === 'dashboard' && (
            <Dashboard user={user} />
          )}
        </main>

        <footer className="footer">
          <div className="footer-content">
            <p>&copy; 2026 VoiceKey Biometrics, Inc.</p>
            <span className="footer-badge">🔒 SOC 2 Type II Certified</span>
            <div className="footer-links">
              <a href="#">Privacy</a>
              <a href="#">Terms</a>
              <a href="#">Security</a>
              <a href="#">Status</a>
            </div>
          </div>
        </footer>

        {toast && <Toast message={toast.message} type={toast.type} />}
      </div>
    </ToastContext.Provider>
  );
}

export default App;
