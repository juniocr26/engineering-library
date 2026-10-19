import type { TocEntry } from './documentation.ts';
import type { MarkdownUnit } from './markdown.ts';
import type { Root, Element } from 'hast';

/** Only an exact structural prefix is redundant. Dates, ADRs and Q IDs survive. */
export function headingTitle(title: string, number: string): string {
  return title.startsWith(`${number} `) ? title.slice(number.length + 1) : title;
}

/** Resolve by document and original AST anchor, never by display text or page. */
export function numberHeadingUnits(units: MarkdownUnit[], entries: TocEntry[], document: string): MarkdownUnit[] {
  const sections = new Map(entries.filter(e => e.documentId === document).map(e => [e.anchor, e]));
  const title = entries.find(e => e.id === document);
  let first = true;
  return units.map(unit => {
    if (unit.heading === undefined) return unit;
    const entry = sections.get(unit.id) ?? (first && unit.headingDepth === 1 ? title : undefined);
    first = false;
    return entry ? { ...unit, navigationNumber: entry.number, navigationId: entry.id } : unit;
  });
}

/** Run after typography; leave source, links, inline markup and anchor IDs intact. */
export function numberedHeading(number?: string) {
  return () => (tree: Root) => {
    if (!number) return;
    const visit = (node: Root | Element) => {
      if (node.type === 'element' && /^h[1-6]$/.test(node.tagName)) {
        const plain = (element: Root | Element): string => element.children.map(child => child.type === 'text' ? child.value : child.type === 'element' ? plain(child) : '').join('');
        let remaining = plain(node).startsWith(`${number} `) ? number.length + 1 : 0;
        const strip = (element: Root | Element) => {
          for (const child of element.children) {
            if (child.type === 'text' && remaining) {
              const count = Math.min(remaining, child.value.length);
              child.value = child.value.slice(count); remaining -= count;
            } else if (child.type === 'element') strip(child);
          }
        };
        strip(node);
        node.children.unshift({ type: 'text', value: `${number} ` });
        return;
      }
      for (const child of node.children) if (child.type === 'element') visit(child);
    };
    visit(tree);
  };
}
