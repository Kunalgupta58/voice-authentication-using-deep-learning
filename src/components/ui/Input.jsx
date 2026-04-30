import './Input.css';

const Input = ({ label, type = 'text', placeholder, value, onChange, error, hint, icon: Icon, id, autoFocus }) => (
    <div className="field">
        {label && <label htmlFor={id} className="field-label">{label}</label>}
        <div className={`field-wrap ${error ? 'field-error' : ''}`}>
            {Icon && <Icon size={17} className="field-icon" />}
            <input
                id={id}
                type={type}
                className="field-input"
                placeholder={placeholder}
                value={value}
                onChange={onChange}
                autoFocus={autoFocus}
            />
        </div>
        {error && <p className="field-msg-error">{error}</p>}
        {hint && !error && <p className="field-hint">{hint}</p>}
    </div>
);

export default Input;
