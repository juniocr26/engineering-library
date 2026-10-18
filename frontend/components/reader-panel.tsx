'use client';
import { useEffect, useRef, type ReactNode } from 'react';
export function ReaderPanel({ title, close, children, closeLabel }: { title: string; close: () => void; children: ReactNode; closeLabel: string }) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const node = dialog.current!;
    const previous = document.activeElement as HTMLElement | null;
    node.showModal();
    return () => { node.close(); previous?.focus({ preventScroll: true }); };
  }, []);
  return <dialog ref={dialog} className="reader-panel paper manuscript-surface" aria-label={title} onCancel={event => { event.preventDefault(); close(); }}>
    <div className="reader-panel-heading"><h2>{title}</h2><button type="button" onClick={close} aria-label={closeLabel}>×</button></div>
    <div className="reader-panel-content">{children}</div>
  </dialog>;
}
