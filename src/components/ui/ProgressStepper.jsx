import React from 'react';
import { Check } from 'lucide-react';
import './ProgressStepper.css';

const ProgressStepper = ({ currentStep, totalSteps = 3, labels = [] }) => (
    <div className="stepper">
        {Array.from({ length: totalSteps }, (_, i) => {
            const step = i + 1;
            const done = step < currentStep;
            const active = step === currentStep;
            return (
                <React.Fragment key={step}>
                    <div className={`step-node ${done ? 'done' : ''} ${active ? 'active' : ''}`}>
                        <div className="step-bubble">
                            {done ? <Check size={13} strokeWidth={3} /> : <span>{step}</span>}
                        </div>
                        {labels[i] && (
                            <span className="step-label">{labels[i]}</span>
                        )}
                    </div>
                    {step < totalSteps && (
                        <div className={`step-track ${done ? 'done' : ''}`}>
                            <div className="step-fill" style={{ width: done ? '100%' : '0%' }} />
                        </div>
                    )}
                </React.Fragment>
            );
        })}
    </div>
);

export default ProgressStepper;
