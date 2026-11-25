import React from 'react';
import { Composition } from 'remotion';
import { DocumentInspector } from './DocumentInspector';
import { ParallaxCharacter } from './ParallaxCharacter';

export const Root: React.FC = () => {
  return (
    <>
      {/* 1. Kinetic Document Inspector with Animated Highlighter & Red Circle */}
      <Composition
        id="DocumentInspector"
        component={DocumentInspector}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* 2. Mario Corti 2.5D Multi-Plane Parallax Rig */}
      <Composition
        id="ParallaxMarioCorti"
        component={ParallaxCharacter}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          photoFile: 'photo_02_mario_corti.png',
          name: 'Mario Corti',
          title: 'Chairman & CEO, Swissair Group',
          subtitle: 'Appointed March 2001 to avert impending default; fought UBS until grounding day.',
        }}
      />

      {/* 3. Philippe Bruggisser 2.5D Multi-Plane Parallax Rig */}
      <Composition
        id="ParallaxBruggisser"
        component={ParallaxCharacter}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          photoFile: 'photo_06_bruggisser.png',
          name: 'Philippe Bruggisser',
          title: 'Architect of the "Hunter Strategy"',
          subtitle: 'Acquired 10+ unprofitable European carriers, accumulating 17 Billion CHF in debt.',
        }}
      />
    </>
  );
};
