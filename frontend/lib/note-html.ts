import { toHtml } from 'hast-util-to-html';
import type { Root, Element, RootContent } from 'hast';
import { noteUrl } from './note-policy.ts';

// Native reader elements remain interactive. Everything else is preserved in an
// opaque sandbox, including CSS, inline SVG, event handlers and embedded documents.
const nativeTags = new Set('a abbr b bdi bdo blockquote br caption cite code col colgroup dd del details dfn div dl dt em figcaption figure h1 h2 h3 h4 h5 h6 hr i img input kbd li mark ol p pre q rp rt ruby s samp small span strong sub summary sup table tbody td th thead time tr u ul var wbr'.split(' '));
const nativeProperties = new Set('align alt checked className colSpan dateTime dir disabled height href lang open reversed rowSpan scope span start title type value width'.split(' '));
export function isolateNoteHtml() {
  return (tree: Root) => {
    const stack: (Root | Element)[] = [tree];
    while (stack.length) {
      const parent = stack.pop()!;
      parent.children = parent.children.map((child): RootContent => {
        if (child.type !== 'element') return child;
        const unsafe = !nativeTags.has(child.tagName) || Object.keys(child.properties).some(key => !nativeProperties.has(key) && key !== 'src' && !key.startsWith('aria') && !key.startsWith('data')) ||
          (['src', 'href'].some(key => typeof child.properties[key] === 'string' && child.properties[key] && !noteUrl(String(child.properties[key]), key))) ||
          (child.tagName === 'input' && child.properties.type !== 'checkbox');
        if (unsafe) return { type: 'element', tagName: 'note-embed', properties: { source: toHtml(child) }, children: [] };
        for (const key of ['src', 'href']) if (typeof child.properties[key] === 'string') child.properties[key] = noteUrl(child.properties[key], key);
        if (child.tagName === 'input') child.properties.disabled = true;
        stack.push(child);
        return child;
      }) as typeof parent.children;
    }
  };
}
