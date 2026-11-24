import { DocumentationReader } from '../../components/documentation-reader';
import { markdownUnits } from '../../lib/markdown';
export default function CommandStressPage() {
  const long = 'docker compose exec -T frontend env PLAYWRIGHT_BROWSERS_PATH=/tmp/' + 'browser-path/'.repeat(25) + ' node tests/browser.cjs\n  echo "$HOME & <value>"';
  return <DocumentationReader project="engineering-library" document="synthetic.md" language="en" units={markdownUnits('```sh\necho ok\n```\n\n```sh\n' + long + '\n```\n\n```sh\n' + Array.from({ length: 100 }, (_, i) => `  echo line_${i}`).join('\n') + '\n```')} entries={[]} query=""/>;
}
