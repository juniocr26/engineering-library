# Demonstrações de desenvolvimento

Comandos explícitos; nunca executados no boot ou em produção. Não use db:reset. O comando depende de Playwright instalado; indique PLAYWRIGHT_MODULE se necessário.

```sh
docker compose exec backend bin/rails db:migrate
cd frontend
BROWSER_BASE_URL=http://localhost:3099 npm run notes:demos
BROWSER_BASE_URL=http://localhost:3099 npm run notes:demos:verify
npm run notes:demos:manifest
```

Para seu navegador, abra architecture/current-state.md e img/visual-components.md com ?lang=pt-BR&noteDemos=1. Abra Development note demonstrations e clique Seed current reader em cada documento e idioma. Download manifest fornece links para notas. O script usa um perfil local persistente separado, com cookie aleatório assinado pelo Rails. Não copie segredos de cookies.

No DBeaver use a conexão local existente em localhost:5499, banco e credenciais do ambiente local. Não divulgue reader_digest. As consultas abaixo são somente leitura e contam todos os proprietários de demonstração; o leitor exibe apenas seu cookie.

```sql
SELECT language, document, count(*) FROM notes
WHERE demo_key IS NOT NULL GROUP BY language, document;
SELECT language, color, count(*) FROM highlights
WHERE demo_key IS NOT NULL GROUP BY language, color;
SELECT language, document, count(*) FROM bookmarks
WHERE demo_key IS NOT NULL GROUP BY language, document;
```

Seeds criam notas Markdown, sete cores, nota sem cor, destaque sem nota e marcadores no início/meio/fim de dois documentos em ambos os idiomas. Âncoras derivam do DOM de medição real. Cleanup é explícito e limitado ao projeto e proprietário; usa demo_key, nunca prefixos no texto. Registros existentes no mesmo trecho geram conflito em vez de serem assumidos pelo seed. Conteúdo estático funciona sem banco. Para inspecionar, abra os links do manifesto, clique no indicador da nota, pré-visualize e amplie tabelas/imagens/diagramas. Valide filtros, fita, idioma e paginação em sua tela.


## Playwright

```sh
npm install --prefix /tmp/engineering-library-browser playwright
export PLAYWRIGHT_MODULE=/tmp/engineering-library-browser/node_modules/playwright
/tmp/engineering-library-browser/node_modules/.bin/playwright install chromium
# Optional: PLAYWRIGHT_EXECUTABLE_PATH=/path/to/installed/browser
# Optional: DEMO_BROWSER_PROFILE=/tmp/engineering-note-demo-browser
```

Execute os comandos npm no host com Node.js disponível e o Compose ativo. O perfil fixture é persistente, mas seu cookie inicial é aleatório e seguro. Não execute dois comandos simultâneos sobre o mesmo perfil. O comando de manifesto lê o último JSON exportado; a verificação consulta o banco via API e abre os indicadores reais. Para uma verificação estática sem seeds: `node tests/visual-catalog.browser.cjs` no diretório frontend, usando as mesmas variáveis de Playwright.

Matriz por documento e idioma: 15 notas, 15 destaques ativos (14 associados a notas e um sem nota) e 3 bookmarks. Total esperado para o perfil fixture em dois documentos e idiomas: 60 notas, 60 destaques, 12 bookmarks. Quatro notas permanecem sem cor. O manifesto lista 76 cenários, incluindo notas e registros independentes. Textos de notas incluem Unicode, títulos, listas, checklist, tabela pequena, tabela larga de 35 linhas, código, imagens e Mermaid. A nota longa combina recursos. Algumas descrições técnicas sintéticas e identificadores permanecem em inglês.

A limpeza remove demonstrações deste proprietário em todo o projeto aberto, em ambos os idiomas. Ela não é executada automaticamente. Pode preservar cores de demonstrações legadas que não possuíam identificação explícita de propriedade, em vez de arriscar remover destaques pessoais.


## Validação em 20/10/2026

Executados: 94 testes frontend, 24 testes Rails (412 assertions), 27 testes Python, typecheck e lint. Edge abriu as 60 notas persistidas, validou sete cores, quatro notas sem cor, tabelas largas e longas, Mermaid e imagens nas notas. A repetição manteve 60 notas, 60 destaques e 12 bookmarks; a verificação após reiniciar Rails passou sem recriar os dados. A limpeza explícita de um perfil temporário preservou o perfil fixture; o teste Rails também preservou registros pessoais e de outro leitor.

Em um contexto sem seeds, o sumário encontrou IMG; JPEG local, SVG local, SVG HTTPS e GIF HTTPS carregaram com dimensões reais; o endereço inválido exibiu o fallback. Flowchart e sequência Mermaid renderizaram, e fullscreen, zoom e pan foram exercitados. A suíte de anotações passou em 1440px e 390px. Firefox e Safari não foram executados. Mídia externa continua dependente do provedor.

O validador do catálogo verificou 451 arquivos Markdown e 3559 links locais. Permanecem dois documentos anteriores sem caminho a partir do índice central: validation/heading-numbering.md e validation/navigation-audit.md; os arquivos IMG não introduzem erros nessa validação.

Limpeza opcional, em uma invocação separada, somente quando desejar remover as demonstrações:

```sh
BROWSER_BASE_URL=http://localhost:3099 npm run notes:demos:cleanup
```
