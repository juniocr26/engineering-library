import Link from 'next/link';
import { LanguageSelector } from '@/components/book-layout';
import { DocumentLanguage } from '@/components/document-language';
import { TableOfContents } from '@/components/table-of-contents';
import { documentationEntries } from '@/lib/documentation';
import { CatalogState } from '@/components/catalog-state';
import { catalogRequest, type Project } from '@/lib/catalog';
import { catalogHref, languageOf, messages } from '@/lib/i18n';
export default async function ProjectPage({ params, searchParams }: { params: Promise<{ slug: string }>; searchParams: Promise<{ edge?: string; lang?: string; page?: string }> }) {
  const { slug } = await params;
  const query = await searchParams;
  const language = languageOf(query.lang);
  const page = Math.max(1, Number.parseInt(query.page ?? '1', 10) || 1);
  const t = messages[language];
  let project: Project | undefined;
  try { project = await catalogRequest<Project>(`/${encodeURIComponent(slug)}`, language); } catch { /* Localized recovery below. */ }
  const header = <header className="toc-header"><Link className="back" href={catalogHref(page, language)}>{t.back}</Link><span>{project?.name ?? slug}</span><details className="toc-mobile-menu"><summary aria-label={language === 'en' ? 'Navigation menu' : 'Menu de navegação'}>☰</summary><Link href={catalogHref(page, language)}>{t.back}</Link></details><LanguageSelector language={language} page={page} slug={slug}/><h1>{language === 'en' ? 'Table of Contents' : 'Sumário'}<span className="toc-quill" aria-hidden="true"/></h1></header>;
  const entries = await documentationEntries(slug, language);
  return <main className="scene toc-scene" lang={language}><DocumentLanguage language={language}/><div className="toc-shell">
    {entries.length ? <TableOfContents initialEnd={query.edge === 'end'} entries={entries} slug={slug} language={language} header={header}/> : <div className="toc-empty paper manuscript-surface">{header}<CatalogState kind={project ? 'noDocs' : 'error'} language={language} page={page}/></div>}
  </div></main>;
}
