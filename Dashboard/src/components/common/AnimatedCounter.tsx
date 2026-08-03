import { useEffect, useRef } from 'react';
import { animate, useMotionValue, useTransform } from 'framer-motion';
import { Typography, type TypographyProps } from '@mui/material';

interface AnimatedCounterProps extends Omit<TypographyProps, 'children'> {
  value: number;
  duration?: number;
  prefix?: string;
  suffix?: string;
}

/**
 * Module 33: counts up to `value` on mount/change instead of popping the number in - used by
 * StatCard and any other KPI display. Driven by framer-motion's `animate()` on a MotionValue
 * (a single requestAnimationFrame loop under the hood), not a per-frame React state update, so
 * re-renders stay at "once on mount + once per prop change" rather than once per animation frame.
 */
export default function AnimatedCounter({ value, duration = 1.1, prefix = '', suffix = '', ...typographyProps }: AnimatedCounterProps) {
  const motionValue = useMotionValue(0);
  const rounded = useTransform(motionValue, (latest) => `${prefix}${Math.round(latest).toLocaleString()}${suffix}`);
  const nodeRef = useRef<HTMLSpanElement | null>(null);

  useEffect(() => {
    const controls = animate(motionValue, value, { duration, ease: 'easeOut' });
    return () => controls.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  useEffect(() => rounded.on('change', (latest) => {
    if (nodeRef.current) nodeRef.current.textContent = latest;
  }), [rounded]);

  return (
    <Typography {...typographyProps}>
      <span ref={nodeRef}>{prefix}0{suffix}</span>
    </Typography>
  );
}
