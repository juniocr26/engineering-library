import hljs from 'highlight.js/lib/core';
import rust from 'highlight.js/lib/languages/rust';
import go from 'highlight.js/lib/languages/go';
import python from 'highlight.js/lib/languages/python';
import ruby from 'highlight.js/lib/languages/ruby';
import javascript from 'highlight.js/lib/languages/javascript';
import typescript from 'highlight.js/lib/languages/typescript';
import java from 'highlight.js/lib/languages/java';
import csharp from 'highlight.js/lib/languages/csharp';
import php from 'highlight.js/lib/languages/php';
import bash from 'highlight.js/lib/languages/bash';
import sql from 'highlight.js/lib/languages/sql';
for (const [name, grammar] of Object.entries({ rust, go, python, ruby, javascript, typescript, java, csharp, php, bash, sql })) hljs.registerLanguage(name, grammar);
/** Split highlighted HTML at original newlines while reopening syntax spans across boundaries. */
export function highlightedLines(source: string, language: string): string[] {
  const html = hljs.getLanguage(language) ? hljs.highlight(source, { language, ignoreIllegals: true }).value : source.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
  const stack: string[] = []; const result: string[] = []; let line = '';
  for (const token of html.split(/(<span[^>]*>|<\/span>|\n)/)) {
    if (token === '\n') { result.push(line + '</span>'.repeat(stack.length)); line = stack.join(''); }
    else { line += token; if (token.startsWith('<span')) stack.push(token); else if (token === '</span>') stack.pop(); }
  }
  result.push(line + '</span>'.repeat(stack.length)); return result;
}
