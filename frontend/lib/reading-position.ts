import { containsLocation, type TableBookUnit } from './table-pagination.ts';

type ReadingUnit = TableBookUnit & { readingAnchor?: string; readingParents?: string[]; readingSection?: string; readingAmbiguous?: boolean };
export type TranslationResult = { anchor?: string; limitation?: 'ambiguous-section' | 'missing-section' | 'document-progress' };

/** Canonical document/project scope is owned by the keyed reader. Never infer
 * translated section equivalence from heading or block ordinals. */
export function resolveTranslatedLocation(previous: readonly ReadingUnit[], next: readonly ReadingUnit[], anchor: string | undefined): TranslationResult {
  if (!next.length) return {};
  const index = previous.findIndex(unit => containsLocation(unit, anchor) || !!anchor?.startsWith(`${unit.id}--row-`));
  const origin = previous[index];
  if (origin?.readingSection) {
    const section = next.filter(unit => unit.readingSection === origin.readingSection);
    const ambiguous = origin.readingAmbiguous || section.some(unit => unit.readingAmbiguous);
    const parent = origin.readingParents?.flatMap(key => {
      const candidates = next.filter(unit => unit.readingSection === key);
      return candidates.length && !candidates.some(unit => unit.readingAmbiguous) ? [candidates[0]] : [];
    })[0];
    if (ambiguous) return { anchor: parent?.id ?? next[0].id, limitation: 'ambiguous-section' };
    if (section.length) {
      // A content hash or source location verifies a block; its ordinal does not.
      const direct = section.find(unit => containsLocation(unit, anchor));
      if (direct) return { anchor };
      const exact = section.filter(unit => unit.readingAnchor && unit.readingAnchor === origin.readingAnchor);
      if (exact.length === 1) {
        const row = anchor?.match(/--row-\d+$/)?.[0];
        return { anchor: row ? `${exact[0].id}${row}` : exact[0].id };
      }
      return { anchor: section[0].id };
    }
    // Missing numbered questions must never silently become a neighboring Q ID.
    if (parent || origin.readingSection.startsWith('question:')) return { anchor: parent?.id ?? next[0].id, limitation: 'missing-section' };
  }
  if (next.some(unit => containsLocation(unit, anchor))) return { anchor };
  // Compatibility for callers supplying an explicit canonical block key.
  if (!origin?.readingSection && origin?.readingAnchor) {
    const exact = next.filter(unit => unit.readingAnchor === origin.readingAnchor);
    if (exact.length === 1) {
      const row = anchor?.match(/--row-\d+$/)?.[0];
      return { anchor: row ? `${exact[0].id}${row}` : exact[0].id };
    }
  }
  const progress = index < 0 || previous.length < 2 ? 0 : index / (previous.length - 1);
  return { anchor: next[Math.round(progress * (next.length - 1))].id, limitation: 'document-progress' };
}

export function translatedLocation(previous: readonly ReadingUnit[], next: readonly ReadingUnit[], anchor: string | undefined): string | undefined {
  return resolveTranslatedLocation(previous, next, anchor).anchor;
}
