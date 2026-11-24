'use client';
import { useEffect, useRef, useState } from 'react';

export function CodeCopy({ text, en }: { text: string; en: boolean }) {
  const [status, setStatus] = useState<'idle' | 'copied' | 'error'>('idle');
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  useEffect(() => () => clearTimeout(timer.current), []);
  const feedback = status === 'copied' ? (en ? 'Copied' : 'Copiado') : status === 'error' ? (en ? 'Could not copy. Select the text and copy manually.' : 'Não foi possível copiar. Selecione o texto e copie manualmente.') : '';
  return <>
    <span className="sr-only" role="status">{feedback}</span>
    <button type="button" className="media-expand" aria-label={en ? 'Copy complete code' : 'Copiar código completo'} title={feedback || (en ? 'Copy complete code' : 'Copiar código completo')} onClick={async event => {
      event.stopPropagation();
      clearTimeout(timer.current);
      try { await navigator.clipboard.writeText(text); setStatus('copied'); }
      catch { setStatus('error'); }
      timer.current = setTimeout(() => setStatus('idle'), 3000);
    }}>{status === 'copied' ? '✓' : status === 'error' ? '!' : <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true"><rect x="8" y="8" width="12" height="13" rx="1"/><path d="M16 8V3H3v13h5"/></svg>}</button>
  </>;
}
