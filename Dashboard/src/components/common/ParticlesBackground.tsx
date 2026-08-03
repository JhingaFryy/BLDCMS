import { useMemo } from 'react';
import { Box } from '@mui/material';

interface Particle {
  left: number;
  top: number;
  size: number;
  duration: number;
  delay: number;
  opacity: number;
  color: string;
}

const PARTICLE_COLORS = ['#2F7DFF', '#22D3EE', '#9D6BFF', '#1FE08A'];

/**
 * Module 33: a lightweight, CSS-only floating-particle backdrop for the Login page - no canvas,
 * no particle-engine dependency (tsparticles etc. would add real bundle weight for a decorative
 * background). A fixed set of absolutely-positioned radial-gradient dots animated purely via
 * `transform`/`opacity` (see the `cyberFloat` keyframe in styles.css), which the browser
 * compositor can run without triggering layout/paint on every frame. Positions/timings are
 * randomized once on mount (useMemo with an empty dep array), not re-rolled on every render.
 */
export default function ParticlesBackground({ count = 22 }: { count?: number }) {
  const particles = useMemo<Particle[]>(
    () =>
      Array.from({ length: count }).map(() => ({
        left: Math.random() * 100,
        top: Math.random() * 100,
        size: 3 + Math.random() * 6,
        duration: 8 + Math.random() * 10,
        delay: Math.random() * -12,
        opacity: 0.25 + Math.random() * 0.45,
        color: PARTICLE_COLORS[Math.floor(Math.random() * PARTICLE_COLORS.length)],
      })),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  return (
    <Box
      aria-hidden
      sx={{
        position: 'absolute',
        inset: 0,
        overflow: 'hidden',
        pointerEvents: 'none',
      }}
    >
      {particles.map((p, i) => (
        <Box
          key={i}
          sx={{
            position: 'absolute',
            left: `${p.left}%`,
            top: `${p.top}%`,
            width: p.size,
            height: p.size,
            borderRadius: '50%',
            backgroundColor: p.color,
            opacity: p.opacity,
            boxShadow: `0 0 ${p.size * 2}px ${p.color}`,
            animation: `cyberFloat ${p.duration}s ease-in-out ${p.delay}s infinite`,
            willChange: 'transform',
          }}
        />
      ))}
    </Box>
  );
}
