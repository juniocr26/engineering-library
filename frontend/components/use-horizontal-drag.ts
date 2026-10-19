'use client';
import { useRef, useState, type MouseEvent, type PointerEvent } from 'react';

/** Mouse enhancement only: native touch, wheel and keyboard scrolling stay intact. */
export function useHorizontalDrag(overflow: boolean) {
  const drag = useRef<{ x: number; y: number; left: number; active: boolean } | null>(null);
  const moved = useRef(false);
  const [dragging, setDragging] = useState(false);
  const end = () => { drag.current = null; setDragging(false); };
  return {
    dragging,
    handlers: {
      onPointerDown(event: PointerEvent<HTMLDivElement>) {
        moved.current = false;
        if (!overflow || event.pointerType !== 'mouse' || event.button !== 0 || event.shiftKey ||
          (event.target as HTMLElement).closest('a,button,input,[data-code-text]') || !window.getSelection()?.isCollapsed) return;
        drag.current = { x: event.clientX, y: event.clientY, left: event.currentTarget.scrollLeft, active: false };
      },
      onPointerMove(event: PointerEvent<HTMLDivElement>) {
        const current = drag.current;
        if (!current) return;
        const dx = event.clientX - current.x;
        if (!current.active && Math.abs(event.clientY - current.y) > Math.abs(dx) + 6) { end(); return; }
        if (!current.active && Math.abs(dx) > 6) {
          current.active = true; moved.current = true; setDragging(true);
          event.currentTarget.setPointerCapture(event.pointerId);
        }
        if (current.active) { event.preventDefault(); event.currentTarget.scrollLeft = current.left - dx; }
      },
      onPointerLeave() { if (!drag.current?.active) end(); },
      onPointerUp: end, onPointerCancel: end, onLostPointerCapture: end,
      onClickCapture(event: MouseEvent<HTMLDivElement>) {
        if (moved.current) { event.preventDefault(); event.stopPropagation(); moved.current = false; }
      },
    },
  };
}
