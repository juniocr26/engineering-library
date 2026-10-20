# Demonstrações de desenvolvimento

Engineering Library usa um conjunto local compartilhado de anotações PostgreSQL, organizado por projeto, documento e idioma, sem contas, sessões ou perfis de leitor. Execute o seed uma vez e abra ou atualize qualquer navegador que acesse a mesma instalação. Não há cadastro de navegador, cookie especial ou ação adicional na interface. Um banco sem anotações mostra coleções vazias.

O startup Docker inicializa apenas metadados do catálogo. Seed e limpeza são comandos opcionais e explícitos de desenvolvimento; nunca são executados no boot ou em produção. Não reinicialize o PostgreSQL nem remova seu volume.

## Comandos

Na raiz do repositório, aplique as migrações e instale Playwright no host, se necessário:

```sh
docker compose up -d --build
docker compose exec backend bin/rails db:migrate
cd frontend
npm install --prefix /tmp/engineering-library-browser playwright
export PLAYWRIGHT_MODULE=/tmp/engineering-library-browser/node_modules/playwright
/tmp/engineering-library-browser/node_modules/.bin/playwright install chromium
export BROWSER_BASE_URL=http://localhost:3099
npm run notes:demos
npm run notes:demos:verify
npm run notes:demos:manifest
```

`PLAYWRIGHT_EXECUTABLE_PATH` permite selecionar um navegador instalado. O CLI abre um navegador descartável apenas para medir âncoras reais; não mantém perfil persistente e grava pelas APIs compartilhadas. `notes:demos` reconcilia registros identificados por `demo_key`, sem duplicatas. Não adota nem sobrescreve notas/marcações manuais em trechos ocupados; o conflito é informado e uma execução interrompida pode deixar seed parcial. Resolva o conflito e execute novamente de forma explícita.

`notes:demos:verify` lê o conjunto compartilhado em um navegador novo e abre indicadores/prévias reais. `notes:demos:manifest` é somente leitura e grava `/tmp/engineering-note-demo-manifest.json` com URLs navegáveis e indicadores de âncoras válidas/inválidas. Não cria nem exclui dados. Reconcilie as demonstrações explicitamente após editar os documentos; anotações inválidas nunca são mostradas sobre textos sem relação.

## Abra o leitor normal

- [architecture/current-state.md · en](http://localhost:3099/projects/engineering-library/docs/architecture/current-state.md?lang=en)
- [architecture/current-state.md · pt-BR](http://localhost:3099/projects/engineering-library/docs/architecture/current-state.md?lang=pt-BR)
- [img/visual-components.md · en](http://localhost:3099/projects/engineering-library/docs/img/visual-components.md?lang=en)
- [img/visual-components.md · pt-BR](http://localhost:3099/projects/engineering-library/docs/img/visual-components.md?lang=pt-BR)

Abra **Destaques e notas** e **Minhas marcações**, navegue até um trecho salvo e clique no indicador sobrescrito da nota. Fitas e cores usam os mesmos dados persistidos. Outro navegador independente ou um reload restaura a mesma coleção. Alterações aparecem no outro navegador após atualizar; não há sincronização por push. Inglês e português permanecem estritamente independentes, sem transferência de anotações entre idiomas.

## Contagens esperadas

Cada documento/idioma tem 15 notas, 15 destaques ativos (14 com notas e um independente) e 3 marcações. Nos dois documentos e idiomas: **60 notas, 60 destaques e 12 marcações**. Quatro notas não têm cor. Por idioma, o painel tem 32 anotações combinadas, incluindo 30 notas: amarelo 6, cada uma das outras seis cores 4. A paginação inicial carrega 20 entradas. O seed cria 76 cenários e o manifesto básico valida 132 âncoras. Anotações manuais e duplicatas legadas preservadas podem aumentar os totais; não são removidas para forçar contagens.

No DBeaver, use a conexão existente em `localhost:5499`, credenciais locais e banco `engineering_library`. Diagnóstico somente leitura:

```sql
SELECT language, document, count(*) FROM notes
WHERE demo_key IS NOT NULL GROUP BY language, document;
SELECT language, color, count(*) FROM highlights
WHERE demo_key IS NOT NULL GROUP BY language, color;
SELECT language, document, count(*) FROM bookmarks
WHERE demo_key IS NOT NULL GROUP BY language, document;
```

## Limpeza explícita

Execute separadamente somente quando desejar remover as demonstrações compartilhadas:

```sh
BROWSER_BASE_URL=http://localhost:3099 npm run notes:demos:cleanup
```

A limpeza remove somente registros identificados como demonstração em todo o projeto Engineering Library, nos dois documentos e idiomas. Notas, destaques e marcações manuais permanecem. Se uma nota manual referencia um destaque de demonstração, a exclusão do destaque anula o vínculo e preserva o Markdown com sua âncora independente. Todos os navegadores refletem a limpeza após atualizar. Não há identidade de navegador envolvida. Não execute seed e limpeza simultaneamente.

## Migração e testes de regressão

Consulte a [migração compartilhada](../architecture/current-state.md#migração-de-anotações-compartilhadas) para a preservação de duplicatas legadas. A transição adiciona índices compartilhados antes de remover propriedade obsoleta; mantém IDs, corpos distintos e relacionamentos. Reverter exige backup revisado, pois a propriedade removida não pode ser reconstruída.

`npm run test:demos:browser` exige instalação QA explicitamente isolada (`SHARED_ANNOTATIONS_TEST=1` e `BROWSER_BASE_URL`), recusa coleções não vazias antes das verificações de fixtures e valida CRUD compartilhado, dois contextos independentes, filtros de idioma, idempotência e limpeza exclusiva de demonstrações. Testes Rails também exercitam registros legados conflitantes em schema PostgreSQL temporário. O startup normal nunca executa esses testes.
