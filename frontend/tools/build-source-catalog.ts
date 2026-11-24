/** Explicit offline snapshot generation. Never invoked by a reader request. */
import { readdir, readFile, writeFile, realpath, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { markdownUnits } from '../lib/markdown.ts';
import { approvedSource } from '../lib/source-snapshot.ts';
import { canonicalSourceKey, sourceTarget } from '../lib/source-links.ts';
const workspace = process.env.SOURCE_WORKSPACE;
if (!workspace || process.env.APPROVE_REFERENCED_SOURCE !== 'yes') throw new Error('Set SOURCE_WORKSPACE and APPROVE_REFERENCED_SOURCE=yes after explicit source approval.');
const approvedProjects = new Set((process.env.APPROVED_SOURCE_PROJECTS ?? 'engineering-library,go-image-optimizer,payment-reconciliation-lab,rust-event-relay,url-shortener').split(','));
const library = path.resolve(process.cwd(), '..');
const docs = process.env.DOCUMENTATION_ROOT ?? path.join(library, 'docs');
const report: Record<string, unknown> = {};
async function files(directory: string): Promise<string[]> {
  return (await Promise.all((await readdir(directory, { withFileTypes: true })).filter(e => !e.isSymbolicLink()).map(e => e.isDirectory() ? files(path.join(directory, e.name)) : e.name.endsWith('.md') ? [path.join(directory, e.name)] : []))).flat();
}
for (const project of await readdir(docs, { withFileTypes: true })) {
  if (!project.isDirectory() || !/^[a-z0-9-]+$/.test(project.name)) continue;
  const slug = project.name;
  if (!approvedProjects.has(slug)) continue;
  const directory = path.join(docs, slug); const output = path.join(directory, 'en/links');
  const records: Record<string, { status: string; sourceKey?: string; sha256?: string; snapshot?: string }> = {};
  const occurrences: { document: string; href: string; path: string; status?: string }[] = [];
  const documents = (await Promise.all(["en", "pt-br"].map(folder => files(path.join(docs, slug, folder))))).flat(); let withoutSources = 0;
  const approvedRoot = path.resolve(workspace, slug);
  let root: string | undefined;
  try { root = await realpath(approvedRoot); if (root !== approvedRoot) root = undefined; } catch { /* Missing repository. */ }
  await mkdir(path.join(output, 'snapshots'), { recursive: true });
  for (const file of documents) {
    const language = file.startsWith(path.join(directory, 'pt-br') + path.sep) ? 'pt-BR' : 'en';
    const relative = path.relative(directory, file).split(path.sep).join('/');
    const document = relative.endsWith('/README.md') ? 'README' : relative.replace(/^(en|pt-br)\//, '');
    let count = 0;
    for (const unit of markdownUnits(await readFile(file, 'utf8'))) for (const href of unit.links ?? []) {
      const target = sourceTarget(slug, document, language, href); if (!target) continue;
      count++; occurrences.push({ document: relative, href, path: target.path });
      if (records[target.path]) continue;
      const record: typeof records[string] = { status: 'excluded', sourceKey: canonicalSourceKey(slug, target.path) }; records[target.path] = record;
      const resolved = approvedProjects.has(slug) ? await approvedSource(root, target.path) : { status: 'unapproved' as const };
      record.status = resolved.status;
      if (resolved.status === 'available') {
        record.sha256 = createHash('sha256').update(resolved.content).digest('hex'); record.snapshot = `snapshots/${record.sha256}.txt`;
        await writeFile(path.join(output, record.snapshot), resolved.content);
      }
    }
    if (!count) withoutSources++;
  }
  // Preserve prior snapshots until the caller has verified the complete replacement catalogs.
  for (const occurrence of occurrences) occurrence.status = records[occurrence.path].status;
  const summary = { documents: documents.length, withoutSources, eligibleOccurrences: occurrences.length, uniqueFiles: Object.keys(records).length,
    integrated: occurrences.filter(o => o.status === 'available').length, missing: occurrences.filter(o => o.status === 'missing').length, excluded: occurrences.filter(o => o.status === 'excluded').length };
  await writeFile(path.join(output, 'catalog.json'), JSON.stringify({ project: slug, schemaVersion: 2, approval: 'Owner explicitly authorized synchronization of referenced source for five portfolio collections on 2026-10-29; sensitive/configuration files and private product source excluded.', files: records, occurrences, summary }, null, 2) + '\n');
  report[slug] = summary;
}
await writeFile(path.join(docs, 'engineering-library/en/operations/source-reference-report.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
