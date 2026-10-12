# Rust Event Relay — Guia de Estudo para Entrevista Técnica

[English](../../en/interviews/rust-event-relay.md) | [Português brasileiro](rust-event-relay.md)

Estudo de portfólio sobre entrega confiável sob falhas. Fontes: [README](../../../../rust-event-relay/README.pt-BR.md), [arquitetura](../../../../rust-event-relay/docs/pt-BR/architecture/overview.md), [ownership](../../../../rust-event-relay/docs/pt-BR/architecture/milestone-2-3.md) e código. Primeira pessoa descreve implementação, não produção. Alternativas são comparações de estudo; ADR 007 registra a decisão de ownership. Auditoria de 2026-10-10 não executou runtime. Atualização de 2026-10-12 usa validação separada do Marco 2.3; veja [dossiê atual](../architecture/rust-event-relay.md).

## 1. Visão geral e escopo

#### Pergunta: Já é um motor de entrega?

**Resposta modelo:** “O binário HTTP carrega configuração/tracing, atende liveness e encerra de forma graciosa. Módulos separados oferecem envelope, reader PostgreSQL, publisher RabbitMQ confirmado e modelos/contratos/schema e mutações PostgreSQL produtivas de ownership. Não há worker ligando aquisição, publicação e conclusão. Entrega ponta a ponta, retries e dead-letter seguem futuros.”

2.1 entrega publisher; 2.2 tipos/portas/migração; 2.3 operações PostgreSQL produtivas. 2.4 orquestração, 2.5 worker/composição e 2.6 experimentos de crash continuam adiados. Documentação de estudo não altera os marcadores desses marcos.

## 2. Arquitetura e caminhos

`main.rs` → config/telemetry → listener TCP → `application::serve`. `/health` devolve `ok\n`; não conecta a banco/broker nem prova readiness. SIGINT/SIGTERM em Unix acionam shutdown. Future de shutdown injetado permite teste em socket efêmero sem estado global de sinais.

Caminho separado: `PgPool` injetado sustenta `PostgresOutboxRepository::read_eligible`, com SELECT parametrizado limitado e restauração validada. `RabbitMqPublisher` implementa `EventPublisher`, possui conexão/channel, declara topologia durável e publica JSON persistente com ID estável/confirm. Nenhum adaptador é chamado pelo HTTP.

[Contratos](../../../../rust-event-relay/src/persistence/ownership.rs) usam futures Send nativos e despacho estático. SQLx/Lapin ficam na infraestrutura; domínio valida invariantes. Portas pequenas explicitam responsabilidades/testes, sem registry de plugins runtime. Despacho dinâmico poderia permitir escolha runtime com custo de alocação/dispatch; não está implementado.

## 3. Identidade e outbox transacional

#### Pergunta: O que precisa ser atômico?

**Resposta modelo:** “O produtor futuro precisa inserir alteração de negócio e evento outbox na mesma transação local. Schema/reader existem, mas nenhum endpoint produtor implementa essa transação aqui. Broker remoto fica fora da transação do banco.”

Envelope preserva UUID v7, ocorrência UTC, versão, agregado, correlation/causation opcionais e JSON. Restauração valida sem regenerar ID. Ordenação UUID não é ordem de entrega; schema_version não implementa compatibilidade automática. JSON/strings flexíveis custam garantias de tipos/formato.

**Aprofundamento:** Chave primária duplicada prova operação idêntica? Não: prova identidade existente, não mesmo payload/efeito. Idempotência/reconciliação do produtor ainda precisam de projeto.

## 4. Snapshot e autoridade

#### Pergunta: Dois workers podem ler o mesmo evento?

**Resposta modelo:** “Sim. Reader filtra pending por cutoff do chamador e limite sem claim ou lock de entrega. Inclui pending com lease e contador esgotado. Snapshot é dado, não autorização para publicar/concluir.”

Ordena disponibilidade/criação/ID. Limite de linhas não limita bytes nem concorrência. Linha inválida selecionada falha todo o lote; sem reparo/quarentena/retry. Pool/deadlines pertencem ao chamador. Decoding privado de timestamps/JSON rejeita valores não suportados e preserva precisão numérica JSON.

## 5. Lease durável e autoridade do banco

#### Pergunta: Por que não segurar transação durante publicação?

**Resposta modelo:** “ADR 007 escolhe aquisição/conclusão curtas com publicação fora da transação. Locks/conexões durante espera de broker custam recursos e não desfazem publicação após rollback. Expiração durável permite recuperação, com custo de tokens/tempo e possível sobreposição de envios.”

Regras puras mantêm leased como pending, incrementam aquisições, substituem ownership expirado por token novo e rejeitam dono antigo no instante exato da expiração. Complete limpa lease e marca processed; release limpa ownership sem agendar retry. ID identifica evento; token identifica aquisição. attempt_count representa aquisições commitadas, incluindo crash antes de enviar, não envios reais.

Portas exigem tempo do banco após lock e aquisição confirmadamente commitada antes de devolver autoridade. **Marco 2.3 implementa os ports em módulo de posse da infraestrutura; reader permanece apenas observação.** Migração 2.2 adiciona campos coerentes; constraints provam forma da linha, não histórico legal/token globalmente novo. `CommitUncertain` significa possível commit; `OwnershipLost`, ausência de autoridade. Nenhum é sucesso presumido.

**Aprofundamento:** Token bloqueia envio RabbitMQ antigo? Não. Processo obsoleto ainda pode enviar; token guarda apenas transições no banco. Efeitos futuros tolerantes a duplicatas exigem idempotência no consumidor.

## 6. Confirms e janelas de falha

| Cenário | Comportamento / limite |
| --- | --- |
| Serialização ou desconexão | Erro classificado, sem aceite confirmado |
| Mandatory sem rota | Mensagem retornada vira Unroutable |
| Confirm negativo | Rejected |
| Timeout/erro/cancelamento após iniciar envio | Aceite pode ser incerto; channel aposentado |
| Ack sem retorno | Sucesso de publisher, não processamento do consumidor |
| Sucesso seguido de futura falha na conclusão | Pode duplicar na recuperação; orquestração ausente |

Mutex serializa uma publicação em voo; espera de mutex e envio/confirm têm deadlines próprios, não prazo total único. Setup/close são limitados. Sem reconexão/retry automático. Rejected/Unroutable definitivos não precisam aposentar channel; incerteza aposenta. Erros formatam categorias sanitizadas e retêm fontes tipadas; expor a cadeia exige política de diagnóstico.

**Resposta modelo:** “Separo indisponibilidade antes de enviar, rejeição conhecida e aceite incerto. Nenhum erro de publicação autoriza processed. Aceite seguido de conclusão incerta é a janela futura de duplicação; confirms/leases não provam exactly-once.”

## 7. Testes e evidências

Testes padrão cobrem envelope, invariantes, limites de ownership, futures de contrato, erros, lifecycle HTTP e confirmações/configuração do publisher. Alguns testes independentes de banco/broker usam sockets TCP locais; independência não significa zero I/O.

PostgreSQL opt-in usa bancos isolados gerados para reads/migrações originais e ownership up/down. RabbitMQ real cobre roteamento/confirms e incerteza por timeout/cancelamento. CI possui jobs padrão/PostgreSQL/RabbitMQ; arquivo de workflow não prova execução remota aprovada. [Validação histórica](../../../../rust-event-relay/docs/pt-BR/testing/validation-results.md) registra execuções anteriores, sem repetição aqui. Modelos/fakes não provam concorrência PostgreSQL; suíte real de 2.3 agora verifica aquisições disjuntas, SKIP LOCKED e expiração após espera sob condições testadas.

## 8. Alternativas e aprofundamento

| Escolha | Benefício | Custo / alternativa razoável |
| --- | --- | --- |
| Outbox local do produtor | Intenção negócio/evento atômica | Produtor ausente; CDC mudaria captura |
| Transações curtas/leases | Evita locks em espera remota | Envio externo obsoleto; lock longo também não desfaz efeito remoto |
| Portas separadas | Observação, autoridade e transporte claros | Mais tipos; adaptador único esconderia semânticas distintas |
| Confirm e mandatory | Detecta aceite/sem rota | Não prova efeito; webhook tem outro ack |
| Scaffold HTTP incremental | Lifecycle testável | Liveness não é relay funcionando |

Pratique: o que acontece na expiração exata? Por que tempo após lock? Como aquisição vazia deixa backlog? Release muda available_at? CommitUncertain é rollback? Como deduplicação e efeito compartilham transação no consumidor? Quais testes devem preceder alegação de produção?

## 9. Roteiro ordenado

1. HTTP/configuração e diferença entre liveness/readiness.
2. Envelope, identidade, ocorrência e validação.
3. Schema/reader, limites, linha inválida e transação do produtor.
4. Confirms, mandatory e aceite incerto.
5. Limites puros de lease/portas; ADR 007 antes de comparar alternativas.
6. Testes/CI/evidência histórica; separar modelos/schema, mutações verificadas e orquestração ausente.
7. Pré-requisitos 2.4–2.6 e idempotência, sem marcar entrega ou estudo concluídos.

## Aprofundamentos adicionais de entrevista fundamentados no código

Perguntas e respostas originais acima foram preservadas. IDs abaixo identificam a sequência adicional; não renumeram material retido. Níveis orientam estudo, não status implementado. Aprofundamentos incluem respostas para manter a sequência autossuficiente.

### Q001 — Introdutória: O que realmente executa quando o binário inicia?

**Resposta:** Implementado: main carrega configuração, inicia tracing JSON, abre TCP e chama ciclo HTTP Axum. GET /health retorna ok fixo; SIGINT/SIGTERM solicitam encerramento gracioso no Unix. O binário não cria pool PostgreSQL, publisher RabbitMQ ou worker polling. Módulos chamáveis separados restauram envelopes, leem snapshots, publicam com confirms e modelam ownership. Separação permite testes focados, mas presença de módulos não prova pipeline de entrega.

Aprofundamento: Por que health pode ficar verde com broker indisponível? Não chama broker/banco; health dos serviços Compose é gate de startup separado. Aprofundamento: O que readiness exigiria? Definir dependência de armazenamento, topologia, worker ativo e capacidade de backlog e compor checks com falhas limitadas. É hipotético, não readiness/métricas entregues. Segurança de memória Rust ajuda em suas fronteiras, mas não torna entrega distribuída correta nem elimina incerteza lógica/transporte. Explique escopo antes de melhorias de confiabilidade.

### Q002 — Intermediária: Como identidade e precisão JSON sobrevivem à persistência?

**Resposta:** Implementado: envelopes novos geram UUID v7 e horário UTC; restauração conserva identidade, ocorrência, strings de agregado, versão não zero, UUIDs opcionais de correlação/causação e JSON. Versão é número, não engine registrada de evolução. JSONB conserva conteúdo semântico, não formatação/ordem original. O adapter usa decodificação JSONB privada com check de byte de versão e arbitrary_precision do serde_json para evitar arredondar inteiros/decimais grandes. Timestamp verificado rejeita infinito/fora da faixa em vez de aritmética insegura. Dado selecionado inválido falha toda a leitura.

Aprofundamento: UUID v7 impõe ordem global de negócio? Não. Timestamps/IDs ajudam ordenação; causalidade e ordem de agregado exigem contrato próprio. Aprofundamento: Por que não reparar silenciosamente eventos? Poderia inventar identidade/significado e esconder corrupção. Quarentena é política futura possível, mas ausente. Payload tipado daria garantias de compilação com acoplamento maior; relay atual usa envelope genérico. Compatibilidade de negócio precisa de validação separada; restauração não valida todo schema de payload.

### Q003 — Desafiadora: Por que snapshot elegível limitado não é permissão para entregar?

**Resposta:** Implementado: leitor PostgreSQL seleciona pending com available_at <= corte, ordena disponibilidade/criação/ID e usa LIMIT verificado. Não usa predicado de ownership, claim ou mutação; dois leitores podem ver o mesmo evento, inclusive pending com lease ou tentativas esgotadas. fetch_all limita linhas, não bytes totais de payload. Snapshot determina visibilidade da consulta; metadados podem envelhecer imediatamente. É contrato de observação, não autoridade de entrega.

Aprofundamento: Lote vazio significa ausência de backlog? Pode significar ausência de linhas até aquele corte; futuras, processadas ou excluídas são outro conjunto. Aquisição vazia também pode indicar leases ativos/tentativas esgotadas, não backlog vazio. Aprofundamento: E uma linha selecionada inválida? Restauração coleta Results; qualquer inválida falha lote sem retorno parcial ou reparo. Isso pode bloquear linhas úteis repetidamente. Política skip/quarentena exige semântica explícita de perda/diagnóstico e testes; não existe. Ampliar leitor para CRUD genérico esconderia garantias distintas.

### Q004 — Desafiadora: Quais garantias de lease foram escolhidas e quais são apenas contratos?

**Resposta:** Implementado: ADR 007 registra transações curtas e publicação fora dos locks. Regras puras usam identidade do evento e token de aquisição, rejeitam autoridade antiga/expirada e limpam ownership coerente em completion/release. Expiração é exclusiva: em expires_at exato o owner perde autoridade. Tentativas contam aquisições commitadas, não envios. Migração impõe campos nullable coerentes em pending; ports descrevem aquisição/completion/release e CommitUncertain. Adapter PostgreSQL produtivo agora implementa esses ports com transações Read Committed curtas, sem retries ocultos.

Aprofundamento: Por que horário do banco após lock? Espera pode tornar amostra anterior incorretamente válida para lease já expirado. Teste real de 2.3 coordena espera por lock atravessando expiração e verifica rejeição de completion e release; igualdade exata permanece evidência determinística do modelo. Aprofundamento: Token faz fencing RabbitMQ? Não. Protege predicados do banco; processo antigo ainda pode enviar. Transação longa manteria locks/conexões em espera remota e não desfaria envio aceito após rollback. Leases trocam esse custo por complexidade de expiração/recuperação e duplicatas possíveis. Deduplicação de consumidor é necessária no pipeline futuro; testes puros não provam concorrência do banco.

### Q005 — Desafiadora: Como confirms, returns, timeouts e completion criam janelas distintas?

**Resposta:** Implementado: publisher envia JSON persistente em topologia durável vinculada, com mandatory e confirms. Ack sem return é sucesso no broker; retorno mandatory é ausência de rota, nack é rejeição e timeout/erro/cancelamento após envio pode ser incerto. Adapter serializa uma chamada e aposenta channel em incerteza; não reconecta ou repete automaticamente. Confirm não é ack de consumidor nem commit de efeito de negócio.

Aprofundamento: E se futuro worker recebe Ack e não confirma completion no banco? Publicação pode ter ocorrido com linha elegível à recuperação, permitindo duplicata. Processar antes de publicar, ao contrário, arrisca perda. Aprofundamento: Como consumidor tornaria efeitos duplicados seguros? Hipoteticamente registrar ID estável e aplicar efeito na mesma transação local com chave única de deduplicação. Efeitos externos secundários precisariam de outbox própria ou coordenação equivalente. Nenhum consumidor/worker existe aqui. Exactly-once não decorre de Ack, mutex ou token.

### Q006 — Intermediária: Como dispatch estático, testes isolados e limites operacionais se relacionam?

**Resposta:** Implementado: ports retornam futures nativas Send e mantêm tipos SQLx/Lapin na infraestrutura. Isso suporta chamadores genéricos/dispatch estático e fakes sem boxing obrigatório. Dispatch dinâmico permitiria adapters escolhidos em runtime, mas exige interface compatível com objetos e frequentemente alocação; é alternativa, não API atual. Testes padrão exercitam invariantes/mapeamento e sockets HTTP locais; PostgreSQL opt-in possui bancos de nomes exatos e broker exercita roteamento/incerteza. Testes puros não provam claims concorrentes; integração separada de 2.3 agora os verifica nas condições testadas.

Aprofundamento: Workflow prova CI aprovado? Não. Execuções históricas são registros separados; auditoria de 2026-10-10 não executou runtime; validação de 2.3 está registrada separadamente. Aprofundamento: O que falta para produção? Orquestração/composição worker, retry/quarentena, efeitos do consumidor, limites de payload/admissão, telemetria, TLS e recuperação. Publisher admite um envio com prazos distintos de gate/publicação; limites de linhas não limitam bytes. Budgets Supervisor e volumes são mecanismos dev, não durabilidade sob queda, capacidade produtiva ou recuperação de backup verificadas. Nenhum gráfico de benchmark se justifica por essas configurações.


### Q007 — Desafiadora: O que COMMIT incerto exige do próximo use case?

**Resposta:** Marco 2.3 implementa ports de adquirir/concluir/liberar em transações Read Committed curtas; reader permanece observação. Aquisição retorna posse somente após confirmação do commit; commit incerto retorna erro mesmo que lease/contador já estejam persistidos. Completion/release também podem ter confirmado antes de perder resposta. Rejeição ordinária pelo servidor é diferente: fixture real com constraint diferida demonstra rollback e OperationFailed. Transporte/protocolo perdido no commit é conservadoramente CommitUncertain; posse incompatível continua OwnershipLost. Não há retry oculto ou conflito convertido em sucesso anterior.

Aprofundamento: Publicar após aquisição incerta? Não há claim ordinário confirmado. Inspecionar lease durável operacionalmente ou aguardar expiração e usar pedido novo, preservando ID do evento. Aprofundamento: Completion incerto? Processed pode estar persistido; repetição/republicação cegas podem interpretar estado incorretamente ou duplicar. Use case precisa expor incerteza e definir reconciliação; token não aplica fencing no RabbitMQ. Aprofundamento: Cancelar future prova rollback? Não. SQLx enfileira rollback da transação aberta descartada, mas commit pode ter ocorrido e cancelamento pode não retornar erro classificado. Testes cobrem cancelamento bloqueado pré-mutação/classificação, e proxy isolado de confirmação perdida nas três operações; cancelamento durante COMMIT continua não verificado. Proxy perde resposta após observar conclusão no servidor e consulta estado independente, demonstrando um resultado incerto confirmado sem generalizar para toda incerteza.
