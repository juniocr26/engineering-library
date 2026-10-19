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
