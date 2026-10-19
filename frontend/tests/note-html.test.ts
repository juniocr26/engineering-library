import { test } from 'node:test';
import assert from 'node:assert/strict';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkRehype from 'remark-rehype';
import rehypeRaw from 'rehype-raw';
import { isolateNoteHtml } from '../lib/note-html.ts';
import type { Element, Root, RootContent } from 'hast';

async function render(source: string) {
  const processor = unified().use(remarkParse).use(remarkGfm).use(remarkRehype, { allowDangerousHtml: true }).use(rehypeRaw).use(isolateNoteHtml);
  return await processor.run(processor.parse(source));
}
function elements(tree: Root): Element[] {
  const stack: RootContent[] = [...tree.children]; const result: Element[] = [];
  while (stack.length) { const node = stack.pop()!; if (node.type === 'element') { result.push(node); stack.push(...node.children); } }
  return result;
}
test('mixed HTML preserves native formatting, arbitrary external images and GFM', async () => {
  const tree = await render('**Markdown** <em>HTML</em>\n\n<img src="https://new-host.example/badge.svg" alt="Badge">\n\n- [x] Task\n\n| A | B |\n|---|---|\n| x | y |');
  const nodes = elements(tree);
  for (const tag of ['strong', 'em', 'img', 'input', 'table']) assert.ok(nodes.some(node => node.tagName === tag));
  assert.equal(nodes.find(node => node.tagName === 'img')?.properties.src, 'https://new-host.example/badge.svg');
  assert.equal(nodes.find(node => node.tagName === 'input')?.properties.disabled, true);
  assert.equal(nodes.filter(node => node.tagName === 'note-embed').length, 0);
});
test('CSS, active HTML, SVG and unknown elements are preserved in opaque embeds', async () => {
  const source = '<div style="position:fixed">Rich <b>HTML</b></div>\n\n<svg onload="parent.pwned=1"><text>SVG</text></svg>\n\n<script>parent.pwned=1</script>\n\n<img src=x onerror="parent.pwned=1">\n\n<iframe src="https://example.com"></iframe>\n\n<a href="javascript:alert(1)">active link</a>\n\nRemaining **content**.';
  const nodes = elements(await render(source));
  assert.equal(nodes.filter(node => node.tagName === 'note-embed').length, 6);
  assert.ok(nodes.some(node => node.tagName === 'strong'));
  assert.ok(!nodes.some(node => ['script', 'svg', 'iframe'].includes(node.tagName)));
  const embeds = nodes.filter(node => node.tagName === 'note-embed').map(node => String(node.properties.source)).join('\n');
  for (const text of ['position:fixed', 'parent.pwned=1', 'onerror', '<svg', '<iframe', 'javascript:alert(1)']) assert.ok(embeds.includes(text));
});
