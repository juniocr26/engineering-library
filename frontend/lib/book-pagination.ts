import { paginateTables, type TableBookUnit, type TableMeasurement } from './table-pagination.ts';
export type BookUnit = TableBookUnit;
/** All sizes come from browser measurements, including margins in the measured wrapper.
 * Table measurements extend the same flow with safe row boundaries and repeated headers.
 */
export function paginateMeasured<T extends BookUnit>(units: readonly T[], heights: readonly number[], capacity: number | ((page: number) => number), tables: ReadonlyMap<number, TableMeasurement> = new Map()): T[][] {
  if (!units.length) return [[]];
  const available = (page: number) => typeof capacity === 'function' ? capacity(page) : capacity;
  if (available(0) <= 0 || heights.length !== units.length) return [[...units]];
  return paginateTables(units, heights, tables, available);
}

/** Compare measured fragments as well as source identity. Equal IDs alone do not
 * imply equal content, row boundaries, column widths or code continuations. */
export function samePagination<T extends BookUnit>(previous: readonly (readonly T[])[], next: readonly (readonly T[])[]): boolean {
  return previous.length === next.length && previous.every((page, index) => page.length === next[index].length && page.every((unit, offset) => {
    const other = next[index][offset];
    if (unit === other) return true;
    const keys = Object.keys(unit) as (keyof T)[];
    return keys.length === Object.keys(other).length && keys.every(key => {
      if (key === 'tablePart') {
        const a = unit.tablePart; const b = other.tablePart;
        return a === b || !!a && !!b && a.start === b.start && a.end === b.end && a.maxHeight === b.maxHeight && a.widths.length === b.widths.length && a.widths.every((width, i) => width === b.widths[i]);
      }
      if (key === 'codePart') {
        const a = unit.codePart; const b = other.codePart;
        return a === b || !!a && !!b && a.start === b.start && a.end === b.end && a.maxHeight === b.maxHeight;
      }
      return Object.is(unit[key], other[key]);
    });
  }));
}
