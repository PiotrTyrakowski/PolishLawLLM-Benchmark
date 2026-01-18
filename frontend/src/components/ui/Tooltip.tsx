'use client';

import { useState, useRef, useCallback } from 'react';
import { Info } from '@phosphor-icons/react';

interface TooltipProps {
  content: string;
  children?: React.ReactNode;
}

export default function Tooltip({ content, children }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [coords, setCoords] = useState({ top: 0, left: 0, alignLeft: false, alignRight: false });
  const triggerRef = useRef<HTMLSpanElement>(null);

  const calculatePosition = useCallback(() => {
    if (triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      const tooltipWidth = 200;
      const viewportWidth = window.innerWidth;
      const padding = 12;

      let left = rect.left + rect.width / 2;
      let alignLeft = false;
      let alignRight = false;

      // Check if tooltip would overflow on the left
      if (left - tooltipWidth / 2 < padding) {
        alignLeft = true;
        left = rect.left;
      }
      // Check if tooltip would overflow on the right
      else if (left + tooltipWidth / 2 > viewportWidth - padding) {
        alignRight = true;
        left = rect.right;
      }

      setCoords({
        top: rect.top - 8,
        left,
        alignLeft,
        alignRight,
      });
    }
    setIsVisible(true);
  }, []);

  const handleInteraction = () => {
    calculatePosition();
  };

  return (
    <span
      ref={triggerRef}
      className="relative inline-flex items-center"
      onMouseEnter={handleInteraction}
      onMouseLeave={() => setIsVisible(false)}
      onTouchStart={handleInteraction}
      onTouchEnd={() => setTimeout(() => setIsVisible(false), 2000)}
    >
      {children || (
        <Info
          size={14}
          className="text-slate-400 hover:text-slate-600 cursor-help transition-colors flex-shrink-0"
          weight="fill"
        />
      )}
      {isVisible && (
        <div
          className={`fixed z-[9999] px-3 py-2 text-xs text-white bg-slate-800 rounded-lg shadow-lg whitespace-normal max-w-[calc(100vw-24px)] sm:max-w-xs -translate-y-full ${
            coords.alignLeft ? '' : coords.alignRight ? '-translate-x-full' : '-translate-x-1/2'
          }`}
          style={{
            minWidth: '160px',
            maxWidth: '280px',
            left: coords.left,
            top: coords.top,
          }}
        >
          {content}
          <div
            className={`absolute top-full -mt-1 w-2 h-2 bg-slate-800 rotate-45 ${
              coords.alignLeft ? 'left-3' : coords.alignRight ? 'right-3' : 'left-1/2 -translate-x-1/2'
            }`}
          />
        </div>
      )}
    </span>
  );
}
