import { sourceLocation } from './source-links.ts';
import type { SourceReference, SourcePart } from './source-links';
/** Row offsets are content locations, independent of viewport-dependent pages. */
export type TablePart = { start: number; end: number; widths: number[]; maxHeight?: number };
export type TableMeasurement = { kind?: 'code'; rows: number[]; header: number; overhead: number; widths: number[]; safe: boolean };
export type TableBookUnit = { code?: SourceReference; codePart?: SourcePart; codeOrigin?: string; id: string; keepWithNext?: boolean; tablePart?: TablePart; tableOrigin?: string };
export function containsLocation(unit: TableBookUnit, location: string | undefined) {
  if (!location) return false;
  if (unit.id === location) return true;
  if (unit.code) {
    const origin = unit.codeOrigin ?? unit.id;
    if (location === origin) return !unit.codePart || unit.codePart.start === 0;
    const prefix = sourceLocation(unit.code, 0).replace(/0$/, '');
    if (!location.startsWith(prefix)) return false;
    const line = Number(location.slice(prefix.length)) - (unit.code.start ?? 1);
    return Number.isInteger(line) && line >= (unit.codePart?.start ?? 0) && line < (unit.codePart?.end ?? unit.code.lines?.length ?? 0);
  }
  const origin = unit.tableOrigin ?? unit.id;
  if (location === origin) return !unit.tablePart || unit.tablePart.start === 0;
  const prefix = `${origin}--row-`;
  if (!location.startsWith(prefix) || !unit.tablePart) return false;
  const row = Number(location.slice(prefix.length));
  return Number.isInteger(row) && row >= unit.tablePart.start && row < unit.tablePart.end;
}
/** Integrated with the book's measured flow. Each iteration consumes a row or flushes a nonempty page. */
export function paginateTables<T extends TableBookUnit>(units: readonly T[], heights: readonly number[], tables: ReadonlyMap<number, TableMeasurement>, capacity: (page: number) => number): T[][] {
  const pages: T[][] = []; let page: T[] = []; let used = 0;
  const flush = () => { if (page.length) { pages.push(page); page = []; used = 0; } };
  units.forEach((unit, index) => {
    const table = tables.get(index);
    if (!table || !table.rows.length) {
      const height = heights[index];
      const required = height + (unit.keepWithNext ? (tables.has(index + 1) ? tables.get(index + 1)!.header + tables.get(index + 1)!.overhead + tables.get(index + 1)!.rows[0] : heights[index + 1] ?? 0) : 0);
      if (page.length && used + required > capacity(pages.length)) flush();
      page.push(unit); used += height; return;
    }
    let start = 0;
    while (start < table.rows.length) {
      const fixed = table.header + table.overhead;
      if (page.length && used + fixed + table.rows[start] > capacity(pages.length)) flush();
      const room = Math.max(1, capacity(pages.length) - used);
      let end = start; let height = fixed;
      if (table.safe) while (end < table.rows.length && height + table.rows[end] <= room) height += table.rows[end++];
      const fallback = !table.safe || end === start;
      if (fallback) { end = table.safe ? start + 1 : table.rows.length; height = room; }
      if (table.kind === 'code') page.push({ ...unit, id: unit.code ? sourceLocation(unit.code, start + (unit.code.start ?? 1)) : unit.id, codeOrigin: unit.id, codePart: { start, end, ...(fallback ? { maxHeight: Math.max(1, room - fixed) } : {}) } });
      else page.push({ ...unit, id: start ? `${unit.id}--row-${start}` : unit.id, tableOrigin: unit.id, tablePart: { start, end, widths: table.widths, ...(fallback ? { maxHeight: Math.max(1, room - table.overhead) } : {}) } });
      used += height; start = end;
      if (start < table.rows.length) flush();
    }
  });
  flush(); return pages.length ? pages : [[]];
}
