import { useState, useEffect } from 'react';
import { Mic } from 'lucide-react';
import './Navbar.css';

const Navbar = ({ onNav, currentPage, user, onSignOut }) => {
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handler = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handler);
        return () => window.removeEventListener('scroll', handler);
    }, []);

    return (
        <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
            <div className="navbar-inner">
                {/* Logo */}
                <div className="logo" onClick={() => onNav(user ? 'dashboard' : 'login')}>
                    <div className="logo-mark">
                        <Mic size={18} />
                    </div>
                    <span className="logo-wordmark">VoiceKey</span>
                    <span className="logo-chip">ENTERPRISE</span>
                </div>

                {/* Center links */}
                <ul className="nav-links">
                    {['Product', 'Solutions', 'Developers', 'Pricing'].map(l => (
                        <li key={l}><a href="#" className="nav-link">{l}</a></li>
                    ))}
                    {user && (
                        <li>
                            <button 
                                className={`nav-link ${currentPage === 'dashboard' ? 'active' : ''}`}
                                onClick={() => onNav('dashboard')}
                                style={{ background: 'none', border: 'none', cursor: 'pointer', font: 'inherit' }}
                            >
                                Dashboard
                            </button>
                        </li>
                    )}
                </ul>

                {/* CTA */}
                <div className="nav-cta">
                    {!user ? (
                        <>
                            <button className="nav-btn-ghost" onClick={() => onNav('login')}>Sign in</button>
                            <button className="nav-btn-primary" onClick={() => onNav('register')}>
                                Get Started
                                <span className="btn-arrow">→</span>
                            </button>
                        </>
                    ) : (
                        <div className="user-profile">
                            <span className="user-name">{user.name}</span>
                            <button className="nav-btn-ghost" onClick={onSignOut}>Sign out</button>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
