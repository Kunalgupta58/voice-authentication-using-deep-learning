import { CheckCircle2, AlertCircle, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './Toast.css';

const ICONS = {
    success: CheckCircle2,
    error: AlertCircle,
    info: Info,
};

const Toast = ({ message, type = 'success' }) => {
    const Icon = ICONS[type] || Info;

    return (
        <AnimatePresence>
            <motion.div
                className={`toast toast-${type}`}
                initial={{ opacity: 0, y: 60, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 60, scale: 0.95 }}
                transition={{ type: 'spring', stiffness: 350, damping: 28 }}
            >
                <Icon size={18} className="toast-icon" />
                <span className="toast-msg">{message}</span>
                <div className="toast-progress" />
            </motion.div>
        </AnimatePresence>
    );
};

export default Toast;
