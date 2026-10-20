'use client';
import { numberHeadingUnits } from '../lib/heading-numbering';
import { referenceContainsLocation, sourceUnits } from '../lib/source-links';
import { useMemo } from 'react';
import { projectDisplayName } from '../lib/project-name';
import { useEffect, useState, type ReactNode } from 'react';
import Link from 'next/link';
import { getReadingSequence, readingNeighbors } from '../lib/reading-order';
import { containsLocation } from '../lib/table-pagination';
import { TextHighlights } from './text-highlights';
import { BookReader } from './book-reader';
import { DocumentLanguage } from './document-language';
import { MarkdownUnit } from './markdown-unit';
import { ReaderTools } from './reader-tools';
import { documentHref } from '../lib/document-links';
import type { TocEntry } from '../lib/documentation';
import type { MarkdownUnit as Unit } from '../lib/markdown';
import type { Language } from '../lib/i18n';

export function DocumentationReader(props: Parameters<typeof ProjectDocumentationReader>[0]) {
  // A project change starts fresh state, including pending bookmark mutations.
  return <ProjectDocumentationReader key={props.project} {...props}/>;
}

function ProjectDocumentationReader({ project, projectName, document: documentId, language, units, entries, query, initialEnd = false }: {
  project: string; projectName?: string; document: string; language: Language; units: Unit[]; entries: TocEntry[]; query: string; initialEnd?: boolean;
}) {
  const en = language === 'en';
  const [location, setLocation] = useState('');
  const [expandedByDocument, setExpandedByDocument] = useState<Record<string, string[]>>({});
  const documentKey = documentId;
  const expansionStorageKey = `reader-sources/${project}/${documentKey}`;
  // Moving between prose anchors does not change the source expansion set.
  // Depend on the referenced source identity, not every location string, so the
  // measured units remain stable for ordinary search/bookmark navigation.
  const locationSource = units.flatMap(unit => unit.references ?? []).find(ref => referenceContainsLocation(ref, location))?.id;
  const expanded = useMemo(() => new Set([...(expandedByDocument[documentKey] ?? []), ...(locationSource ? [locationSource] : [])]), [expandedByDocument, documentKey, locationSource]);
  const flowUnits: Unit[] = useMemo(() => sourceUnits(numberHeadingUnits(units, entries, documentId), expanded), [units, entries, documentId, expanded]);
  function toggleSource(id: string) {
    const next = new Set(expanded);
    if (next.has(id)) next.delete(id); else next.add(id);
    setExpandedByDocument(previous => ({ ...previous, [documentKey]: [...next] }));
    try { sessionStorage.setItem(expansionStorageKey, JSON.stringify([...next])); } catch { /* Storage is optional. */ }
    const owner = units.find(unit => unit.references?.some(ref => ref.id === id));
    if (owner) { setLocation(owner.id); setLocationRequest(previous => previous + 1); window.history.replaceState({ ...window.history.state, bookLocation: null }, '', `#${encodeURIComponent(owner.id)}`); }
  }
  const [locationRequest, setLocationRequest] = useState(0);
  const neighbors = readingNeighbors(getReadingSequence(project, language, entries), documentId);
  const title = entries.find(entry => entry.id === documentId)?.title ?? units.find(unit => unit.heading !== undefined)?.text ?? documentId;
  useEffect(() => {
    const navigateAnnotation = (event: Event) => {
      const target = (event as CustomEvent<{ project: string; document: string; language: string; anchor: string }>).detail;
      if (target.project !== project || target.document !== documentId || target.language !== language) return;
      setLocation(target.anchor); setLocationRequest(previous => previous + 1);
    };
    window.addEventListener('reader-annotation-location', navigateAnnotation);
    return () => window.removeEventListener('reader-annotation-location', navigateAnnotation);
  }, [project, documentId, language]);

  useEffect(() => {
    const update = () => {
      try { setLocation(decodeURIComponent(window.location.hash.slice(1))); setLocationRequest(previous => previous + 1); } catch { setLocation(''); }
    };
    update(); window.addEventListener('hashchange', update);
    return () => window.removeEventListener('hashchange', update);
  }, [documentId, language, units]);

  useEffect(() => {
    try {
      const stored: unknown = JSON.parse(sessionStorage.getItem(expansionStorageKey) ?? '[]');
      if (!Array.isArray(stored)) return;
      const valid = new Set(units.flatMap(unit => (unit.references ?? []).map(ref => ref.id)));
      const restored = stored.filter((id): id is string => typeof id === 'string' && valid.has(id));
      if (restored.length) setExpandedByDocument(previous => ({ ...previous, [documentKey]: [...new Set([...(previous[documentKey] ?? []), ...restored])] }));
    } catch { /* Reading works when session storage is disabled. */ }
  }, [expansionStorageKey, documentKey, units]);

  useEffect(() => {
    const ids = units.flatMap(unit => (unit.references ?? []).filter(ref => referenceContainsLocation(ref, location)).map(ref => ref.id));
    if (ids.length) setExpandedByDocument(previous => {
      const current = previous[documentKey] ?? [];
      const next = [...new Set([...current, ...ids])];
      try { sessionStorage.setItem(expansionStorageKey, JSON.stringify(next)); } catch { /* Storage is optional. */ }
      return ids.every(id => current.includes(id)) ? previous : { ...previous, [documentKey]: next };
    });
  }, [location, units, documentKey, expansionStorageKey]);

  const header = (toolbar: (action: ReactNode) => ReactNode, action: ReactNode) => <header className="reader-document-header">
    <Link href={`/projects/${encodeURIComponent(project)}?lang=${language}`}>← {en ? 'Contents' : 'Sumário'}</Link><span>{projectDisplayName(project, projectName)}</span>
    {toolbar(action)}
    <nav className="reader-document-languages" aria-label={en ? 'Language' : 'Idioma'}>{(['pt-BR', 'en'] as const).map(lang => <Link key={lang} href={documentHref(project, documentId, lang)} aria-current={lang === language ? 'true' : undefined} hrefLang={lang}>{lang === 'en' ? '🇺🇸 English' : '🇧🇷 Português'}</Link>)}</nav>
  </header>;

  return <main className="scene toc-scene" lang={language} onClick={event => {
    const link = (event.target as HTMLElement).closest<HTMLAnchorElement>('a[href]');
    if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const target = new URL(link.href);
    if (target.pathname === window.location.pathname && target.search === window.location.search && target.hash) {
      try { setLocation(decodeURIComponent(target.hash.slice(1))); setLocationRequest(previous => previous + 1); } catch { /* Invalid anchors keep their native link behavior. */ }
    }
  }}><DocumentLanguage language={language}/><div className="toc-shell documentation-shell">
    <TextHighlights project={project} document={documentId} language={language}><ReaderTools project={project} projectName={projectName} document={documentId} language={language} entries={entries} title={title} headings={flowUnits.filter(unit => unit.heading !== undefined)}>{({ toolbar, pageAction }) => <BookReader key={documentId} initialEnd={initialEnd} previousChapter={neighbors.previous} nextChapter={neighbors.next} previousIsContents={neighbors.previousIsContents} units={flowUnits} project={project} language={language} title={title} header={action => header(toolbar, action)} location={location} locationRequest={locationRequest}
      renderUnit={unit => <MarkdownUnit unit={unit} project={project} document={documentId} language={language} query={containsLocation(unit, location) ? query : ''} expanded={expanded} toggleSource={toggleSource} location={location}/>}
      pageAction={pageAction}/>}</ReaderTools></TextHighlights>
    {location && !flowUnits.some(unit => containsLocation(unit, location) || location.startsWith(`${unit.id}--row-`)) && <p role="status" className="reader-notice">{en ? 'This saved location is unavailable: the source or translation may have changed. Showing the document start.' : 'Esta posição está indisponível: o código ou a tradução pode ter mudado. Exibindo o início do documento.'}</p>}
  </div></main>;
}
