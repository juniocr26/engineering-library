# Demonstrações de desenvolvimento

Engineering Library usa um conjunto local compartilhado de anotações PostgreSQL, organizado por projeto, documento e idioma, sem contas, sessões ou perfis de leitor. Execute o seed uma vez e abra ou atualize qualquer navegador que acesse a mesma instalação. Não há cadastro de navegador, cookie especial ou ação adicional na interface. Um banco sem anotações mostra coleções vazias.

O startup Docker inicializa apenas metadados do catálogo. Seed e limpeza são comandos opcionais e explícitos de desenvolvimento; nunca são executados no boot ou em produção. Não reinicialize o PostgreSQL nem remova seu volume.

## Comandos

Na raiz do repositório, inicie os serviços pelo shell do host. O startup aplica migrações; a imagem de desenvolvimento inclui Playwright e Chromium:

```sh
# Execute no shell do host, na raiz do repositório.
docker compose up -d --build --wait --wait-timeout 300
docker compose exec -T frontend npm run notes:demos
docker compose exec -T frontend npm run notes:demos:verify
docker compose exec -T frontend npm run notes:demos:manifest
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
docker compose exec -T frontend npm run notes:demos:cleanup
```

A limpeza remove somente registros identificados como demonstração em todo o projeto Engineering Library, nos dois documentos e idiomas. Notas, destaques e marcações manuais permanecem. Se uma nota manual referencia um destaque de demonstração, a exclusão do destaque anula o vínculo e preserva o Markdown com sua âncora independente. Todos os navegadores refletem a limpeza após atualizar. Não há identidade de navegador envolvida. Não execute seed e limpeza simultaneamente.

## Migração e testes de regressão

Consulte a [migração compartilhada](../architecture/current-state.md#migração-de-anotações-compartilhadas) para a preservação de duplicatas legadas. A transição adiciona índices compartilhados antes de remover propriedade obsoleta; mantém IDs, corpos distintos e relacionamentos. Reverter exige backup revisado, pois a propriedade removida não pode ser reconstruída.

`test:demos:browser` exige instalação QA explicitamente isolada (`SHARED_ANNOTATIONS_TEST=1` e `BROWSER_BASE_URL`), recusa coleções não vazias antes das verificações de fixtures e valida CRUD compartilhado, dois contextos independentes, filtros de idioma, idempotência e limpeza exclusiva de demonstrações. Testes Rails também exercitam registros legados conflitantes em schema PostgreSQL temporário. O startup normal nunca executa esses testes.

O frontend deve estar ativo para instalar e limpar demos. O manifesto fica no container; copie com `docker compose cp frontend:/tmp/engineering-note-demo-manifest.json /tmp/engineering-note-demo-manifest.json`. Os URLs desse manifesto usam a porta interna 3000; para abrir no host, substitua a origem por `http://localhost:3099`.

## Test database / Banco de testes

```sh
docker compose exec -T -e RAILS_ENV=test backend sh -c 'bin/rails db:prepare && bin/rails test test/integration/note_demos_api_test.rb'
```

Esse teste cria demonstrações e anotações manuais sintéticas no banco com sufixo `_test` do PostgreSQL existente. Verifica idempotência e preservação de notas, destaques e marcações manuais após limpar demos.

Para a regressão completa do CLI e navegador, use os mesmos três serviços. Os comandos abaixo criam apenas um banco temporário no PostgreSQL existente e recriam o backend existente para apontar a ele. O frontend continua usando `http://backend:3000`; não há outro servidor ou perfil de leitor. Requer os três serviços ativos, permissão do papel PostgreSQL para criar banco e nenhum outro processo editando anotações durante o teste: os navegadores verão temporariamente o dataset sintético. O trap restaura a configuração original em caso de falha; nesse caso, o banco temporário fica disponível para inspeção. Em sucesso, só esse banco temporário é removido. Não altere `.env` durante o procedimento e não execute diretamente a suíte contra o banco compartilhado.

```sh
(
  set -eu
  LIBRARY_QA_DB="engineering_library_workflow_check_$(date +%s)"
  restore_backend() {
    docker compose up -d --no-deps --wait --wait-timeout 300 backend
  }
  trap restore_backend EXIT
  docker compose exec -T postgres sh -c 'createdb -U "$POSTGRES_USER" "$1"' sh "$LIBRARY_QA_DB"
  POSTGRES_DB="$LIBRARY_QA_DB" docker compose up -d --no-deps --wait --wait-timeout 300 backend
  docker compose exec -T -e SHARED_ANNOTATIONS_TEST=1 frontend npm run test:demos:browser
  restore_backend
  trap - EXIT
  docker compose exec -T postgres sh -c 'dropdb -U "$POSTGRES_USER" "$1"' sh "$LIBRARY_QA_DB"
)
```
