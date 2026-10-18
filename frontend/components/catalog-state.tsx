 'use client';
import { useRouter } from 'next/navigation';
import { messages, type Language } from '@/lib/i18n';
export function CatalogState({ kind, language }: { kind: 'empty' | 'error' | 'loading' | 'noDocs'; language: Language; page?: number }) {
  const router = useRouter();
  const t = messages[language];
  return <div className="state" role={kind === 'error' ? 'alert' : 'status'}><p>{t[kind]}</p>{kind === 'error' && <button className="lang" onClick={() => router.refresh()}>{t.retry}</button>}</div>;
}
