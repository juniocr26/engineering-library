'use client';
import { BookReader } from '../../components/book-reader';
import { MarkdownUnit } from '../../components/markdown-unit';
import type { MarkdownUnit as Unit } from '../../lib/markdown';
export default function TableStressClient({ units, language, location }: { location?: string; units: Unit[]; language: 'en' | 'pt-BR' }) {
  return <main className="scene toc-scene" lang={language}><div className="toc-shell documentation-shell"><BookReader location={location} units={units} project="synthetic" language={language} title="Synthetic tables" renderUnit={unit => <MarkdownUnit unit={unit} project="synthetic" document="fixture" language={language} query=""/>}/></div></main>;
}
