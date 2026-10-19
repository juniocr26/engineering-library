import type { Element, Root, Text } from 'hast';

function textNodes(node: Element): Text[] {
  // Inline code and image alternatives are never prose. Links and emphasis can
  // contain prose, but their attributes (URLs, IDs, etc.) are never changed.
  return node.children.flatMap(child => child.type === 'text' ? [child]
    : child.type === 'element' && child.tagName !== 'code' ? textNodes(child) : []);
}

/** A stateful formatter keeps sentence context across inline emphasis and links.
 * Only uppercase prose words change; mixed case and technical literals survive.
 */
export function createCursiveNormalizer() {
  let firstWord = true;
  return (text: string): string => text.replace(/\S+/gu, token => {
    // Commands, paths, identifiers and calls are technical literals, even when
    // authors did not wrap them in inline code.
    if (/[/\\_`=]|^--|\w\.\w|\w\(/u.test(token)) return token;
    return token.replace(/\p{L}[\p{L}\p{M}]*/gu, word => {
      const initial = firstWord;
      firstWord = false;
      if (word !== word.toUpperCase()) return word;
      const lower = word.toLowerCase();
      return initial ? lower.charAt(0).toUpperCase() + lower.slice(1) : lower;
    });
  });
}

/** Presentation only: never use this value for IDs, URLs, search or metadata. */
export function normalizeCursiveLabel(text: string): string {
  return createCursiveNormalizer()(text);
}

export function cursiveHeadings() {
  return (tree: Root) => {
    const visit = (node: Root | Element) => {
      if (node.type === 'element' && /^h[123]$/u.test(node.tagName)) {
        const normalize = createCursiveNormalizer();
        for (const text of textNodes(node)) text.value = normalize(text.value);
        return;
      }
      for (const child of node.children) if (child.type === 'element') visit(child);
    };
    visit(tree);
  };
}
