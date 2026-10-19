const table = '| Component | Responsibility | Failure policy | Owner | Storage | Trace | Region | Recovery |\n|---|---|---|---|---|---|---|---|\n' + Array.from({ length: 35 }, (_, i) => `| Worker ${i + 1} | Persist a synthetic engineering event and emit a trace identifier | Retry transient failures with bounded exponential backoff and jitter; retain the original event identifier | Platform engineering | PostgreSQL durable transaction | synthetic-trace-${i + 1} | Local development | Replay from the original event after validation |`).join('\n');
const diagram = '```mermaid\nflowchart LR\n  Reader --> Validation\n  Validation --> PostgreSQL\n```';
const code = '```typescript\nconst persist = (body: string) => ({ body, revision: 1 });\nconsole.log(persist("ação 📚"));\n```';
export const noteDemos = [
  ['Plain paragraphs', 'A reader records why a decision was made. The note belongs to a stable passage in the document.\n\nRemoving its color preserves the reasoning for a later review.'],
  ['Unicode', 'Persistência, revisão e observação: ação, coração, São Paulo.\n\n📚 🔍 ✅ — 日本語 — Ελληνικά — café.'],
  ['Typography', '# Decision record\n## Context\n**Durable notes** preserve *reasoning* alongside ~~temporary state~~ stable anchors.'],
  ['Lists', '1. Validate ownership\n2. Save Markdown\n\n- Keep the original source\n- Resolve the passage\n\n- [x] Store Unicode\n- [ ] Review the next revision'],
  ['Quotes and links', '> A recoverable failure should leave the draft intact.\n\n---\n\nRead the [PostgreSQL documentation](https://www.postgresql.org/docs/).'],
  ['Code', 'Use `revision` as a display value. This code is never executed.\n\n' + code],
  ['Small table', '| Operation | Preserved |\n|---|---|\n| Remove color | Note |\n| Delete note | Highlight |'],
  ['Wide table', '# Worker responsibilities\n\n' + table],
  ['Approved image', '## Library illustration\n\n![Library writer](/assets/writer-library.jpg)'],
  ['Approved SVG', '## Persistence boundary\n\n![Reader to database](/assets/notes/persistence.svg)'],
  ['Flowchart', '## Save path\n\n' + diagram],
  ['Complex diagram', '```mermaid\nflowchart TD\n  Input --> Validate\n  Validate --> Ownership\n  Ownership --> Anchor\n  Anchor --> Transaction\n  Transaction --> Database\n  Database --> Response\n  Response --> Reader\n  Validate --> Error\n  Error --> Draft\n  Draft --> Input\n```'],
  ['Long mixed note', '# Engineering review 📚\n\n' + Array.from({ length: 12 }, (_, i) => `## Review ${i + 1}\n\nA durable annotation separates presentation from persistence. Revisit its text anchor after layout changes.\n\n${code}\n\n`).join('\n') + table + '\n\n' + diagram + '\n\n![Persistence](/assets/notes/persistence.svg)'],
  ['Colored passage', '# Colored annotation\n\nThis note remains attached to its logical passage while its green color is changed.'],
  ['Color removed', '# Independent annotation\n\nThe original green highlight was deliberately removed. This note and its indicator remain.'],
  ['Portuguese isolation', '# Anotação em português\n\nEsta nota pertence somente ao trecho em português. A troca de idioma não traduz nem duplica anotações.'],
] as const;
