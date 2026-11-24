# Engineering Library: propriedade do catálogo, leitor e anotações

[Sumário](../index.md) | [English](../../en/architecture/current-implementation.md)

Revisado em 2026-11-10. Público: mantenedores Rails/Next e curadores. A: código inspecionado. Verificação estática difere de execução Rails/browser. O proprietário identifica este repositório/versão como privado, centralizando documentação das coleções autorizadas de portfólio e Viva Bem privado. Uma versão pública separada está planejada para depois.

<!-- reading-section: ownership -->
## Markdown e metadados têm responsabilidades distintas

Capítulos canônicos ficam em docs/<slug>/{en,pt-br}; API usa en/pt-BR. CATALOG_ROOT e DOCUMENTATION_ROOT precisam apontar à mesma coleção. PostgreSQL armazena identidade e anotações compartilhadas, sem corpos canônicos. Mapeamentos históricos do manifesto são metadados de validação/importação, sem comprovar quantidade fixa em runtime. Nova coleção TracePaw não deve ser omitida porque inventário antigo a antecede.

`Catalog::Files` valida slug/contenção, lê bios com YAML seguro e deriva categorias de bullets/índices existentes. `Catalog::Sync.call` percorre diretórios imediatos válidos sem symlink, exige ID/nome iguais nos idiomas e aborta antes de escrever com identidades inválidas/duplicadas. Usa transação/advisory lock, atualiza por stable_id e desativa ausentes sem apagar. Não migra bookmarks ou instala redirects após mudança de slug.

Sincronizar catálogo altera banco; não é validação Markdown. Diretório/bio novo não comprova indexação em execução. Nenhuma sincronização ou mutação de anotações ocorreu aqui. Não alterar hashes históricos/snapshots apenas para aceitar nova coleção no validador.

<!-- reading-section: reader -->
## Descoberta Next, Markdown e navegação

`frontend/lib/documentation.ts` descobre recursivamente com contenção/symlink, exclui bios, trata identidade README e suprime índices só navegacionais. IDs bilíngues canônicos, sem ordem por título traduzido ou página física, orientam sumário/leitura. Traduções ausentes ficam indisponíveis; caminhos iguais não comprovam equivalência semântica.

`frontend/lib/markdown.ts` interpreta remark/GFM em unidades semânticas, deriva slugs/fingerprints e respeita reading-section ou IDs de pergunta únicos. Duplicação é ambígua. Markdown documental e conteúdo rico de notas usam pipelines distintos; rehype-raw instalado não comprova HTML em capítulos. Usar Markdown comum, tabelas GFM e Mermaid suportado; preservar âncoras ao alterar títulos.

Paginação física é apresentação calculada no browser. Paginação PostgreSQL do catálogo não é paginação do leitor. Parser aprovado não comprova tabelas/código longos em toda resolução. Nenhuma interface/controle foi alterado pela atualização documental.

<!-- reading-section: search -->
## Busca e referências aprovadas

Rota GET document-search remove espaços, aceita 2–100 caracteres, percorre unidades do projeto/idioma selecionado e retorna até 80 resultados com trechos/âncoras e truncated. Usa substring sem diferenciar caixa, sem embeddings, busca semântica ou full-text PostgreSQL. Linhas de fontes aprovadas podem participar por source-search/source-references.

`approvedSource` em source-snapshot.ts é controle do gerador offline, sem leitor genérico de arquivos da máquina em runtime. Rejeita caminhos absolutos/traversal/ocultos/dependências, extensões não suportadas, saída da raiz real, binários/excesso e padrões reconhecidos de segredo. Limite: 512000 bytes. Complementa aprovação explícita; aprovar projeto não autoriza qualquer snapshot/publicação. Nenhuma geração ocorreu aqui.

<!-- reading-section: annotations -->
## Anotações compartilhadas e segurança

API Rails expõe projetos, bookmarks, highlights, notes e anotações combinadas. São compartilhados pela instalação com escopo projeto/documento/idioma, sem contas ou propriedade por navegador. CSRF não é identidade. Rotas de demos de notas só em desenvolvimento possuem mutações explícitas e não devem ser executadas como verificação inofensiva.

`Note::anchor_key` usa hash de block/start/end/exact, ignorando prefix/suffix de relocalização; mudar apenas contexto não altera identidade. Nota é UTF-8 até 5 MiB, com segmentos validados via Highlight. Highlight associado deve corresponder à localização. FK anula highlight_id ao remover destaque e preserva nota. Bookmarks usam localização lógica mais location_variant; notas são anotações, sem virar capítulos canônicos.

Schema declara índices/restrições, sem medir desempenho ou comprovar privacidade implantada. Manter notas, fontes, exportações e logs em fronteiras privadas aprovadas. Não adicionar identidades ocultas para explicar compartilhamento.

<!-- reading-section: operations -->
## Operações, verificação e recuperação futura

Compose existente usa PostgreSQL/Rails/Next e Dockerfile multi-target. Comandos da aplicação pertencem aos runtimes aprovados; Python estático funciona sem Docker. Startup/instalação e preparação de catálogo/banco têm efeitos e não foram invocados. [Verificação](../testing/documentation.md) distingue 28 testes de fixtures aprovados de Rails/browser não executados e resultados antigos.

Ollama/RAG, embeddings e geração assistida permanecem direção futura, sem infraestrutura implementada de busca. [Padrão documental](../training/documentation-standard.md) preservado detém rótulos, regras, templates e orientação de recuperação; este capítulo não o abrevia/substitui.

Fontes: backend/app/services/catalog/{files,sync}.rb, backend/config/routes.rb, backend/db/schema.rb, backend/app/models/note.rb; frontend/lib/{documentation,markdown,source-snapshot}.ts; frontend/app/api/document-search/[project]/route.ts; frontend/package.json; tools/check_docs.py e tools/check_catalog.py. Rever idiomas após mudanças de descoberta, identidade, parser, anotações, busca ou privacidade. Auditorias preservam datas e não estabelecem aceite atual de runtime.
