import { readdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import GithubSlugger from 'github-slugger';

const root = process.env.DOCUMENTATION_ROOT ?? path.resolve(process.cwd(), '../docs/projects');
const text = (node: { value?: string; children?: unknown[] }): string => node.value ?? (node.children ?? []).map(child => text(child as Parameters<typeof text>[0])).join('');
async function files(dir: string): Promise<string[]> {
  return (await Promise.all((await readdir(dir, { withFileTypes: true })).filter(e => !e.isSymbolicLink()).map(e => e.isDirectory() ? files(path.join(dir, e.name)) : e.name.endsWith('.md') ? [path.join(dir, e.name)] : []))).flat();
}
const projects = [];
for (const project of (await readdir(root, { withFileTypes: true })).filter(e => e.isDirectory()).map(e => e.name).sort()) {
  const documents = [];
  for (const file of (await files(path.join(root, project))).sort()) {
    const relative = path.relative(path.join(root, project), file);
    const language = relative.startsWith('docs/en/') || relative === 'README.md' ? 'en' : relative.startsWith('docs/pt-BR/') || relative === 'README.pt-BR.md' ? 'pt-BR' : undefined;
    const source = await readFile(file, 'utf8');
    const slugger = new GithubSlugger();
    const stack: { depth: number; anchor: string }[] = [];
    const headings = unified().use(remarkParse).use(remarkGfm).parse(source).children.filter(n => n.type === 'heading').map(n => {
      const title = text(n); const anchor = slugger.slug(title);
      while (stack.length && stack.at(-1)!.depth >= n.depth) stack.pop();
      const parent = stack.at(-1)?.anchor;
      stack.push({ depth: n.depth, anchor });
      return { title, depth: n.depth, anchor, parent, question: title.match(/^Q\d+\b/i)?.[0] };
    });
    documents.push({ relative, language, headings });
  }
  projects.push({ project, documents });
}
const output = process.argv[2] ?? '/tmp/engineering-library-navigation-inventory.json';
await writeFile(output, JSON.stringify({ projects }, null, 2));
for (const p of projects) console.log(`${p.project}: ${p.documents.length} Markdown, ${p.documents.reduce((n,d) => n + d.headings.length, 0)} headings`);
console.log(`Complete inventory: ${output}`);

if (process.argv.includes('--validate')) {
  const { documentationEntries } = await import('../lib/documentation.ts');
  const { numberHeadingUnits, numberedHeading, headingTitle } = await import('../lib/heading-numbering.ts');
  const { markdownUnits } = await import('../lib/markdown.ts');
  const { getReadingSequence } = await import('../lib/reading-order.ts');
  if (process.env.BACKEND_URL) {
    const catalog: string[] = [];
    let totalPages = 1;
    for (let page = 1; page <= totalPages; page++) {
      const response = await fetch(`${process.env.BACKEND_URL}/api/projects?lang=en&page=${page}`);
      if (!response.ok) throw new Error(`Catalog unavailable: ${response.status}`);
      const data = await response.json(); totalPages = data.pagination.total_pages;
      catalog.push(...data.projects.map((project: { slug: string }) => project.slug));
    }
    if (JSON.stringify(catalog.sort()) !== JSON.stringify(projects.map(p => p.project).sort())) throw new Error('Catalog and collection inventory differ');
    console.log(`Active backend catalog verified: ${catalog.length} projects across ${totalPages} pages`);
  }
  const reports = [];
  let failures = 0;
  for (const project of projects) {
    const errors: string[] = [];
    const ambiguities: string[] = [];
    const localized = await Promise.all((['en', 'pt-BR'] as const).map(language => documentationEntries(project.project, language)));
    const languages = [];
    for (const [i, language] of (['en', 'pt-BR'] as const).entries()) {
      const entries = localized[i];
      const ids = new Set<string>();
      const byId = new Map(entries.map(e => [e.id, e]));
      const counters = new Map<string, number>();
      let headingsExpected = 0;
      let headingsFound = 0;
      const excluded = [];
      for (const entry of entries) {
        if (ids.has(entry.id)) errors.push(`${language}: duplicate ${entry.id}`);
        ids.add(entry.id);
        const parent = entry.parentId ? byId.get(entry.parentId) : undefined;
        if (entry.parentId && !parent) errors.push(`${language}: missing parent ${entry.id}`);
        const key = entry.parentId ?? '@root';
        const ordinal = (counters.get(key) ?? 0) + 1; counters.set(key, ordinal);
        const number = parent ? `${parent.number}.${ordinal}` : `${ordinal}`;
        if (entry.number !== number || entry.depth !== (parent ? parent.depth! + 1 : 0)) errors.push(`${language}: numbering/depth ${entry.id}`);
        if (!entry.href && !entry.id.startsWith('category:')) ambiguities.push(`${language}: unavailable document ${entry.id}`);
        if (entry.documentId) {
          headingsFound++;
          const counterpart = localized[1-i].find(e => e.id === entry.id);
          if (!counterpart || !counterpart.href) ambiguities.push(`${language}: unverified translation ${entry.id}`);
          else if (counterpart.number !== entry.number || counterpart.depth !== entry.depth) ambiguities.push(`${language}: bilingual structural mismatch ${entry.id} (${entry.number} vs ${counterpart.number})`);
        }
      }
      for (const doc of project.documents.filter(d => d.language === language)) {
        const id = doc.relative.startsWith('README') ? 'README' : doc.relative.slice(`docs/${language}/`.length);
        const entry = byId.get(id);
        if (!entry) {
          const source = await readFile(path.join(root, project.project, doc.relative), 'utf8');
          const navigationOnly = !source.split('\n').filter(line => line.trim() && !/^#\s|^\s*(?:[-*]\s+)?\[[^\]]+\]\([^)]+\)\s*$/.test(line)).length;
          const reason = id === 'index.md' ? 'project navigation index' : id === 'faq/study-guide.md' ? 'legacy compatibility study guide (existing FAQ duplicates retained on disk)' : navigationOnly && id.endsWith('/index.md') ? 'navigation-only index' : undefined;
          excluded.push({ id, reason: reason ?? 'UNEXPECTED OMISSION', headings: doc.headings.length });
          if (!reason) errors.push(`${language}: omitted document ${id}`);
          continue;
        }
        const units = markdownUnits(await readFile(path.join(root, project.project, doc.relative), 'utf8'));
        const numbered = numberHeadingUnits(units, entries, id);
        for (const unit of numbered.filter(u => u.heading !== undefined)) {
          const canonical = entries.find(e => e.id === unit.navigationId);
          if (!canonical || canonical.number !== unit.navigationNumber) errors.push(`${language}: reader numbering ${id}#${unit.id}`);
          const tree: import('hast').Root = { type: 'root', children: [{ type: 'element', tagName: `h${unit.headingDepth}`, properties: {}, children: [{ type: 'text', value: unit.text }] }] };
          numberedHeading(unit.navigationNumber)()(tree);
          const heading = tree.children[0];
          const rendered = heading.type === 'element' ? heading.children.map(n => n.type === 'text' ? n.value : '').join('') : '';
          if (canonical && rendered !== `${canonical.number} ${headingTitle(unit.text, canonical.number)}`) errors.push(`${language}: rendered number ${id}#${unit.id}`);
        }
        const expected = doc.headings.filter((h,index) => !(index === 0 && h.depth === 1));
        headingsExpected += expected.length;
        const stack: { depth: number; id: string }[] = [];
        for (const h of expected) {
          const match = entries.find(e => e.documentId === id && e.anchor === h.anchor);
          while (stack.length && stack.at(-1)!.depth >= h.depth) stack.pop();
          const parent = stack.at(-1)?.id ?? id;
          if (!match || match.parentId !== parent) errors.push(`${language}: missing/misnested heading ${id}#${h.anchor}`);
          if (match) stack.push({ depth: h.depth, id: match.id });
        }
        for (const node of entries.filter(e => e.documentId === id)) {
          if (!units.some(u => u.id === node.anchor)) errors.push(`${language}: unreachable ${node.id}`);
          const url = new URL(node.href!, 'https://reader.invalid');
          if (decodeURIComponent(url.hash.slice(1)) !== node.anchor || !url.pathname.endsWith(`/docs/${id}`) || url.searchParams.get('lang') !== language) errors.push(`${language}: wrong destination ${node.id}`);
        }
      }
      const sequence = getReadingSequence(project.project, language, entries);
      if (sequence.length !== entries.filter(e => e.href && !e.documentId).length + 1) errors.push(`${language}: duplicate chapters`);
      languages.push({ language, entries: entries.length, headingsExpected, headingsFound, excluded, tree: entries });
    }
    failures += errors.length;
    const baselineUnnumberedHeadings = languages.map(l => ({ language: l.language, missing: l.headingsExpected }));
    reports.push({ project: project.project, baselineUnnumberedHeadings, errors, ambiguities, languages });
    console.log(`${project.project}: ${languages.map(l => `${l.language}=${l.entries} entries, ${l.headingsFound}/${l.headingsExpected} headings`).join('; ')}; ${errors.length} errors; ${ambiguities.length} unverified bilingual targets`);
  }
  await writeFile('/tmp/navigation-audit.json', JSON.stringify(reports, null, 2));
  const summary = ['# Full-library navigation audit', '', 'Generated from every collection and every Markdown AST. Counts below cover navigable trees; the inventory also includes excluded legacy documents and metadata. Translation ambiguities are not verified equivalents. No technical Markdown was rewritten.', '', '| Project | EN entries | PT-BR entries | Heading coverage EN/PT | Structural errors | Bilingual findings (unverified targets / structure) |', '| --- | ---: | ---: | --- | ---: | ---: |'];
  for (const r of reports) summary.push(`| ${r.project} | ${r.languages[0].entries} | ${r.languages[1].entries} | ${r.languages.map(l => `${l.headingsFound}/${l.headingsExpected}`).join(' / ')} | ${r.errors.length} | ${r.ambiguities.length} |`);
  for (const r of reports) {
    summary.push('', `## ${r.project}`, '', `Before correction: ${r.baselineUnnumberedHeadings.map(l => `${l.language}: ${l.missing} internal reader headings lacked structural numbers`).join('; ')}. Existing document/category numbering did not require a reset fix.`, '', 'Correction: reader heading units resolve the existing canonical entry by document ID and AST anchor; the Markdown renderer and local chapter links consume its resolved number. TOC and project chapter links retain the same tree. Audit checks heading metadata and the shared HAST numbering transform; it does not certify browser layout.', '', 'Excluded files (explicit compatibility/navigation policy):', ...r.languages.flatMap(l => l.excluded.map(d => `- ${l.language} ${d.id}: ${d.reason}; ${d.headings} headings inventoried.`)), '', `Unresolved bilingual findings: ${r.ambiguities.length} (unverified targets and structural differences). Details and complete trees are in navigation-audit.json. Missing canonical section metadata is reported rather than inferred from translated ordinal positions.`, ...r.errors);
  }
  await writeFile('/tmp/navigation-audit.md', summary.join('\n') + '\n');
  if (failures) process.exitCode = 1;
}
