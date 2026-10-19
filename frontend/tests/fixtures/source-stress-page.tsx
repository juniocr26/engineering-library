import { DocumentationReader } from '../../components/documentation-reader';
import type { MarkdownUnit } from '../../lib/markdown';
export default function SourceStressPage() {
  const ref = { id: 'source-stress', path: 'synthetic/continuous.rs', href: './continuous.rs', language: 'rust', status: 'available' as const, lines: Array.from({ length: 200 }, (_, i) => i === 170 ? '    let marker_171 = "needle_171";' : i === 20 ? `    let long_line = "${'x'.repeat(400)}";` : `    let value_${i + 1} = ${i}; // line ${i + 1}`) };
  const repeated = { ...ref, id: 'source-stress-repeat' };
  const units: MarkdownUnit[] = [{ id: 'intro', source: '## Continuous source\n\n[synthetic/continuous.rs](./continuous.rs) and [same file again](./continuous.rs)', text: 'Continuous source', links: [ref.href, ref.href], references: [ref, repeated] }, { id: 'after', source: 'After the complete source.', text: 'After the complete source.' }];
  return <DocumentationReader project="engineering-library" document="synthetic.md" language="en" units={units} entries={[]} query="needle_171"/>;
}
