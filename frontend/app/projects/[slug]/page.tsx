import Link from 'next/link';
import { BookLayout } from '@/components/book-layout';
import { CatalogState } from '@/components/catalog-state';
import { catalogRequest, type Project } from '@/lib/catalog';
import { catalogHref, languageOf, messages, categoryLabels } from '@/lib/i18n';
export default async function ProjectPage({ params, searchParams }: { params: Promise<{ slug: string }>; searchParams: Promise<{ lang?: string; page?: string }> }) {
  const { slug } = await params;
  const query = await searchParams;
  const language = languageOf(query.lang);
  const page = Math.max(1, Number.parseInt(query.page ?? '1', 10) || 1);
  const t = messages[language];
  let project: Project | undefined;
  try { project = await catalogRequest<Project>(`/${encodeURIComponent(slug)}`, language); } catch { /* Localized recovery below. */ }
  return <BookLayout language={language} page={page} slug={slug}><Link className="back" href={catalogHref(page, language)}>{t.back}</Link>{project ? <><h2 className="section-title">{project.name}</h2><p>{project.description}</p><h3>{t.index}</h3>{project.categories?.length ? <><p>{t.remote}</p>{project.categories.map(category => <a className="category" key={category.url} href={category.url}>{categoryLabels[language][category.name] ?? category.name} <span aria-hidden="true">↗</span></a>)}</> : <CatalogState kind="noDocs" language={language}/>}</> : <CatalogState kind="error" language={language} page={page}/>}</BookLayout>;
}
