import type { TocEntry } from './documentation';
import type { Language } from './i18n';

export type ReadingEntry = { id: string | null; href: string };

/** null identifies the contents; IDs and order come exclusively from the canonical TOC. */
export function getReadingSequence(project: string, language: Language, entries: readonly TocEntry[]): ReadingEntry[] {
  return [
    { id: null, href: `/projects/${encodeURIComponent(project)}?lang=${language}` },
    ...entries.filter((entry): entry is TocEntry & { href: string } => !!entry.href && !entry.documentId).map(({ id, href }) => ({ id, href })),
  ];
}

export function getPreviousDocument(sequence: readonly ReadingEntry[], current: string | null) {
  const index = sequence.findIndex(entry => entry.id === current);
  return index > 0 ? sequence[index - 1] : undefined;
}

export function getNextDocument(sequence: readonly ReadingEntry[], current: string | null) {
  const index = sequence.findIndex(entry => entry.id === current);
  return index >= 0 ? sequence[index + 1] : undefined;
}

export function getFirstDocument(sequence: readonly ReadingEntry[]) {
  return sequence.find(entry => entry.id !== null);
}

export function getLastDocument(sequence: readonly ReadingEntry[]) {
  return sequence.findLast(entry => entry.id !== null);
}

/** Resolve route intent only. Physical pagination belongs to BookReader. */
export function readingNeighbors(sequence: readonly ReadingEntry[], current: string | null) {
  const previous = getPreviousDocument(sequence, current);
  return {
    previous: previous ? `${previous.href}&edge=end` : undefined,
    next: getNextDocument(sequence, current)?.href,
    previousIsContents: previous?.id === null,
  };
}
