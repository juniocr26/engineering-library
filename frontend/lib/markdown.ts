import type { RootContent, ListItem } from 'mdast';
import { createHash } from 'node:crypto';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import GithubSlugger from 'github-slugger';
import type { SourceReference, SourcePart } from './source-links';
import type { TablePart } from './table-pagination';

export type MarkdownUnit = { readingAnchor?: string; links?: string[]; references?: SourceReference[]; code?: SourceReference; codePart?: SourcePart; codeOrigin?: string; id: string; source: string; text: string; heading?: string; keepWithNext?: boolean; tableOrigin?: string; tablePart?: TablePart; table?: { header: string; rows: string[]; definitions: string } };
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
  let sectionIndex = 0;
  let blockIndex = 0;
  return tree.children.filter(node => node.type !== 'definition' && node.type !== 'html').flatMap<{ node: RootContent | ListItem; identityRaw: string | undefined }>(node => {
    // Leave ordinary lists and their historic bookmark anchors intact.
    const sourceList = node.type === 'list' && links(node as TextNode, linkDefinitions).some(href => /\.(?:rs|go|py|rb|[jt]sx?|java|cs|php|sh|sql|json|ya?ml|toml)(?:#.*)?$/i.test(href));
    return sourceList && node.type === 'list' ? node.children.map((child, index) => ({ node: child, identityRaw: index === 0 ? source.slice(node.position!.start.offset, node.position!.end.offset) : undefined })) : [{ node, identityRaw: undefined }];
  }).map(({ node, identityRaw }) => {
    const raw = source.slice(node.position!.start.offset, node.position!.end.offset);
    const text = plain(node as TextNode);
    const heading = node.type === 'heading' ? slugger.slug(text) : undefined;
    if (heading !== undefined) { section = heading; sectionIndex += 1; blockIndex = 0; }
    const base = heading ?? `${section}--${createHash('sha256').update(identityRaw ?? raw).digest('hex').slice(0, 16)}`;
    const ordinal = occurrences.get(base) ?? 0; occurrences.set(base, ordinal + 1);
    const table = node.type === 'table' ? {
      header: source.slice(node.position!.start.offset, node.children[1]?.position?.start.offset ?? node.position!.end.offset),
      rows: node.children.slice(1).map(row => source.slice(row.position!.start.offset, row.position!.end.offset)), definitions,
    } : undefined;
    return { readingAnchor: `section-${sectionIndex}/block-${blockIndex++}`, links: links(node as TextNode, linkDefinitions), table, id: ordinal ? `${base}-${ordinal}` : base, source: `${raw}\n\n${definitions}`, text, heading, keepWithNext: node.type === 'heading' };
  });
}
