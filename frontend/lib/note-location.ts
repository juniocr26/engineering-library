import type { TextAnchor } from './text-anchors';

/** A shared passage may contain distinct legacy notes; never choose one by text alone. */
export function noteAtSelection<T extends { highlight_id: number | null; segments: TextAnchor[] }>(notes: T[], segments: TextAnchor[], highlightId?: number): T | undefined {
  const attached = highlightId === undefined ? undefined : notes.find(note => note.highlight_id === highlightId);
  if (attached) return attached;
  const independent = notes.filter(note => note.highlight_id === null && note.segments.length === segments.length && note.segments.every((part, index) => part.block === segments[index].block && part.start === segments[index].start && part.end === segments[index].end && part.exact === segments[index].exact));
  return independent.length === 1 ? independent[0] : undefined;
}
