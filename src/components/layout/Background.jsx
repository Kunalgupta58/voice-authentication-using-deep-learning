import './Background.css';

const PARTICLES = Array.from({ length: 28 }, (_, i) => ({
    id: i,
    size: Math.random() * 3 + 1,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 8,
    dur: Math.random() * 12 + 8,
    opacity: Math.random() * 0.4 + 0.1,
}));

const Background = () => (
    <div className="bg-root" aria-hidden="true">
        {/* Deep radial glow spots */}
        <div className="bg-spot bg-spot-1" />
        <div className="bg-spot bg-spot-2" />
        <div className="bg-spot bg-spot-3" />

        {/* Rotating mesh gradient */}
        <div className="bg-mesh" />

        {/* Grid overlay */}
        <div className="bg-grid" />

        {/* Floating particles */}
        <svg className="bg-particles" viewBox="0 0 100 100" preserveAspectRatio="none">
            {PARTICLES.map(p => (
                <circle
                    key={p.id}
                    cx={p.x}
                    cy={p.y}
                    r={p.size * 0.1}
                    fill="var(--accent-primary)"
                    opacity={p.opacity}
                >
                    <animate
                        attributeName="cy"
                        values={`${p.y};${p.y - 15};${p.y}`}
                        dur={`${p.dur}s`}
                        repeatCount="indefinite"
                        begin={`${p.delay}s`}
                    />
                    <animate
                        attributeName="opacity"
                        values={`${p.opacity};${p.opacity * 2};${p.opacity}`}
                        dur={`${p.dur}s`}
                        repeatCount="indefinite"
                        begin={`${p.delay}s`}
                    />
                </circle>
            ))}
        </svg>

        {/* Noise texture */}
        <div className="bg-noise" />
    </div>
);

export default Background;
