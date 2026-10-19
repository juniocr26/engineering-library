# Engineering Library: arquitetura atual

Revisão estática do código: 2026-10-19. Esta página descreve a árvore atual; descrições históricas do scaffold foram superadas. [Frontend em formato de livro e catálogo](../guides/book-frontend.md) detalha o leitor.

## Propósito e limites da evidência

A biblioteca mantém explicações de engenharia, FAQs e evidências em dois idiomas. Markdown em `docs/projects/` define documentos e bios. Rails serve metadados e favoritos anônimos; Next.js renderiza o livro interno. Foram examinados código e definições de testes, sem iniciar serviços ou executar testes dependentes de banco. Não se estabelece implantação em produção, capacidade medida ou agente de IA.

## Base implementada

`backend/config/routes.rb` expõe `GET /api/projects`, `GET /api/projects/:id`, ícones e listagem/criação/exclusão de favoritos, além de `/up`. `CatalogProject` e `Bookmark` possuem schema PostgreSQL, validações e índices reais. `/up` indica boot do Rails; não consulta o catálogo nem comprova prontidão do PostgreSQL.

`Catalog::Sync` percorre diretórios, valida concordância de identidade/nome entre bios e duplicidade de IDs estáveis antes das escritas. Um advisory lock transacional serializa atualizações no banco; registros são encontrados por `stable_id`, renomeados por slug e desativados quando ausentes. Registros inalterados evitam escrita. Erros de validação preservam o último índice válido. A transação não congela arquivos: mantenha-os estáveis durante a sincronização. Editar documentos Markdown dispensa ingestão no banco; editar metadados exige `catalog:sync` explícito.

`Catalog::Page` seleciona registros ativos em páginas fixas de cinco, na ordem determinística `lower(display_name) COLLATE "C", stable_id`. Paginação por offset é simples e apoiada por índice, mas não forma snapshot entre requisições durante mudanças. Next busca JSON no servidor com `cache: 'no-store'` e timeout de cinco segundos. Sua leitura dos arquivos da coleção é separada da API de metadados Rails.

`compose.yaml` define PostgreSQL, Rails e Next. Portas são publicadas em loopback. Dados PostgreSQL usam `.dockerized-postgres` do host: persistência, sem backup validado. Os dois serviços recebem a coleção documental somente para leitura. Diretórios de dependências/build são bind mounts de desenvolvimento. Dependências de health na partida não implementam recuperação automática da aplicação diante de toda falha posterior.

## Responsabilidades e trade-offs

Rails controla metadados indexados, paginação do catálogo e persistência de favoritos. Next controla Markdown, ordem lógica dos documentos e paginação física medida no navegador. Conteúdo de arquivos e metadados do banco têm fronteiras de consistência diferentes. `Catalog::Files.read` resolve caminhos reais dentro do projeto validado; `collectionFile` aplica verificações próprias no Next. Nenhuma delas constitui sandbox livre de corrida em filesystem hostil.

Favoritos anônimos identificam o navegador por cookie assinado, HttpOnly e SameSite=Lax; o banco guarda seu digest SHA-256. Mutações exigem token do verifier vinculado ao digest e à finalidade. Isso oferece identidade local do navegador e proteção CSRF, sem login ou sincronização entre dispositivos. Índice único evita duplicação da localização lógica. O limite de 200 usa contagem antes do insert e não é um teto transacional sob concorrência. A sintaxe da âncora é validada; a existência de cada âncora não é verificada ao criar o favorito.

## Contrato do catálogo

Navegação: Biblioteca → Projeto → Idioma → Categoria → Documento. `documentationEntries` une IDs relativos dos dois idiomas, ordena deterministicamente, omite índices apenas navegacionais e mantém índices substanciais. Traduções ausentes não têm destino. `reading-order.ts` deriva vizinhos das mesmas entradas. Páginas físicas dependem de fontes, diagramas, imagens e viewport; URLs/favoritos usam documento/âncora lógica, sem persistir números físicos.

Respostas técnicas ficam diretamente em `faq/index.md`. Caminhos `study-guide.md` e âncoras anteriores permanecem por compatibilidade. Expansões de código usam snapshots aprovados endereçados por conteúdo, sem leitura arbitrária de repositórios irmãos em runtime; veja [referências de código](source-references.md). Adicionar links de código não aprova nem regenera seus snapshots automaticamente.

## Segurança e evidência pendente

O catálogo contém portfólio público. Não implementa autenticação de contas ou autorização de biblioteca privada. Isolamento de favoritos é mais restrito que controle de acesso aos documentos. Assinatura de cookies depende de segredo estável; perder a identidade do navegador impede acesso ordinário aos favoritos anteriores. Rejeição de padrões SVG e triagem dos snapshots são medidas defensivas, sem garantia genérica de sanitização.

O validador atual verifica links locais, âncoras, idiomas, IDs Q, títulos preservados e alcance. Não comprova tradução, paginação runtime, URLs externas ou prontidão de implantação. Definições de testes cobrem sincronização, paginação, travessia de caminhos, isolamento anônimo e CSRF; ler esses testes não significa executá-los.

Evidências: `backend/app/services/catalog/{files,sync,page,presenter}.rb`, `backend/app/controllers/api/{projects,bookmarks}_controller.rb`, `backend/db/schema.rb`, `backend/test/models/catalog_test.rb`, `backend/test/integration/{catalog_api,bookmarks_api}_test.rb`, `frontend/lib/{catalog,documentation,document-links}.ts` e `compose.yaml`. Veja [escopo da auditoria e pendências](../operations/documentation-audit-2026-10-19.md).
