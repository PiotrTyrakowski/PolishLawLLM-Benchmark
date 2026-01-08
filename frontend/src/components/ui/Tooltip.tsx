'use client';

import { useState, useRef } from 'react';
import { Info } from '@phosphor-icons/react';

interface TooltipProps {
  content: string;
  children?: React.ReactNode;
}

export default function Tooltip({ content, children }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [coords, setCoords] = useState({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLSpanElement>(null);

  const handleMouseEnter = () => {
    if (triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      setCoords({
        top: rect.top - 8,
        left: rect.left + rect.width / 2,
      });
    }
    setIsVisible(true);
  };

  return (
    <span
      ref={triggerRef}
      className="relative inline-flex items-center"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children || (
        <Info
          size={14}
          className="text-slate-400 hover:text-slate-600 cursor-help transition-colors"
          weight="fill"
        />
      )}
      {isVisible && (
        <div
          className="fixed z-[9999] px-3 py-2 text-xs text-white bg-slate-800 rounded-lg shadow-lg whitespace-normal max-w-xs -translate-x-1/2 -translate-y-full"
          style={{
            minWidth: '200px',
            left: coords.left,
            top: coords.top,
          }}
        >
          {content}
          <div className="absolute left-1/2 -translate-x-1/2 top-full -mt-1 w-2 h-2 bg-slate-800 rotate-45" />
        </div>
      )}
    </span>
  );
}
