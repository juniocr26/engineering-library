# Relatório de catalogação — 2026-10-18

## Entrega e escopo

Catálogo implementado com navegação **Biblioteca → Projeto → Idioma → Índice → Categoria → Documento**. Entrada principal: [index.md](index.md); entradas por idioma: [English](en/index.md) e [Português brasileiro](pt-BR/index.md). As seis coleções têm dois READMEs, índices bilíngues, capítulos indexados, proveniência e entrevistas. Não há catálogo separado por assunto nem catálogo recursivo dentro da entrada Engineering Library.

Somente `engineering-library/docs/` foi alterado. Os cinco repositórios irmãos permaneceram limpos. Não houve stage, commit, push, rede, execução de aplicação, Docker, migração ou teste de integração de aplicação. Nenhuma funcionalidade de frontend, backend ou agente de IA foi implementada. O pequeno verificador em `docs/validation/` valida arquivos de documentação sem escrever ou executar aplicações; não é um agente nem framework de automação.

## Inventário e exclusões

Incluídos: `engineering-library`, `env-auditor`, `go-image-optimizer`, `payment-reconciliation-lab`, `rust-event-relay` e `url-shortener`. A descoberta considerou diretórios imediatos com marcador Git, documentação e estrutura própria, sem inferir projetos a partir de dependências ou fixtures.

Excluídos do inventário de projetos: `.github/` do diretório pai (metadados compartilhados), caches/dependências (`node_modules`, `vendor`, `.cargo-cache`), builds (`target`, `.next`, `dist`, `build`), cópias `.local-backups`, armazenamento `.dockerized-*`, internos Git e fixtures aninhadas. Não foram lidos valores de `.env`, dados de bancos, backups ou chaves. Somente os nomes de variáveis do template público da Library foram inspecionados. `rust-event-relay/docs/audit/` é evidência gerada histórica fora das coleções mantidas por idioma; não foi importada. `rust-event-relay/docs/pt-BR/manual/` está vazio e não gerou capítulo vazio. READMEs auxiliares de frontend/backend são referências de componentes, não projetos independentes.

## Árvore entregue

```text
docs/
├── index.md
├── catalog-review.md
├── catalog-provenance.json
├── validation/check_catalog.py
├── en/index.md                    # referências anteriores preservadas
├── pt-BR/index.md                 # referências anteriores preservadas
└── projects/
    ├── engineering-library/
    ├── env-auditor/
    ├── go-image-optimizer/
    ├── payment-reconciliation-lab/
    ├── rust-event-relay/
    └── url-shortener/
```

Cada projeto contém `README.md`, `README.pt-BR.md`, `docs/en/index.md` e `docs/pt-BR/index.md`. Cada categoria abaixo existe nos dois idiomas, tem `index.md` e páginas substantivas. Os índices listam todos os nomes de arquivos; ADRs e nomes significativos das fontes foram mantidos.

| Projeto | Categorias nos dois idiomas | Markdown na coleção |
| --- | --- | ---: |
| engineering-library | architecture, guides, operations, technical-interview, testing | 28 |
| env-auditor | architecture, guides, operations, security, technical-interview, testing | 40 |
| go-image-optimizer | adr, api, architecture, docker, guides, operations, security, technical-interview, testing | 50 |
| payment-reconciliation-lab | adr, api, architecture, database, docker, guides, operations, security, technical-interview, testing | 60 |
| rust-event-relay | adr, architecture, database, docker, guides, integrations, operations, security, technical-interview, testing | 154 |
| url-shortener | api, architecture, database, docker, guides, operations, security, technical-interview, testing | 52 |

## Contagens e preservação

- **248 arquivos Markdown importados** dos cinco repositórios irmãos: READMEs e páginas mantidas em `docs/en` e `docs/pt-BR`. São snapshots, com links adaptados e capítulos completos acrescentados aos índices; não são cópias necessariamente byte a byte.
- **12 entrevistas realocadas**, uma por projeto/idioma, preservando integralmente títulos, numeração e histórico. Os 12 caminhos antigos viraram atalhos para evitar duas cópias integrais da mesma entrevista. A nota sobre o status atual aparece somente na entrevista própria da Library.
- **126 novos Markdown de organização e conteúdo**, além dos importados e realocados. Incluem 98 índices de categoria, índices/READMEs próprios da Library, proveniência, arquitetura atual, propostas futuras, entrevista complementar, entrada central e este relatório.
- Total: **386 novos Markdown**, **14 Markdown existentes atualizados**, um JSON novo de proveniência e um verificador Python novo. Total final: **436 Markdown** dentro de `docs/`, dos quais **384** nas seis coleções de projeto.
- **0 traduções de fontes monolíngues necessárias**: os caminhos importados já tinham correspondentes. Foram redigidas **11 novas páginas explicativas em pt-BR**, equivalentes às versões inglesas (seis proveniências e cinco páginas próprias da Library); navegação e README próprio também são bilíngues. Essas contrapartes estão incluídas nas contagens de criação, não são arquivos adicionais.
- Os demais documentos anteriores da Library foram preservados. Guias de ambiente e validador são reutilizados por referência. Índices antigos conservam seu conteúdo e ganham seleção de projetos e lista completa de referências.

[Mapa de proveniência](catalog-provenance.json): revisão Git e remote observados, caminhos importados e SHA-256 das fontes, origem/revisão/hash das entrevistas realocadas, títulos preservados e fontes selecionadas para inspeção. Não é banco nem índice de busca. Nenhum remote foi consultado pela rede. O remote de payment-reconciliation-lab ainda aponta para `aurora-bakery`; isso foi registrado sem inventar outro endereço.

## Entrevistas

Todos os projetos possuem `technical-interview/index.md` e `study-guide.md` nos dois idiomas. O material existente cobre mecanismos, falhas, alternativas, limites e aprofundamentos. A Library ganhou também `application-and-catalog.md`, com Q101–Q106 alinhadas entre idiomas: Rails/Next.js, Compose/bind mounts, PostgreSQL/liveness, catálogo bilíngue, inferência local versus APIs e geração incremental baseada em evidências. Cada resposta distingue código inspecionado, arquitetura documentada e proposta. Não se atribuem motivações originais sem evidência.

## Validação executada

Executar da raiz do workspace:

```sh
python3 -B engineering-library/docs/validation/check_catalog.py
python3 -B engineering-library/tools/check_docs.py --workspace .
python3 -B -m unittest discover -s engineering-library/tools -p test_check_docs.py -v
git -C engineering-library diff --check
git -C engineering-library diff --stat
git -C engineering-library status --short --untracked-files=all
```

- **Verificador do catálogo:** seis projetos, 248 importações presentes; 436 Markdown; zero erros e zero avisos. Confere inventário, existência de links locais/âncoras, alcance desde entrada central e índices de cada projeto, caminhos bilíngues, IDs Q equivalentes, capítulos com conteúdo, títulos das entrevistas preservados, hashes das fontes importadas e duplicatas exatas. Nenhuma duplicata exata entre páginas de projeto ao final.
- **Validador legado:** exit 1, **16 erros e 18 avisos**. Dois erros preexistentes são a categoria desconhecida/vazia `rust-event-relay/docs/pt-BR/manual`; 18 avisos são links restritos de fixtures do Go, sem leitura de seus destinos. Os outros 14 erros são falsos positivos `obsolete-library-name`: a regra legada rejeita o nome `technical-interview` obrigatório neste marco nos links dos dois índices e 12 atalhos. O scanner legado não percorre `docs/projects/`; por isso não substitui a verificação adicional. Sua implementação/configuração fora de `docs/` não foi alterada. Não se declara que esse comando passou.
- **Testes do validador documental:** 22 testes passaram. São fixtures sintéticas temporárias de navegação/parser/segurança, não testes de aplicações ou infraestrutura.
- **Git:** `diff --check` passou; diff e arquivos novos inspecionados. Conferência dos cinco irmãos: status vazio. Todos os caminhos modificados/novos da Library ficam em `docs/`. Nada foi adicionado ao stage.
- **Preservação:** todos os títulos das 12 entrevistas coincidem com a revisão original; equivalência de IDs bilíngues passou. Links de código recebem checagem de existência, sem importar código para a biblioteca. Links restritos foram convertidos em texto nas cópias.

O parser compartilhado cobre um subconjunto de Markdown: não certifica HTML/MDX arbitrário, equivalência completa ao renderizador GitHub, qualidade semântica das traduções ou veracidade técnica. Nenhuma URL externa foi buscada. Inspeção estática seletiva de código/configuração/testes não equivale a auditoria de todos os arquivos nem a resultados de execução.

## Lacunas e pontos para revisão

- Os marcos Rust contêm afirmações datadas contraditórias sobre features, rollout e prontidão. Foram preservados como história. Começar pelos documentos de cenários e Milestone 6.3; este trabalho não reconfirmou serviços nem medições.
- A antiga resposta Q001 da Library descrevia fase sem API/banco; uma nota temporal explícita contextualiza o scaffold atual. Rails possui health, Next.js possui landing/status e PostgreSQL possui configuração de desenvolvimento; isso não é API de catálogo, livro interativo ou IA implementada.
- Payment Reconciliation Lab ainda mantém catálogo legado somente leitura. Não há conciliação, matching, webhook ou Stripe implementados, apesar do nome/direção futura.
- Benchmarks, alta disponibilidade, restauração, implantação de produção e integração real de dependências não foram revalidados. Resultados históricos mantêm sua data/escopo.
- A coleção textual está centralizada, mas links de código local exigem a organização do workspace com repositórios irmãos. Uma exportação isolada precisaria de conversão para URLs remotas verificadas; isso não foi presumido.
- Tradução de conteúdo herdado foi preservada; paridade estrutural não é uma revisão editorial integral. Atualizações futuras precisam comparar fontes, preservar notas autorais e julgar significado técnico.
- O validador legado precisa de evolução futura para conhecer a hierarquia por projeto e a categoria exigida. Este marco não muda ferramentas/configuração fora de `docs/`.
