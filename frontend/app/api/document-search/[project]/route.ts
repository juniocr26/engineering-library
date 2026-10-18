import { documentationEntries, documentationSource } from '@/lib/documentation';
import { documentHref } from '@/lib/document-links';
import { markdownUnits } from '@/lib/markdown';
import { languageOf } from '@/lib/i18n';
export async function GET(request: Request, { params }: { params: Promise<{ project: string }> }) {
  const { project } = await params;
  const url = new URL(request.url); const query = (url.searchParams.get('q') ?? '').trim();
  if (query.length < 2 || query.length > 100) return Response.json({ results: [], truncated: false });
  const language = languageOf(url.searchParams.get('lang') ?? undefined);
  const entries = await documentationEntries(project, language);
  if (!entries.length) return Response.json({ error: 'Project not found' }, { status: 404 });
  const results: { title: string; excerpt: string; href: string; anchor: string }[] = [];
  // The repository collection is small; scan authoritative Markdown, without another index.
  for (const entry of entries.filter(entry => entry.href)) {
    const source = await documentationSource(project, entry.id, language);
    if (source === null) continue;
    for (const unit of markdownUnits(source)) {
      const offset = unit.text.toLowerCase().indexOf(query.toLowerCase());
      if (offset < 0) continue;
      const href = documentHref(project, entry.id, language, unit.id).replace('?lang=', `?q=${encodeURIComponent(query)}&lang=`);
      results.push({ title: entry.title, excerpt: unit.text.slice(Math.max(0, offset - 65), offset + query.length + 110), href, anchor: unit.id });
      if (results.length === 80) return Response.json({ results, truncated: true });
    }
  }
  return Response.json({ results, truncated: false });
}
