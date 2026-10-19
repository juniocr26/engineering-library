export const highlightColors = ['yellow', 'blue', 'pink', 'orange', 'purple', 'red', 'green'] as const;
export type HighlightColor = typeof highlightColors[number];
export type TextAnchor = { block: string; start: number; end: number; exact: string; prefix: string; suffix: string };
export type SavedHighlight = { id: number; color: HighlightColor; segments: TextAnchor[] };
export function textAnchor(block: string, text: string, start: number, end: number): TextAnchor {
  return { block, start, end, exact: text.slice(start, end), prefix: text.slice(Math.max(0, start - 48), start), suffix: text.slice(end, end + 48) };
}
/** Offsets are UTF-16 DOM text offsets. Relocation requires a unique contextual quote in the same logical block. */
export function resolveTextAnchor(anchor: TextAnchor, text: string): [number, number] | null {
  const matches = (start: number) => text.slice(Math.max(0, start - anchor.prefix.length), start) === anchor.prefix && text.slice(start + anchor.exact.length, start + anchor.exact.length + anchor.suffix.length) === anchor.suffix;
  if (text.slice(anchor.start, anchor.end) === anchor.exact && matches(anchor.start)) return [anchor.start, anchor.end];
  const candidates: number[] = [];
  for (let index = text.indexOf(anchor.exact); index >= 0; index = text.indexOf(anchor.exact, index + 1)) if (matches(index)) candidates.push(index);
  return candidates.length === 1 ? [candidates[0], candidates[0] + anchor.exact.length] : null;
}
export function toolbarPosition(rect: { left: number; top: number; bottom: number }, width: number, height: number) {
  return { left: Math.max(8, Math.min(rect.left, width - 320)), top: Math.max(8, Math.min(rect.top >= 60 ? rect.top - 54 : rect.bottom + 8, height - 60)) };
}
