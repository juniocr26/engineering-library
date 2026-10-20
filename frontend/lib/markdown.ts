import type { RootContent, ListItem } from 'mdast';
import { createHash } from 'node:crypto';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import GithubSlugger from 'github-slugger';
import type { SourceReference, SourcePart } from './source-links';
import type { TablePart } from './table-pagination';

export type MarkdownUnit = { command?: { value: string; language?: string }; navigationNumber?: string; navigationId?: string; readingParents?: string[]; readingSection?: string; readingAmbiguous?: boolean; readingAnchor?: string; links?: string[]; references?: SourceReference[]; code?: SourceReference; codePart?: SourcePart; codeOrigin?: string; id: string; source: string; text: string; heading?: string; headingDepth?: number; navigationKey?: string; keepWithNext?: boolean; tableOrigin?: string; tablePart?: TablePart; table?: { header: string; rows: string[]; definitions: string } };
type TextNode = { value?: string; alt?: string; children?: TextNode[] };
const links = (node: TextNode & { type?: string; url?: string; identifier?: string }, definitions: Map<string, string>): string[] => [...(node.type === 'link' && node.url ? [node.url] : node.type === 'linkReference' && node.identifier && definitions.has(node.identifier) ? [definitions.get(node.identifier)!] : []), ...(node.children ?? []).flatMap(child => links(child, definitions))];
const plain = (node: TextNode): string => node.value ?? node.alt ?? node.children?.map(plain).join('') ?? '';

/** Parse Markdown syntax before dividing into semantic, content-addressed book units. */
export function markdownUnits(source: string): MarkdownUnit[] {
  const tree = unified().use(remarkParse).use(remarkGfm).parse(source);
  const definitions = tree.children.filter(node => node.type === 'definition').map(node => source.slice(node.position!.start.offset, node.position!.end.offset)).join('\n');
  const linkDefinitions = new Map(tree.children.filter(node => node.type === 'definition').map(node => [node.identifier, node.url]));
  const slugger = new GithubSlugger();
  const occurrences = new Map<string, number>();
  let section = 'start';
  const questionId = (text: string) => text.match(/^\s*(Q\d+)\b/i)?.[1].toUpperCase();
  const questionCounts = new Map<string, number>();
  const canonicalSections = new Map<RootContent, string>();
  const canonicalCounts = new Map<string, number>();
  let pendingSection: string | undefined;
  for (const node of tree.children) {
    if (node.type === 'html') {
      pendingSection = node.value.match(/^<!--\s*reading-section:\s*([a-zA-Z0-9_.:-]+)\s*-->$/)?.[1];
    } else if (node.type === 'heading' && pendingSection) {
      canonicalSections.set(node, pendingSection);
      canonicalCounts.set(pendingSection, (canonicalCounts.get(pendingSection) ?? 0) + 1);
      pendingSection = undefined;
    }
    const id = node.type === 'heading' ? questionId(plain(node as TextNode)) : undefined;
    if (id) questionCounts.set(id, (questionCounts.get(id) ?? 0) + 1);
  }
  const sectionStack: { depth: number; key: string }[] = [];
  let readingParents: string[] = [];
  let readingSection = 'document-start';
  let questionDepth = 0;
  let readingAmbiguous = false;
  return tree.children.filter(node => node.type !== 'definition' && node.type !== 'html').flatMap<{ node: RootContent | ListItem; identityRaw: string | undefined }>(node => {
    // Leave ordinary lists and their historic bookmark anchors intact.
    const sourceList = node.type === 'list' && links(node as TextNode, linkDefinitions).some(href => /\.(?:rs|go|py|rb|[jt]sx?|java|cs|php|sh|sql|json|ya?ml|toml)(?:#.*)?$/i.test(href));
    return sourceList && node.type === 'list' ? node.children.map((child, index) => ({ node: child, identityRaw: index === 0 ? source.slice(node.position!.start.offset, node.position!.end.offset) : undefined })) : [{ node, identityRaw: undefined }];
  }).map(({ node, identityRaw }) => {
    const raw = source.slice(node.position!.start.offset, node.position!.end.offset);
    const text = plain(node as TextNode);
    const heading = node.type === 'heading' ? slugger.slug(text) : undefined;
    if (node.type === 'heading') {
      section = heading!;
      while (sectionStack.length && sectionStack.at(-1)!.depth >= node.depth) sectionStack.pop();
      const question = questionId(text);
      if (question) {
        readingSection = `question:${question}`;
        questionDepth = node.depth;
        readingAmbiguous = questionCounts.get(question)! > 1;
      } else if (canonicalSections.has(node)) {
        const canonical = canonicalSections.get(node)!;
        readingSection = `section:${canonical}`;
        questionDepth = node.depth;
        readingAmbiguous = canonicalCounts.get(canonical)! > 1;
      } else if (!questionDepth || node.depth <= questionDepth) {
        // Identical headings can be verified; translated ordinal positions cannot.
        readingSection = `heading:${text}`;
        questionDepth = 0;
        readingAmbiguous = false;
      }
    }
    if (node.type === 'heading') {
      readingParents = [...new Set(sectionStack.map(item => item.key).filter(key => key !== readingSection))].reverse();
      sectionStack.push({ depth: node.depth, key: readingSection });
    }
    const base = heading ?? `${section}--${createHash('sha256').update(identityRaw ?? raw).digest('hex').slice(0, 16)}`;
    const ordinal = occurrences.get(base) ?? 0; occurrences.set(base, ordinal + 1);
    const table = node.type === 'table' ? {
      header: source.slice(node.position!.start.offset, node.children[1]?.position?.start.offset ?? node.position!.end.offset),
      rows: node.children.slice(1).map(row => source.slice(row.position!.start.offset, row.position!.end.offset)), definitions,
    } : undefined;
    const fingerprint = createHash('sha256').update(raw).digest('hex').slice(0, 16);
    return { command: node.type === 'code' && node.lang !== 'mermaid' ? { value: node.value, language: node.lang ?? undefined } : undefined, readingParents, readingSection, readingAmbiguous, readingAnchor: `${readingSection}/content:${fingerprint}`, links: links(node as TextNode, linkDefinitions), table, id: ordinal ? `${base}-${ordinal}` : base, source: `${raw}\n\n${definitions}`, text, heading, navigationKey: node.type === 'heading' ? questionId(text) ? `question:${questionId(text)}` : canonicalSections.has(node) ? `section:${canonicalSections.get(node)}` : undefined : undefined, headingDepth: node.type === 'heading' ? node.depth : undefined, keepWithNext: node.type === 'heading' };
  });
}
