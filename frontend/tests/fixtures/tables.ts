/** Fictional values only. No environment files or project configuration are read. */
export function syntheticTable(count: number, columns = 10, language = 'en') {
  const headers = Array.from({ length: columns }, (_, i) => i === 0 ? 'Synthetic variable identifier' : `${language === 'en' ? 'Detailed column heading' : 'Cabeçalho detalhado da coluna'} ${i}`);
  return `| ${headers.join(' | ')} |\n| ${headers.map(() => '---').join(' | ')} |\n` + Array.from({ length: count }, (_, row) => {
    const id = `FICTIONAL_ENVIRONMENT_VARIABLE_FOR_PAGINATION_${String(row).padStart(4, '0')}`;
    return `| ${Array.from({ length: columns }, (_, col) => col === 0 ? `\`${id}\`` : col === 1 ? `${language === 'en' ? 'Fictional description.' : 'Descrição fictícia.'} `.repeat(1 + row % 5) : col === 2 ? `\`example-only-${row}-${'abcdef'.repeat(15)}\`` : col === 3 ? `[Example ${row}](https://example.invalid/item/${row})` : `sample-${row}-${col}`).join(' | ')} |`;
  }).join('\n');
}
export const tableFixtures = [5, 30, 200, 500].map((rows, index) => ({ rows, columns: [8, 10, 12, 10][index], source: syntheticTable(rows, [8, 10, 12, 10][index]) }));
