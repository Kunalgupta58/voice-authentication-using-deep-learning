import { motion } from 'framer-motion';
import './Button.css';

const Button = ({
    children,
    onClick,
    variant = 'primary',
    disabled = false,
    loading = false,
    icon: Icon,
    className = '',
    type = 'button',
    size = 'md',
}) => {
    return (
        <motion.button
            type={type}
            className={`btn btn-${variant} btn-${size} ${disabled || loading ? 'btn-disabled' : ''} ${className}`}
            onClick={!disabled && !loading ? onClick : undefined}
            disabled={disabled || loading}
            whileHover={!disabled && !loading ? { scale: 1.02 } : {}}
            whileTap={!disabled && !loading ? { scale: 0.97 } : {}}
            transition={{ type: 'spring', stiffness: 400, damping: 20 }}
        >
            {loading ? (
                <span className="btn-spinner" />
            ) : Icon ? (
                <Icon size={size === 'sm' ? 14 : 18} className="btn-icon" />
            ) : null}
            <span>{children}</span>
        </motion.button>
    );
};

export default Button;
