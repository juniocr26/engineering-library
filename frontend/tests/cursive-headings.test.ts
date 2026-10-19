import test from 'node:test';
import assert from 'node:assert/strict';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cursiveHeadings } from '../lib/cursive-headings.ts';
import { markdownUnits } from '../lib/markdown.ts';

function render(source: string) {
  return renderToStaticMarkup(createElement(Markdown, {
    remarkPlugins: [remarkGfm], rehypePlugins: [cursiveHeadings],
  }, source));
}

for (const [source, expected] of [
  ['ARQUITETURA E FLUXO', 'Arquitetura e fluxo'],
  ['RULES DE SOBRESCRITA DO FILESYSTEM', 'Rules de sobrescrita do filesystem'],
  ['DESENVOLVIMENTO DO PROJETO', 'Desenvolvimento do projeto'],
  ['arquitetura e fluxo', 'arquitetura e fluxo'],
  ['3. RULES DE SOBRESCRITA no filesystem', '3. Rules de sobrescrita no filesystem'],
  ['3. rules DE SOBRESCRITA no filesystem', '3. rules de sobrescrita no filesystem'],
  ['2. Arquitetura E FLUXO', '2. Arquitetura e fluxo'],
  ['Arquitetura e PostgreSQL', 'Arquitetura e postgresql'],
  ['API CLI HTTP FAQ ADR', 'Api cli http faq adr'],
  ['API E CLI PARA O PROJETO', 'Api e cli para o projeto'],
  ['ADR 001 — USAR RUST PARA O RELAY', 'Adr 001 — usar rust para o relay'],
  ['USAR POSTGRESQL COM NEXT.JS E DOCKER', 'Usar postgresql com next.js e docker'],
  ['USAR --dry-run PARA O PROJETO', 'Usar --dry-run para o projeto'],
  ['USAR ./src/API.ts E /etc/config COM NODE_ENV E getHTTPClient()', 'Usar ./src/api.ts e /etc/config com node_env e gethttpclient()'],
  ['CONFIGURAÇÃO E EXECUÇÃO — VISÃO GERAL', 'Configuração e execução — visão geral'],
  ['PROJECT DEVELOPMENT AND ARCHITECTURE', 'Project development and architecture'],
  ['USAR ACME XYZ Foobar', 'Usar acme xyz foobar'],
  ['USAR ACME XYZ', 'Usar acme xyz'],
  ['DESENVOLVIMENTO DO PROJETO COM API E CLI PARA CONFIGURAÇÃO E EXECUÇÃO EM PRODUÇÃO',
    'Desenvolvimento do projeto com api e cli para configuração e execução em produção'],
]) {
  test(`cursive heading: ${source}`, () => {
    for (const level of [1, 2, 3]) assert.equal(render(`${'#'.repeat(level)} ${source}`), `<h${level}>${expected}</h${level}>`);
  });
}

test('nested emphasis and links normalize with sentence context; code and attributes survive', () => {
  assert.equal(render('## ADR 001 — **USAR** `RUST API` PARA O [PROJETO](./API.md#UPPER)'),
    '<h2>Adr 001 — <strong>usar</strong> <code>RUST API</code> para o <a href="./API.md#UPPER">projeto</a></h2>');
});

test('first letter is tracked across emphasis and links, including lowercase starts', () => {
  assert.equal(render('## 3. **rules** DE [SOBRESCRITA](./API.md#UPPER) no filesystem'),
    '<h2>3. <strong>rules</strong> de <a href="./API.md#UPPER">sobrescrita</a> no filesystem</h2>');
});

test('only cursive heading levels change; paragraphs, tables, code and other headings do not', () => {
  const source = '#### ARQUITETURA E FLUXO\n\nARQUITETURA E FLUXO\n\n```sh\nUSAR API\n```\n\n| API | CLI |\n| --- | --- |\n| USAR | RUST |';
  const original = renderToStaticMarkup(createElement(Markdown, { remarkPlugins: [remarkGfm] }, source));
  assert.equal(render(source), original);
});

test('presentation leaves canonical source, heading anchors, duplicate IDs and search text unchanged', () => {
  const source = '## ARQUITETURA E FLUXO\n\n## ARQUITETURA E FLUXO';
  const units = markdownUnits(source);
  const snapshot = structuredClone(units);
  for (const unit of units) assert.match(render(unit.source), /Arquitetura e fluxo/);
  assert.deepEqual(units, snapshot);
  assert.deepEqual(units.map(unit => unit.id), ['arquitetura-e-fluxo', 'arquitetura-e-fluxo-1']);
  assert.ok(units.every(unit => unit.text === 'ARQUITETURA E FLUXO'));
});
