export type BookUnit = { id: string; keepWithNext?: boolean };
/** All sizes come from browser measurements, including margins in the measured wrapper. */
export function paginateMeasured<T extends BookUnit>(units: readonly T[], heights: readonly number[], capacity: number): T[][] {
  if (!units.length) return [[]];
  if (capacity <= 0 || heights.length !== units.length) return [[...units]];
  const pages: T[][] = []; let page: T[] = []; let used = 0;
  units.forEach((unit, index) => {
    const height = heights[index];
    const required = height + (unit.keepWithNext ? (heights[index + 1] ?? 0) : 0);
    if (page.length && used + required > capacity) { pages.push(page); page = []; used = 0; }
    page.push(unit); used += height;
  });
  if (page.length) pages.push(page);
  return pages;
}
