'use client';
import type { ReactNode } from 'react';
import { BookReader } from './book-reader';
import type { TocEntry } from '../lib/documentation';
import type { Language } from '../lib/i18n';
export function TableOfContents({ entries, slug, language, header }: { entries: TocEntry[]; slug: string; language: Language; header: ReactNode }) {
  return <BookReader units={entries} header={header} project={slug} language={language} title={language === 'en' ? 'Table of Contents' : 'Sumário'} renderUnit={entry => {
    const text = <><span className="chapter-number">{entry.number}</span><span>{entry.title}</span></>;
    const content = entry.href ? <a href={entry.href}>{text}<span className="toc-leader" aria-hidden="true"/>↗</a> : <span aria-disabled={!entry.heading || undefined}>{text}</span>;
    return entry.heading ? <h2 className="toc-chapter">{content}</h2> : <div className="toc-document">{content}</div>;
  }}/>;
}
