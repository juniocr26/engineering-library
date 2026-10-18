import { notFound } from 'next/navigation';
import { documentationEntries, documentationSource } from '@/lib/documentation';
import { markdownUnits } from '@/lib/markdown';
import { languageOf } from '@/lib/i18n';
import { DocumentationReader } from '@/components/documentation-reader';

export default async function DocumentPage({ params, searchParams }: {
  params: Promise<{ slug: string; document: string[] }>; searchParams: Promise<{ lang?: string; q?: string }>;
}) {
  const { slug, document } = await params;
  const query = await searchParams;
  const language = languageOf(query.lang);
  const id = document.join('/');
  const source = await documentationSource(slug, id, language);
  if (source === null) notFound();
  const units = markdownUnits(source);
  const entries = await documentationEntries(slug, language);
  return <DocumentationReader key={`${slug}/${id}`} project={slug} document={id} language={language} units={units} entries={entries} query={(query.q ?? '').slice(0, 100)}/>;
}
