import React from 'react';
import {
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

interface ParallaxCharacterProps {
  photoFile: string;
  name: string;
  title: string;
  subtitle: string;
  backdropColor?: string;
}

export const ParallaxCharacter: React.FC<ParallaxCharacterProps> = ({
  photoFile,
  name,
  title,
  subtitle,
  backdropColor = '#120d0b',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 1. Camera Orbit / Push-In (MagnatesMedia signature dynamic framing)
  const cameraZoom = interpolate(frame, [0, 150], [1.0, 1.08], {
    extrapolateRight: 'clamp',
  });
  const cameraPanX = interpolate(frame, [0, 150], [0, -35], {
    extrapolateRight: 'clamp',
  });

  // 2. Background Parallax (Moves opposite to camera, slower)
  const bgPanX = interpolate(frame, [0, 150], [20, -15], {
    extrapolateRight: 'clamp',
  });
  const bgScale = interpolate(frame, [0, 150], [1.12, 1.18]);

  // 3. Foreground Subject (Moves faster for intense depth separation)
  const subjectPanX = interpolate(frame, [0, 150], [-25, 30], {
    extrapolateRight: 'clamp',
  });
  const subjectScale = interpolate(frame, [0, 150], [1.0, 1.05]);

  // 4. Subtle Breathing / Sway Physics
  const breathing = Math.sin(frame * 0.05) * 4;
  const tilt = Math.cos(frame * 0.04) * 0.6;

  // 5. Lower-Third Glassmorphic Badge Entry Spring
  const badgeSpring = spring({
    frame: frame - 18,
    fps,
    config: { damping: 14, mass: 0.6, stiffness: 120 },
  });
  const badgeTranslateX = interpolate(badgeSpring, [0, 1], [-100, 0]);
  const badgeOpacity = interpolate(badgeSpring, [0, 1], [0, 1]);

  // 6. Floating Cinematic Dust Particles (2.5D Atmosphere)
  const particles = [
    { x: 300, y: 400, size: 4, speed: 0.8, opacity: 0.4 },
    { x: 500, y: 700, size: 6, speed: 1.2, opacity: 0.6 },
    { x: 800, y: 300, size: 3, speed: 0.5, opacity: 0.3 },
    { x: 1200, y: 600, size: 5, speed: 1.0, opacity: 0.5 },
    { x: 1500, y: 450, size: 7, speed: 1.4, opacity: 0.7 },
    { x: 1650, y: 800, size: 4, speed: 0.9, opacity: 0.4 },
  ];

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        backgroundColor: '#070504',
        overflow: 'hidden',
        position: 'relative',
        fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
      }}
    >
      {/* Layer 1: Background Atmospheric Plate */}
      <div
        style={{
          position: 'absolute',
          top: -50,
          left: -50,
          width: 2020,
          height: 1180,
          backgroundImage: `radial-gradient(circle at 65% 40%, #3a2219 0%, #150f0c 60%, #050403 100%)`,
          transform: `scale(${bgScale}) translate3d(${bgPanX}px, 0, 0)`,
          filter: 'blur(8px)',
        }}
      />

      {/* Layer 2: Volumetric Rim Light / Studio Glow */}
      <div
        style={{
          position: 'absolute',
          top: 100,
          right: 350,
          width: 800,
          height: 800,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(230, 150, 70, 0.22) 0%, rgba(0, 0, 0, 0) 70%)',
          pointerEvents: 'none',
        }}
      />

      {/* Layer 3: Floating 3D Dust Motes */}
      {particles.map((p, i) => {
        const currentY = (p.y - frame * p.speed * 1.5) % 1080;
        const currentX = p.x + Math.sin((frame + i * 20) * 0.03) * 15;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: currentY,
              left: currentX,
              width: p.size,
              height: p.size,
              borderRadius: '50%',
              backgroundColor: '#ffd79e',
              opacity: p.opacity,
              boxShadow: `0 0 10px rgba(255, 215, 158, 0.8)`,
              pointerEvents: 'none',
            }}
          />
        );
      })}

      {/* Layer 4: Foreground Subject with Dynamic Cutout Parallax */}
      <div
        style={{
          position: 'absolute',
          bottom: -30,
          right: 180,
          transform: `scale(${subjectScale}) translate3d(${subjectPanX}px, ${breathing}px, 0) rotate(${tilt}deg)`,
          transformOrigin: 'bottom center',
        }}
      >
        <Img
          src={staticFile(photoFile)}
          style={{
            maxHeight: 980,
            maxWidth: 1050,
            objectFit: 'contain',
            filter:
              'drop-shadow(0 25px 45px rgba(0, 0, 0, 0.95)) drop-shadow(0 0 15px rgba(210, 140, 60, 0.25)) contrast(1.08) brightness(0.96)',
          }}
        />
      </div>

      {/* Layer 5: Glassmorphic Lower-Third Dossier Badge */}
      <div
        style={{
          position: 'absolute',
          bottom: 120,
          left: 140,
          transform: `translate3d(${badgeTranslateX}px, 0, 0)`,
          opacity: badgeOpacity,
          maxWidth: 720,
        }}
      >
        <div
          style={{
            backgroundColor: 'rgba(16, 12, 10, 0.85)',
            backdropFilter: 'blur(20px)',
            borderLeft: '6px solid #b31b1b',
            borderTop: '1px solid rgba(255, 255, 255, 0.12)',
            borderRight: '1px solid rgba(255, 255, 255, 0.05)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
            padding: '24px 36px',
            borderRadius: '0 8px 8px 0',
            boxShadow: '0 20px 50px rgba(0, 0, 0, 0.7)',
          }}
        >
          <div
            style={{
              fontSize: 13,
              fontWeight: 800,
              letterSpacing: '0.22em',
              color: '#d64d4d',
              textTransform: 'uppercase',
              marginBottom: 8,
            }}
          >
            CONFIDENTIAL ARCHIVE // KEY FIGURE
          </div>
          <div
            style={{
              fontSize: 44,
              fontWeight: 900,
              letterSpacing: '-0.02em',
              color: '#ffffff',
              textTransform: 'uppercase',
              marginBottom: 6,
            }}
          >
            {name}
          </div>
          <div
            style={{
              fontSize: 19,
              fontWeight: 600,
              color: '#e0c9aa',
              letterSpacing: '0.04em',
              marginBottom: 6,
            }}
          >
            {title}
          </div>
          <div
            style={{
              fontSize: 14,
              color: '#9c8c7c',
              letterSpacing: '0.02em',
              lineHeight: 1.4,
            }}
          >
            {subtitle}
          </div>
        </div>
      </div>

      {/* Layer 6: Edge Vignette */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: 1920,
          height: 1080,
          background:
            'radial-gradient(circle at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.7) 100%)',
          pointerEvents: 'none',
        }}
      />
    </div>
  );
};
