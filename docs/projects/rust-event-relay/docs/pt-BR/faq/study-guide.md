# Limite de leitura — atualização em 2026-10-18


Use o [dossiê atual](../architecture/overview.md) e as [questões do escopo final](#questões-do-escopo-local-final) para o comportamento presente. Questões abaixo preservam escopo dos marcos, inclusive produtor, consumidor e integração antes ausentes. Mecanismos seguem úteis; “futuro”, “não implementado” e “atual” pertencem às datas originais. Q001–Q007 preservadas.

## Questões e respostas históricas

# Rust Event Relay — Guia de Estudo para Entrevista Técnica

## Atualização de engenharia — Marco 2.5, 2026-10-12

O [worker Rust separado](../architecture/milestone-2-5.md) compõe configuração validada, tracing JSON, pool/repositório PostgreSQL dedicado e lifecycle RabbitMQ. [Scheduling da aplicação](../../../../../../../rust-event-relay/backend/src/application/worker.rs) usa dispatch estático/dependências controladas; [composição](../../../../../../../rust-event-relay/backend/src/bin/relay.rs) constrói infraestrutura concreta. Admite uma entrega por vez, sem tarefas criadas pelo worker, com token novo por invocação. NoEvent espaça uma chamada, sem provar backlog vazio. Apenas aceitação confirmada e conclusão Applied permitem próxima admissão imediata.

Lição geral: pacing entre invocações controla pressão operacional; não grava agenda durável de retry. Rust usa defaults de 1000 ms para idle/failure e 5000 ms para reconnect, preservando available_at/last_error/attempts. Eventos elegíveis inválidos/permanentemente falhos ainda podem obstruir progresso. Fairness, backoff/jitter, quarentena e DLQ exigem políticas/evidências próprias.

Lição geral: conexão inutilizável é fato de lifecycle, sem autorizar repetição de efeito anterior. Rust fecha/substitui após Unavailable/Uncertain ou canal sabidamente aposentado/desconectado, sem adquirir quando falta publisher usável. Serialization/Unroutable/Rejected preservam conexão usável. Reconectar não reconcilia aceitação passada. Aquisição incerta não fornece claim confirmado; conclusão incerta pode esconder processed. Sem compensação ou republicação do claim anterior.

Exemplo Rust concreto, abreviado do worker, com tipos dos ports existentes:

```rust
let request = AcquireRequest::new(config.lease); // token novo
let outcome = deliver_once(repository, publisher, request).await;
let action = decision(&outcome); // distingue publicação e conclusão
// Continue, Idle, Pace ou Replace; esperas devem disputar com shutdown.
```

Lição geral: shutdown compartilha budget finito. Primeiro interrompe admissão, permite drain, cancela ao expirar esse prazo e fecha publisher/pool com o mesmo deadline absoluto. Descartar future pode ocultar efeitos persistidos/aceitos; release cego de claim abandonado é inseguro. Defaults Rust: drain 15 s dentro de 25 s total; Supervisor 30 s por filho; Compose 65 s para grupos sequenciais. Timeout de aquisição do pool não limita consultas: statement/lock de sessão dedicada são 5 s/3 s, distintos das esperas de rede RabbitMQ e do lease durável de 60 s. Esses tempos não garantem lease ativo.

[Testes controlados](../../../../../../../rust-event-relay/backend/tests/worker.rs) demonstram política; [composição real isolada](../../../../../../../rust-event-relay/backend/tests/worker_smoke.rs) verifica entrega/conclusão e Supervisor individual/coletivo. Happy path não demonstra crash/recuperação. Migração compartilhada de posse continua pendente, autostart relay é false e /health prova liveness HTTP. Falha de configuração/setup encerra sanitizadamente; outage RabbitMQ em runtime reconecta explicitamente. Somente imagem/container app foram atualizados, preservando infraestrutura/dados compartilhados.

Referência transferível para futuras melhorias do Viva Bem: limitar admissão, separar construção de infraestrutura e scheduling, distinguir aceitação externa e conclusão durável, preservar incerteza/erros primários e de cleanup e planejar encerramento finito. Trata-se de referência futura; não se afirma que Viva Bem utiliza essa arquitetura, nem se descreve/modifica implementação privada. Interface gráfica opcional só após conclusão do núcleo, se houver necessidade operacional concreta. Próximo Rust: 2.6, experimentos integrados de crash/falha/recuperação e fechamento do marco; sem alegações de throughput/fairness/efeitos do consumidor ou at-least-once ponta a ponta.

Seções datadas preservam escopo histórico; status do worker é atualizado por esta seção.


## Atualização de entrevista 2.4 — 2026-10-12

Pergunta: O que acontece quando broker aceita, mas completion falha?

**Resposta:** O caso de uso chamável `deliver_once` retorna `Published` com claim original e resultado separado de completion. Somente `Ok(Applied)` significa conclusão durável reconhecida. OwnershipLost e erros, incluindo CommitUncertain, não causam novo envio nem release. Recuperação pode duplicar ID estável. Falhas de publicação preservam erro original e cleanup; falhas definitivas liberam uma vez, Uncertain mantém lease. Cancelamento pode ocultar efeitos sem retornar erro. Consulte [dossiê atual](../architecture/overview.md) para ports, limites do lease e evidência.

Aprofundamento: Já é worker relay em execução? Não. 2.4 é caso de uso chamável; 2.5 compõe/opera polling, lifecycle/reconexão do publisher e Supervisor. 2.6 testa crash/recuperação ponta a ponta. Seções anteriores preservam escopo de seus marcos.


[English](../../en/faq/study-guide.md) | [Português brasileiro](study-guide.md)

Estudo de portfólio sobre entrega confiável sob falhas. Fontes: [README](../../../README.pt-BR.md), [arquitetura](../architecture/overview.md), [ownership](../architecture/milestone-2-3.md) e código. Primeira pessoa descreve implementação, não produção. Alternativas são comparações de estudo; ADR 007 registra a decisão de ownership. Auditoria de 2026-10-10 não executou runtime. Atualização de 2026-10-12 usa validação separada do Marco 2.3; veja [dossiê atual](../architecture/overview.md).

## 1. Visão geral e escopo

#### Pergunta: Já é um motor de entrega?

**Resposta modelo:** “O binário HTTP carrega configuração/tracing, atende liveness e encerra de forma graciosa. Módulos separados oferecem envelope, reader PostgreSQL, publisher RabbitMQ confirmado e modelos/contratos/schema e mutações PostgreSQL produtivas de ownership. Não há worker ligando aquisição, publicação e conclusão. Entrega ponta a ponta, retries e dead-letter seguem futuros.”

2.1 entrega publisher; 2.2 tipos/portas/migração; 2.3 operações PostgreSQL produtivas. 2.4 orquestração, 2.5 worker/composição e 2.6 experimentos de crash continuam adiados. Documentação de estudo não altera os marcadores desses marcos.

## 2. Arquitetura e caminhos

`main.rs` → config/telemetry → listener TCP → `application::serve`. `/health` devolve `ok\n`; não conecta a banco/broker nem prova readiness. SIGINT/SIGTERM em Unix acionam shutdown. Future de shutdown injetado permite teste em socket efêmero sem estado global de sinais.

Caminho separado: `PgPool` injetado sustenta `PostgresOutboxRepository::read_eligible`, com SELECT parametrizado limitado e restauração validada. `RabbitMqPublisher` implementa `EventPublisher`, possui conexão/channel, declara topologia durável e publica JSON persistente com ID estável/confirm. Nenhum adaptador é chamado pelo HTTP.

[Contratos](../../../../../../../rust-event-relay/backend/src/persistence/ownership.rs) usam futures Send nativos e despacho estático. SQLx/Lapin ficam na infraestrutura; domínio valida invariantes. Portas pequenas explicitam responsabilidades/testes, sem registry de plugins runtime. Despacho dinâmico poderia permitir escolha runtime com custo de alocação/dispatch; não está implementado.

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

PostgreSQL opt-in usa bancos isolados gerados para reads/migrações originais e ownership up/down. RabbitMQ real cobre roteamento/confirms e incerteza por timeout/cancelamento. CI possui jobs padrão/PostgreSQL/RabbitMQ; arquivo de workflow não prova execução remota aprovada. [Validação histórica](../testing/validation-results.md) registra execuções anteriores, sem repetição aqui. Modelos/fakes não provam concorrência PostgreSQL; suíte real de 2.3 agora verifica aquisições disjuntas, SKIP LOCKED e expiração após espera sob condições testadas.

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


## Recuperação integrada — Perguntas de aprofundamento, Marco 2.6

### Por que confirmar publicação antes de processed ainda permite duplicatas?

Porque RabbitMQ e PostgreSQL não compartilham uma transação. No caso B, aceitação foi confirmada e o processo morreu antes de completion. O banco permaneceu pending; outro worker recuperou após expiração e publicou o mesmo ID. Confirm-before-complete evita concluir sem aceitação confirmada, mas não elimina a janela entre sistemas. Consumidor precisa tratar duplicatas; o experimento não implementa essa regra de negócio.

### O que CommitUncertain permite concluir?

Somente que o chamador não recebeu resultado durável conhecido. O proxy de teste perdeu a resposta após observar COMMIT no servidor: pool independente viu processed e o restart não adquiriu. Outro schedule incerto pode ter resultado diferente. Não liberar ou republicar cegamente evita compensar uma conclusão que já ocorreu; inspeção/reconciliação precisam de evidência própria.

### Token novo impede o worker antigo de enviar ao broker?

Não. A complete/release de A foi rejeitada quando B possuía token novo, mas o publisher anterior ainda enviou o envelope original. SQL protege transição local, e RabbitMQ não verifica esse token. Lease expirado não significa que o processo antigo parou; separar autoridade durável de fencing externo explica duplicação mesmo sem posse SQL sobreposta.

### Como comprovar concorrência sem contar apenas mensagens?

Segurar completion com advisory lock isolado, iniciar dois binários e observar duas posses commitadas com tokens distintos/count 1/leases vivos e duas esperas SQL. Conferir o conjunto de IDs do broker separadamente, liberar barreira e verificar processed. Isso sustenta o schedule observado, não fairness, ordem de negócio ou ausência universal de duplicatas.

### Quando chamar a pipeline de fundação pelo menos uma vez?

Após relacionar código e experimentos a eventos duráveis válidos, recuperação de trabalho pending e aceitação confirmada antes de completion. A formulação exige disponibilidade eventual, worker ativo/reiniciado, falhas resolvíveis, storage suportado e tratamento downstream de duplicatas. Exclui poison, rejeição permanente, count esgotado, power loss e efeitos exactly-once não testados. Dizer exatamente quais processos são originais e quais adapters/lifecycles são instrumentados torna a afirmação revisável.

[Evidência e fronteiras](../architecture/milestone-2-6.md) | [Aceitação e premissas](../operations/milestone-2-review.md).

## Integração durável — Marco 3.3

[Decisões contextuais, jitter sem viés, pausas separadas, manutenção finita e cancelamento](../adr/008-durable-failure-policy.md). Integração implementada e testada em infraestrutura isolada; rollout compartilhado permanece pendente. Descrições anteriores mantêm escopo histórico. Scanning geral fica em 3.4, replay em 3.5 e fechamento em 3.6.

## Questões do escopo local final

[Dossiê atual](../architecture/overview.md)

### Q008 — Introdutória: O que agora é real na UI?

**Resposta:** Produtor, relay e consumidor executam trabalho local real. Uma execução cria fato/outbox atomicamente e normalmente muda estoque 10 para 15. Ações duplicadas e concorrentes republicam o envelope original, mantendo um efeito e estoque 15. Uma rejeição controlada antes do envio exercita retry persistido. Animações de crash/corrida/perda de confirmação ou ACK são educacionais, sem derrubar infraestrutura. Kill, reconexão e resultados ambíguos reais pertencem a testes isolados.

Aprofundamento: Por que manter simulação? Expõe tempo/incerteza sem controles globais inseguros. Explique o valor educacional separando fatos persistidos de etapas ilustradas.

### Q009 — Intermediária: Como idempotência do produtor difere de deduplicação do consumidor?

**Resposta:** O produtor identifica intenção fixa por UUID: mesma intenção resolve execução existente, conteúdo alterado conflita. Uma transação registra recebimento, fixture inicial e outbox, evitando fato confirmado sem registro de encaminhamento. Consumidor usa recibo durável por nome/ID do evento e valida conteúdo imutável, confirmando recibo e estoque juntos. Cliente pode perder resposta após commit; inspecionar a mesma identidade é mais seguro que criar outra intenção. Nenhuma fronteira torna transporte exatamente uma vez.

Aprofundamento: Email/pagamento externo entraria na transação? Não. Exige protocolo próprio de idempotência/encaminhamento durável; o projeto demonstra apenas mutação local de estoque.

### Q010 — Desafiadora: Por que contar aquisições em vez de mensagens enviadas?

**Resposta:** O fato durável é aquisição confirmada, inclusive crash antes de enviar; worker não conta com certeza todas as mensagens aceitas externamente sob perda de confirmação. attempt_count vitalício não é zerado. Baseline/máximo do ciclo definem saldo; revisão/token novo protegem transições. Lease expirado permite outra aquisição, mas não impede publicação antiga. Contador não é quantidade de mensagens no broker nem prova de exclusividade externa.

Aprofundamento: Replay apaga esgotamento? Replay autorizado inicia ciclo com estado/revisão esperados e requisição auditada, preservando histórico e evento. Limites de armazenamento/histórico inválido permanecem; não é reparo irrestrito.

### Q011 — Desafiadora: Como duplicatas concorrentes evitam dois incrementos?

**Resposta:** Inserção única do recibo precede mutação em READ COMMITTED. Apenas vencedor aplica efeito e completa recibo. Outra inserção espera conflito; novo comando observa vencedor confirmado e compara conteúdo imutável restaurado. Conteúdo igual retorna Duplicate sem incrementar; diferente não é aceito como mesmo evento. Completude diferida impede commit parcial. Retenção da identidade integra correção, não é limpeza opcional.

Aprofundamento: Por que BYTEA e não só hash? Representação versionada permite restauração/igualdade do modelo sem depender apenas de colisão de digest ou normalização JSONB. Custa armazenamento/validação. Alteração pelo proprietário do banco permanece fora das proteções.

### Q012 — Desafiadora: O que confirms, processed, recibos e ACKs provam?

**Resposta:** Confirm estabelece aceitação observada pelo publisher. processed_at registra transição protegida do relay. Recibo concluído estabelece efeito local. Depois consumidor tenta enviar ACK; sucesso não estabelece recebimento no broker. Fatos podem aparecer em ordens distintas. Crash após confirm antes de processed permite republicar; crash após commit antes da liquidação do ACK permite reentrega. ID estável/recibo retido impedem segundo efeito local suportado, não transporte duplicado.

Aprofundamento: O que significa unknown? Falta de confirmação não prova commit ou rollback. Preserve identidade, inspecione e não compense/reenvie apenas por timeout. Snapshot sem recibo também não exclui commit posterior.

### Q013 — Intermediária: Por que quarentena não é apenas NACK e descarte?

**Resposta:** Aplicação preserva entrada rejeitada/não suportada/conflitante por publicação confirmada em quarentena antes de ACK na origem. Falha ou impossibilidade de preservação exata mantém origem pendente. Evidência primária é separada de falha secundária de preservação/ACK. dead_letter SQL é terminal do relay, não essa topologia. Política de dead-letter do broker seria outro protocolo com outras evidências/janelas.

Aprofundamento: Quarentena pode duplicar? Sim: preservação confirmada e ACK desconhecido podem repetir na reentrega. Evita perda intencional; não torna duas operações AMQP atômicas.

### Q014 — Intermediária: Como inspecionar histórico sem disparar trabalho?

**Resposta:** GET de histórico/evidência e seleção de ação carregam snapshots com observed_at. Não submetem intenção nem repetem ação. Refresh falho mantém observação; após 15 segundos fica stale. Polling/timeout limitados e fechar modal controlam só observação. Correlação execução/ação/evento separa Duplicate de tráfego sem relação. Contagens limitadas são limites inferiores. Bearer/origem/header restringem HTTP local; session storage contém IDs, não token.

Aprofundamento: Por que não reenviar unknown automaticamente? A ação anterior pode ter publicado/confirmado. Nova ação é trabalho novo explícito; GET não resolve toda incerteza distribuída nem deve fingir isso.

### Q015 — Desafiadora: O que defender sobre testes, operação e capacidade?

**Resposta:** Testes puros/fakes demonstram política/sequência; PostgreSQL/RabbitMQ/processos isolados cobrem falhas selecionadas; browser separa UI real/ilustrada. Manifesto de 2026-10-17 registra aceite em sua base, não revisão atual ou CI remoto. Launcher principal, artefatos runtime/test separados e controles nomeados Supervisor sustentam operação local. Limites de recursos/retenção rejeitam excesso sem apagar evidência. Não são capacidade produtiva medida, recuperação de desastre ou HA/TLS.

Aprofundamento: O que justificaria produção? Segurança de transporte, menor privilégio, retenção/restauração de banco e broker, responsabilidade operacional e evidência por carga. São melhorias hipotéticas, não bloqueios adicionados retroativamente ao escopo local concluído.
