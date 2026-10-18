# Frontend do livro e catálogo

[Índice do projeto](../index.md) · [English](../../en/guides/book-frontend.md)

A página inicial implementa o protótipo HTML aprovado: duas páginas no desktop, pergaminho único até 920px e ilustração recortada acima dos projetos. Os tokens e texturas CSS ficam em `frontend/app/globals.css`. A ilustração e o selo EL fornecidos ficam em `frontend/public/assets/`; `app/icon.png` fornece o ícone do framework. A referência visual não é usada como fundo da página. O título usa a fonte Great Vibes distribuída localmente com sua licença SIL Open Font License.

## Responsabilidades

- `app/page.tsx` consulta o catálogo Rails no servidor. `app/projects/[slug]/page.tsx` gera o sumário dos documentos reais com `lib/documentation.ts`; os links abrem Markdown no repositório público enquanto o leitor não existe.
- `components/book-layout.tsx`, `project-list.tsx`, `pagination.tsx` e `catalog-state.tsx` implementam livro, cartões, navegação e estados localizados de vazio, erro e carregamento. `document-language.tsx` atualiza o idioma do documento após navegação; a estrutura inicial usa português.
- `lib/i18n.ts` define os idiomas e URLs. `lib/pagination.ts` calcula os indicadores limitados, separado da apresentação. `lib/catalog.ts` contém contratos e acesso à API apenas no servidor, usando o `BACKEND_URL` existente.
- No Rails, `Catalog::Files` lê arquivos restritos ao catálogo. `Catalog::Sync` indexa identidades. `Catalog::Page` conta, ordena e pagina no PostgreSQL. `Catalog::Presenter` lê as descrições localizadas dos registros selecionados. `Api::ProjectsController` responde HTTP.

## Metadados Markdown

Cada projeto possui `bio/en.md`, `bio/pt-BR.md` e `bio/icon.svg`. Os seis projetos estão cobertos. As duas bios seguem este formato:

```markdown
---
id: identificador-estavel-do-projeto
name: Nome Canônico do Projeto
---

Descrição localizada e concisa do propósito verificado do projeto.
```

Mantenha `id` imutável ao renomear diretórios. Ambos os arquivos devem concordar em `id` e `name` canônico. O corpo é descrição compacta em texto simples, sem renderização Markdown. Bios inválidas ou ausentes interrompem a sincronização antes de qualquer escrita no banco e informam o slug. Preserve o identificador para não criar outra identidade. Renomeações conflitantes falham transacionalmente sem sobrescrever outro registro. Projetos ausentes ficam inativos, sem exclusão. Restaurar o identificador os reativa. Não sincronize enquanto edita arquivos do catálogo: a transação de escrita é serializada, mas a descoberta não é uma fotografia atômica do sistema de arquivos.

Os ícones são SVGs locais originais com viewBox 24×24 e traços de tinta consistentes, sem scripts, recursos externos ou conteúdo ativo. O Rails os serve por endpoint restrito; Next encaminha essas requisições. Ícones indisponíveis usam o livro de fallback local. O selo EL continua sendo a identidade principal.

## API e paginação

`GET /api/projects?page=2&lang=en` retorna `projects` (slug, nome canônico, descrição localizada) e `pagination` (page, total_pages, total_projects, page_size). `GET /api/projects/:slug?lang=en` acrescenta índices existentes de categorias. `GET /api/projects/:slug/icon` serve o SVG local. Não retorna caminhos absolutos nem documentos Markdown.

O PostgreSQL guarda somente identificador estável, slug, nome, indicador ativo e timestamps. Caminhos de bios e ícones derivam do slug. Markdown é a fonte de verdade. Não existe sincronização automática na inicialização: execute `catalog:sync` após alterações no catálogo.

O tamanho é sempre cinco; clientes não podem aumentá-lo. A ordenação usa `lower(display_name) COLLATE "C"`, seguida de `stable_id` imutável: ordem determinística de bytes sem distinção de maiúsculas, independente do idioma. Um índice parcial de expressão atende os ativos. Páginas inválidas, negativas, zero, fracionárias ou longas demais selecionam a primeira; números além do limite selecionam a última. Sem projetos, aparece o estado vazio na página 1 de 1. Múltiplos exatos de cinco não criam página extra.

Parâmetros de URL preservam idioma e página. Os controles mostram vizinhos, extremos e reticências, com no máximo nove indicadores. Setas nos limites ficam desabilitadas. A página atual tem `aria-current`; o foco de teclado é visível. Português é o padrão e o título nunca é traduzido. Não há tradução automática em execução.

## Desenvolvimento e verificação

Na raiz do repositório:

```sh
docker compose up -d --build
docker compose exec -T backend bundle exec rails db:prepare catalog:sync
docker compose exec -T backend sh -c 'RAILS_ENV=test bundle exec rails db:prepare && bundle exec rails test'
docker compose exec -T frontend npm test
docker compose exec -T frontend npm run typecheck
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
python3 -B docs/validation/check_catalog.py
git diff --check
```

O Compose acrescenta somente montagem de documentação em leitura em `/docs/projects`; preserva configuração do banco e ambiente. Fora do Docker, o caminho padrão é `docs/projects`, irmão do Rails; `CATALOG_ROOT` permite substituição nos testes. Os testes usam o banco Rails de teste separado. Não execute build e servidor de desenvolvimento simultaneamente no mesmo `.next`; pare o desenvolvimento ou use outro diretório de build.

Limites atuais: sem leitor completo, edição, favoritos, autenticação ou busca. Indisponibilidade da API mostra erro localizado com nova tentativa. O leitor futuro deverá resolver links com segurança, renderizar Markdown de forma acessível e preservar navegação por projeto, idioma e categoria.

Verificação no navegador (instale Playwright e Chromium antes em diretório temporário):

```sh
# Run a production server on port 3100 after building.
docker compose exec -T frontend npm run start -- --port 3100
# In another terminal, with the external Playwright module path:
docker compose exec -T frontend sh -c 'PLAYWRIGHT_MODULE=/tmp/el-browser/node_modules/playwright node tests/browser.cjs'
```

## Identidade reutilizável de manuscrito

`ManuscriptDecorations` posiciona assets locais originais sobre `.manuscript-surface`, abaixo de `.content`. `BookLayout` aplica o sistema ao catálogo e aos índices existentes de projetos. Futuros leitores, FAQ e páginas de documentação devem reutilizar essa superfície com a composição `reading`; essas telas futuras não foram implementadas aqui. As variantes `catalog`, `reading` e `illustration` usam composições determinísticas baseadas no conteúdo em `lib/manuscript.ts`, sem `Math.random()`.

Os assets ficam em `frontend/public/assets/manuscript/`: `parchment/` contém o WebP de granulação e seu original SVG editável; `burns/`, `ink/`, `wax/`, `erasures/` e `ornaments/` contêm contornos queimados, tinta absorvida, cera âmbar, traços riscados sem conteúdo linguístico e a pena do título. Reutilize os arquivos em vez de duplicar texturas. Para regenerar o WebP, use Sharp sobre `aged-fibers-master.svg` com qualidade WebP 82 no ambiente do frontend.

Concentre marcas fortes nas margens, cantos e espaços livres. O papel mais claro preserva textos, código e tabelas; ajuste as posições para documentos longos. A decoração fica oculta de tecnologias assistivas e ignora eventos de ponteiro; o título continua como texto real. Preserve foco e contraste. Abaixo de 920px a ilustração segue no fluxo existente de página única; em 480px a pena e as marcas diminuem sem eliminar a identidade envelhecida. As animações usam CSS; não há imagens remotas ou dependência gráfica adicional. Somente o WebP compacto é decodificado para a granulação; os SVGs são compartilhados e armazenáveis em cache. O SVG original serve para edição e não é carregado pela interface.

## Sumário responsivo e motor compartilhado

`lib/documentation.ts` une os caminhos canônicos dos dois idiomas, ordena categorias e arquivos, inclui README na ordenação normal e usa títulos H1 locais. Traduções ausentes ficam indisponíveis. Índices apenas navegacionais são omitidos; índices substantivos, como ENV, permanecem. O frontend lê `DOCUMENTATION_ROOT` (montagem somente leitura `/docs/projects` no Compose); fora do Docker, usa `../docs/projects`. PostgreSQL continua responsável apenas pelo catálogo de projetos.

`BookReader` recebe unidades e função de renderização. Um contêiner invisível e inerte mede alturas reais, incluindo espaçamento. `ResizeObserver`, carregamento de fontes e mudanças de idioma/conteúdo recalculam limites. Cabeçalhos permanecem com o primeiro item quando possível. Unidades maiores que a área disponível possuem rolagem local acessível. Numeração de capítulos independe dos fólios. Resize tenta preservar a primeira unidade visível.

O mesmo ciclo de transição atende `spread` acima de 920px e `single-page` nos demais tamanhos. Avançar gira a folha direita em -180 graus pela borda esquerda; voltar gira a folha esquerda em +180 graus pela borda direita. Faces, perspectiva e sombras compartilham as texturas. Botões, setas do teclado e gestos horizontais deliberados navegam; gestos verticais permanecem disponíveis. Movimento reduzido troca imediatamente. A trava evita transições sobrepostas; resize cancela a transição com segurança.

`lib/manuscript.ts` combina projeto, identidades canônicas ordenadas e variante versionada. Idioma e número físico não entram na semente. O mesmo conjunto de conteúdo mantém as marcas; agrupamentos diferentes recebem outra composição. Queimaduras, tinta, cera, rasuras, líquidos e abrasões são camadas absolutas nas margens, sem eventos de ponteiro nem impacto na medição. Nenhuma dependência gráfica foi adicionada. O catálogo inicial permanece preservado; a versão inspecionada não possuía hamburger mobile, então o sumário fornece um menu hamburger mínimo e acessível para voltar ao catálogo.

Limites: documentos abrem no GitHub; o leitor Markdown completo não foi implementado. Unidades excepcionalmente altas usam rolagem interna. A curvatura é aproximada por perspectiva e iluminação de uma folha rígida. Testes automatizados não comprovam todos os documentos, fontes e níveis de zoom.
