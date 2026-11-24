# Engineering Library — campanha adaptativa de IA, documentação e preservação

Estado: **FINAL**.

Foram integradas melhorias locais de seleção/citação, retenção de tentativas e perfis sintáticos explícitos. O caller passou de **1.9.19 para 1.9.35**. A suíte atual passou em **234 testes Ruby / 1.494 asserções**. A recuperação independente executou os perfis reais e reproduziu os três binários Go byte a byte.

O modelo permanece **llama3.2:3b**, sem treinamento de pesos. Não foi demonstrada melhora geral de compreensão/completude da geração neural nem prontidão para publicar manuais automaticamente. Ganhos sintáticos, operacionais e locais são separados dos erros do modelo. Não houve staging, commit, push, publicação ou alteração dos repositórios externos.

## 1. Tempo efetivo, janela e interrupções

| Marco | UTC / interpretação |
| --- | --- |
| Início verificável | 2026-11-18T22:38:49+00:00 |
| Início em São Paulo | 2026-11-18T19:38:49-03:00 |
| Alvo aproximado de 12 horas | 2026-11-19T10:38:49.117950+00:00 |
| Fechamento desta auditoria/relatório | 2026-11-19T10:38:58+00:00 |
| Fotografia em São Paulo | 2026-11-19T07:38:58-03:00 |
| Tempo entre início e fotografia | 12:00:09 |
| Duração ativa contínua do agente | Não instrumentada; não se inventa tempo de CPU/GPU ou de trabalho contínuo. |

A emissão do suplemento final e seu recibo são operações de entrega posteriores à fotografia do relatório. Os horários de arquivo/validação ficam no recibo de fechamento, sem antecipar testes ou fabricar um término futuro.

Houve duas sinalizações breves de pausa/retomada da meta. O primeiro processo de inferência ainda estava vivo ao retomar; sua sessão foi conferida e não reiniciada. Não se afirma uma pausa efetiva do processo nem se subtrai intervalo não medido. Na segunda retomada já não havia inferência pendente; foram revalidados diff e conhecimento antes de continuar.

Os 96 envelopes documentais contêm **10.959,68 s** acumulados de `total_duration` do servidor. Há duração de parede registrada para 84 chamadas, somando **9.632,79 s**; 13 registros, inclusive seções do coordenador, não oferecem esse campo. Esses acumulados não são duração ativa da campanha, tempo de CPU/GPU ou horas de treinamento. [Auditoria de durações e contagem](.local-backups/adaptive-20261118/all-diagnostics-and-call-accounting-verified-v3.json).

## 2. Escopo autorizado, fontes de instrução e plano

O pedido adaptativo mais recente, com 785 linhas, foi preservado em [pedido autorizado](.local-backups/adaptive-20261118/authorized-request.txt). Foram lidos integralmente o plano mestre do proprietário, o relatório mais recente recuperado de arquivo com 35.587 bytes e cinco relatórios anteriores acessíveis. Um destes cinco já era uma reconstrução de campanha anterior; seu hash prova a cópia acessível, não uma nova recuperação de um original. Cópias exatas dos cinco textos e do plano foram preservadas privadamente.

A campanha autorizou código do agente, testes necessários, documentação local, pesquisa/dados e recuperação isolada. Treinamento dependia de nove pré-requisitos; nenhum piloto foi improvisado. O escopo não incluiu UI, fontes externas graváveis, downloads de modelos/frameworks, instalação global, serviços pagos, envio de mensagens, publicação ou operações de histórico/staging.

O plano combinou avaliação factual, seleção/contexto, transferência, EN/PT, incremental, integração, dados e preservação. A fila inicial tinha 100 candidatos; tarefas foram acrescentadas a partir de erros e fontes reais. Os alvos por categoria eram candidatos, não quotas de inferência ou promessa de concluir todos os projetos.

## 3. Identidade e estado Git

| Item | Valor |
| --- | --- |
| Repositório | engineering-library |
| Raiz | /Users/juniorosa/Documents/Projetos/Projeto VivaBem/engineering-library |
| Origin | https://github.com/parceiro-vivabem/engineering-library.git |
| Branch | main |
| HEAD inicial e atual | fca0302c7ac7636e23866304495eabe962a95bac |
| Estado inicial | Limpo em Git; backups ignorados anteriores já existiam. |
| Estado desta emissão | 9 arquivos modificados e 85 criados, incluindo este relatório; tudo sem staging. |
| Índice preservado SHA-256 | dc4568fe59dddc85b145dc51345009f55f2bdf1bb0fcc77cbd2011dbbed0e2ba |
| Exclusões de arquivos preexistentes | Nenhum |
| Operações de histórico/remote | Nenhum |

O relatório antigo removido pelo proprietário antes do baseline não foi restaurado na raiz. Este é um arquivo novo. Clones locais de recuperação e cópias experimentais são artefatos privados; não receberam commits nem sugestões de commit próprias. O campo histórico `repository_revision` do manifesto foi preservado; `operational_snapshot` identifica a base fca0302 e os bytes não commitados. [Baseline](.local-backups/adaptive-20261118/baseline.json); [inventário final de arquivos e hashes](.local-backups/adaptive-20261118/working-tree-inventory-final.json).

## 4. Modelo, runtime e recursos

| Componente | Observado |
| --- | --- |
| Modelo aprovado | llama3.2:3b; GGUF Q4_K_M; parâmetro reportado 3.2B |
| Digest de runtime | a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72 |
| Blob de pesos SHA-256 | dde5aa3fc5ffc17176b5e8bdc82f587b24b2678c6c66101bf7da77af9f7ccdff |
| Blob de pesos | 2.019.377.376 bytes; grafo completo com 7 blobs e manifests. |
| Ollama | 0.40.16; somente o modelo aprovado; cloud desabilitada no serviço existente. |
| Host | Apple M1 Pro, 16 GB, 10 CPUs; observação filtrada sem serial/UUID. |
| Docker | Linux ARM64; 10 CPUs e cerca de 7,75 GiB; inferência observada em CPU, size_vram=0. |
| Backend | Ruby 3.4.11; Python 3.11.2. |
| Runtimes em cache | Go 1.27.4; Node 24.22.0 / TypeScript 5.9.3; Python Linux 3.14.10 e nativo 3.14.7 já disponíveis. |
| Serviços normais | Backend, frontend, Ollama, PostgreSQL e research saudáveis; start times anteriores à campanha. |

Os primeiros `sysctl` no sandbox falharam; a identidade de hardware posterior foi coletada por outra observação filtrada. Não se transforma a falha inicial em resultado positivo. Os serviços não foram reiniciados ou reconfigurados. Na observação durante inferência com uma thread, Ollama usava cerca de 2,792 GiB e 100% de uma CPU; é fotografia, não pico. Compiladores próprios foram isolados, sem rede, imagens já em cache, fonte somente leitura e limites de CPU/RAM.

| Contexto | size reportado por /api/ps | Resultado/limite |
| --- | --- | --- |
| 16.384 | 4.411.485.060 bytes | Observação em horário próprio. |
| 8.192 | 3.455.183.748 bytes | Quatro respostas mantiveram exatamente os fatos incorretos da comparação maior. |
| 4.096 | 2.891.028.888 bytes | MinFunc manteve os mesmos fatos incorretos; pacote Binary maior recusado antes do modelo. |

A redução reportada entre 16k e 4k é cerca de 34,46%, não benchmark controlado de pico/memória ou ganho factual. O byte guard conservador não foi contornado; padrões globais permaneceram iguais. O último `/api/ps` vazio é descarregamento por `keep_alive=0`, não perda do modelo. A fotografia de fechamento registrou apenas o processo do serviço Ollama, sem runner, cerca de 58,18 MiB e CPU reportada 0,00%; o host ainda tinha aproximadamente 347,34 GB livres no corte. Isso é uma observação separada, sem alegação de pico ou duração ativa. [Recursos de fechamento](.local-backups/adaptive-20261118/closing-resource-observation.json). [Identidade final](.local-backups/adaptive-20261118/final-runtime-identity-verified.json); [serviços](.local-backups/adaptive-20261118/final-container-identities.txt).

## 5. Fila adaptativa e pontos de retomada

| Situação | Tarefas |
| --- | --- |
| BLOCKED_PARSER | 1 |
| CANDIDATE_REQUIRES_PREFLIGHT | 87 |
| INCONCLUSIVE | 17 |
| INCONCLUSIVE_PARTIAL_CONTRACT | 2 |
| INCONCLUSIVE_PARTIAL_SOURCE_COVERAGE | 1 |
| INTEGRATED | 15 |
| INTEGRATED_DOCUMENTATION | 1 |
| REFUSED_CONTEXT_BUDGET | 1 |
| REJECTED | 72 |
| REJECTED_TRUNCATED | 2 |
| SUPERSEDED_SELECTION_LIMIT | 4 |
| VERIFIED | 9 |
| VERIFIED_CANDIDATE_DATASET_NOT_TRAINING_APPROVED | 1 |
| VERIFIED_CURATED_REVIEW_NOT_NEW_INFERENCE | 1 |
| VERIFIED_EXPERIMENTAL | 4 |
| VERIFIED_EXPERIMENTAL_OPTIONAL_CLI | 1 |
| VERIFIED_INTEGRATED | 2 |
| VERIFIED_INTEGRATED_OPT_IN | 1 |
| VERIFIED_LOCAL_COVERAGE_GAIN_NOT_WHOLE_APPROVAL | 1 |
| VERIFIED_PREFLIGHT | 1 |
| VERIFIED_PREFLIGHT_BOUNDARIES_NOT_SEMANTIC_APPROVAL | 1 |
| VERIFIED_SOURCE_REVIEWED_DRAFT | 1 |
| VERIFIED_WITH_DECLARED_SCOPE_LIMIT | 1 |
| VERIFIED_WITH_SAFE_REFUSALS_AND_EXPECTATION_CORRECTION | 1 |

Fotografia: **228 tarefas**, 322 eventos append-only, 100 candidatos iniciais; 87 candidatos ainda exigem preflight. Estados finos não são somados como uma taxa uniforme de sucesso. Revisões, controles, replays e tarefas de preservação não equivalem a inferências.

Não houve encerramento por esgotamento da primeira lista. A fila foi reabastecida com AST, ownership, Unicode, tipos, recursos, capacidade de fatos e recuperação. Restam candidatos úteis para uma próxima janela. Há 24 checkpoints neste corte; o maior intervalo observado foi 65.4 minutos, acima do alvo aproximado de 30 minutos. Os intervalos e os pontos reais foram mantidos, sem retroagir timestamps. A fila/último checkpoint instruem a conferir processos antes de repetir chamadas. [Leitor da fila](.local-backups/adaptive-20261118/research_queue.py); [eventos](.local-backups/adaptive-20261118/queue-events.jsonl); [checkpoints](.local-backups/adaptive-20261118/checkpoints).

## 6. Contagem de execução e independência

Foram verificadas **97 chamadas reais concluídas**: **96 respostas documentais HTTP 200**, das quais **94 JSON completos** e **duas truncadas**, mais **um smoke probe do store restaurado**. A última auditoria compara cada envelope/registro canônico, distingue as respostas únicas e verifica timestamps dentro da campanha. Os 188 registros linguísticos dos dez manifests diagnósticos correspondem exatamente às respostas originais. Não houve correção silenciosa de texto bruto.

Foram excluídos dessa contagem GETs de identidade, testes HTTP falsos, ASTs, fatos determinísticos, replays históricos, no-ops e recusas anteriores ao transporte. A falha inicial de montagem em nove tentativas numéricas não virou nove inferências; recusas de seleção, byte guard ou caminho read-only também não. Os 17 pares de candidatos sintáticos são outra proveniência e não somam chamadas neurais.

Fontes/perguntas foram selecionadas manualmente; assistência e feedback foram declarados. Referências Codex e respostas esperadas não entraram nos baselines independentes. No trio Go final, o IR condicional/explicação determinística ficou fora do pedido ao modelo. Dois casos Axum em uma família continuaram reservados, sem geração nesta campanha; isso não prova novidade perante pré-treinamento nem constitui um holdout aprovado e diversificado. [Ledger canônico](.local-backups/adaptive-20261118/inference-ledger-v6.json); [conferência integral](.local-backups/adaptive-20261118/all-diagnostics-and-call-accounting-verified-v3.json).

## 7. Avaliação factual antes/depois

| Ensaio | Informação útil/ganho observado | Perda, erro ou decisão |
| --- | --- | --- |
| Starlette, baseline/assistido | Feedback reparou alguns ramos. | Novas alegações de helpers, erros e fluxo; sem aprovação integral. |
| Core/chi/Go iniciais | Trechos úteis e nomes parcialmente corretos. | Delegações, precedência, callbacks, limites e nil confundidos. |
| Redis/DuckDB/Ruff/OpenCV numéricos | Alguns nomes/retornos reconhecidos. | Guardas, capacidade como espaços, destino de match, limites ou papéis incorretos. |
| Seed neural do reuso | Reuso operacional verificado em chamada real e atualização de metadados. | Para return 7, inventou intervalo 1..7, concorrência e restrições de entrada; o cache preservou o mesmo rascunho errado, sem ganho factual. |
| SQLx/Fastify, 13 seções | 10 aplicações mecânicas; quatro arquivos montados. | 12 rejeições factuais e uma inconclusão; omissões e APIs/erros/papéis errados. |
| Blender escalar | Valores numéricos de max_i iguais no empate. | Identidade do ramo de igualdade descrita errada; não se alega divergência numérica para inteiros. min_ff sem prova completa de NaN. |
| Comentários removidos | Alguns erros desapareceram. | Outros fatos corretos sumiram ou novas afirmações surgiram; não promovido. |
| Go AST / repeat_penalty | Estrutura melhor; Driver deixou de truncar em um ensaio. | Fatos ainda errados; parâmetros padrão não mudaram. |
| Metadados retirados / contexto de tipos | Tipos/campos tornaram-se visíveis em alguns ensaios. | Campo tratado como callable; papéis perdidos ou helpers inventados. |
| Contexto 8k / 4k | Alocação reportada menor; guardas operacionais funcionaram. | Respostas comparáveis conservaram defeitos; não há ganho de compreensão. |
| Pergunta de contrato literal | Algumas correções locais. | Sete chamadas: cinco rejeições, uma inconclusão, uma truncada. |
| maxItems, seed 43, seis chamadas | Scalar5: quinto helper acrescentado; primeiros quatro objetos idênticos. | Scalar2 e Ruff idênticos entre tetos; erro de “mínimo maxval”, quarto Error e identificadores traduzidos persistiram. |
| Teto explícito no fluxo normal, seis chamadas | Capacidade de 5 funciona no writer/replay e cache. | Uma única fact por resposta; nenhuma aprovação integral; perdeu nomes/papéis ou manteve duplicatas/omissões. |
| Novos três baselines Go | Contratos comparáveis aos fatos sintáticos já verificados. | NilPayloadConverter inventa erro onde consta nil,nil; Matcher atribui metadados do preparador à aplicação; Value extrapola helper. |

O [atlas de erros e limites](.local-backups/adaptive-20261118/error-and-scope-atlas-v1.json) consolida 11 categorias com referências por SHA: erros neurais, confusão entre preparador e aplicação, perda com contexto de tipos, tradução de identificadores, ganho local incompleto e limites operacionais/inconclusivos. São categorias sobrepostas, não 11 novas inferências nem uma taxa de sucesso.

A presença de fatos corretos isolados é preservada; não se chama uma resposta inteira de correta quando há erro crítico ou contrato omitido. A campanha não estabeleceu nota global de projeto, 95% de compreensão ou documentação autônoma pronta. Contagens de arquivos, testes e fatos não são métricas de entendimento. Os ganhos fortes desta janela estão nos limites verificáveis dos preparadores, fatos de sintaxe, proteção e recuperação.

Exemplo direto: a fonte de `NilPayloadConverter.ToPayload` tem `return nil, nil` na continuação. O modelo afirmou erro para entrada não nula e inventou uma divisão interface/não interface. O perfil sintático mantém `isInterfaceNil(value)`, `newPayload(nil, c), nil` e `nil, nil`, sem atribuir ao helper comportamento não mostrado. Esse ganho é de extração/renderização, não pesos aprendidos.

## 8. EN/PT-BR

As respostas foram lidas integralmente nos dois idiomas e confrontadas com suas citações. Identificadores e valores não são traduzidos nos fatos de fonte revisados. Os erros do modelo incluem `Success`/`Failure`/`Error` traduzidos, papéis de parâmetros/retorno trocados, gramática degradada e falsos erros repetidos nos dois idiomas. Traduções equivalentes podem repetir o mesmo erro; equivalência não prova verdade.

Nos perfis determinísticos aceitos, a sequência de código inline e as expressões/valores foi comparada entre línguas. Isso valida preservação do material codificado, não toda nuance linguística ou comportamento externo. As versões iniciais de capítulos Codex com diferenças de formatação de keywords foram preservadas; não se declarou igualdade literal quando a revisão separava apresentação e semântica. Os 17 candidatos sintáticos atuais passaram na conferência literal e continuam pendentes de aprovação humana.

## 9. Mudanças efetivamente integradas e consumidores

| Mudança | Evidência/limite | Consumo real |
| --- | --- | --- |
| Linha exata de citação | 7 casos reais / 14 citações bilíngues; não usa a primeira ocorrência igual. | Command normal; ativo. |
| Seleção Go retornando função / interface{} | 10 unidades reais antes perdidas; 16 controles de interface 9→16 e cinco seleções reais. | Preparador legado; ativo. |
| Python async fonte | Perfil de if/else com await; declaração/parametrização preservadas; 5 casos aceitos e 12 recusas no conjunto de 17. | SourceFactCommand explícito; sem modelo. |
| Go AST opcional | 11 métodos e nove tipos recuperados; grouped declarations fora do perfil. | GoAstCommand/launcher 1.4.0; explícito. |
| Go sole return | 8 casos reais aceitos de 12; callbacks limitados; sem inferir semântica do helper. | GoSourceFactCommand explícito. |
| Go call/defer/return | 6 contratos reais; ordem escrita não prova mutex, sucesso do defer ou ausência de corrida. | GoDeferredFactCommand explícito. |
| Go guarda/continuação | 6 iniciais + 15 novos contratos; cinco recusas na transferência; previsão original 19/20. | GoIfReturnFactCommand explícito. |
| Ownership | Hint AST reduz falsa recusa; referências de assinatura/callee em fatos imutáveis verificadas; contraexemplos continuam recusados. | Guardas normais preservados; exceção não aceita prosa arbitrária do modelo. |
| JS faixas e guarda inicial | 7 packets de faixas; 12 guardas reais aceitas/3 recusas no piloto; lexical $ não prova binding Emscripten. | Dois CLIs opcionais, sem dependência Node obrigatória do backend. |
| Separadores físicos | 5 contraprovas Python e ramo C++ ocultado corrigidos; JS recusa U+2028/U+2029 em vez de citar outra função. | LF/CRLF explícitos; bare CR fora dos perfis Python/nativo. |
| Retenção de tentativas | Input antes de inferir, resultado antes de validar, modos privados, bytes inválidos em base64 quando necessário. | Writer normal, inclusive audit desligado. |
| Reuso exato de fatos | OFF por padrão; contexto preparado idêntico permite reuso com atualização de proveniência; mudanças relevantes invalidam. | Não é cache semântico de dependências nem aprovação do conteúdo reutilizado. |
| Eco de instrução observado | Replay dos quatro itens antigos antes aceitos agora recusa a instrução completa de schema; prosa técnica legítima permanece. | Guarda ancorado e estreito; não valida verdade nem todo eco parafraseado. |
| DOCS_FACT_LIMIT | 1..5 explícito, padrão 4; prompt/schema/validador/cache/fingerprint/input/manifest/coordenador coerentes. | Capacidade opcional; nenhuma promoção geral da qualidade. |

As referências de `agent/research/` registram evidência e estados. O writer comum não carrega esses JSON como contexto nem como treinamento. O consumo efetivo foi verificado nos CLIs, nos hashes de código e em execuções a partir do clone recuperado. `bootstrap.py knowledge` verifica bytes/inventário; não prova que um modelo leu ou aprendeu esses registros. A reconciliação atual conferiu 38 registros anteriores e 18 métodos reais com hashes iguais aos do clone executado. Corrigiu por suplemento a referência inexistente `Command.process_project`: o consumidor real é `Command.process`. O registro antigo foi preservado. Ver [reconciliação](agent/research/adaptive-20261118/learning-consumer-reconciliation.json). O código, defaults e pontos explícitos de entrada distinguem integração de arquivo apenas preservado.

## 10. Hipóteses mantidas, privadas e rejeitadas

Foram mantidas as correções operacionais acima após controles e integração. A opção de teto cinco foi mantida como capacidade explícita, sem mudar o padrão quatro. O ganho raw escalar não autoriza extrapolar para Ruff/SDK ou para o prompt normal.

Continuam experimentais: type checking Go com exports (111 pacotes, 110 exports, sete fontes SQLx) em fallback GOPATH; Clang ternário (31 controles: 12 aceitações/19 recusas, três consumidores privados); e Python 3.14 existente (nove casos, três aceitos/seis recusados, uma elegibilidade nova e paridade nativo/Linux). O grafo modular Go original não foi verificado; Clang depende do SDK/compilador do host; o backend não recebeu fallback Python 3.14 automático.

Não foram promovidas alterações genéricas de pergunta, metadados, remoção de comentários ou repeat_penalty. A releitura histórica confirmou que regex de semântica específicas de fonte falharam em transferência e que Go AST já havia sido pesquisada privadamente em 17/11. A novidade atual é integração limitada e consumo real, não “primeira AST de sempre”. O ledger anterior de 122 registros foi reconciliado em 64 VERIFIED, 21 EXPERIMENTAL, 34 REJECTED, um SUPERSEDED e dois NEEDS_REVALIDATION; isso não significa reexecutar todos os resultados históricos.

## 11. Documentação produzida, autoria e publicação

| Conjunto | Artefatos | Classificação |
| --- | --- | --- |
| Rascunhos neurais temáticos privados | 5 capítulos / 10 arquivos EN/PT, segundo reviewed-model-chapter-manifest | Texto do modelo preservado, enquadramento/revisão Codex; não aprovado. |
| Correções privadas iniciais | 4 capítulos / 8 arquivos, mais par Starlette background/errors | Codex após fonte; versões com falhas preservadas; não treino gold. |
| SQLx/Fastify model | 13 seções, 4 arquivos montados | 12 rejeitadas / 1 inconclusa na revisão; não publicadas. |
| SQLx/Fastify corrigidos em agent/research | 4 arquivos EN/PT; 13 seções / 35 parágrafos por língua | Codex, citações fonte/licenças; revisão humana pendente. |
| Go standard library em agent/research | 2 arquivos EN/PT; 4 seções / 10 parágrafos por língua; 6 unidades exatas | Codex, fontes Go e licença preservadas; imagem fixada, sem Git SHA inventado. |
| Fatos de fonte e perfis privados | Árvores completas em preserved-* e protocolos de cada perfil | Sintaxe limitada, sem runtime/sem treino automático. |

Os seis arquivos de capítulos SQLx/Fastify/Go na árvore versionável são correções de autoria Codex, não respostas do modelo apresentadas como melhoradas. O capítulo Go trata NaN/Compare, comparable/valor zero, busca binária e MinFunc como varredura, corrigindo erros concretos observados. Nenhum desses artefatos foi incorporado ao catálogo público ou alterou o leitor, suas telas, banco, notas ou bookmarks. [Rascunhos temáticos](.local-backups/adaptive-20261118/reviewed-model-chapter-manifest.json); [correções privadas](.local-backups/adaptive-20261118/codex-corrected-chapter-manifest.json).

## 12. Dados e os nove gates de treinamento

Há **94 pares neurais diagnósticos / 188 linhas linguísticas**, duas respostas truncadas brutas e dez versões append-only. Separadamente, **17 pares sintáticos / 34 linhas** rederivados de produtores atuais coincidem com entregas já revisadas: 6 Go guarda, 6 Go defer e 5 Python async. Preservam 16 arquivos fonte e seis licenças; o NOTICE Prometheus foi acrescentado por suplemento, mantendo o manifest original.

Os candidatos são casos de desenvolvimento já expostos; dois componentes amplos de família não bastam para um holdout diversificado. Não houve split aleatório de línguas/linhas, nem promoção pós-hoc a “não visto”. As 32 demonstrações contextuais preexistentes também não se tornaram treinamento aprovado. **Gold aprovado: zero. Linhas aprovadas para treino: zero. Treinamento, passos de otimizador, adapters e novos pesos: zero.**

| Gate | Situação final |
| --- | --- |
| 1. Base treinável/tokenizer | Não demonstrados nas raízes/cache inspecionados; o GGUF de deploy não é automaticamente uma base LoRA/QLoRA validada. |
| 2. Exemplos aprovados para treino | Não atendido; candidatos/revisões Codex não são aprovação humana de treino. |
| 3. Licença/confidencialidade para uso | Proveniência/licenças/NOTICE preservados; aprovação específica de uso ainda pendente. |
| 4. Holdout por família | Parcial: pares e famílias ligados; dois Axum reservados em uma família não cumprem o gate amplo. |
| 5. Compute/memória | Hardware e inferência observados; nenhum piloto de memória/GPU de treino validado. |
| 6. Frameworks | torch, transformers, peft, bitsandbytes, mlx, accelerate, safetensors e tokenizers ausentes nos dois Pythons inspecionados. |
| 7. Checkpoint/adapters | Recuperação de deploy/pesquisa/ferramentas comprovada; serializer de optimizer/adapters de treino inexistente. |
| 8. Orçamento/rollback de piloto | Não validado para base/framework reais; nenhum piloto iniciado. |
| 9. Isolamento de treino seguro | Deploy preservado; segurança de um trainer não disponível não foi certificada. |

Resultado: **0/9 gates plenamente demonstrados**. Não se instalou framework ou baixou checkpoint para contornar os outros gates. Nenhum consumo automático por trainer/contexto ordinário existe. [Readiness atual](.local-backups/adaptive-20261118/training-readiness-v2.json); [candidatos](.local-backups/adaptive-20261118/source-syntax-candidate-dataset-v1-final/manifest.json); [NOTICE suplementar](.local-backups/adaptive-20261118/source-syntax-candidate-dataset-v1-final/license-notice-supplement-v1.json).

## 13. Preservação, Git LFS e dependências

O investimento existente foi mantido: grafo completo Ollama, manifests, licenças/configuração pequenas, proposta de oito partes de pesos mais seis partes pequenas (14 no total), dados/protocolos/revisões, source snapshots, callers congelados, imagens/caches de ferramentas e falhas. Não se apagaram campanhas anteriores. O objeto `model` do manifesto atual é idêntico ao do HEAD inicial; o store original foi verificado novamente.

Git LFS continua indisponível (`git lfs version` exit 1). Não houve instalação, novo tracking, staging, object upload, custo remoto ou certificação de disponibilidade remota. As partes/model store são dependências locais separadas das cápsulas; só clonar Git não recupera os pesos. As 14 partes estão em `.local-backups/unattended-20261118/model-artifacts/lfs-parts-a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`; o store independente está em `.local-backups/preservation-20261118-followup/restored-models`. O [localizador verificado](.local-backups/adaptive-20261118/model-artifact-location-reconciliation.json) corrige a descrição resumida de caminho em um recibo antigo sem alterar aquela cápsula. Os seis pequenos blobs Git-embutidos são verificados, mas não substituem o GGUF completo.

O material privado em `.local-backups/` e caches está fora do catálogo e dos payloads de build desnecessários. `agent/` mantém código, ferramentas, registros e inventário lógico dos artefatos revisados; os datasets privados/candidatos não aprovados são referenciados com hashes e escopo. O inventário privado com finalidade por arquivo acompanha o pacote; arquivos derivados de cópias antigas são classificados como cópias, sem alegar nova autoria. [LFS](.local-backups/adaptive-20261118/final-git-lfs-availability.json); [store original](.local-backups/adaptive-20261118/final-original-model-store-verify.json); [inventário privado](.local-backups/adaptive-20261118/private-artifact-file-inventory-final.json).

## 14. Recuperações realmente executadas

| Prova | Resultado | Dependência/limite |
| --- | --- | --- |
| Store independente, 22:56 UTC | 7 blobs completos; geração real OK, stop, 8,49 s; somente o PID próprio foi parado. | 1 chamada do total de 97; original 11434 preservado. |
| Store novo no fechamento | 14 partes reconstituídas pelas ferramentas do clone35; 7 blobs e um link V2 exato; inodes independentes do original. | Sem inferência nova ou pesos treinados; cópia grande fora das cápsulas. |
| Clones locais intermediários 22/28 | Consumo real e verificações próprias preservados. | Cortes históricos, não o código final. |
| Cápsula 05:27:59 / caller30 | 82 operacionais + manifest (83 no total); suíte210/1268 e consumidores Go/Python/JS. | Anterior às correções posteriores; não rotular como final. |
| Cápsula 09:01:21 / caller35 | 114 operacionais + manifest (115 no total), 14.124 privados; 1.061.604.659 B brutos / 615.341.157 B comprimidos privados. | Pesos separados; extração independente regular e hashes completos. |
| Clone35 da extração | 234 Ruby / 1494; 28 launcher Go; 29 preparadores; quatro perfis reais com fontes extraídas. | Ruby usa bundle existente; source locations provam código do clone. |
| Runtime JS recém-extraído | 145 arquivos íntegros, dois CLIs reais e 56 testes completos no código recuperado. | Linux ARM64 com loader/libs compatíveis; não Windows/Mac/arbitrário. |
| Rebuild Go com cache novo | Três binários byte a byte idênticos; smoke IR nativo no recompilado. | Compilador fixado já em cache, fonte da extração; não novo Docker daemon. |

A cápsula final de corpo preserva 116 arquivos operacionais mais o manifest (117 no total) e 17.745 arquivos privados. Sua extração independente passou novamente em 234/1494 Ruby e 28 controles nativos Go; os leitores extraídos verificaram os dados neurais e os candidatos sintáticos. A cápsula e seu fechamento são descritos em [recibo final de corpo](.local-backups/adaptive-20261118/final-body-capsule-verified.json). Este relatório e o manifesto que o fixa entram no suplemento de fechamento, evitando um hash autorreferente do próprio pacote. O suplemento fica em `.local-backups/adaptive-20261118/capsules/closing-report-supplement-20261119/`, com `receipt.json`, `inventory.json`, `private-inventory-delta.json` e `verification-receipt.json`; o recibo global é `.local-backups/adaptive-20261118/closing-delivery-verified.json`. Recibos/sidecars são parte da entrega; conservar o diretório completo de cápsulas, as partes de modelo e os checkpoints anteriores. Não há claim de recuperação remota, clone Git autossuficiente, runtime Ruby hermético ou execução Windows/nativo AMD64.

## 15. Testes, comandos e resultados

| Comando efetivamente usado | Resultado / escopo |
| --- | --- |
| docker exec backend bundle exec ruby -Itest -e Dir[test/offline/*_offline.rb]... | 234 runs /1494 assertions, zero failures/errors/skips; layout /app e árvore recuperada. |
| python3 agent/test/go_source_ast_test.py | 28 testes nativos; também Linux ARM64; hashes/launcher/parser reais. |
| python3 -m unittest discover -s backend/test/offline -p *_offline.py | 29 testes dos preparadores a partir do clone recuperado. |
| node agent/test/javascript_leading_guard.test.cjs TYPESCRIPT | 33 testes, runtime recuperado e código do clone. |
| node agent/test/javascript_ranges.test.cjs TYPESCRIPT | 23 testes, runtime recuperado e código do clone. |
| Controles parser Go 106+24+28 | 158 por alvo; MacARM64 e LinuxARM64 reais, AMD64 emulado. |
| bootstrap.py knowledge / verify --store STORE | Conhecimento por hash e stores verificados; nenhum treino nem inferência implícita. |
| go build -p1 -trimpath -buildvcs=false, CGO=0 | Parser próprio recompilado da cápsula; três SHA-256 iguais aos empacotados. |
| git diff --check / git diff --cached --raw | Sem erros de whitespace e staging vazio; HEAD/índice originais. |

Comandos completos, argv, stdout/stderr e recibos estão nos scripts/logs, em especial [capsule35-full-offline-tests.log](.local-backups/adaptive-20261118/capsule35-full-offline-tests.log), [capsule35-source-consumers.jsonl](.local-backups/adaptive-20261118/capsule35-source-consumers.jsonl), [capsule35-fresh-js-runtime.json](.local-backups/adaptive-20261118/capsule35-fresh-js-runtime.json) e [capsule35-go-rebuild/rebuild-receipt.json](.local-backups/adaptive-20261118/capsule35-go-rebuild/rebuild-receipt.json).

As falhas de harness não foram apagadas: mount read-only, tmpfs noexec, script de parser/Python errado, stub recursivo, fonte em caminho privado alternativo, expectativa de trailing LF, expectativa incorreta de dereference e localização de /agent nos fixtures foram corrigidos sem transformar a falha inicial em aprovação. No Mac, substituições de executáveis foram atômicas por novo inode após detectar SIGKILL de um overwrite anterior.

## 16. Inventário obrigatório — engineering-library

Alterações preexistentes em Git: **Nenhum**. Fontes externas, catálogo público, UI, Compose, Dockerfiles e dotenv não receberam mudanças retidas. Exclusões de arquivos preexistentes: **Nenhum**. Todos os itens abaixo são mudanças desta campanha; artefatos privados ignorados têm inventário separado com finalidade/hash, não são implicitamente arquivos Git.

### Modificados

| Arquivo | Motivo |
| --- | --- |
| agent/README.md | Documentar perfis opcionais, consumidores reais, decisões rejeitadas, limites e recuperação, preservando o histórico anterior. |
| agent/recovery/manifest.json | Fixar hashes/tamanhos dos artefatos operacionais e a fotografia não commitada; manter o objeto model idêntico ao HEAD inicial. |
| backend/lib/documentation/command.rb | Caller 1.9.35: citação pela linha selecionada, seleção Go, reuso opcional, retenção de tentativas, origem/hints, recusa do eco observado e limite explícito de fatos. |
| backend/lib/documentation/native_structure.py | Melhorar seleção de funções Go e interface{} sem deslocar posições; usar LF físico nas verificações de corpo/preprocessador. |
| backend/lib/documentation/project_command.rb | Coordenador 1.0.6: propagar a opção explícita de reuso de unidades às seções e validar seu tipo antes de transporte. |
| backend/lib/documentation/python_structure.py | Preservar linhas físicas LF/CRLF e leitura UTF-8 bruta nas faixas Python. |
| backend/test/offline/documentation_command_offline.rb | Regressões ligadas aos defeitos reais de seleção, eco, limite, cache e proteção de escrita; controles legítimos preservados. |
| backend/test/offline/documentation_project_offline.rb | Verificar propagação de reuso/limite pelo coordenador e a montagem real das duas línguas. |
| backend/test/offline/native_structure_offline.py | Contraprovas Go/interface{}, corpos e separadores físicos; recusas seguras em formatos não suportados. |

### Criados

| Arquivo | Finalidade |
| --- | --- |
| agent/research/adaptive-20261118/async-declaration-source-facts.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-ASYNC-DECLARATION-SYNTAX. |
| agent/research/adaptive-20261118/caller35-independent-recovery.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-CALLER35-INDEPENDENT-CAPSULE-RECOVERY. |
| agent/research/adaptive-20261118/campaign-capsule-recovery.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-IMMUTABLE-CAPSULE-RECOVERY. |
| agent/research/adaptive-20261118/chapters/fastify/en.md | Capítulo de correção escrito pelo Codex em EN/PT, revisado contra fonte e pendente de aprovação humana. |
| agent/research/adaptive-20261118/chapters/fastify/pt-br.md | Capítulo de correção escrito pelo Codex em EN/PT, revisado contra fonte e pendente de aprovação humana. |
| agent/research/adaptive-20261118/chapters/go-stdlib/en.md | Capítulo de correção escrito pelo Codex em EN/PT, revisado contra fonte e pendente de aprovação humana. |
| agent/research/adaptive-20261118/chapters/go-stdlib/pt-br.md | Capítulo de correção escrito pelo Codex em EN/PT, revisado contra fonte e pendente de aprovação humana. |
| agent/research/adaptive-20261118/chapters/go-stdlib/source-excerpts.json | Citações exatas, linhas, hashes e proveniência do capítulo Go. |
| agent/research/adaptive-20261118/chapters/go-stdlib/source/LICENSE | Licença original do código Go preservado com o capítulo experimental. |
| agent/research/adaptive-20261118/chapters/go-stdlib/source/VERSION | Identidade observada do provedor Go em cache; não inventa revisão Git. |
| agent/research/adaptive-20261118/chapters/go-stdlib/source/cmp.go | Fonte Go original, com copyright, para verificar as citações do capítulo. |
| agent/research/adaptive-20261118/chapters/go-stdlib/source/sort.go | Fonte Go original, com copyright, para verificar as citações do capítulo. |
| agent/research/adaptive-20261118/chapters/manifest.json | Citações exatas, linhas, hashes e proveniência do capítulo Go. |
| agent/research/adaptive-20261118/chapters/source-licenses/fastify.LICENSE | Citações exatas, linhas, hashes e proveniência do capítulo Go. |
| agent/research/adaptive-20261118/chapters/source-licenses/sqlx.LICENSE | Citações exatas, linhas, hashes e proveniência do capítulo Go. |
| agent/research/adaptive-20261118/chapters/sqlx/en.md | Capítulo de correção escrito pelo Codex em EN/PT, revisado contra fonte e pendente de aprovação humana. |
| agent/research/adaptive-20261118/chapters/sqlx/pt-br.md | Capítulo de correção escrito pelo Codex em EN/PT, revisado contra fonte e pendente de aprovação humana. |
| agent/research/adaptive-20261118/citation-source-location.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-CITATION-SOURCE-LOCATION. |
| agent/research/adaptive-20261118/clang-ternary-experimental.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-CLANG-TERNARY-EXPERIMENT. |
| agent/research/adaptive-20261118/context-size-observation.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-CONTEXT-SIZE-OBSERVATION. |
| agent/research/adaptive-20261118/context4096-resource-observation.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-CONTEXT4096-OBSERVATION. |
| agent/research/adaptive-20261118/diagnostic-dataset-progress-v7.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-DIAGNOSTIC-DATASET-PROGRESS-V7. |
| agent/research/adaptive-20261118/diagnostic-dataset-supplements.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-DIAGNOSTIC-DATASET-SUPPLEMENTS. |
| agent/research/adaptive-20261118/explicit-fact-limit.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-EXPLICIT-FACT-LIMIT. |
| agent/research/adaptive-20261118/fact-ceiling-generation-decision.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-FACT-CEILING-GENERATION-EVALUATION. |
| agent/research/adaptive-20261118/generation-attempt-preservation.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-GENERATION-ATTEMPT-PRESERVATION. |
| agent/research/adaptive-20261118/go-ast-receiver-owner-validation.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-GO-AST-RECEIVER-OWNER-VALIDATION. |
| agent/research/adaptive-20261118/go-call-defer-return-source-facts.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-GO-CALL-DEFER-RETURN-FACTS. |
| agent/research/adaptive-20261118/go-callback-source-selection.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-GO-CALLBACK-SOURCE-SELECTION. |
| agent/research/adaptive-20261118/go-empty-interface-source-selection.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-GO-EMPTY-INTERFACE-BOUNDARIES. |
| agent/research/adaptive-20261118/go-guard-incremental-and-source-candidates.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-GO-GUARD-INCREMENTAL-SOURCE-CANDIDATES. |
| agent/research/adaptive-20261118/go-guard-neural-baselines-and-diagnostics-v10.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-GO-GUARD-NEURAL-COMPARISON. |
| agent/research/adaptive-20261118/go-guard-transfer-and-runtime-layout.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-GO-GUARD-TRANSFER20-LAYOUT. |
| agent/research/adaptive-20261118/go-if-return-source-facts.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-GO-IF-RETURN-FALLTHROUGH. |
| agent/research/adaptive-20261118/go-sole-return-source-facts.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-GO-SOLE-RETURN-SOURCE-FACTS. |
| agent/research/adaptive-20261118/go-standalone-type-context.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-GO-STANDALONE-TYPE-CONTEXT. |
| agent/research/adaptive-20261118/go-standard-ast-optional-selection.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-GO-STANDARD-AST-OPTIONAL-SELECTION. |
| agent/research/adaptive-20261118/go-static-type-probe-experimental.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-GO-STATIC-TYPE-PROBE. |
| agent/research/adaptive-20261118/go-stdlib-source-reviewed-chapter.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-GO-STDLIB-CORRECTION-CHAPTER. |
| agent/research/adaptive-20261118/javascript-ast-range-preparation.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-JAVASCRIPT-AST-RANGE-PREPARER. |
| agent/research/adaptive-20261118/javascript-leading-guard.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-JS-LEADING-GUARD. |
| agent/research/adaptive-20261118/javascript-physical-line-separators.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-JS-PHYSICAL-LINE-SEPARATORS. |
| agent/research/adaptive-20261118/javascript-runtime-local-recovery.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-JAVASCRIPT-RUNTIME-LOCAL-RECOVERY. |
| agent/research/adaptive-20261118/learning-consumer-reconciliation.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-CURRENT-LEARNING-CONSUMER-RECONCILIATION. |
| agent/research/adaptive-20261118/literal-contract-question-decision.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-LITERAL-CONTRACT-QUESTION. |
| agent/research/adaptive-20261118/physical-lf-source-provenance.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-PHYSICAL-LF-SOURCE-PROVENANCE. |
| agent/research/adaptive-20261118/prior-report-review.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-ACCESSIBLE-PRIOR-REPORTS-REVIEW. |
| agent/research/adaptive-20261118/python314-parser-experimental.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-PYTHON314-PARSER-COMPATIBILITY. |
| agent/research/adaptive-20261118/schema-instruction-echo.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-NARROW-SCHEMA-INSTRUCTION-ECHO. |
| agent/research/adaptive-20261118/source-and-diagnostic-integrity-audit.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-SOURCE-DIAGNOSTIC-INTEGRITY-AUDIT. |
| agent/research/adaptive-20261118/source-fact-provenance.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-EXPLICIT-AST-SOURCE-FACTS. |
| agent/research/adaptive-20261118/source-reviewed-project-chapters.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-SOURCE-REVIEWED-PROJECT-CHAPTERS. |
| agent/research/adaptive-20261118/source-unit-result-reuse.json | Registro versionável de evidência, integração/decisão e limites: ADAPT18-EXACT-SOURCE-REQUEST-REUSE. |
| agent/test/go_source_ast_test.py | Controles do parser/CLI e recusas de integridade, citações e formatos fora do perfil. |
| agent/test/javascript_leading_guard.test.cjs | Controles do parser/CLI e recusas de integridade, citações e formatos fora do perfil. |
| agent/test/javascript_ranges.test.cjs | Controles do parser/CLI e recusas de integridade, citações e formatos fora do perfil. |
| agent/tools/go-source-ast/GO-LICENSE | Licença BSD original do provedor Go, junto ao parser empacotado. |
| agent/tools/go-source-ast/README.md | Artefato operacional local autorizado; finalidade detalhada no próprio arquivo e no manifesto de recuperação. |
| agent/tools/go-source-ast/bin/go-source-ast-darwin-arm64 | Parser Go estático para a plataforma indicada; executável próprio verificado, sem executar a fonte analisada. |
| agent/tools/go-source-ast/bin/go-source-ast-linux-amd64 | Parser Go estático para a plataforma indicada; executável próprio verificado, sem executar a fonte analisada. |
| agent/tools/go-source-ast/bin/go-source-ast-linux-arm64 | Parser Go estático para a plataforma indicada; executável próprio verificado, sem executar a fonte analisada. |
| agent/tools/go-source-ast/main.go | Implementação AST própria usando biblioteca padrão Go; extração e contratos sintáticos limitados. |
| agent/tools/go-source-ast/manifest.json | Versão 1.4.0, compilador fixado e hashes dos três binários/fontes/licença. |
| agent/tools/go_source_ast.py | Launcher opcional que verifica integridade e escolhe o binário nativo permitido. |
| agent/tools/javascript_leading_guard.cjs | CLI opcional Node/TypeScript para faixas ou guarda inicial; sintaxe e citações, sem avaliação do módulo. |
| agent/tools/javascript_ranges.cjs | CLI opcional Node/TypeScript para faixas ou guarda inicial; sintaxe e citações, sem avaliação do módulo. |
| backend/lib/documentation/go_ast_command.rb | Entrada/consumidor explícito do perfil de fonte indicado; writer, proveniência e proteção comuns. |
| backend/lib/documentation/go_deferred_fact_command.rb | Entrada/consumidor explícito do perfil de fonte indicado; writer, proveniência e proteção comuns. |
| backend/lib/documentation/go_deferred_facts.py | Produtor/renderizador determinístico de fatos sintáticos limitados, com erros e recusas explícitos. |
| backend/lib/documentation/go_if_return_fact_command.rb | Entrada/consumidor explícito do perfil de fonte indicado; writer, proveniência e proteção comuns. |
| backend/lib/documentation/go_if_return_facts.py | Produtor/renderizador determinístico de fatos sintáticos limitados, com erros e recusas explícitos. |
| backend/lib/documentation/go_return_facts.py | Produtor/renderizador determinístico de fatos sintáticos limitados, com erros e recusas explícitos. |
| backend/lib/documentation/go_source_fact_command.rb | Entrada/consumidor explícito do perfil de fonte indicado; writer, proveniência e proteção comuns. |
| backend/lib/documentation/python_async_facts.py | Produtor/renderizador determinístico de fatos sintáticos limitados, com erros e recusas explícitos. |
| backend/lib/documentation/source_fact_command.rb | Entrada/consumidor explícito do perfil de fonte indicado; writer, proveniência e proteção comuns. |
| backend/test/offline/documentation_attempt_preservation_offline.rb | Regressões do perfil indicado, origem imutável, proteção da fonte/documentos e ausência de inferência. |
| backend/test/offline/documentation_citation_spans_offline.rb | Regressões do perfil indicado, origem imutável, proteção da fonte/documentos e ausência de inferência. |
| backend/test/offline/documentation_go_ast_offline.rb | Regressões do perfil indicado, origem imutável, proteção da fonte/documentos e ausência de inferência. |
| backend/test/offline/documentation_go_deferred_facts_offline.rb | Regressões do perfil indicado, origem imutável, proteção da fonte/documentos e ausência de inferência. |
| backend/test/offline/documentation_go_if_return_facts_offline.rb | Regressões do perfil indicado, origem imutável, proteção da fonte/documentos e ausência de inferência. |
| backend/test/offline/documentation_go_source_facts_offline.rb | Regressões do perfil indicado, origem imutável, proteção da fonte/documentos e ausência de inferência. |
| backend/test/offline/documentation_source_facts_offline.rb | Regressões do perfil indicado, origem imutável, proteção da fonte/documentos e ausência de inferência. |
| backend/test/offline/documentation_source_reuse_offline.rb | Regressões do perfil indicado, origem imutável, proteção da fonte/documentos e ausência de inferência. |
| backend/test/offline/python_structure_offline.py | Regressões do perfil indicado, origem imutável, proteção da fonte/documentos e ausência de inferência. |
| ENGINEERING_LIBRARY_ADAPTIVE_CAMPAIGN_2026-11-19.md | Relatório final solicitado: resultados, limites, inventários e continuidade. |

### Somente inspecionados

`compose.yaml`, `compose.research.yaml`, `docker/Dockerfile`, `backend/Makefile`, `frontend/lib/catalog.ts`, os registros/instruções/skills existentes em `agent/`, os helpers de recuperação, metadados/licenças/model-bundle e controles de documentação/qualidade existentes foram lidos ou verificados por hash para confirmar integração e limites. Leitura por hash não é alegada como revisão manual integral. O inventário de alterações e o manifesto distinguem esses arquivos dos modificados. Não houve staging real nos testes: stubs Git dos testes não são operações no índice do projeto.

| Arquivo somente inspecionado | Relevância |
| --- | --- |
| .dockerignore | Conferir exclusão de modelos, backups e arquivos desnecessários do contexto de build. |
| .gitignore | Conferir escopo Git e exclusão do laboratório/dados privados. |
| agent/IDENTITY_NORMALIZATION.md | Conferir instrução/configuração/contexto preexistente e seu papel no agente; sem nova autoria/treinamento. |
| agent/authoring.json | Conferir instrução/configuração/contexto preexistente e seu papel no agente; sem nova autoria/treinamento. |
| agent/evaluation.json | Conferir instrução/configuração/contexto preexistente e seu papel no agente; sem nova autoria/treinamento. |
| agent/experimental-session.en.md | Conferir instrução/configuração/contexto preexistente e seu papel no agente; sem nova autoria/treinamento. |
| agent/experimental-session.pt-BR.md | Conferir instrução/configuração/contexto preexistente e seu papel no agente; sem nova autoria/treinamento. |
| agent/instructions.en.md | Conferir instrução/configuração/contexto preexistente e seu papel no agente; sem nova autoria/treinamento. |
| agent/instructions.pt-BR.md | Conferir instrução/configuração/contexto preexistente e seu papel no agente; sem nova autoria/treinamento. |
| agent/recovery/bootstrap.py | Verificar helper/metadado/blob pequeno de preservação e grafo do modelo; não substitui pesos grandes. |
| agent/recovery/bundle.py | Verificar helper/metadado/blob pequeno de preservação e grafo do modelo; não substitui pesos grandes. |
| agent/recovery/model-bundle.json | Verificar helper/metadado/blob pequeno de preservação e grafo do modelo; não substitui pesos grandes. |
| agent/skills/LICENSE.upstream | Conferir skill/licença/proveniência preexistente, preservando conteúdo e identidade. |
| agent/skills/authoring/SKILL.md | Conferir skill/licença/proveniência preexistente, preservando conteúdo e identidade. |
| agent/skills/evidence/SKILL.md | Conferir skill/licença/proveniência preexistente, preservando conteúdo e identidade. |
| agent/skills/provenance.json | Conferir skill/licença/proveniência preexistente, preservando conteúdo e identidade. |
| agent/skills/review/SKILL.md | Conferir skill/licença/proveniência preexistente, preservando conteúdo e identidade. |
| agent/sources.json | Conferir instrução/configuração/contexto preexistente e seu papel no agente; sem nova autoria/treinamento. |
| backend/Gemfile | Identificar dependências Ruby já disponíveis e manter o bundle existente. |
| backend/Gemfile.lock | Identificar dependências Ruby já disponíveis e manter o bundle existente. |
| backend/Makefile | Identificar entradas existentes de documentação/testes; não implica execução deste wrapper. |
| backend/bin/test-offline | Identificar entradas existentes de documentação/testes; não implica execução deste wrapper. |
| backend/lib/documentation/research.rb | Conferir integração de pesquisa/referências e modos offline existentes. |
| compose.research.yaml | Conferir serviços, mounts e integração existentes sem alterar configuração. |
| compose.yaml | Conferir serviços, mounts e integração existentes sem alterar configuração. |
| docker/Dockerfile | Conferir imagem, entrypoint e layout de inicialização existentes. |
| docker/backend-entrypoint.sh | Conferir imagem, entrypoint e layout de inicialização existentes. |
| frontend/lib/catalog.ts | Conferir catálogo público e comprovar ausência de publicação/alteração de UI. |

[Hashes e escopo da inspeção; todos idênticos ao HEAD inicial](.local-backups/adaptive-20261118/root-inspected-only-inventory.json).

## 17. Inventário obrigatório — repositórios externos

Nos **15 originais**, mudanças preexistentes: **Nenhum**; criados: **Nenhum**; modificados: **Nenhum**; excluídos: **Nenhum**; estado: **sem alterações**. Para cada um foram conferidos `git rev-parse HEAD`, `git status --porcelain` com `GIT_OPTIONAL_LOCKS=0` e correspondência byte a byte dos snapshots preservados. Não se sugerem commits. As cópias técnicas/experimentos dentro da Engineering Library são artefatos desta campanha e não mudanças nos originais.

| Nome exato | Revisão | Fontes preservadas únicas / scan automático | Lista completa e relevância |
| --- | --- | --- | --- |
| chi | c64ed7d6635f33a8b2feaff7dcfa55677023ac7d | 6 / 90 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/chi.json) |
| axum | 36d38c4cf2766cd7313dd53d808f30546ee36b1e | 2 / 0 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/axum.json) |
| click | 08b803cf32ceb2ae6a772c62d5da42757a897d44 | 4 / 0 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/click.json) |
| fastify | 825d7722e4932a39193729997c76535d0a963b6b | 31 / 31 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/fastify.json) |
| sqlx | 41dac167fdad5e3fd81d66cafba0951dc6823a30 | 8 / 16 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/sqlx.json) |
| starlette | 271c277da0ff64e2048a4d46ecc812b9d61db5f6 | 7 / 0 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/starlette.json) |
| sdk-go | 7e0d845246d36fc7f62ade2af885554f94c29db9 | 17 / 523 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/sdk-go.json) |
| redis | 1a9eb051aa243f9d0e5a8a8afa6c4801bf52a9fb | 1 / 0 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/redis.json) |
| duckdb | e41515de6f7efb19b43293ab49cb967cd64ab9f9 | 1 / 0 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/duckdb.json) |
| prometheus | b2a602494b65bda38316eabaef7e0d834a6814dd | 12 / 766 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/prometheus.json) |
| ruff | 0222c19dd8e0c9a927f2e47bf3774a108431da25 | 2 / 0 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/ruff.json) |
| opencv | 5d0660acfed08650cafec4876b4792a369a20601 | 6 / 0 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/opencv.json) |
| core | 67ec6a4b7dcaed80b59930be6744f4944b5073e3 | 12 / 9672 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/core.json) |
| blender | 023dcaed86e9c190c7615b450b3ccb2c3c53fbfc | 4 / 0 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/blender.json) |
| godot | 4d0d43b77dd2ffbd7dc867c08bcc3dd9962fd7e7 | 32 / 32 | [arquivos, quotes, licenças e escopo](.local-backups/adaptive-20261118/per-repository-inspected-file-inventories/godot.json) |

Os 11.130 caminhos de scan são únicos: 9.672 Core, 1.395 Go e 63 JS. Não se somam novamente as fatias sobrepostas de 5.000/9.672 Core ou os scans Go anteriores. Há 146 fontes públicas únicas preservadas, 193 registros de citações e expansão dos 96 packets neurais; oito linhas sem inferência foram separadas. Não se afirma leitura manual de 11 mil arquivos.

### Fontes preservadas/selecionadas por original



**chi — sem alterações.** `_examples/versions/data/errors.go`; `middleware/recoverer.go`; `middleware/route_headers.go`; `middleware/throttle.go`; `middleware/timeout.go`; `mux.go` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


**axum — sem alterações.** `axum/src/extract/query.rs`; `axum/src/extract/state.rs` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


**click — sem alterações.** `src/click/core.py`; `src/click/exceptions.py`; `src/click/shell_completion.py`; `src/click/utils.py` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


**fastify — sem alterações.** `lib/config-validator.js`; `lib/content-type-parser.js`; `lib/content-type.js`; `lib/context.js`; `lib/decorate.js`; `lib/error-handler.js`; `lib/error-serializer.js`; `lib/error-status.js`; `lib/errors.js`; `lib/four-oh-four.js`; `lib/handle-request.js`; `lib/head-route.js`; `lib/hooks.js`; `lib/initial-config-validation.js`; `lib/log-controller.js`; `lib/logger-factory.js`; `lib/logger-pino.js`; `lib/noop-set.js`; `lib/plugin-override.js`; `lib/plugin-utils.js`; `lib/reply.js`; `lib/req-id-gen-factory.js`; `lib/request.js`; `lib/route.js`; `lib/schema-controller.js`; `lib/schemas.js`; `lib/server.js`; `lib/symbols.js`; `lib/validation.js`; `lib/warnings.js`; `lib/wrap-thenable.js` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


**sqlx — sem alterações.** `bind.go`; `named.go`; `sqlx.go`; `types/types.go`; `reflectx/reflect.go`; `doc.go`; `named_context.go`; `sqlx_context.go` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


**starlette — sem alterações.** `starlette/background.py`; `starlette/concurrency.py`; `starlette/datastructures.py`; `starlette/endpoints.py`; `starlette/middleware/errors.py`; `starlette/routing.py`; `starlette/websockets.py` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


**sdk-go — sem alterações.** `contrib/gcp/cloudrun/otel/plugin.go`; `contrib/opentelemetry-v2/provider.go`; `contrib/sysinfo/cgroups.go`; `contrib/tools/workflowcheck/workflow/testdata/src/go.temporal.io/sdk/workflow/workflow.go`; `converter/composite_data_converter.go`; `converter/nil_payload_converter.go`; `converter/payload_converter.go`; `interceptor/tracing/tracing_interceptor_v2.go`; `internal/client.go`; `internal/cmd/prepare-release/target.go`; `internal/common/backoff/retry.go`; `internal/common/cache/lru.go`; `internal/common/metrics/capturing_handler.go`; `internal/context.go`; `internal/extstore/internal_extstore.go`; `internal/internal_activity.go`; `internal/internal_retry.go` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


**redis — sem alterações.** `src/expire.c` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


**duckdb — sem alterações.** `src/common/types/value.cpp` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


**prometheus — sem alterações.** `cmd/prometheus/main.go`; `cmd/promtool/tsdb.go`; `config/config.go`; `discovery/manager.go`; `discovery/oci/oci.go`; `discovery/xds/kuma_mads.pb.go`; `model/histogram/float_histogram.go`; `model/histogram/generic.go`; `model/labels/labels_common.go`; `model/labels/matcher.go`; `notifier/sendloop.go`; `promql/engine.go` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


**ruff — sem alterações.** `crates/ruff/src/lib.rs`; `crates/ruff_workspace/src/settings.rs` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


**opencv — sem alterações.** `modules/core/include/opencv2/core/cvdef.h`; `modules/core/include/opencv2/core/hal/interface.h`; `modules/core/src/arithm.cpp`; `modules/imgproc/src/thresh.cpp`; `modules/core/include/opencv2/core/version.hpp`; `modules/core/include/opencv2/core/cv_cpu_dispatch.h` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


**core — sem alterações.** `homeassistant/components/advantage_air/climate.py`; `homeassistant/components/amcrest/binary_sensor.py`; `homeassistant/components/androidtv/media_player.py`; `homeassistant/components/balboa/select.py`; `homeassistant/components/braviatv/coordinator.py`; `homeassistant/components/control4/media_player.py`; `homeassistant/components/modern_forms/light.py`; `homeassistant/components/openevse/select.py`; `homeassistant/components/overkiz/alarm_control_panel.py`; `homeassistant/components/rituals_perfume_genie/select.py`; `homeassistant/components/sql/sensor.py`; `homeassistant/components/unifiprotect/select.py` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


**blender — sem alterações.** `intern/cycles/util/math_base.h`; `source/blender/blenlib/BLI_math_base_c.hh`; `source/blender/blenlib/BLI_math_inline.hh`; `source/blender/blenlib/intern/math_base_inline.cc` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


**godot — sem alterações.** `misc/dist/html/service-worker.js`; `misc/utility/svgo.config.mjs`; `modules/webrtc/library_godot_webrtc.js`; `modules/websocket/library_godot_websocket.js`; `modules/webxr/native/library_godot_webxr.js`; `modules/webxr/native/webxr.externs.js`; `platform/web/eslint.config.cjs`; `platform/web/js/engine/config.js`; `platform/web/js/engine/engine.externs.js`; `platform/web/js/engine/engine.js`; `platform/web/js/engine/features.js`; `platform/web/js/engine/iframe.js`; `platform/web/js/engine/preloader.js`; `platform/web/js/jsdoc2rst/publish.js`; `platform/web/js/libs/audio.position.worklet.js`; `platform/web/js/libs/audio.worklet.js`; `platform/web/js/libs/library_godot_audio.js`; `platform/web/js/libs/library_godot_debugger.js`; `platform/web/js/libs/library_godot_display.js`; `platform/web/js/libs/library_godot_editor_debugger.js`; `platform/web/js/libs/library_godot_emscripten.js`; `platform/web/js/libs/library_godot_fetch.js`; `platform/web/js/libs/library_godot_input.js`; `platform/web/js/libs/library_godot_javascript_singleton.js`; `platform/web/js/libs/library_godot_os.js`; `platform/web/js/libs/library_godot_runtime.js`; `platform/web/js/libs/library_godot_webgl2.externs.js`; `platform/web/js/libs/library_godot_webgl2.js`; `platform/web/js/libs/library_godot_webmidi.js`; `platform/web/js/patches/patch_em_gl.js`; `thirdparty/glslang/glslang/OSDependent/Web/glslang.after.js`; `thirdparty/glslang/glslang/OSDependent/Web/glslang.pre.js` Relevância: contratos e/ou elegibilidade/compilação estática indicados no JSON; artefatos gerados ficam somente na Engineering Library.


O provedor Go standard library é a imagem fixada `golang@sha256:0a5f7fe796599ff487605987432e7619ae45beeb2fba4c2ce0b907879932aebf`, não um repositório Git adicional com SHA inventado. Sete arquivos de fonte/licença/versão foram preservados; `cmp/cmp.go` e `slices/sort.go` foram lidos integralmente. Headers host Clang/SDK têm inventário separado de 145 identidades sem cópia proprietária. SQLx foi compilado para exports estáticos em cópia própria; nenhuma aplicação, suíte upstream, init ou programa dos 15 projetos foi executado nesta campanha. As provas nativas com stubs descritas nos relatórios de 17/11 são históricas, não execuções desta janela.

## 18. Riscos, bloqueios e limites restantes

- O validador mecânico não verifica semântica geral; ainda aceita prosa genérica com substrings ou metadados indevidamente atribuídos à aplicação. O guarda de eco corrige só a instrução completa observada.
- Perfis de fonte são subconjuntos explícitos. Tipos/imports, comportamento de helpers, efeitos, aridade de valores de chamadas, completude e runtime não se inferem de citações/AST. Recusas não viram documentação inventada.
- O cache opt-in vincula pedido preparado, versões/modelo/skills e mantém proveniência de arquivo completo; não resolve invalidação semântica por dependências externas não selecionadas. Quatro [controles próprios](.local-backups/adaptive-20261118/incremental-dependency-scope-v1/review.json), com zero modelo, confirmaram: helper não configurado produz no-op com reuso OFF e ON; helper selecionado invalida; helper configurado mas fora das unidades selecionadas atualiza metadados e reutiliza os fatos do pedido idêntico. O stub só descreve a chamada, sem inventar o resultado do helper.
- O parser normal Python permanece 3.11; a alternativa 3.14 foi privada e checksum-bound. Decorators/generics fora do perfil não receberam fallback silencioso.
- Nenhuma resposta neural recebeu aprovação integral de publicação/treino nesta campanha; há fatos corretos parciais e ganhos locais preservados. Não há nota global ou 95%.
- Falta aprovação de dados, base/tokenizer treináveis, framework e piloto/holdout validados para treino. Candidatos e licenças preservados não encerram esses gates.
- LFS/remote ausentes; arquivos ignorados e partes grandes continuam dependências locais. Cópias redundantes locais não equivalem a desastre remoto.
- Windows, AMD64 nativo, runtime Ruby hermético e portabilidade genérica Clang/SDK/Node não foram comprovados.
- Checkpoints tiveram intervalos além do alvo aproximado; os horários reais e o gap máximo estão declarados.

## 19. Retomada segura e reprodução

1. Ler este relatório, o recibo de fechamento, a fila e o checkpoint mais recente. Conferir a existência real de processos antes de repetir um pedido. Todas as 97 chamadas desta janela já estão completas.
2. Preservar mudanças do proprietário. Usar novo clone/workspace; não fazer reset/clean/stash, staging, commit ou push. Verificar base/manifest/hashes antes de executar consumidores.
3. Restaurar primeiro a cápsula de corpo verificada e depois o suplemento de relatório/manifest. Partes/model graph, runtime e checkpoints anteriores são dependências explicitadas; não presumir que só Git as contém.
4. Rodar `python3 agent/recovery/bootstrap.py knowledge`; verificar store independente antes de qualquer runtime. Nunca sobrescrever o original. Os scripts `prepare_capsule_recovery35.py`, `run_capsule35_offline.rb`, `run_capsule35_source_consumers.rb` e `restore_capsule35_js_runtime.py` conservam o roteiro executado e seus limites.
5. Para dados, validar manifests pais, reviews, source packets e o suplemento NOTICE. Manter famílias/pares/línguas juntos. Diagnósticos e candidatos não podem entrar automaticamente em trainer.
6. Selecionar uma tarefa substantiva da fila, congelar critérios/fontes antes da inferência e registrar ganho, perda e afirmações sem apoio. Não repetir falhas idênticas para buscar um resultado favorável.

Os scripts de recuperação registrados têm caminhos desta instalação e destinos únicos. Adaptar explicitamente um novo destino sem sobrescrever os existentes; não chamar repetidamente scripts que recusam workspace já criado. Não existe `GENERAL_TRAINING` demonstrado nesta árvore.

## 20. Próxima campanha e conclusão auditável

A próxima janela deve priorizar dependências/helper contracts com fonte verificável e invalidação incremental, loader Go fiel ao módulo e transferência em novos construtos/famílias. Depois, submeter os candidatos sintáticos à revisão de treinamento e ampliar holdout separado; só considerar LoRA/QLoRA quando os nove gates estiverem demonstrados. Não há justificativa nesta evidência para trocar defaults, baixar modelos ou treinar agora.

O [suplemento de preflight da fila](.local-backups/adaptive-20261118/remaining-backlog-preflight-reconciliation.json) verificou os hashes dos 87 candidatos em 25 contratos, sem novas inferências ou revisão do Axum reservado. Ele corrige a referência histórica genérica 123/710: o baseline real desta campanha era 143/798 e o caller atual exige novo baseline específico. Tarefas no mesmo contrato não contam como transferência independente. A [matriz atual de limites](.local-backups/adaptive-20261118/remaining-unit-boundaries-v1/review.json) executou 23 seletores reais em contratos não Axum: 20 selecionados e três recusas (duas classes Python e Value::DECIMAL); os nove Go coincidiram nas citações entre parser nativo e consumidor Linux. Os dois Axum não foram analisados novamente. Isso prepara escolhas de unidades, sem aprovar semântica, baseline neural ou treino; os 87 candidatos continuam exigindo preflight completo.

Os 87 candidatos ainda não preflightados são continuidade preservada, não justificativa para prometer entendimento geral ou executar indefinidamente além da janela. O resultado entregue é um agente local com operações e extrações limitadas mais verificáveis, pesquisa positiva/negativa rastreável e recuperação realmente exercitada. Não são pesos novos nem manuais completos publicados.

Sugestões de Conventional Commit pertencem apenas à Engineering Library e serão apresentadas como sugestões; nenhuma será executada. Os recibos finais, hashes, status e evidência de pacote estão nos links acima e no suplemento de fechamento.
