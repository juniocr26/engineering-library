import { catalogRequest, type Project } from '@/lib/catalog';
import { projectDisplayName } from '@/lib/project-name';
import { notFound } from 'next/navigation';
import { documentationEntries, documentationSource } from '@/lib/documentation';
import { integrateSources } from '@/lib/source-references';
import { markdownUnits } from '@/lib/markdown';
import { languageOf } from '@/lib/i18n';
import { DocumentationReader } from '@/components/documentation-reader';
import ProjectPage from '../../page';

export default async function DocumentPage({ params, searchParams }: {
  params: Promise<{ slug: string; document: string[] }>; searchParams: Promise<{ edge?: string; lang?: string; q?: string }>;
}) {
  const { slug, document } = await params;
  const query = await searchParams;
  const language = languageOf(query.lang);
  const id = document.join('/');
  // The retained Markdown index URL uses the same canonical, numbered contents.
  if (id === 'index.md') return ProjectPage({ params: Promise.resolve({ slug }), searchParams: Promise.resolve(query) });
  const source = await documentationSource(slug, id, language);
  if (source === null) notFound();
  let name: string | undefined;
  try { name = (await catalogRequest<Project>(`/${encodeURIComponent(slug)}`, language)).name; } catch { /* Keep local documentation available with a readable fallback. */ }
  const units = await integrateSources(slug, id, language, markdownUnits(source));
  const entries = await documentationEntries(slug, language);
  return <DocumentationReader initialEnd={query.edge === 'end'} key={`${slug}/${id}`} project={slug} projectName={projectDisplayName(slug, name)} document={id} language={language} units={units} entries={entries} query={(query.q ?? '').slice(0, 100)}/>;
}
