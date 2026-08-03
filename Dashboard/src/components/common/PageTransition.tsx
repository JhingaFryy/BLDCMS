import type { ReactNode } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useLocation } from 'react-router-dom';

/**
 * Module 33: a lightweight page fade/slide-up transition, keyed by route pathname so navigating
 * between pages retriggers it. Wraps AppLayout's routed content - only `opacity`/`transform`
 * animate (GPU-cheap), duration is short (180ms) per the module's "avoid excessive/slow
 * animations" guidance. `mode="wait"` is intentionally NOT used - waiting for the outgoing page
 * to fully exit before the new one enters would make navigation feel slower, not smoother.
 */
export default function PageTransition({ children }: { children: ReactNode }) {
  const location = useLocation();

  return (
    <AnimatePresence initial={false}>
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.18, ease: 'easeOut' }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
