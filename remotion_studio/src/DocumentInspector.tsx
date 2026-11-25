import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

export const DocumentInspector: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 1. Camera push & subtle continuous drift
  const cameraScale = interpolate(frame, [0, 150], [0.96, 1.08], {
    extrapolateRight: 'clamp',
  });

  // Camera shake at highlight impact (frame 50)
  const shake =
    frame >= 50 && frame <= 62
      ? Math.sin((frame - 50) * 1.5) * 4 * (1 - (frame - 50) / 12)
      : 0;

  // 2. Paper Drop & 3D tilt spring entry
  const paperEntry = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 90 },
  });
  const translateY = interpolate(paperEntry, [0, 1], [-80, 0]);
  const rotateX = interpolate(paperEntry, [0, 1], [15, 6]);
  const rotateY = interpolate(paperEntry, [0, 1], [-20, -4]);

  // 3. Yellow Highlighter animation across "DEBT DEFICIT: 17 BILLION CHF"
  // Triggered between frame 30 and frame 55
  const highlightProgress = interpolate(frame, [30, 52], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 4. Red Organic Hand-Drawn Circle around "BANKRUPTCY IMMINENT"
  // Triggered between frame 50 and frame 75
  const circleProgress = interpolate(frame, [50, 72], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  // Ellipse perimeter ~ 2 * pi * sqrt((a^2 + b^2)/2) where a=180, b=45 -> ~760
  const circleDashoffset = 800 * (1 - circleProgress);

  // 5. Red Distressed Rubber Stamp: "BAILOUT DENIED"
  const stampTrigger = frame - 80;
  const stampSpring = spring({
    frame: stampTrigger > 0 ? stampTrigger : 0,
    fps,
    config: { damping: 12, mass: 0.5, stiffness: 220 },
  });
  const stampScale = interpolate(stampSpring, [0, 1], [3.2, 1.0]);
  const stampOpacity = stampTrigger > 0 ? interpolate(stampSpring, [0, 1], [0, 0.95]) : 0;

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        backgroundColor: '#0a0807',
        backgroundImage: 'radial-gradient(circle at 50% 45%, #2a1a14 0%, #0d0908 65%, #050303 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        perspective: 1200,
        overflow: 'hidden',
        fontFamily: 'Georgia, serif',
      }}
    >
      {/* Volumetric Overhead Studio Spotlight */}
      <div
        style={{
          position: 'absolute',
          width: 1200,
          height: 1200,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(255, 210, 140, 0.12) 0%, rgba(0, 0, 0, 0) 70%)',
          pointerEvents: 'none',
        }}
      />

      {/* Main 3D Container with Camera Scale & Shake */}
      <div
        style={{
          transform: `scale(${cameraScale}) translate3d(${shake}px, ${translateY + shake * 0.5}px, 0) rotateX(${rotateX}deg) rotateY(${rotateY}deg) rotateZ(-1.5deg)`,
          transformStyle: 'preserve-3d',
          transition: 'none',
        }}
      >
        {/* Physical Paper Shadow */}
        <div
          style={{
            position: 'absolute',
            top: 25,
            left: 20,
            width: 1050,
            height: 680,
            backgroundColor: 'rgba(0, 0, 0, 0.65)',
            filter: 'blur(35px)',
            borderRadius: 8,
          }}
        />

        {/* The Aged Document Case File */}
        <div
          style={{
            position: 'relative',
            width: 1050,
            height: 680,
            backgroundColor: '#f5ecd7',
            backgroundImage:
              'radial-gradient(#efe2c5 1px, transparent 1px), radial-gradient(#eadab7 1px, #f5ecd7 1px)',
            backgroundSize: '40px 40px',
            backgroundPosition: '0 0, 20px 20px',
            color: '#1a1918',
            padding: '50px 70px',
            boxSizing: 'border-box',
            borderRadius: 4,
            boxShadow: 'inset 0 0 80px rgba(120, 80, 40, 0.25), 0 15px 35px rgba(0, 0, 0, 0.4)',
            border: '1px solid rgba(160, 130, 90, 0.4)',
          }}
        >
          {/* Top Confidential Header */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              borderBottom: '2px solid #2d2620',
              paddingBottom: 15,
              marginBottom: 30,
            }}
          >
            <div>
              <span
                style={{
                  fontSize: 22,
                  fontWeight: 900,
                  letterSpacing: '0.18em',
                  color: '#8b1e1e',
                  textTransform: 'uppercase',
                }}
              >
                STRICTLY CONFIDENTIAL // INTERNAL DOSSIER
              </span>
              <div style={{ fontSize: 13, color: '#685e54', marginTop: 4, letterSpacing: '0.05em' }}>
                CASE REF: SWISSAIR-RESTRUCTURING-OCT2001 // KLOTEN HQ
              </div>
            </div>
            <div
              style={{
                border: '2px solid #8b1e1e',
                color: '#8b1e1e',
                padding: '4px 14px',
                fontWeight: 800,
                fontSize: 14,
                letterSpacing: '0.12em',
                borderRadius: 2,
              }}
            >
              FILE #SA-901
            </div>
          </div>

          {/* Document Content / Body */}
          <div style={{ lineHeight: 1.8, fontSize: 19, color: '#25211c' }}>
            <p style={{ margin: '0 0 16px 0' }}>
              <strong>MEMORANDUM FOR:</strong> Swissair Group Executive Board & Mario Corti
            </p>
            <p style={{ margin: '0 0 16px 0' }}>
              <strong>SUBJECT:</strong> Emergency Liquidity Facility Assessment & Hunter Strategy Deficit
            </p>
            <p style={{ margin: '0 0 20px 0', fontSize: 18, color: '#3c352d' }}>
              Following prolonged audit of the Belgian (Sabena) and French aviation acquisitions, the current debt exposure has exceeded all collateral reserves held in Zurich:
            </p>

            {/* Crucial Data Box with Animated Highlighter */}
            <div
              style={{
                position: 'relative',
                backgroundColor: 'rgba(230, 218, 195, 0.6)',
                borderLeft: '5px solid #2d2620',
                padding: '16px 24px',
                margin: '25px 0',
                fontSize: 22,
                fontWeight: 700,
                color: '#151310',
              }}
            >
              <div style={{ position: 'relative', display: 'inline-block' }}>
                {/* Yellow Highlighter Stroke */}
                <span
                  style={{
                    position: 'absolute',
                    top: '12%',
                    left: 0,
                    width: `${highlightProgress}%`,
                    height: '80%',
                    backgroundColor: 'rgba(255, 235, 59, 0.65)',
                    mixBlendMode: 'multiply',
                    borderRadius: 3,
                    boxShadow: '0 0 12px rgba(255, 235, 59, 0.5)',
                    pointerEvents: 'none',
                  }}
                />
                <span>TOTAL ACCUMULATED DEBT: 17,000,000,000 CHF</span>
              </div>
            </div>

            {/* Paragraph with Hand-Drawn Red Ink Circle */}
            <div style={{ position: 'relative', fontSize: 18, marginTop: 20 }}>
              <span>
                UBS and Credit Suisse consortium confirmed that without an immediate cash injection of 450 Million CHF before{' '}
              </span>
              <span style={{ position: 'relative', display: 'inline-block', fontWeight: 800 }}>
                <span>OCTOBER 2, 2001</span>

                {/* Hand-Drawn SVG Red Circle */}
                <svg
                  style={{
                    position: 'absolute',
                    top: -15,
                    left: -20,
                    width: 220,
                    height: 60,
                    overflow: 'visible',
                    pointerEvents: 'none',
                  }}
                >
                  <path
                    d="M 10 25 C 20 8, 190 5, 200 24 C 210 44, 30 52, 12 36 C 4 28, 50 12, 130 14"
                    fill="none"
                    stroke="#b31b1b"
                    strokeWidth="3.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeDasharray="800"
                    strokeDashoffset={circleDashoffset}
                    style={{
                      filter: 'drop-shadow(0 0 3px rgba(179, 27, 27, 0.4))',
                    }}
                  />
                </svg>
              </span>
              <span>, fuel credit lines will be frozen worldwide.</span>
            </div>
          </div>

          {/* Rubber Stamp: "BAILOUT REJECTED" */}
          <div
            style={{
              position: 'absolute',
              bottom: 60,
              right: 80,
              transform: `scale(${stampScale}) rotate(-16deg)`,
              opacity: stampOpacity,
              border: '6px solid #a81c1c',
              color: '#a81c1c',
              padding: '10px 28px',
              fontFamily: 'Impact, sans-serif',
              fontSize: 36,
              letterSpacing: '0.18em',
              textTransform: 'uppercase',
              borderRadius: 6,
              boxShadow: '0 0 15px rgba(168, 28, 28, 0.4)',
              transformOrigin: 'center center',
            }}
          >
            BAILOUT REJECTED
          </div>
        </div>
      </div>
    </div>
  );
};
