import type { Element, Root, Text } from 'hast';

function textNodes(node: Element): Text[] {
  // Inline code and image alternatives are never prose. Links and emphasis can
  // contain prose, but their attributes (URLs, IDs, etc.) are never changed.
  return node.children.flatMap(child => child.type === 'text' ? [child]
    : child.type === 'element' && child.tagName !== 'code' ? textNodes(child) : []);
}

/** Display-only sentence casing for the h1–h3 styled in manuscript cursive.
 * Preserve the first letter's case, lowercase the rest, and leave monospace
 * inline code, source text, search indexes and canonical unit IDs untouched.
 */
export function cursiveHeadings() {
  return (tree: Root) => {
    const visit = (node: Root | Element) => {
      if (node.type === 'element' && /^h[123]$/u.test(node.tagName)) {
        let firstLetter = true;
        for (const text of textNodes(node)) {
          text.value = text.value.replace(/\p{L}/gu, letter => {
            if (firstLetter) { firstLetter = false; return letter; }
            return letter.toLowerCase();
          });
        }
        return;
      }
      for (const child of node.children) if (child.type === 'element') visit(child);
    };
    visit(tree);
  };
}
