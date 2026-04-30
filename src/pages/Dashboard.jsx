import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
    Layout, 
    Mail, 
    Cloud, 
    Database, 
    FileText, 
    Settings, 
    Shield, 
    ExternalLink 
} from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import './Dashboard.css';

const MOCK_APPS = [
    { id: 1, name: 'Secure Mail', icon: Mail, desc: 'Encrypted communication suite', category: 'Productivity' },
    { id: 2, name: 'Cloud Drive', icon: Cloud, desc: 'Biometric-locked storage', category: 'Storage' },
    { id: 3, name: 'Data Engine', icon: Database, desc: 'Real-time analytics platform', category: 'Infrastructure' },
    { id: 4, name: 'Doc Vault', icon: FileText, desc: 'Regulatory compliance records', category: 'Legal' },
    { id: 5, name: 'Sys Config', icon: Settings, desc: 'Network & identity settings', category: 'Admin' },
    { id: 6, name: 'Threat Watch', icon: Shield, desc: 'AI-driven security monitoring', category: 'Security' },
];

export default function Dashboard({ user }) {
    const [time, setTime] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    const formatTime = (date) => {
        return date.toLocaleTimeString('en-US', { 
            hour12: false, 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });
    };


    return (
        <motion.div 
            className="dashboard-page"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <header className="dashboard-header">
                <div className="welcome-section">
                    <h1>Welcome back, <span className="gradient-text">{user?.name || 'User'}</span></h1>
                    <p>Your biometric session is active and secure.</p>
                </div>
                <div className="clock-section">
                    <div className="live-clock">{formatTime(time)}</div>
                    <p className="date-display">System Time (UTC)</p>
                </div>
            </header>

            <section className="dashboard-stats">
                <GlassCard className="stat-card">
                    <span className="stat-value">99.9%</span>
                    <span className="stat-label">System Uptime</span>
                </GlassCard>
                <GlassCard className="stat-card">
                    <span className="stat-value">12</span>
                    <span className="stat-label">Active Apps</span>
                </GlassCard>
                <GlassCard className="stat-card">
                    <span className="stat-value">0</span>
                    <span className="stat-label">Security Alerts</span>
                </GlassCard>
            </section>

            <section className="apps-section">
                <div className="section-header" style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <Layout size={20} className="accent-color" />
                    <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Your Workspace</h2>
                </div>
                
                <div className="apps-grid">
                    {MOCK_APPS.map((app, index) => (
                        <motion.div
                            key={app.id}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.05 }}
                        >
                            <GlassCard className="app-card" glow>
                                <div className="app-card-content">
                                    <div className="app-icon-wrapper">
                                        <app.icon size={28} />
                                    </div>
                                    <div className="app-info">
                                        <h3>{app.name}</h3>
                                        <p>{app.desc}</p>
                                    </div>
                                    <ExternalLink size={16} style={{ marginLeft: 'auto', opacity: 0.3 }} />
                                </div>
                            </GlassCard>
                        </motion.div>
                    ))}
                </div>
            </section>

            <footer style={{ marginTop: 'auto', padding: '2rem 0', opacity: 0.5, fontSize: '0.8rem', textAlign: 'center' }}>
                <p>VoiceKey Dashboard v2.4.0-stable | ECAPA-TDNN Core v1.2</p>
            </footer>
        </motion.div>
    );
}
