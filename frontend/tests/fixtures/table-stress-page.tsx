import { markdownUnits } from '../../lib/markdown';
import { syntheticTable } from './tables';
import TableStressClient from './table-stress-client';
export default async function StressPage({ searchParams }: { searchParams: Promise<Record<string, string>> }) {
  const params = await searchParams;
  const language = params.lang === 'pt-BR' ? 'pt-BR' : 'en';
  const count = Math.min(500, Number(params.rows) || 30);
  const source = syntheticTable(count, Number(params.columns) || 10, language);
  const units = markdownUnits(source);
  if (params.before) units.unshift(...markdownUnits('Fictional paragraph before the table.'));
  if (params.oversized) units[0].table!.rows[0] = units[0].table!.rows[0].replace('Fictional description.', 'Fictional description. '.repeat(250));
  if (params.oversized) units[0].source = `${units[0].table!.header}${units[0].table!.rows.join('\n')}`;
  return <TableStressClient key={`${count}/${language}/${params.oversized}`} units={units} language={language} location={params.row ? `${units[0].id}--row-${params.row}` : undefined}/>;
}
