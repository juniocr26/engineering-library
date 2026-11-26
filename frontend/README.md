# Engineering Library frontend

Private Engineering Library component belonging to Viva Bem, maintained in this private repository for authorized internal use. See the [repository overview](../README.md) for access and confidentiality boundaries.

Componente privado da Engineering Library pertencente à Viva Bem, mantido neste repositório privado para uso interno autorizado. Consulte a [visão geral do repositório](../README.pt-BR.md) para os limites de acesso e confidencialidade.

Next.js App Router with TypeScript, a bilingual antique-book catalog and an internal Markdown reader. Shared browser-measured pagination and page turning support desktop spreads and mobile single pages. Reader panels provide project search, chapters and shared PostgreSQL bookmarks, highlights and notes via the same-origin Rails proxy.

Use the repository-root Compose configuration. See [development documentation](../docs/engineering-library/en/guides/application-development.md) for setup, dependency recovery, lint, type checks and builds.

See [reader architecture and validation](../docs/engineering-library/en/guides/book-frontend.md) for routes, Markdown safety, logical anchors, shared annotation scopes and CSRF and browser test commands.

### Fullscreen documentation media

Markdown images (including SVG image resources) and rendered Mermaid diagrams have
an accessible expand button. The viewer fits media to the viewport, supports zoom
from 1× to 8×, bounded dragging, wheel zoom, two-pointer pinch, reset and Escape.
Native modal dialog behavior traps focus and blocks background interaction; closing
returns focus to the expand button. The viewer is portaled outside the book.

Run the optional browser regression from the repository root against a running Compose frontend:

```sh
docker compose exec -T frontend node tests/media-viewer.browser.mjs
```

`MEDIA_DOCUMENT_URL` can select another document containing a rendered diagram or
image. The script checks desktop, tablet and mobile sizes, opening/closing, zoom,
reset, dragging, keyboard focus and preservation of URL and physical page content.

### Embedded source references

All documented projects share collision-safe source identities, independent
expandable occurrences, measured code continuation, collapsed-source search and
fingerprint-aware bookmarks. See [source-reference architecture](../docs/engineering-library/en/architecture/source-references.md)
and the [Portuguese version](../docs/engineering-library/pt-br/architecture/source-references.md).
Generate approved snapshots explicitly with `tools/build-source-catalog.ts`;
the reader never reads sibling repositories at runtime.

## Current integration / Integração atual

The frontend calls Rails through same-origin proxies and server-side `BACKEND_URL`. Catalog registration is idempotent and separate from inference. MakeDocs invokes the same default Ruby command as the CLI; the coordinator reports completion after required host delivery. Generated prose remains a draft requiring factual/translation review. Use the managed root launcher because the host adapter requires POSIX Python.

O frontend consulta Rails por proxies de mesma origem e `BACKEND_URL` no servidor. Cadastro é idempotente e separado da inferência. MakeDocs usa o mesmo comando Ruby padrão da CLI; o coordenador conclui após a entrega obrigatória ao host. A prosa continua rascunho sujeito à revisão factual/de tradução. Use o launcher da raiz: o adapter exige Python POSIX no host.

## Local dependencies / Dependências locais

The existing Compose services install physical dependency sources in `frontend/node_modules` and `backend/vendor/bundle`. All runtimes and package managers stay in Docker. See [installation, refresh and VS Code limitations](../docs/engineering-library/en/guides/application-development.md#local-dependency-sources-docker-development).

Os serviços existentes do Compose instalam fontes físicas em `frontend/node_modules` e `backend/vendor/bundle`. Runtimes e gerenciadores permanecem no Docker. Consulte [instalação, atualização e limitações do VS Code](../docs/engineering-library/pt-br/guides/application-development.md#fontes-locais-de-dependências-desenvolvimento-docker).

## Leitor e mídia: referência em português

Next.js App Router/TypeScript apresenta catálogo bilíngue e leitor de livro antigo. Paginação medida no navegador e virada de folhas atendem páginas duplas no desktop e únicas no celular. Painéis de busca, capítulos, marcadores, destaques e notas usam localizações lógicas e PostgreSQL compartilhado por proxy Rails; não existem contas pessoais.

Imagens Markdown/SVG e diagramas Mermaid oferecem expansão em diálogo modal, zoom de 1× a 8×, arraste limitado, roda, gesto de pinça, reset e Escape. Foco retorna ao botão de expansão ao fechar. O teste de navegador existente `tests/media-viewer.browser.mjs` permite selecionar documento por `MEDIA_DOCUMENT_URL` e verifica tamanhos, interação e preservação de URL/conteúdo; não foi executado nesta revisão documental.

Referências expansíveis usam identidades sem colisão, ocorrências independentes, continuação medida de código, busca mesmo recolhidas e marcadores vinculados a fingerprints. Snapshots são aprovados explicitamente por `tools/build-source-catalog.ts`; cadastro do host não concede leitura arbitrária ao navegador. Consulte [arquitetura das referências](../docs/engineering-library/pt-br/architecture/source-references.md) e [leitor](../docs/engineering-library/pt-br/guides/book-frontend.md).
