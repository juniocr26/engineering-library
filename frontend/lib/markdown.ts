import { createHash } from 'node:crypto';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import GithubSlugger from 'github-slugger';
import type { TablePart } from './table-pagination';

export type MarkdownUnit = { id: string; source: string; text: string; heading?: string; keepWithNext?: boolean; tableOrigin?: string; tablePart?: TablePart; table?: { header: string; rows: string[]; definitions: string } };
type TextNode = { value?: string; alt?: string; children?: TextNode[] };
const plain = (node: TextNode): string => node.value ?? node.alt ?? node.children?.map(plain).join('') ?? '';

/** Parse Markdown syntax before dividing into semantic, content-addressed book units. */
export function markdownUnits(source: string): MarkdownUnit[] {
  const tree = unified().use(remarkParse).use(remarkGfm).parse(source);
  const definitions = tree.children.filter(node => node.type === 'definition').map(node => source.slice(node.position!.start.offset, node.position!.end.offset)).join('\n');
  const slugger = new GithubSlugger();
  const occurrences = new Map<string, number>();
  let section = 'start';
  return tree.children.filter(node => node.type !== 'definition' && node.type !== 'html').map(node => {
    const raw = source.slice(node.position!.start.offset, node.position!.end.offset);
    const text = plain(node as TextNode);
    const heading = node.type === 'heading' ? slugger.slug(text) : undefined;
    if (heading !== undefined) section = heading;
    const base = heading ?? `${section}--${createHash('sha256').update(raw).digest('hex').slice(0, 16)}`;
    const ordinal = occurrences.get(base) ?? 0; occurrences.set(base, ordinal + 1);
    const table = node.type === 'table' ? {
      header: source.slice(node.position!.start.offset, node.children[1]?.position?.start.offset ?? node.position!.end.offset),
      rows: node.children.slice(1).map(row => source.slice(row.position!.start.offset, row.position!.end.offset)), definitions,
    } : undefined;
    return { table, id: ordinal ? `${base}-${ordinal}` : base, source: `${raw}\n\n${definitions}`, text, heading, keepWithNext: node.type === 'heading' };
  });
}
