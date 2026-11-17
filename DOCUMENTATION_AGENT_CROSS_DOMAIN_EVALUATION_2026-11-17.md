# Campanha de documentação entre domínios — em andamento

Início verificável: **2026-11-17 03:50:23 America/Sao_Paulo (06:50:23 UTC)**. A leitura inicial dos anexos precedeu esse horário e está excluída da duração. Campanha autorizada para aproximadamente 12 horas de trabalho substantivo, sem espera artificial. Este é um checkpoint; não constitui encerramento nem certificação de qualidade.

O working tree inicial de Engineering Library estava limpo, HEAD `dc6201133797a7308071aaf1d3eefad6d7edf314`. Implementações verificadas: caller `1.9.12`, coordenador de projetos `1.0.1`. O relatório de 16/11 já não existe na raiz atual; foi consultada sua versão histórica em `535231b:DOCUMENTATION_AGENT_GRAPHICS_EVALUATION_2026-11-16.md` e o recibo privado de encerramento. O texto histórico disponível é um checkpoint, não comprovação de todos os resultados finais.

## Inventário original

Todos os clones estão em `/Users/juniorosa/Documents/Projetos/Portifólio`, foram identificados por remoto e estavam limpos. São somente leitura; nenhum projeto permanente Viva Bem integra a avaliação.

| Clone | Remoto GitHub | Revisão original |
|---|---|---|
| redis | redis/redis | 1a9eb051aa243f9d0e5a8a8afa6c4801bf52a9fb |
| duckdb | duckdb/duckdb | e41515de6f7efb19b43293ab49cb967cd64ab9f9 |
| ruff | astral-sh/ruff | 0222c19dd8e0c9a927f2e47bf3774a108431da25 |
| helix | helix-editor/helix | 49986e6674e5658164a88f599ec8c822e62ad0db |
| starlette | encode/starlette | 271c277da0ff64e2048a4d46ecc812b9d61db5f6 |
| sdk-go | temporalio/sdk-go | 7e0d845246d36fc7f62ade2af885554f94c29db9 |
| esp-hal | esp-rs/esp-hal | e800b19c30bc208aa93d600fb158cf8cef42a4fe |
| opencv | opencv/opencv | 5d0660acfed08650cafec4876b4792a369a20601 |
| core | home-assistant/core | 67ec6a4b7dcaed80b59930be6744f4944b5073e3 |
| prometheus | prometheus/prometheus | b2a602494b65bda38316eabaef7e0d834a6814dd |

## Evidência e artefatos

- Baseline privado: `.local-backups/cross-domain-20261117/baseline.json`, com estado Git, hash do índice, hashes de ambientes e documentação permanente.
- Fontes e plano congelados: `source-freeze.json` e `plan.json` nesse diretório privado.
- Referências Codex: `.local-backups/cross-domain-20261117/codex-reference/<clone>/{en,pt-br}.md`, 20 arquivos congelados em `reference-freeze.json` antes da inferência local. São referências limitadas e também exigem avaliação independente.
- Geração real: backend existente, `make docs DOCS_WORKFLOW=project DOCS_ARGS='--config /docs/.evaluations/cross-domain-20261117/plan.json --project <clone>'`.
- Artefatos temporários: `docs/.evaluations/cross-domain-20261117/library/projects/<clone>/{en,pt-br}.md`; logs e resultados em `docs/.evaluations/cross-domain-20261117/`. A existência e os capítulos serão contados após cada execução. Uma resposta bruta não conta como documento montado.
- Contexto local: somente trechos explícitos de código e skills ativas; sem referências Codex, documentação upstream ou feedback do revisor. Modelo local `llama3.2:3b`, contexto 4096, uma thread, pesquisa offline.

## Ambiente

Reutilizados os containers existentes backend/Ollama; clones já montados somente leitura em `/extra-sources-1`. Serviços backend, frontend, PostgreSQL, Ollama e pesquisa estavam saudáveis no preflight. Recursos, redes, volumes e memória foram inspecionados. Nenhuma porta, serviço ou volume novo criado. Nenhum restart ou limpeza global realizado. Execução da aplicação e testes serão feitos em Docker; Python do host foi usado somente para inventários de arquivos e preparação dos artefatos.

## Protocolo e pendências

Similaridade histórica permanece separada: 40% semântica, 25% cobertura, 15% equivalência bilíngue, 10% estrutura e 10% texto normalizado. A política de qualidade independente será congelada antes das notas: 35/20/15/10/10/10 conforme a regra adicional 3. Incremental ainda não avaliado implica nota provisória, sem inventar resultado. Erros factuais críticos bloqueiam prontidão de publicação independentemente das notas e do aceite do dono.

Pendentes: geração e revisão factual dos dez projetos; comparação antiga/revisada; qualidade absoluta; mutações/restauração; no-op; regressões; diagnóstico real do leitor; apresentação temporária no catálogo quando viável; limpeza seletiva; inventário final e sugestões de commits EN/PT-BR. Nenhuma meta percentual foi atingida ou medida até este checkpoint.

## Primeiro marco de execução

Referências independentes: 20 arquivos EN/PT-BR, quatro seções por repositório, congelados antes da primeira inferência local. Plano: 40 passes. A primeira tentativa Redis terminou em 747,23 s: event-loop gerado, configuração rejeitada por tradução de literais e persistência interrompida por timeout de transporte; build ainda não executado nessa tentativa. O coordenador não montou um projeto completo após a falha de transporte. DuckDB prossegue. Resumos de seções existem; não são apresentados como pacotes completos de projeto.

Foi encontrada uma inversão factual no primeiro texto Redis: diz que o descritor **dentro** do limite produz erro, enquanto o código testa `fd >= setsize`. A tradução também contém vocabulário incorreto. A validação literal não detecta essa inversão. Outro retorno traduz `yes/no` para `sim/não` e atribui relação não demonstrada entre conversão booleana e `server.saveparams`; esse retorno foi rejeitado pelo guard existente. Nenhum desses resultados recebeu aprovação de publicação.

### Experimentos executados

- Redis: compilação de `redis-server` e `redis-cli` do código original, sem módulos opcionais/TLS; PING, SET/GET, SAVE e leitura após reinício passaram usando socket Unix e diretório sintético, sem porta TCP. Um teste separado do corpo original de `yesnotoi` passou, detectou mutação e passou após restauração.
- DuckDB: corpos originais de Transaction, com declarações/dependências sintéticas para isolar estado somente leitura; original e restauração passaram, mutação foi detectada. Não equivale a executar o banco completo.
- Ruff: `resolve_default_files` original, com caminhos da biblioteca padrão; original/restauração passaram e mutação foi detectada.
- Helix: enum e método de operações originais, com String como substituto sintético de Tendril; contagem Unicode passou, mutação para bytes foi detectada e restauração passou. Nenhum editor completo foi executado.
- esp-hal: método `delay_nanos` original, Duration/Delay instrumentados sinteticamente; fronteiras 0/1/999/1000/1001/u32::MAX verificadas, truncamento mutante detectado e restauração passou. Nenhuma precisão temporal ou dispositivo foi certificado.
- OpenCV: guard CMake original rejeitou build na árvore. Primeiro candidato experimental tinha sintaxe inválida; preservado como falha do experimento. Candidato corrigido altera o operando da igualdade, permite o caso mutado e volta à rejeição original após restauração. Não houve teste de processamento de imagem.
- Starlette: módulo Config original completo executado em Python 3.14, com precedência ambiente/arquivo/default, conversão e erros; mutação de booleano detectada e restauração passou.
- Home Assistant Core: funções originais extraídas via AST e constante original de tamanho, exceção sintética; fronteiras de identificador e estados 255/256 verificadas, mutação detectada e restauração passou. Nenhum bootstrap ou integração de dispositivos executado.
- Temporal sdk-go: testes upstream `TestRawValueCompositeDataConverter` e `TestCompositeDataConverter_MixedValues` passaram no módulo converter. Nenhum servidor Temporal foi executado.
- Prometheus: primeira tentativa revelou necessidade de gravar go.work.sum e preservou clone somente leitura; segunda tentativa, em cópia isolada, esgotou tmpfs ao extrair dependências. Terceira tentativa usa volume Docker da campanha em disco; resultado pendente. Não há alegação de erro funcional no projeto por essas falhas ambientais.

### Candidatos em avaliação

O coordenador atual falha na segunda montagem bilíngue com `JSON::GeneratorError` por bytes UTF-8 lidos como ASCII-8BIT. Após corrigir apenas o encoding em cópia privada, dois testes também reproduziram regravação desnecessária de arquivos. Candidato privado `1.0.2` preserva bytes/mtime/inode de saídas idênticas, preserva idioma não alterado e faz rollback de bytes Unicode diante de falha na segunda gravação. Passou em 12 testes/48 asserções. Ainda não promovido durante o congelamento da primeira geração.

A ferramenta `tools/documentation_quality.py` define qualidade independente, estados explícitos por afirmação, crédito parcial de cobertura e um controle por grupos estritos. Não muda resultados históricos. Notas sem revisão completa permanecem incompletas; incremental ausente produz somente nota provisória normalizada sobre os 90% avaliáveis. Erros críticos bloqueiam prontidão, sem transformar similaridade em gate de qualidade. Os testes incluem alteração de evidência, critérios sem evidência, erro crítico compartilhado e inventário incompleto. A política foi congelada antes de medir notas desta campanha.

### Leitor — evidência real limitada

O diagnóstico existente `reader-stability.browser.cjs` falhou esperando paginação pronta em 60 s. Probes Chromium desktop 1720×876 e mobile 390×844 confirmaram HTTP 200, 47 unidades Markdown na superfície oculta e **zero unidades visíveis**; `data-pagination=measuring` e `aria-busy=true` persistiram. Fontes carregadas, sem imagens ou elementos pendentes. Geometria disponível e estável nos snapshots.

Um probe observou zero callbacks rAF/ResizeObserver/MutationObserver da aplicação e nenhuma associação React na superfície do leitor. Os scripts retornaram HTTP 200 com MIME JavaScript; houve erros de handshake HMR. Isso localiza a primeira fronteira ainda sem sucesso na hidratação/execução cliente, mas **não prova que HMR é a causa**. As capturas visuais confirmam “Paginando…” permanente. Nenhum componente visual foi alterado. Artefatos privados: `reader-existing-diagnostic.log`, `reader-probe.ndjson`, `reader-trace.json`, `reader-hydration.json`; capturas temporárias dentro da árvore de avaliação serão arquivadas antes da limpeza.

## No-op e avaliação inicial verificados

O candidato de montagem foi promovido para coordenador `1.0.2`; caller permanece `1.9.12`. A versão de evidência de seções permanece `1.0.1`, pois a mudança foi somente de montagem e não altera a seleção nem o prompt da inferência inicial. Os processos iniciais de Redis/DuckDB já haviam carregado o coordenador anterior; os seguintes usam a montagem corrigida, com o mesmo caller, modelo, fontes, skills e prompt. Isso é registrado para não atribuir melhoria de prosa à correção de montagem.

Regressão offline completa de documentação: **101 testes, 547 asserções, zero falhas/erros/skips**. A ferramenta de qualidade passou em 11 testes. Evidência privada em `documentation-regressions.log` e `quality-tests.log`.

Uma cópia congelada do pacote DuckDB foi montada em container descartável com os mesmos caminhos internos e **rede desativada**. `make docs` real com baseline falhou no journal UTF-8 após no-op dos quatro passes. Com a correção, a primeira execução atualizou apenas `assembly.json` para a nova versão, sem reescrever Markdown. A segunda preservou hash, mtime e inode dos **19 arquivos verificados**, inclusive manifest de montagem; o contador de requisições de modelo permaneceu em quatro, todas históricas. Não houve inferência nova.

Na cópia isolada, `make docs` também preservou a documentação em onze cenários: fonte original, alteração em arquivo não selecionado, comentário irrelevante em arquivo selecionado, restaurações, mudança de estado, rename, remoção de contrato e texto humano fora dos blocos gerenciados de índice. **Limitação reproduzida:** até um comentário fora dos trechos selecionados muda o hash do arquivo inteiro e exige inferência. Mudanças relevantes/rename foram detectadas e, com modelo indisponível de propósito, falharam preservando as versões anteriores. Remoção invalidou os ranges e preservou os documentos. Isso comprova detecção/preservação/restauração, **não** atualização factual automática após mutação; esta ainda precisa de inferência real e revisão dos dois idiomas. Um erro inicial de sintaxe do harness também foi preservado antes do retry corrigido.

### Primeira comparação: DuckDB, quatro seções limitadas

Escopo declarado pelo avaliador: `chapter` (agregado de quatro seções), não projeto inteiro. A referência também omite arquitetura ampla, testes e operações. Os números abaixo não são notas de qualidade de todo o DuckDB.

| Medida | Referência Codex | Geração inicial local |
|---|---:|---:|
| Qualidade provisória, incremental não avaliado | 88,89% | 58,52% |
| Precisão das afirmações emitidas no inventário revisado | 100% | 71,43% |
| Cobertura das afirmações obrigatórias, com crédito parcial | 100% | 30% |
| Controle por grupos estritos | 100% | 0% |

Similaridade composta no protocolo original: **27,68%** (semântica 10%; cobertura por grupos estritos 0%; equivalência bilíngue 85,71%; estrutura 100%; texto normalizado 8,23%). O controle de grupos explica perda de informação em cobertura, sem apagar os erros factuais. Não foi calculado um composto revisado incompatível para alegar melhoria.

Dois problemas impedem prontidão do pacote local: atribuição errada da condição de DBConfig às opções “já definidas” em vez de registro conhecido, e interpretação imprecisa da faixa de compatibilidade CMake como mínimo de versões. Também faltam transição SetReadWrite, SetModifications vazio e detalhes de ownership/configuração. O português omite active query no construtor, traduz o identificador Transaction e deixa “handle” sem tradução. A classificação independe da similaridade baixa. Pacotes e julgamentos congelados em `.local-backups/cross-domain-20261117/duckdb-review.json`.

Prometheus: o teste amplo de configuração também excedeu 1 GiB de memória ao compilar SDKs de descoberta; o container experimental foi encerrado seletivamente. Um teste menor com as funções originais de timestamp passou nas fronteiras positivas/negativas, conversão UTC e ida/volta em milissegundos; a mutação de arredondamento para truncamento foi detectada e a restauração passou. Temporal converter passou adicionalmente em contrato nil no pacote real, mutação para rejeição indevida e restauração com hashes idênticos, além dos controles upstream.

### Revisão da própria referência Codex

Antes da inferência ampliada, foi detectado um erro na referência independente ampliada DuckDB: ela dizia que `ConvertParamListToMap` movia os valores do vetor. O código passa `val` como lvalue; o construtor recebe Value por valor e move sua cópia local para o membro. A alegação original de transferência dos elementos do vetor não tinha suporte. A seção v1 foi classificada como rejeitada por erro de ownership; os arquivos e hashes originais foram preservados. Uma v2 revisada no código foi congelada separadamente em `expanded-codex-reference-reviewed/`, ainda antes da inferência ampliada. As primeiras referências de quatro seções e seus resultados não foram alterados. Uma revisão de clareza também trocou “shutdown boundary” por “main-loop boundary” no texto Redis ampliado. Isso não representa ganho do modelo local nem permite tratar Codex como verdade absoluta.

A interpretação de `cmake_minimum_required(VERSION 3.14...3.29)` foi conferida também na [documentação oficial do CMake](https://cmake.org/cmake/help/latest/command/cmake_minimum_required.html): 3.14 é o mínimo e 3.29 define a versão de políticas, sem proibir versões posteriores. A consulta pública não recebeu código privado nem foi incluída no contexto do modelo local.

### Separação metodológica de qualidade — protocolos preservados

O protocolo de qualidade v1 limitava a dimensão cobertura pelo inventário de afirmações derivado da referência. Isso acoplava qualidade absoluta à sobreposição com Codex. O protocolo **v2** remove esse limite: a cobertura absoluta usa critérios revisados contra fontes, enquanto cobertura parcial de afirmações e grupos estritos continuam diagnósticos separados. Pesos 35/20/15/10/10/10 e gate factual foram preservados. O código, a política, os packets e o replay v1 permanecem em `quality-policy-v1/`; o v2 foi congelado em `quality-policy-v2-frozen.json`.

Nos **mesmos arquivos e julgamentos** DuckDB, a nota provisória muda de 58,52% (v1) para 59,26% (v2). A referência permanece 88,89%. Essa diferença é **somente metodológica**, não melhoria do agente. A similaridade original continua 27,68%. As comparações futuras entre geração inicial e candidatos devem usar a mesma política v2 e o mesmo corpus congelado.

Ruff inicial: qualidade provisória v2 65,74%, referência 88,89%, similaridade 41,54%. Há omissões importantes e uma afirmação sobre a implementação do Maturin sem suporte no trecho citado; esse trecho não entrou no catálogo ativo. Helix inicial: qualidade provisória v2 61,11%, referência 88,89%, similaridade 29,55%; gate crítico rejeita a inversão do fallback de runtime e a confusão entre membros e dependências do workspace. Todos são agregados de quatro seções limitadas, sem nota de projeto completo.

A primeira integração temporária no catálogo contém **duas seções Ruff revisadas parcialmente**, com 13 arquivos próprios, índices portáteis e navegação entre idiomas. O capítulo de watcher com guardas incompletas e o de empacotamento sem fonte suficiente ficam na evidência privada. O catálogo retornou a entrada e o frontend recuperou o contrato real; 12 arquivos Markdown e 12 links locais foram conferidos sem erro. Isso não comprova renderização visual pronta, que permanece bloqueada no diagnóstico do leitor. `catalog-database-before.json`, `catalog-database-owned.json` e `temporary-catalog-owned.json` registram a restauração futura; o lifecycle existente capturou os dez destinos antes da primeira escrita.

### Correção do diagnóstico do leitor — origem canônica

Os parágrafos anteriores registram uma hipótese histórica, não a conclusão atual. A falha de hidratação foi reproduzida com o override `127.0.0.1:3000`; na origem configurada pelo projeto, `localhost:3000`, o mesmo serviço e os mesmos arquivos renderizam sete unidades visíveis, com fontes carregadas e sem erros de página. A allowlist de origem do servidor de desenvolvimento Next.js inclui localhost; o IP usado no diagnóstico não estava nela. Um A/B isolado também renderizou com configuração original e com debug channel desativado, sem evidência para promover essa alteração. Nenhum componente visual ou configuração do serviço foi alterado.

A captura `reader-origin-localhost.png` foi inspecionada visualmente: conteúdo legível em duas folhas, controles e navegação presentes. Um smoke real na origem correta passou em desktop 1720 px nos dois idiomas: avançar, retornar e redimensionar preservando âncora, sem erros JavaScript. O teste móvel encontrou interceptação de clique pelo portal do overlay de desenvolvimento Next.js; o diagnóstico permanece em andamento. A suíte existente passou do estado ready, mas falhou em seu helper de âncora ao procurar atributo de destaque em uma unidade de código que não o possui. Esses resultados não equivalem a aprovação de toda a suíte de estabilidade.

### Revisões iniciais adicionais — mesmo protocolo v2

| Corpus de quatro seções | Qualidade local provisória | Similaridade original | Classificação absoluta |
|---|---:|---:|---|
| ESP HAL | 65,74% | 33,30% | Incompleto |
| Temporal SDK Go | 72,22% | 34,02% | Incompleto |
| Home Assistant Core | 64,81% | 28,69% | Incompleto |

Incremental ainda não avaliado nesses packets; não são notas de projeto inteiro. As referências limitadas recebem 88,89%, também incompletas pela ausência de arquitetura e operações amplas. ESP HAL omite ceiling de nanossegundos, sealing, afinidade de core, forwarding DelayNs e chama membros de workspace de dependências. Temporal preserva o bypass RawValue e prioridade ProtoJSON, mas omite propagação imediata de erro e possui duas seções rejeitadas. Core omite recoverability e defaults de sincronização; traduz duas strings do enum como se fossem valores de API. Arquivos, fontes e julgamentos estão congelados individualmente. O rótulo legado de similaridade “conditionally accepted” para Temporal não significa prontidão: sua cobertura estrita é zero e a avaliação absoluta permanece incompleta.

O smoke móvel passou em EN/PT após fechar o indicador de desenvolvimento com um clique normal: avanço, retorno e resize com âncora preservada, sem erros de página. A condição é explícita: com o indicador aberto, o botão anterior fica obstruído. Não houve clique forçado, alteração de CSS nem correção visual aplicada. Isso é evidência de navegação funcional, com uma limitação da apresentação em desenvolvimento.

Um candidato privado de sumário na montagem passou em 13 testes/62 asserções, mas **não foi promovido**: usava anchors HTML que o parser/renderizador atual do leitor ignora (`skipHtml`). O teste verificava correspondência de strings Markdown, sem comprovar navegação no produto. O candidato e essa contraprova foram preservados em `navigation-candidate-v1/`. A política de cobertura em preparação foi isolada desse formato para evitar atribuir ganho de organização à geração factual.

### Contraprova de navegação nas referências — notas anteriores preservadas

O parser real `frontend/lib/markdown.ts` foi executado em Docker sobre os vinte arquivos de referência congelados. **79 de 80 destinos do sumário não correspondem a uma unidade navegável do leitor** (só `event-loop` em Redis EN coincide com o slug do heading). Os anchors HTML são utilizáveis em renderizadores como GitHub, mas não são portáveis para este leitor, que os ignora. As fontes remotas continuam válidas e fixadas por revisão.

Revisão de julgamento, sem trocar política v2 nem pesos: `indexes_navigation` e `portable_links` das referências passam de completo a parcial. Nas seis avaliações já concluídas, a qualidade Codex provisória passa de **88,89% antes da auditoria para 83,33% depois dela**. As duas notas e a evidência do parser ficam nos packets `*-review-navigation-reviewed.json`. As notas locais e toda similaridade original permanecem idênticas. Isso corrige uma avaliação favorável demais à referência; não é progresso de geração nem mudança retroativa dos arquivos. A classificação absoluta continua incompleta.

### Experimentos adicionais de contratos

A classe original `ConfigEntryState` passou no teste de seus oito valores e flags recoverable. Mutar `loaded` de true para false foi detectado; a restauração tem hash idêntico. O primeiro harness tentou analisar o módulo inteiro com Python 3.11 e falhou na sintaxe `type` de Python mais novo. O retry executou só a classe original delimitada, sem alegar compatibilidade do módulo completo ou boot do Home Assistant.

A função original Prometheus `verifyLabelLimits`, com seus pacotes reais `labels` e `model`, passou em nil/limites desativados, igualdade de contagem e comprimento UTF-8 medido em bytes. A mutação `>` para `>=` foi detectada no limite igual, e a restauração passou. Executado sem rede no volume privado da campanha; não equivale a teste de coleta em rede nem build completo do Prometheus.

Um candidato privado de validação identifica o falso positivo de unicidade em “um único byte”, que expressa quantidade em português. Sua suíte passa em 71 testes/411 asserções preservando controles de unicidade real. Ainda não foi promovido. Remover esse falso positivo não tornaria a resposta Redis aprovada: outra afirmação atribui little-endian a `rdbLoadTime` sem suporte no trecho. Validação mecânica e aprovação factual continuam distintas.

### Candidato de recuperação explícita — contraprova e execução real

O candidato privado do coordenador adiciona `--project SLUG --recover rollback|complete` para a montagem. O journal versionado registra bytes anteriores/candidatos dos idiomas e do manifest, sem inferência. Preflight rejeita arquivos humanos, symlinks, paths extras e hashes inconsistentes; uma interrupção durante recuperação mantém estados próprios reconhecíveis para retry. Uma segunda verificação detecta edição humana chegada depois do preflight. Journals legados continuam bloqueados para inspeção manual.

Suíte privada: **22 testes/147 asserções**, zero falhas/erros/skips. Em container isolado sem rede e sem checkout de origem montado, documentos reais DuckDB congelados foram usados com uma nota sintética de fault injection, sem alterar seus fatos. Falha na gravação do manifest deixou o journal pendente. `make docs` baseline rejeitou a opção de recuperação; o candidato concluiu rollback e complete com exit 0. Rollback restaurou os hashes UTF-8 e preservou mtime/inode do inglês não alterado; complete alinhou os hashes do manifest com os dois arquivos. A montagem seguinte foi no-op. Isso demonstra recuperação de bytes, não aprovação factual da documentação DuckDB. Um primeiro harness sem Bundler falhou em carregar Nokogiri e foi preservado antes do retry corrigido.

Ruff temporário: oito combinações capítulo/idioma/viewport passaram no navegador real. Em mobile foi necessário avançar uma página para chegar ao contrato após a proveniência; o primeiro harness pressupunha incorretamente que o símbolo estaria na página inicial. O retry navegou com controles reais, sem forçar clique. Evidência e capturas em `reader-catalog-ruff-paged.ndjson` e no diretório privado de avaliação.

### Baseline dos dez projetos — quatro seções por projeto

As 40 seções planejadas resultaram em **35 seções geradas e cinco rejeições de validação** após completar timeouts. Há dez pares EN/PT montados em `docs/.evaluations/cross-domain-20261117/completed-baseline-library/projects/<slug>/`. As quatro tentativas com timeout300, as respostas completas com timeout900 e as montagens originais permanecem separadas. Um audit mecânico conferiu **44 requisições**: cada card coincide com os ranges originais, sem documentos upstream, referências Codex ou feedback no contexto inicial. Isso verifica identidade/exclusão do contexto, sem provar entendimento semântico.

| Projeto | Qualidade Codex provisória após auditoria | Qualidade local provisória | Similaridade original | Gate absoluto local |
|---|---:|---:|---:|---|
| redis | 83,33% | 62,50% | 26,02% | Rejeitado por erro crítico |
| duckdb | 83,33% | 59,26% | 27,68% | Rejeitado por erro crítico |
| ruff | 83,33% | 65,74% | 41,54% | Incompleto |
| helix | 83,33% | 61,11% | 29,55% | Rejeitado por erro crítico |
| starlette | 83,33% | 72,22% | 36,87% | Incompleto |
| sdk-go | 83,33% | 72,22% | 34,02% | Incompleto |
| esp-hal | 83,33% | 65,74% | 33,30% | Incompleto |
| opencv | 83,33% | 54,94% | 36,83% | Rejeitado por erro crítico |
| core | 83,33% | 64,81% | 28,69% | Incompleto |
| prometheus | 83,33% | 72,22% | 30,24% | Incompleto |

As notas são do agregado de quatro trechos, **não de projetos completos**. Incremental segue não avaliado nesses packets: qualidade normalizada sobre 90 pontos, sem nota completa. Os 83,33% das referências substituem somente o julgamento anterior de navegação; todos os 88,89% pré-auditoria e a política anterior permanecem rastreáveis. A precisão de 100% em inventários estreitos não demonstra completude nem certificação de toda a prosa/projeto. Similaridade não decide publicação.

O coordenador com recuperação explícita foi promovido a **1.0.3**. Regressão completa após a promoção: **111 testes/646 asserções**, zero falhas/erros/skips; ferramentas: **68 testes**, todos passaram. Caller1.9.12 e evidência de seção1.0.1 permanecem, preservando os fingerprints das fontes. O plano ampliado de 30 seções foi iniciado de modo monitorado às **09:57:08Z**, depois de congelar 209 arquivos da rodada complementar/montagem; suas referências independentes revisadas já estavam congeladas.

### Integração temporária observável nos dez projetos

O catálogo contém dez entradas próprias: duas seções Ruff e uma seção parcial revisada de cada outro repositório. São **112 arquivos temporários próprios**, incluindo 102 Markdown e dez cópias do fallback existente; 102 links locais foram validados sem problemas. As montagens completas e rejeições permanecem separadas. A apresentação dos nove capítulos adicionais encurta apenas a proveniência; fatos/citações permanecem, exceto OpenCV, que usa o primeiro período verificado e identifica explicitamente a seleção editorial. As notas iniciais não foram recalculadas sobre esses recortes.

**40 combinações projeto/idioma/viewport passaram no navegador real**, com conteúdo técnico visível, paginação ready, fontes carregadas e zero erros de página. Capturas OpenCV móvel PT e DuckDB desktop EN foram inspecionadas visualmente. Os trechos de código usam a rolagem horizontal existente; o indicador Next continua sendo uma limitação de desenvolvimento para cliques no botão anterior móvel. Esses checks não certificam todas as páginas, todos os links ou a suíte de estabilidade inteira.

A inclusão no catálogo usou a tabela existente, após checar ausência de donos dos slugs, e registrou exatamente dez linhas próprias. A primeira tentativa de registrar evidência em /sources falhou por mount read-only antes de alterar o banco; o retry gravou na árvore de avaliação autorizada e passou. Os dez destinos foram capturados pelo lifecycle antes da primeira escrita; todos os arquivos, linhas e mídia próprios serão retirados no encerramento. Originais e material permanente permanecem preservados.

### Separação de candidatos de validação — sem ganho fictício por contagem

Replay das **40 respostas completas congeladas**, usando a validação real em memória e os mesmos arquivos fonte: o candidato combinado bloqueou a chamada OpenCV sem suporte e removeu o falso positivo Redis de “um único byte”; a quantidade aceita permaneceu 35. A v1 verificava “calls/invokes”, mas não a redação real “uses the ... function”; não detectou o caso real apesar de testes sintéticos passarem. Essa v1 foi preservada, a sintaxe capturada foi adicionada e a v2 detectou o erro. Os testes passaram em 73 casos/422 asserções.

A política foi então dividida: o candidato **somente de símbolo chamado** preserva a rejeição Redis existente e altera apenas uma decisão entre as 40 respostas, bloqueando o bundle OpenCV que contém a chamada sem suporte. São 34 aceitos mecanicamente contra 35 no baseline; não é melhoria de compreensão nem certificação dos demais aceitos. A correção de cardinalidade fica privada: permitir esse texto não corrige a alegação separada de little-endian no mesmo bundle. O caller ativo continua 1.9.12. Uma regeneração real do caso OpenCV e do controle correto Ruff foi preparada, sem feedback ou referência no contexto, para depois da rodada ampliada.

### Candidato de remoção de duplicatas exatas — informação preservada

A configuração Starlette gerou a mesma explicação de `_perform_cast` três vezes, com a mesma citação. Um candidato separado valida **todos** os itens primeiro e remove somente repetições com o mesmo evidence_id, inglês e português byte a byte. Traduções diferentes, cards diferentes e falhas de validação permanecem. A resposta bruta continua imutável.

Suíte privada: 73 testes/424 asserções passaram. Replay das mesmas 40 respostas: todas as decisões de validação permaneceram iguais; os conjuntos de blocos únicos de prosa/citação EN/PT são idênticos. Apenas Starlette configuração mudou: **4 para 2 blocos** por idioma, de 4.518 para 2.150 bytes EN e de 4.627 para 2.201 bytes PT no corpo dos fatos. Isso é remoção de repetição sem informação nova, não aumento de precisão ou cobertura. As notas iniciais e as respostas originais não foram alteradas.

O candidato combinado de renderização reúne somente esse dedup e o guard de chamada sem suporte; exclui a dispensa de “único byte”. Foram preparados três casos de `make docs` real (controle Ruff, duplicatas Starlette e chamada OpenCV), ainda sem iniciar inferência em paralelo à rodada ampliada. Sua retenção depende do resultado real e das regressões; caller ativo segue 1.9.12.

### Sumário nativo retido e no-op após migração

A v2 do índice passou em **25 testes/170 asserções**, em **100 links dos vinte documentos no parser real**, e em quatro cenários de navegador EN/PT desktop/mobile. O clique saltou de páginas 1–2 para 3–4 no desktop e de 1 para 3 no celular; a troca de idioma manteve a seção canônica. Um erro inicial do harness usava um rótulo adivinhado e confundia readingSection herdado em subtítulos com navigationKey do heading canônico. O harness foi corrigido e seu erro preservado, sem alteração de produto para fazê-lo passar.

O coordenador **1.0.4** foi retido. Ele usa links de headings Markdown e os comentários reading-section já suportados pelo leitor, preservando títulos e corpo; títulos formatados fora do subconjunto suportado mantêm a montagem anterior sem um slug presumido. Nenhum componente/CSS/fluxo visual foi alterado. Regressão completa: **114 testes/669 asserções**, zero falhas/erros/skips.

Em replay isolado com rede desativada, `make docs` migrou apenas EN, PT e assembly.json para o índice. As **duas execuções seguintes preservaram hash, mtime e inode de 39 documentos/manifests**, com quatro requisições de modelo históricas e nenhuma nova. Logs e fontes staged continuam fora da afirmação de zero escrita.

A avaliação manteve os mesmos pesos/políticas e exatamente os mesmos fatos/citações. Organização local melhora por índice funcional; links de fontes ainda são rótulos de path/hash, portanto o critério de links portáteis fica parcial. A qualidade provisória sobe **8,33 pontos percentuais** por montagem, sem melhora de compreensão, precisão ou cobertura. Similaridade original muda apenas pela navegação adicionada. Pacotes antes/depois permanecem em `navigation-candidate-v2/`; os gates críticos continuam rejeitando os mesmos quatro pacotes. As URLs de fontes são fixadas por revisão e correspondem às fontes locais verificadas; disponibilidade HTTP externa não foi validada nesta auditoria.
