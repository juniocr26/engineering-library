import { containsLocation, type TableBookUnit } from './table-pagination.ts';

type ReadingUnit = TableBookUnit & { readingAnchor?: string };

/** Translation keys describe Markdown structure without changing persisted bookmark IDs. */
export function translatedLocation(previous: readonly ReadingUnit[], next: readonly ReadingUnit[], anchor: string | undefined): string | undefined {
  if (!next.length) return undefined;
  if (next.some(unit => containsLocation(unit, anchor))) return anchor;
  const index = previous.findIndex(unit => containsLocation(unit, anchor) || !!anchor?.startsWith(`${unit.id}--row-`));
  const origin = previous[index];
  if (origin?.readingAnchor) {
    const equivalent = next.find(unit => unit.readingAnchor === origin.readingAnchor);
    if (equivalent) {
      const row = anchor?.match(/--row-(\d+)$/)?.[0];
      return row ? `${equivalent.id}${row}` : equivalent.id;
    }
    const section = origin.readingAnchor.split('/')[0];
    const nearest = next.filter(unit => unit.readingAnchor?.startsWith(`${section}/`));
    if (nearest.length) return nearest[nearest.length - 1].id;
  }
  const progress = index < 0 || previous.length < 2 ? 0 : index / (previous.length - 1);
  return next[Math.round(progress * (next.length - 1))].id;
}
