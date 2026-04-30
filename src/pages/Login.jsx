import { useState, useContext, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, ArrowRight, ShieldCheck, Fingerprint, Zap } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import VoiceRecorder from '../components/voice/VoiceRecorder';
import { useVoiceRecorder } from '../hooks/useVoiceRecorder';
import { ToastContext } from '../contexts/ToastContext';
import './Login.css';

const FEATURES = [
    { icon: ShieldCheck, title: 'Zero-Trust Security', desc: 'Voice biometrics verified by ECAPA-TDNN neural networks.' },
    { icon: Fingerprint, title: 'Uniquely Yours', desc: 'Your vocal signature is cryptographically irreversible.' },
    { icon: Zap, title: 'Sub-Second Auth', desc: 'Authentication completes in under 800ms on average.' },
];

const DEFAULT_LOGIN_PHRASE = 'This is my voice and I am using it to prove my identity to the system right now, my access code is 3856 and I request to be authenticated.';


export default function Login({ onSuccess, onSwitch }) {
    const [screen, setScreen] = useState('user'); // 'user' | 'voice'
    const [username, setUsername] = useState('');
    const [challengeId, setChallengeId] = useState(null);
    const showToast = useContext(ToastContext);

    const [loginPhrase, setLoginPhrase] = useState(DEFAULT_LOGIN_PHRASE);
    const loginCompleteRef = useRef(null);

    const handleLoginBlob = useCallback(async (blob) => {
        await loginCompleteRef.current?.(blob);
    }, []);

    const { status, setStatus, startRecording, audioBlob, reset } = useVoiceRecorder(handleLoginBlob);

    useEffect(() => {
        loginCompleteRef.current = async (blob) => {
            try {
                const formData = new FormData();
                formData.append('username', username);
                formData.append('audio', blob, 'login.webm');
                if (challengeId) {
                    formData.append('challenge_id', challengeId);
                }

                const response = await fetch('/api/login', {
                    method: 'POST',
                    body: formData,
                });

                const data = await response.json();

                if (response.ok) {
                    setStatus('success');
                    showToast?.(`Welcome back, ${data.username}! Authentication successful.`, 'success');
                    onSuccess?.(data);
                } else {
                    setStatus('error');
                    showToast?.(data.detail || 'Authentication failed.', 'error');
                }
            } catch (error) {
                console.error('Login error:', error);
                setStatus('error');
                showToast?.('Connection error. Please try again.', 'error');
            }
        };
    }, [username, challengeId, showToast, onSuccess, setStatus]);


    const goVoice = async () => {
        if (!username.trim()) return showToast?.('Please enter your username.', 'error');
        
        try {
            const response = await fetch('/api/liveness-phrase');
            if (!response.ok) {
                const data = await response.json().catch(() => null);
                throw new Error(data?.detail || 'Unable to fetch liveness phrase.');
            }

            const data = await response.json();
            setLoginPhrase(data.phrase);
            setChallengeId(data.challenge_id);
            setScreen('voice');
        } catch (error) {
            console.warn('Could not fetch liveness phrase:', error);
            showToast?.('Unable to load the liveness challenge. Please try again.', 'error');
        }
    };


    const handleReplay = () => {
        if (!audioBlob) return;
        const url = URL.createObjectURL(audioBlob);
        new Audio(url).play();
    };

    return (
        <div className="login-page">
            {/* Left branding panel */}
            <div className="login-brand">
                <motion.div
                    className="brand-content"
                    initial={{ opacity: 0, x: -30 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, ease: 'easeOut' }}
                >
                    <div className="brand-badge">🔒 Enterprise-Grade Voice Auth</div>
                    <h1 className="brand-heading">
                        Security that <br />
                        <span className="gradient-text">Knows Your Voice.</span>
                    </h1>
                    <p className="brand-desc">
                        VoiceKey's ECAPA-TDNN neural model processes over 192 vocal frequency features to create an unbreakable biometric identity — uniquely yours.
                    </p>

                    {/* Stats row */}
                    <div className="brand-stats">
                        {[
                            { val: '99.97%', label: 'Accuracy' },
                            { val: '<800ms', label: 'Auth time' },
                            { val: '2048-bit', label: 'Encryption' },
                        ].map(s => (
                            <div key={s.label} className="stat">
                                <span className="stat-val">{s.val}</span>
                                <span className="stat-lbl">{s.label}</span>
                            </div>
                        ))}
                    </div>

                    {/* Feature list */}
                    <ul className="brand-features">
                        {FEATURES.map(f => (
                            <li key={f.title} className="feature-item">
                                <div className="feature-icon-wrap"><f.icon size={18} /></div>
                                <div>
                                    <p className="feature-title">{f.title}</p>
                                    <p className="feature-desc">{f.desc}</p>
                                </div>
                            </li>
                        ))}
                    </ul>
                </motion.div>
            </div>

            {/* Right auth panel */}
            <div className="login-form">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.15 }}
                    style={{ width: '100%', maxWidth: 460 }}
                >
                    <GlassCard glow>
                        <AnimatePresence mode="wait">
                            {screen === 'user' ? (
                                <motion.div
                                    key="user"
                                    initial={{ opacity: 0, x: 30 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -30 }}
                                    transition={{ duration: 0.3 }}
                                    className="auth-pane"
                                >
                                    <div className="auth-header">
                                        <h2 className="auth-title">Welcome back</h2>
                                        <p className="auth-sub">Sign in with your voice — no passwords needed.</p>
                                    </div>

                                    <Input
                                        id="login-username"
                                        label="Username"
                                        placeholder="Enter your username..."
                                        icon={User}
                                        value={username}
                                        onChange={e => setUsername(e.target.value)}
                                        autoFocus
                                    />

                                    <Button
                                        className="w-full"
                                        size="lg"
                                        icon={ArrowRight}
                                        onClick={goVoice}
                                    >
                                        Continue with Voice
                                    </Button>

                                    <div className="or-divider"><span>OR</span></div>

                                    <Button variant="secondary" className="w-full" size="md">
                                        Sign in with SSO
                                    </Button>

                                    <p className="auth-legal">
                                        By continuing you agree to our <a href="#">Terms</a> and <a href="#">Privacy Policy</a>.
                                    </p>

                                    <p className="auth-switch">
                                        New to VoiceKey?&nbsp;
                                        <button className="auth-switch-btn" onClick={onSwitch}>Create an account →</button>
                                    </p>
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="voice"
                                    initial={{ opacity: 0, x: 30 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -30 }}
                                    transition={{ duration: 0.3 }}
                                    className="auth-pane"
                                >
                                    <div className="auth-header">
                                        <h2 className="auth-title">Voice Authentication</h2>
                                        <p className="auth-sub">Authenticating as <strong className="username-highlight">{username}</strong></p>
                                    </div>

                                    <VoiceRecorder
                                        status={status}
                                        onRecord={() => { reset(); startRecording(13000); }}
                                        onReplay={audioBlob ? handleReplay : null}
                                        duration={13}
                                        phrase={loginPhrase}
                                        timeLeft={undefined}

                                    />

                                    {status === 'idle' && (
                                        <button className="auth-back-btn" onClick={() => { setScreen('user'); reset(); }}>
                                            ← Not you? Change user
                                        </button>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </GlassCard>
                </motion.div>
            </div>
        </div>
    );
}
