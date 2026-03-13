'use client';

import { useEffect, useRef } from 'react';

interface LordIconProps {
  src: string;
  trigger?: 'hover' | 'click' | 'loop' | 'loop-on-hover' | 'morph' | 'morph-two-way';
  colors?: string;
  delay?: number;
  size?: number;
  className?: string;
}

export function LordIcon({ 
  src, 
  trigger = 'hover', 
  colors, 
  delay = 0, 
  size = 32,
  className = '' 
}: LordIconProps) {
  const iconRef = useRef<HTMLElement>(null);

  useEffect(() => {
    // Load Lord Icon script if not already loaded
    if (!document.querySelector('script[src*="lordicon"]')) {
      const script = document.createElement('script');
      script.src = 'https://cdn.lordicon.com/lordicon.js';
      script.async = true;
      document.head.appendChild(script);
    }
  }, []);

  return (
    <lord-icon
      ref={iconRef}
      src={src}
      trigger={trigger}
      colors={colors}
      delay={delay}
      style={{ width: `${size}px`, height: `${size}px` }}
      className={className}
    />
  );
}

// TypeScript declaration for lord-icon element
declare global {
  namespace JSX {
    interface IntrinsicElements {
      'lord-icon': {
        ref?: React.Ref<HTMLElement>;
        src: string;
        trigger?: string;
        colors?: string;
        delay?: number;
        style?: React.CSSProperties;
        className?: string;
      };
    }
  }
}