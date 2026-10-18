import Link from 'next/link';
export default function MissingDocument() {
  return <main className="scene"><section className="toc-empty paper manuscript-surface"><h1>Documento não encontrado / Document not found</h1><p>Este documento não está disponível neste idioma. / This document is unavailable in this language.</p><Link href="/">← Engineering Library</Link></section></main>;
}
