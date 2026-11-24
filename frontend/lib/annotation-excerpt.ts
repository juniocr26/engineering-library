import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import { decodeNamedCharacterReference } from 'decode-named-character-reference';

type Node = { type: string; value?: string; alt?: string; children?: Node[] };
const decode = (value: string) => value.replace(/&(#x[\da-f]+|#\d+|[a-z][\da-z]+);/gi, (match, entity: string) => {
  if (!entity.startsWith('#')) return decodeNamedCharacterReference(entity) || match;
  const number = entity[1].toLowerCase() === 'x' ? parseInt(entity.slice(2), 16) : Number(entity.slice(1));
  return number > 0 && number <= 0x10ffff ? String.fromCodePoint(number) : '';
});
function plain(node: Node): string {
  if (['definition', 'footnoteDefinition'].includes(node.type)) return '';
  if (node.type === 'html') return decode((node.value ?? '').replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1>/gi, '').replace(/<[^>]*>/g, ' '));
  if (node.type === 'image' || node.type === 'imageReference') return node.alt ?? '';
  if (node.value !== undefined) return node.value;
  const separator = ['root', 'list', 'table', 'tableRow', 'blockquote', 'listItem'].includes(node.type) ? ' ' : '';
  return (node.children ?? []).map(plain).join(separator);
}
/** Parse without executing HTML, then count user-visible graphemes, including ZWJ emoji. */
export function noteExcerpt(markdown: string) {
  const readable = plain(unified().use(remarkParse).use(remarkGfm).parse(markdown) as Node).replace(/\s+/gu, ' ').trim();
  const characters: string[] = [];
  for (const item of new Intl.Segmenter(undefined, { granularity: 'grapheme' }).segment(readable)) {
    characters.push(item.segment);
    if (characters.length > 100) break;
  }
  return { text: characters.slice(0, 100).join('') + (characters.length > 100 ? '…' : ''), truncated: characters.length > 100 };
}
