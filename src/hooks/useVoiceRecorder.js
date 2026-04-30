import { useState, useRef, useCallback } from 'react';

export const useVoiceRecorder = (onComplete) => {
    const [status, setStatus] = useState('idle');
    const [audioBlob, setAudioBlob] = useState(null);
    const [timeLeft, setTimeLeft] = useState(null);
    const mediaRef = useRef(null);
    const chunksRef = useRef([]);
    const timerRef = useRef(null);

    const startRecording = useCallback(async (durationMs = 10000) => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mr = new MediaRecorder(stream);
            mediaRef.current = mr;
            chunksRef.current = [];

            mr.ondataavailable = e => { if (e.data.size > 0) chunksRef.current.push(e.data); };

            mr.onstop = async () => {
                clearInterval(timerRef.current);
                setTimeLeft(null);
                stream.getTracks().forEach(t => t.stop());
                const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
                setAudioBlob(blob);
                setStatus('processing');
                try {
                    await onComplete?.(blob);
                } catch {
                    setStatus('error');
                }
            };

            mr.start();
            setStatus('recording');

            // Countdown timer
            const secs = Math.round(durationMs / 1000);
            setTimeLeft(secs);
            timerRef.current = setInterval(() => {
                setTimeLeft(prev => {
                    if (prev <= 1) { clearInterval(timerRef.current); return 0; }
                    return prev - 1;
                });
            }, 1000);

            setTimeout(() => {
                if (mr.state === 'recording') mr.stop();
            }, durationMs);
        } catch (err) {
            console.error('Mic error:', err);
            setStatus('error');
        }
    }, [onComplete]);

    const reset = useCallback(() => {
        clearInterval(timerRef.current);
        setStatus('idle');
        setAudioBlob(null);
        setTimeLeft(null);
        chunksRef.current = [];
    }, []);

    return { status, setStatus, audioBlob, timeLeft, startRecording, reset };
};
