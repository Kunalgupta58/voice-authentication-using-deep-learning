import { useState, useContext, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, ArrowRight, ArrowLeft, Mic } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import ProgressStepper from '../components/ui/ProgressStepper';
import VoiceRecorder from '../components/voice/VoiceRecorder';
import { useVoiceRecorder } from '../hooks/useVoiceRecorder';
import { ToastContext } from '../contexts/ToastContext';
import './Register.css';

const PHRASES = [
    'The bright morning sun rises slowly over the distant mountains, painting the sky in shades of gold and orange while birds begin to sing their gentle songs in the trees.',
    'Speaking every word carefully and clearly helps the system capture the unique patterns in my voice, so I must take my time and speak each syllable with full confidence.',
    'My voice contains special frequency patterns that no other person in the world has, and by recording these phrases the system will learn to recognize me accurately every time.',
];

const STEP_LABELS = ['Sample 1', 'Sample 2', 'Sample 3'];

const STEP_HINTS = [
    'Read the phrase clearly at your natural speaking pace.',
    'Try to match the same tone and volume as before.',
    'Final sample — speak deliberately and clearly.',
];

export default function Register({ onSuccess, onSwitch }) {
    const [step, setStep] = useState(0);          // 0: username, 1-3: voice
    const [username, setUsername] = useState('');
    const [blobs, setBlobs] = useState([]);
    const [submitting, setSubmitting] = useState(false);
    const showToast = useContext(ToastContext);
    const registerCompleteRef = useRef(null);

    const handleRegisterBlob = useCallback(async (blob) => {
        await registerCompleteRef.current?.(blob);
    }, []);

    const { status, setStatus, audioBlob, timeLeft, startRecording, reset } =
        useVoiceRecorder(handleRegisterBlob);

    useEffect(() => {
        registerCompleteRef.current = async (blob) => {
            await new Promise(r => setTimeout(r, 1200));
            setStatus('success');
            setBlobs(prev => [...prev, blob]);
        };
    }, [setStatus]);

    const isVoiceStep = step > 0;
    const voiceStepIndex = step - 1; // 0-based

    const handleNext = async () => {
        if (step === 0) {
            if (!username.trim()) return showToast?.('Please enter a username.', 'error');
            setStep(1);
            return;
        }

        if (status !== 'success') return showToast?.('Please complete the recording first.', 'error');

        if (step < 3) {
            setStep(s => s + 1);
            reset();
            return;
        }

        // Step 3 done → submit
        setSubmitting(true);
        try {
            const formData = new FormData();
            formData.append('username', username);
            // Ensure we have exactly 3 blobs as expected by the backend
            blobs.forEach((b, i) => {
                formData.append(`audio${i + 1}`, b, `sample${i + 1}.webm`);
            });

            const response = await fetch('/api/register', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                showToast?.('Voice profile created! You can now sign in.', 'success');
                onSuccess?.();
            } else {
                showToast?.(data.detail || 'Registration failed.', 'error');
            }
        } catch (error) {
            console.error('Registration error:', error);
            showToast?.('Connection error. Please try again.', 'error');
        } finally {
            setSubmitting(false);
        }

    };

    const handleBack = () => {
        if (step === 0) return;
        setStep(s => s - 1);
        reset();
    };

    return (
        <div className="reg-page">
            <motion.div
                className="reg-wrapper"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <GlassCard glow>
                    {/* Header */}
                    <div className="reg-header">
                        <div className="reg-header-top">
                            <h2 className="reg-title">Create Voice Profile</h2>
                            {isVoiceStep && (
                                <span className="reg-step-badge">
                                    Step {step}/3
                                </span>
                            )}
                        </div>
                        <p className="reg-sub">
                            {step === 0
                                ? 'Choose your username to get started.'
                                : `Read the phrase below aloud to capture your voiceprint. ${STEP_HINTS[voiceStepIndex]}`}
                        </p>
                    </div>

                    {/* Progress stepper (shown from step 1) */}
                    {isVoiceStep && (
                        <ProgressStepper
                            currentStep={step}
                            totalSteps={3}
                            labels={STEP_LABELS}
                        />
                    )}

                    {/* Content */}
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={step}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            transition={{ duration: 0.25 }}
                            className="reg-content"
                        >
                            {step === 0 ? (
                                <div className="reg-username-step">
                                    <Input
                                        id="reg-username"
                                        label="Username"
                                        placeholder="Choose a unique username…"
                                        icon={User}
                                        value={username}
                                        onChange={e => setUsername(e.target.value)}
                                        hint="This will be linked to your biometric voice profile."
                                        autoFocus
                                    />

                                    <div className="reg-tips">
                                        {['🎤 3 voice samples required (~45 seconds total)', '🔒 Voiceprint stored as encrypted embeddings', '🚀 Works on all devices with a microphone'].map(t => (
                                            <p key={t} className="tip">{t}</p>
                                        ))}
                                    </div>
                                </div>
                            ) : (
                                <VoiceRecorder
                                    status={status}
                                    onRecord={() => { reset(); startRecording(15000); }}
                                    onReplay={audioBlob ? () => { const u = URL.createObjectURL(audioBlob); new Audio(u).play(); } : null}
                                    duration={15}
                                    phrase={PHRASES[voiceStepIndex]}
                                    timeLeft={timeLeft}
                                />
                            )}
                        </motion.div>
                    </AnimatePresence>

                    {/* Recorded samples list */}
                    {isVoiceStep && blobs.length > 0 && (
                        <div className="reg-samples">
                            {blobs.map((_, i) => (
                                <div key={i} className="sample-pill">
                                    ✓ Sample {i + 1} saved
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Footer actions */}
                    <div className="reg-footer">
                        {step > 0 && (
                            <Button variant="ghost" icon={ArrowLeft} size="md" onClick={handleBack} disabled={submitting}>
                                Back
                            </Button>
                        )}
                        <Button
                            variant="primary"
                            icon={step === 3 ? Mic : ArrowRight}
                            size="lg"
                            className={step === 0 ? 'w-full' : ''}
                            onClick={handleNext}
                            disabled={(isVoiceStep && status !== 'success') || submitting}
                            loading={submitting}
                        >
                            {step === 0 ? 'Start Voice Enrollment' : step === 3 ? 'Complete Profile' : 'Next Sample'}
                        </Button>
                    </div>

                    {/* Switcher — always visible, inside card */}
                    <p className="reg-switch">
                        Already enrolled?&nbsp;
                        <button className="reg-switch-btn" onClick={onSwitch}>Sign in →</button>
                    </p>
                </GlassCard>
            </motion.div>
        </div>
    );
}
