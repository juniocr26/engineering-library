# Frontend do livro e catálogo

[Índice do projeto](../index.md) · [English](../../en/guides/book-frontend.md)

A página inicial implementa o protótipo HTML aprovado: duas páginas no desktop, pergaminho único até 920px e ilustração recortada acima dos projetos. Os tokens e texturas CSS ficam em `frontend/app/globals.css`. A ilustração e o selo EL fornecidos ficam em `frontend/public/assets/`; `app/icon.png` fornece o ícone do framework. A referência visual não é usada como fundo da página. O título usa a fonte Great Vibes distribuída localmente com sua licença SIL Open Font License.

## Responsabilidades

- `app/page.tsx` consulta o catálogo Rails no servidor. `app/projects/[slug]/page.tsx` gera o sumário dos documentos reais com `lib/documentation.ts`; os links abrem o leitor interno em `/projects/[slug]/docs/[...document]`.
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
docker compose run --rm --no-deps frontend npm run build
python3 -B docs/validation/check_catalog.py
git diff --check
```

O Compose monta documentação em leitura em `/docs/projects`; Rails usa `CATALOG_ROOT=/docs/projects`. Dependências ficam nas imagens e cada contêiner frontend tem seu próprio tmpfs `.next`. Fora do Docker, o caminho padrão é `docs/projects`, irmão do Rails; `CATALOG_ROOT` permite substituição nos testes. Os testes usam o banco Rails de teste separado. Não execute build e servidor de desenvolvimento simultaneamente no mesmo `.next`; pare o desenvolvimento ou use outro diretório de build.

Limites atuais: sem edição de documentação, autenticação ou sincronização de marcações entre dispositivos. Indisponibilidade da API mostra erro localizado com nova tentativa. O leitor resolve arquivos Markdown com escopo validado e preserva navegação por projeto e idioma.

Verificação no navegador (instale Playwright e Chromium antes em diretório temporário):

```sh
# Build and serve in one isolated container, using its own temporary cache.
docker compose run --rm --no-deps --name engineering-library-preview frontend sh -c 'npm run build && exec npm run start -- --hostname 0.0.0.0 --port 3100'
# In another terminal, with the external Playwright module path:
docker compose exec -T frontend sh -c 'BROWSER_BASE_URL=http://engineering-library-preview:3100 PLAYWRIGHT_MODULE=/tmp/el-browser/node_modules/playwright node tests/browser.cjs'
```

## Identidade reutilizável de manuscrito

`ManuscriptDecorations` posiciona assets locais originais sobre `.manuscript-surface`, abaixo de `.content`. `BookLayout` aplica o sistema ao catálogo e aos índices existentes de projetos. O leitor documental reutiliza essa superfície com a composição `reading`. As variantes `catalog`, `reading` e `illustration` usam composições determinísticas baseadas no conteúdo em `lib/manuscript.ts`, sem `Math.random()`.

Os assets ficam em `frontend/public/assets/manuscript/`: `parchment/` contém o WebP de granulação e seu original SVG editável; `burns/`, `ink/`, `wax/`, `erasures/` e `ornaments/` contêm contornos queimados, tinta absorvida, cera âmbar, traços riscados sem conteúdo linguístico e a pena do título. Reutilize os arquivos em vez de duplicar texturas. Para regenerar o WebP, use Sharp sobre `aged-fibers-master.svg` com qualidade WebP 82 no ambiente do frontend.

Concentre marcas fortes nas margens, cantos e espaços livres. O papel mais claro preserva textos, código e tabelas; ajuste as posições para documentos longos. A decoração fica oculta de tecnologias assistivas e ignora eventos de ponteiro; o título continua como texto real. Preserve foco e contraste. Abaixo de 920px a ilustração segue no fluxo existente de página única; em 480px a pena e as marcas diminuem sem eliminar a identidade envelhecida. As animações usam CSS; não há imagens remotas ou dependência gráfica adicional. Somente o WebP compacto é decodificado para a granulação; os SVGs são compartilhados e armazenáveis em cache. O SVG original serve para edição e não é carregado pela interface.

## Sumário responsivo e motor compartilhado

`lib/documentation.ts` une os caminhos canônicos dos dois idiomas, ordena categorias e arquivos, inclui README na ordenação normal e usa títulos H1 locais. Traduções ausentes ficam indisponíveis. Índices apenas navegacionais são omitidos; índices substantivos, como ENV, permanecem. O frontend lê `DOCUMENTATION_ROOT` (montagem somente leitura `/docs/projects` no Compose); fora do Docker, usa `../docs/projects`. PostgreSQL continua responsável apenas pelo catálogo de projetos.

`BookReader` recebe unidades e função de renderização. Um contêiner invisível e inerte mede alturas reais, incluindo espaçamento. `ResizeObserver`, carregamento de fontes e mudanças de idioma/conteúdo recalculam limites. Cabeçalhos permanecem com o primeiro item quando possível. Unidades maiores que a área disponível possuem rolagem local acessível. Numeração de capítulos independe dos fólios. Resize tenta preservar a primeira unidade visível.

O mesmo ciclo de transição atende `spread` acima de 920px e `single-page` nos demais tamanhos. Avançar gira a folha direita em -180 graus pela borda esquerda; voltar gira a folha esquerda em +180 graus pela borda direita. Faces, perspectiva e sombras compartilham as texturas. Botões, setas do teclado e gestos horizontais deliberados navegam; gestos verticais permanecem disponíveis. Movimento reduzido troca imediatamente. A trava evita transições sobrepostas; resize cancela a transição com segurança.

`lib/manuscript.ts` combina projeto, identidades canônicas ordenadas e variante versionada. Idioma e número físico não entram na semente. O mesmo conjunto de conteúdo mantém as marcas; agrupamentos diferentes recebem outra composição. Queimaduras, tinta, cera, rasuras, líquidos e abrasões são camadas absolutas nas margens, sem eventos de ponteiro nem impacto na medição. Nenhuma dependência gráfica foi adicionada. O catálogo inicial permanece preservado; a versão inspecionada não possuía hamburger mobile, então o sumário fornece um menu hamburger mínimo e acessível para voltar ao catálogo.

Limites: referências a código fora das coleções documentais ficam sem destino no leitor. Unidades excepcionalmente altas usam rolagem interna. A curvatura é aproximada por perspectiva e iluminação de uma folha rígida. Testes automatizados não comprovam todos os documentos, fontes e níveis de zoom.

### Contagem dinâmica de páginas físicas

O motor compartilhado mostra `Página 1 de N` em página única e `Página 1–2 de N` em modo duplo (inglês: `Page 1 of N`). A última folha ímpar conta uma vez; a folha acompanhante vazia não entra no total. O total corresponde ao tamanho do resultado da paginação medida no navegador, nunca a uma estimativa por caracteres ou ao total do catálogo.

Antes de obter medidas válidas, ou enquanto fontes e imagens do conteúdo carregam, os controles mostram `Paginando…` e impedem a navegação. As folhas exibem o estado de paginação até que as novas medidas estejam disponíveis. Carga/erro de imagens, conclusão de fontes, resize das unidades/áreas, idioma e conteúdo provocam nova medição. Geometria idêntica não reconstrói páginas nem cancela uma virada. O indicador fica em uma linha para não alterar a capacidade medida quando seus dígitos mudam.

A repaginação localiza a âncora canônica de leitura no novo conjunto de páginas e alinha o resultado ao par quando necessário. Números físicos e totais ficam apenas no estado do navegador; PostgreSQL persiste apenas posições lógicas das marcações. Marcações guardam posições canônicas de conteúdo, independentemente desses números variáveis por viewport.

`tests/book-browser.cjs` compara o total publicado com agrupamento independente das medidas DOM, percorre até o último par e verifica resize responsivo, os dois idiomas e mudanças de métricas de fonte. O teste usa o sumário. `tests/document-reader-browser.cjs` cobre Markdown real, capítulos, busca, Mermaid, persistência das marcações e navegação responsiva.

## Navegação interna e leitor Markdown

A investigação confirmou URLs GitHub fixas em `documentationEntries`. Não existiam rota de documento, renderizador Markdown, busca ou API de marcações. Eram funcionalidades ausentes. O gerador do sumário e os metadados de categorias Rails agora retornam rotas internas. A paginação do catálogo permanece independente.

`/projects/[slug]/docs/[...document]` usa o App Router para acesso direto, refresh e histórico. `documentationSource` resolve IDs canônicos (`README` ou caminho relativo `.md`) no projeto e idioma selecionados. Valida segmentos, resolve caminhos reais e rejeita arquivos ausentes ou fora do projeto com 404 em pergaminho, sem expor caminhos locais. Índices apenas navegacionais continuam acessíveis por links relativos. Links HTTP(S)/mail externos mantêm seu destino; Markdown dentro das coleções resolve relativamente ao arquivo original, inclusive entre idiomas/projetos. Referências a código fora das coleções ficam sem destino. Imagens usam endpoint de arquivos com extensões permitidas, CSP restritiva e nosniff.

`markdownUnits` usa AST remark/GFM para preservar cabeçalhos, parágrafos, listas, código, tabelas e referências. Cabeçalhos usam slugs GitHub; outros blocos usam hash da seção/conteúdo, sem depender da posição numérica. `MarkdownUnit` usa react-markdown sem HTML bruto. Mermaid carrega sob demanda em modo strict, com fonte acessível e fallback textual em caso de erro; sua renderização pendente impede a publicação prematura do total. Conteúdo largo usa rolagem local; uma unidade semântica maior que a folha permanece acessível por rolagem interna. O total conta as folhas físicas do motor, não subdivisões dessa rolagem.

`DocumentationReader` integra `BookReader` e painéis de pergaminho com dialog nativo. Busca, capítulos e lista de marcações têm controles distintos. Cada folha visível possui marcação própria e fita animada no canto. Painéis contêm o foco, restauram-no ao fechar e aceitam Escape. Capítulos, resultados e marcações usam as mesmas rotas e âncoras; o motor encontra a página física correspondente. As setas mantêm a virada existente; controles nos limites de capítulos animam a folha de saída e depois carregam a rota de destino, que exibe o conteúdo após a medição. Âncoras removidas ou sem correspondência no idioma exibem aviso explícito e fallback para o início. Não há equivalência presumida entre números físicos nos idiomas.

## Busca e marcações compartilhadas no PostgreSQL

`GET /api/document-search/:project?q=...&lang=...` pesquisa diretamente o texto dos blocos Markdown do projeto/idioma, com até 80 resultados, trechos e rotas internas com âncora. A interface aplica debounce, cancela requisições antigas e mostra carga, vazio e erro. Não existe índice separado para sincronizar. O bloco selecionado recebe destaque vermelho. Índices apenas navegacionais, HTML bruto e decoração não são pesquisados.

Rails expõe APIs compartilhadas de marcações, destaques, notas e anotações combinadas, via rotas Next de mesma origem. Os dados usam projeto canônico, documento e idioma obrigatório. GET fornece token CSRF assinado da aplicação com expiração, sem cookies ou cadastro de navegador; mutações exigem `X-Annotation-CSRF`. O proxy verifica Origin, encaminha o cabeçalho CSRF e usa `no-store`. Não há contas, perfis de leitor ou sessões de anotações.

As migrações `20261020010000` e `20261020020000` convertem as anotações existentes para armazenamento compartilhado, sem excluir linhas nem alterar corpos de notas ou chaves estrangeiras. A localização da marcação usa projeto, documento, idioma, âncora e `location_variant` determinístico para preservar duplicatas legadas. Repetir a criação reutiliza a localização existente. Notas mantêm seus IDs e vínculo opcional único com destaque; o índice de trecho não é único, preservando notas distintas no mesmo local. A API retorna 422 para conteúdo inválido, 403 para CSRF ausente/inválido, 404 para ID ausente ou fora do escopo e 503 em falha do banco. Números físicos de páginas nunca são persistidos.

Todo navegador que acessa esta instalação vê as mesmas anotações salvas ao abrir ou atualizar o leitor. Trocar o idioma seleciona uma coleção separada, sem copiar anotações. Mudanças no conteúdo podem invalidar âncoras; o leitor informa posições indisponíveis. Não há autorização de documentos privados. Seed e limpeza de demonstrações são ações explícitas do CLI; consulte [demonstrações de desenvolvimento](../img/development-demos.md).

Documentos ausentes usam `notFound()` do Next: a tela de erro pode chegar com HTTP 200 quando o loading do ancestral já iniciou streaming; sem streaming, a resposta usa 404. Os endpoints de arquivos retornam 404 diretamente. Referência: [Next not-found](https://nextjs.org/docs/app/api-reference/file-conventions/not-found).

Execute a regressão de navegador do leitor com Playwright instalado fora da árvore de dependências da aplicação:

```sh
docker compose exec -T frontend env PLAYWRIGHT_BROWSERS_PATH=/tmp/el-browsers PLAYWRIGHT_MODULE=/tmp/el-browser/node_modules/playwright node tests/document-reader-browser.cjs
```

## Navegação contínua pela sequência canônica

`frontend/lib/reading-order.ts` separa a ordem lógica dos documentos da paginação física. `getReadingSequence(project, language, entries)` recebe os mesmos metadados de `documentationEntries` exibidos no sumário. A primeira entrada tem `id: null` e a URL interna do sumário; as demais preservam os identificadores estáveis e as URLs internas localizadas, na ordem do catálogo. Categorias e traduções indisponíveis não têm URL e são excluídas. O catálogo já exclui índices apenas de navegação e preserva índices substantivos. Não há ordenação por título traduzido nem manifesto paralelo: novos arquivos Markdown legíveis passam a participar automaticamente na posição canônica. Documentos correspondentes mantêm a mesma ordem relativa nos dois idiomas; traduções ausentes são puladas.

`getPreviousDocument`, `getNextDocument`, `getFirstDocument` e `getLastDocument` consultam essa sequência. Identificadores desconhecidos não têm vizinhos; uma coleção vazia contém apenas o sumário. `readingNeighbors` transforma os vizinhos em intenções de rota. O avanço abre o início; o retorno acrescenta `edge=end`. O destino só resolve sua última página física após medir fontes, imagens, diagramas e geometria da tela. Cada documento mantém sua própria contagem; números físicos não são copiados do leitor anterior nem persistidos no PostgreSQL.

`TableOfContents` e `DocumentationReader` fornecem essas intenções ao `BookReader` existente. Setas comuns continuam virando páginas físicas. Nos limites, o controle correspondente recebe o ícone com barra e a descrição acessível de capítulo, incluindo sumário ↔ primeiro documento. O último documento encerra a sequência, sem retorno circular. Cliques, teclado e gestos compartilham o bloqueio e a animação direcional existentes; movimento reduzido dispensa a animação. As rotas vizinhas são pré-carregadas. A animação de saída usa as folhas do documento atual, sem tentar renderizar o destino ainda não carregado no verso. Depois da troca de rota, o leitor mostra o estado de paginação até concluir as próprias medições.

O App Router mantém o histórico de rotas. A entrada atual também conserva a âncora lógica da página, preservando os campos de histórico do Next; ao retornar, essa âncora é resolvida na geometria atual. Redimensionar preserva a posição lógica, em vez de um número físico antigo. URLs diretas abrem o início, salvo uma âncora ou intenção explícita de fim. Arquivos removidos após a descoberta usam a recuperação interna de documento não encontrado; traduções ausentes na descoberta não viram destinos.

`tests/reading-order.test.ts` cobre o resolvedor. `tests/continuous-reading.browser.cjs` verifica os dois sentidos, mudanças de categoria, URLs diretas, encerramento no último documento, indicadores do destino, histórico, layouts responsivos e movimento reduzido usando a coleção real. A execução utiliza a mesma instalação externa de Playwright da regressão do leitor.


Use o nome do diretório como slug técnico e defina um `name` oficial legível ao criar cada biografia (por exemplo `Env Auditor`, `Go Image Optimizer`, `URL Shortener`). Preserve siglas e nomes próprios; não traduza o nome oficial entre idiomas. Forneça as duas descrições localizadas e `icon.svg`. Não existe gerador separado de metadados. Bios legadas com nome ausente ou vazio recebem um nome derivado do slug com siglas comuns preservadas; bios ausentes, IDs inválidos e nomes que não sejam texto continuam inválidos. O fallback não substitui nomes explícitos. Cards, cabeçalhos do sumário e do leitor e rótulos de marcações usam o nome do catálogo; URLs e associações de marcações mantêm o slug. Execute `catalog:sync` após editar os metadados para atualizar a mesma linha no PostgreSQL pelo ID estável, sem migração de esquema.
