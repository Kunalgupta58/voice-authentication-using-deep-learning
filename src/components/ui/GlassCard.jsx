import { motion } from 'framer-motion';
import './GlassCard.css';

const GlassCard = ({ children, className = '', hover = false, glow = false }) => (
    <motion.div
        className={`gcard ${glow ? 'gcard-glow' : ''} ${className}`}
        whileHover={hover ? { y: -4, boxShadow: '0 30px 60px rgba(0,0,0,0.6)' } : {}}
        transition={{ type: 'spring', stiffness: 300, damping: 24 }}
    >
        <div className="gcard-inner">{children}</div>
    </motion.div>
);

export default GlassCard;
