export function pageNumbers(current: number, total: number): (number | 'ellipsis')[] {
  const pages = Math.max(1, Math.floor(total));
  const page = Math.max(1, Math.min(pages, Math.floor(current)));
  const visible = new Set([1, pages]);
  for (let n = Math.max(1, page - 1); n <= Math.min(pages, page + 1); n++) visible.add(n);
  if (page <= 2) visible.add(Math.min(3, pages));
  if (page >= pages - 1) visible.add(Math.max(1, pages - 2));
  const result: (number | 'ellipsis')[] = [];
  let previous = 0;
  for (const n of [...visible].sort((a, b) => a - b)) {
    if (n - previous === 2) result.push(previous + 1);
    else if (n - previous > 2) result.push('ellipsis');
    result.push(n); previous = n;
  }
  return result;
}
