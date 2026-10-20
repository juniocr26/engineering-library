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
  ['Approved image', '## Library illustration\n\n![Library writer](/assets/writer-library.jpg)\n\n![External SVG](https://www.w3.org/Icons/w3c_home.svg)\n\n![Missing illustration](/assets/intentional-missing-image.png)'],
  ['Approved SVG', '## Persistence boundary\n\n![Reader to database](/api/shared-assets/diagrams/reader-storage.svg)'],
  ['Flowchart', '## Save path\n\n' + diagram],
  ['Sequence diagram', '```mermaid\nsequenceDiagram\n  Reader->>Rails: Save note\n  Rails->>PostgreSQL: Persist anchor\n  PostgreSQL-->>Reader: Saved\n```'],
  ['Long mixed note', '# Engineering review 📚\n\n' + Array.from({ length: 12 }, (_, i) => `## Review ${i + 1}\n\nA durable annotation separates presentation from persistence. Revisit its text anchor after layout changes.\n\n${code}\n\n`).join('\n') + table + '\n\n' + diagram + '\n\n![Persistence](/assets/notes/persistence.svg)'],
  ['Short note', 'Review this decision.'],
  ['Color removed', '# Independent annotation\n\nThe original highlight color was deliberately removed. This note and its indicator remain.'],
] as const;

/** Localized fixture prose; code, identifiers and media URLs remain shared. */
export function localizedDemoBody(body: string, language: 'en' | 'pt-BR') {
  if (language === 'en') return body;
  const translations: [string, string][] = [
    ['Component', 'Componente'], ['Responsibility', 'Responsabilidade'], ['Failure policy', 'Política de falha'], ['Owner', 'Responsável'], ['Storage', 'Armazenamento'], ['Region', 'Região'], ['Recovery', 'Recuperação'],
    ['Local development', 'Desenvolvimento local'], ['Platform engineering', 'Engenharia de plataforma'],
    ['Persist a synthetic engineering event and emit a trace identifier', 'Persistir um evento sintético de engenharia e emitir um identificador de rastreamento'],
    ['Retry transient failures with bounded exponential backoff and jitter; retain the original event identifier', 'Repetir falhas transitórias com espera exponencial limitada e jitter; manter o identificador original'],
    ['Replay from the original event after validation', 'Reprocessar a partir do evento original após validação'],
    ['A reader records why a decision was made. The note belongs to a stable passage in the document.', 'O leitor registra o motivo de uma decisão. A nota pertence a um trecho estável do documento.'],
    ['Removing its color preserves the reasoning for a later review.', 'Remover a cor preserva o raciocínio para revisão posterior.'],
    ['Review this decision.', 'Revisar esta decisão.'], ['Decision record', 'Registro de decisão'], ['Context', 'Contexto'],
    ['Durable notes', 'Notas persistentes'], ['preserve', 'preservam'], ['reasoning', 'raciocínio'], ['temporary state', 'estado temporário'], ['stable anchors', 'âncoras estáveis'],
    ['Validate ownership', 'Validar propriedade'], ['Save Markdown', 'Salvar Markdown'], ['Keep the original source', 'Manter a fonte original'], ['Resolve the passage', 'Localizar o trecho'],
    ['Store Unicode', 'Persistir Unicode'], ['Review the next revision', 'Revisar a próxima versão'],
    ['A recoverable failure should leave the draft intact.', 'Uma falha recuperável deve manter o rascunho intacto.'],
    ['Read the', 'Consulte a'], ['documentation', 'documentação'], ['Use `revision` as a display value. This code is never executed.', 'Use `revision` como valor de exibição. Este código nunca é executado.'],
    ['Operation', 'Operação'], ['Preserved', 'Preservado'], ['Remove color', 'Remover cor'], ['Delete note', 'Excluir nota'], ['Highlight', 'Destaque'], ['Note', 'Nota'],
    ['Worker responsibilities', 'Responsabilidades dos workers'], ['Library illustration', 'Ilustração da biblioteca'], ['Persistence boundary', 'Limite de persistência'], ['Save path', 'Fluxo de gravação'],
    ['Engineering review', 'Revisão de engenharia'], ['Review ', 'Revisão '],
    ['A durable annotation separates presentation from persistence. Revisit its text anchor after layout changes.', 'Uma anotação persistente separa apresentação de armazenamento. Confira sua âncora textual após mudanças no layout.'],
    ['Independent annotation', 'Anotação independente'], ['The original highlight color was deliberately removed. This note and its indicator remain.', 'A cor do destaque original foi removida explicitamente. Esta nota e seu indicador permanecem.'],
  ];
  return translations.reduce((value, [from, to]) => value.replaceAll(from, to), body);
}
