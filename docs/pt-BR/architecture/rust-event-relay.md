## Marco 3.6 atual — aceitação integrada, 13/10/2026

**Marco 3 fechado com limitações explícitas não bloqueantes no escopo implementado definido; prontidão do projeto completo/produção é decisão distinta.** Base Rust `1b8b96998466eb10f68d59c2289c6abf66cd686e`; Library `665779b73de226c7eb39b621536249252f623c9f`; ambos inicialmente sem alterações locais. A [revisão estável](../../../../rust-event-relay/docs/pt-BR/operations/milestone-3-review.md) reúne matriz requisito/código/invariante/teste/runtime/limite dos Marcos 1, 2 e 3.1–3.5, comandos e leitura guiada. Seções anteriores mantêm seus escopos históricos datados.

Princípio geral: implementação, executável carregado, schema, topologia e apresentação no browser são evidências independentes. Build altera artefatos; não identifica revisão ativa. Testes não comprovam deploy, CI remota, efeito de negócio nem todas as agendas. Observação de linha não autoriza mutação; confirmação do broker não demonstra consumo; incerteza exige observação durável independente. Imutabilidade da aplicação não impede alteração pelo owner do banco.

Evidência Rust: 69 testes padrão passaram, 88 opt-in ignorados; 63 funções PostgreSQL (15 repository, 1 schema de posse, 12 ownership, 18 retry, 7 discovery, 10 replay); 3 broker; 5 smoke worker/Supervisor; recuperação integrada reportou 17 passes, sendo 16 funções substantivas e um helper sem efeito. Novos casos verificam Supervisor isolado direto/interativo, stop intencional e restart de saída inesperada nos dois aliases, além de matar processo exato após schedule, terminalização e replay commitados, verificam sucesso no último orçamento, identidade/histórico/conteúdo, token novo e recibo repetido. Regressões PostgreSQL cobrem replay concorrendo com discovery/isolation antiga e aquisição; down destrutivo mantém evento reabilitado, mas perde auditoria, que re-up não recupera. CLI SQLx real aplicou cinco upgrades, conferiu histórico SHA-384, no-op e down/re-up em banco descartável exato.

Evidência de apresentação: npm ci/type-check/build e 13 funções Chromium 156.0.8078.4 passaram em 320/375/768/1024/1920px. Screenshots renderizados, teclado/foco/scroll do modal, cancelamento/reprodução, movimento reduzido, conteúdo longo, console/recursos/favicon conferidos. Não é certificação completa de acessibilidade nem cobertura Firefox/WebKit. Falha inicial: npm ci invalidou cache Vite ativo reutilizado pelos testes. Agora servidor novo em 5174 e cache próprio isolam a aceitação; asserções preservadas. Browser Chromium configurado na CI, sem alegação de execução remota.

**Frontend de apresentação verificado; integração real com backend não implementada.** Sem caminho fetch/XHR/proxy/CORS existente; comportamento consumer continua preview futuro. Credenciais operacionais ficam no servidor, nunca em VITE_*. Projeção live somente leitura depende de contrato separado de endpoint/modelo/autorização/observação antes de adapter limitado. Não converter auditoria em dashboard operacional ou controles destrutivos.

Runtime compartilhado: quatro migrações/checksums bem-sucedidos até 20261012000000 e zero linhas outbox; migração 5 pendente e replay API desativada. Recursos reais/esperados: vhost relay, exchange direct durável relay.events, fila classic durável relay.local, binding event; somente relay.local permanece, ready/unacknowledged/consumers zero. Dead_letter SQL não é DLQ broker. API autenticada/permissões restritas e formulário Chromium/página da fila verificados. Zero consumers esperado antes do consumidor de negócio.

PIDs http/relay 11/12 e hashes carregados mantidos; revisão ativa exata desconhecida. Cargo test substituiu artefatos do target padrão, mantendo inodes carregados agora deleted; builds separados também passaram. Sem restart/migração compartilhados. Restart futuro carregará artefatos atuais em disco. Vite compartilhado 5173 ficou com cache antigo após instalação; restart deliberado de desenvolvimento pendente. Apresentação atual passou isoladamente. Bancos/topologia/diretórios recovery e Supervisor próprios ausentes após cleanup; sem publish/consume/purge/reset/troca de credenciais/reparo inseguro compartilhado.

Estude um exemplo normal real, depois composição → worker/caso de uso → contratos → adapters. Compare crash após confirmação, expiração de lease, retry durável, descoberta insegura e replay com ACK COMMIT perdido. Aprenda newtypes/Result/traits/Send/cancelamento Rust separadamente das decisões distribuídas de commit/posse/identidade/incerteza; relacione invariantes aos testes da revisão. São princípios transferíveis, não cópia de produto privado nem garantias produtivas.

Pré-requisitos Marco 4: definir efeito de negócio local e schema dedupe por ID estável; usar topologia isolada, prefetch limitado e ACK manual após commit atômico dedupe/efeito; validar duplicatas/concorrência, crash antes do commit, crash após commit/antes de ACK, reconexão e redelivery. Replay com ID já commitado pode intencionalmente não gerar efeito adicional. Efeito externo exige outro protocolo. Produtor API, frontend live, reparo, retenção, benchmarks, HA/TLS, backup e hardening seguem separados. Library alterada somente em documentação; Viva Bem não modificado.

## Protótipo de apresentação — 2026-10-12

O design azul aprovado foi reconstruído em componentes Vue tipados, sem wrapper do HTML exportado. A landing ocupa toda a viewport com ilustração decorativa e launcher compacto. Dialog nativo mantém o fundo visível, contém/restaura foco, aceita Escape/Close, bloqueia interação de fundo e scroll do body, e permite scroll interno em telas pequenas. Tokens CSS centralizam o design. Reduced motion remove animações sem acelerar a leitura.

`BaseButton`, `BaseSelect`, `BaseModal`, `ScenarioLauncher`, `ScenarioExperience`, `StageProgress`, `MessageFlow`, `ActivityPulse`, `EnvelopePreview` e `EventOutput` dividem responsabilidades reutilizáveis. Fixtures tipadas ficam separadas da renderização; `usePlayback` mantém timer cancelável com cleanup ao fechar/desmontar/replay. Cada etapa dura 3,6 segundos para leitura, independentemente dos timestamps simulados. Apresentação local sem chamadas de API ou execução de infraestrutura.

Cinco cenários: entrega confirmada, crash após confirmação com recovery, workers concorrentes, acknowledgement de conclusão perdido e idempotência futura do consumer. Estados interrompidos, pulados, incertos e futuros mantêm rótulos explícitos. Aceitação não prova processamento do consumer; recovery pode republicar o mesmo ID; tokens protegem transições no banco, não publicação externa. CommitUncertain não prova commit/rollback; inspeção independente encontra commit neste cenário. Deduplicação atômica com efeito local no banco é planejada, não implementada; efeito externo não compartilha automaticamente a transação. Integração futura exige adapters de API e observações reais acordados separadamente. Veja [componentes e testes de browser](../../../../rust-event-relay/frontend/README.md).

## Preparação estrutural — 2026-10-12

`frontend/` contém apresentação Vue e `backend/` contém modelos, interfaces, casos de uso, repositories e adapters Rust. Princípio geral: dependências apontam para dentro e apresentação no browser não duplica autoridade de entrega. Escolha deste projeto: preservar módulos e contratos focados, evitar camadas vazias e workspace Cargo sem finalidade. Dockerfile: `docker/Dockerfile`; configuração física: `docker/supervisor/normal.conf`; Compose, caches e persistência na raiz. Supervisor gerencia processos http/relay, não filas. `start all` inicia relay mesmo com autostart=false: rollout compartilhado permanece pendente.

Veja [guia do projeto](../../../../rust-event-relay/docs/pt-BR/guides/frontend-backend.md) e [guia do frontend](../../../../rust-event-relay/frontend/README.md). Protótipo de apresentação Vue implementado; Marco 3 permanece escopo separado. PostgreSQL/RabbitMQ preservados; painel localhost:15672. HTTP/API autenticados usando credenciais existentes do contêiner; formulário browser não testado. Credenciais do .env diferem e precisam ser alinhadas separadamente antes do rollout. Código, dependências e runtime da biblioteca não foram alterados.

# rust-event-relay: dossiê de implementação

## Atualização de engenharia — Marco 2.5, 2026-10-12

O [worker Rust separado](../../../../rust-event-relay/docs/pt-BR/architecture/milestone-2-5.md) compõe configuração validada, tracing JSON, pool/repositório PostgreSQL dedicado e lifecycle RabbitMQ. [Scheduling da aplicação](../../../../rust-event-relay/backend/src/application/worker.rs) usa dispatch estático/dependências controladas; [composição](../../../../rust-event-relay/backend/src/bin/relay.rs) constrói infraestrutura concreta. Admite uma entrega por vez, sem tarefas criadas pelo worker, com token novo por invocação. NoEvent espaça uma chamada, sem provar backlog vazio. Apenas aceitação confirmada e conclusão Applied permitem próxima admissão imediata.

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

[Testes controlados](../../../../rust-event-relay/backend/tests/worker.rs) demonstram política; [composição real isolada](../../../../rust-event-relay/backend/tests/worker_smoke.rs) verifica entrega/conclusão e Supervisor individual/coletivo. Happy path não demonstra crash/recuperação. Migração compartilhada de posse continua pendente, autostart relay é false e /health prova liveness HTTP. Falha de configuração/setup encerra sanitizadamente; outage RabbitMQ em runtime reconecta explicitamente. Somente imagem/container app foram atualizados, preservando infraestrutura/dados compartilhados.

Referência transferível para futuras melhorias do Viva Bem: limitar admissão, separar construção de infraestrutura e scheduling, distinguir aceitação externa e conclusão durável, preservar incerteza/erros primários e de cleanup e planejar encerramento finito. Trata-se de referência futura; não se afirma que Viva Bem utiliza essa arquitetura, nem se descreve/modifica implementação privada. Interface gráfica opcional só após conclusão do núcleo, se houver necessidade operacional concreta. Próximo Rust: 2.6, experimentos integrados de crash/falha/recuperação e fechamento do marco; sem alegações de throughput/fairness/efeitos do consumidor ou at-least-once ponta a ponta.

Seções datadas preservam escopo histórico; status do worker é atualizado por esta seção.


## Atualização atual de engenharia — Marco 2.4, 2026-10-12

A biblioteca Rust agora oferece [orquestração de uma tentativa de entrega](../../../../rust-event-relay/docs/pt-BR/architecture/milestone-2-4.md), implementada em [application/delivery.rs](../../../../rust-event-relay/backend/src/application/delivery.rs). Usa ports focados de aquisição/publicação/transição com despacho estático e futures nativas Send. O caso de uso possui sequência e política básica de liberação; infraestrutura possui transações SQL e AMQP. Não exige serviço de encaminhamento nem motor genérico de workflows. O binário HTTP continua sem compor worker.

Princípio geral: separar autoridade reconhecida, aceitação externa confirmada, conclusão local durável e efeitos no consumidor. O caso de uso publica o envelope original emprestado somente após aquisição reconhecida; depois completa somente quando publisher confirma aceitação. `Published` registra um fato sobre o broker; sucesso da entrega exige também completion `Ok(Applied)`. Nenhum comprova processamento do consumidor ou efeitos exatamente uma vez. Erro de completion após aceitação pode gerar publicação duplicada na recuperação, preservando ID estável.

Princípio geral: cleanup não pode apagar falha principal. `PublicationFailed` mantém PublishError original e `ReleaseOutcome` independente. Release pode reconhecer aplicação, perder posse, falhar ou ter commit incerto. Incerteza não pode ser tratada como prova de rollback ou não aceitação. CommitUncertain na aquisição não retorna claim e impede publicação; em completion ocorre após aceitação conhecida e pode ocultar estado processed. Repetir cegamente qualquer operação é inseguro.

Escolha do projeto: Unavailable e Serialization falham antes do envio; Unroutable e Rejected são resultados definitivos do broker. Cada um dispara release protegido por ownership uma vez. Uncertain mantém lease, adiando recuperação sem reconciliar aceitação nem eliminar duplicatas. RabbitMQ aposenta canal incerto; a composição futura deve substituí-lo. Release preserva disponibilidade, contador e diagnóstico; elegibilidade imediata pode produzir falha repetida rápida sem política do worker. Não há retry, nova aquisição ou reconexão ocultos.

Princípio geral: leases recuperam claims abandonados, mas não impedem publisher externo obsoleto. PostgreSQL permanece autoritativo depois dos locks; checagem pelo relógio da aplicação foi omitida. Aquisição reconhecida pode retornar expirada. Cancelamento durante aquisição pode ocultar lease persistido; depois da aquisição pode abandonar claim; durante publicação pode ocultar aceitação; após aceitação pode deixar pending; durante commit de completion/release pode ocultar transição aplicada. Descartar future pode não produzir erro tipado e não comprova rollback ou não aceitação. Não há cleanup destacado nem Drop assíncrono; recuperação depende de expiração durável.

Cinco [testes com fakes](../../../../rust-event-relay/backend/tests/delivery_use_case.rs) cobrem preservação completa do envelope, todas as categorias de publicação/transição, erros principal/cleanup, espera pela confirmação, cancelamento sincronizado e Send/despacho estático. Demonstram ordem e ausência de chamadas proibidas, não rollback real nem não aceitação do broker. Consulte [evidência Rust datada](../../../../rust-event-relay/docs/pt-BR/testing/validation-results.md#marco-24--2026-10-12) e handoff (relatório 2.5 ausente neste checkout). Próximo é **2.5, composição e operação do worker**, incluindo polling, lifecycle/reconexão do publisher e integração Supervisor; **2.6** cobre experimentos ponta a ponta de crash/recuperação. Nenhuma garantia ponta a ponta ou alegação de desempenho é feita.

Seções datadas anteriores preservam seu escopo; afirmações de ausência da orquestração 2.4 são substituídas por esta atualização.


[English](../../en/architecture/rust-event-relay.md) | [Português brasileiro](rust-event-relay.md)

Revisão estática: 2026-10-10. Este projeto independente não tem chamadas runtime verificadas a outro repositório do portfólio. Links de evidência sustentam as explicações completas abaixo.

## Atualização de engenharia — Marco 2.3, 2026-10-12

O Rust agora implementa aquisição/conclusão/liberação pelos ports existentes, com 12 casos de integração PostgreSQL isolados aprovados. [Implementação e instantes de decisão](../../../../rust-event-relay/docs/pt-BR/architecture/milestone-2-3.md), [validação datada](../../../../rust-event-relay/docs/pt-BR/testing/validation-results.md#marco-23--2026-10-12) e continuidade (arquivo ausente no checkout 2.4) distinguem evidência atual da revisão histórica abaixo. Metadados de schema/migração do banco de desenvolvimento foram consultados sem escrita: migração de posse continua pendente. Código de aplicação, dependências e infraestrutura da Library não mudaram.

### Princípios gerais ilustrados pelo adapter Rust

Lease durável registra autoridade temporária no armazenamento e permite recuperação se worker desaparecer. ID estável identifica envelope original; token novo identifica uma aquisição. Expiração revoga autoridade de transição mesmo antes de outra aquisição. Token não revoga envios externos sem fencing no destino. RabbitMQ não aplica fencing desses tokens: aceitação seguida de completion falho/incerto ainda pode duplicar. Correção no banco não é garantia de entrega ponta a ponta.

Transações curtas separam posse de espera remota por publicação. Row locks serializam alterações enquanto mantidos; leases persistem autoridade após commit. Adapter escolhe Read Committed explicitamente e seleciona um candidato pending vencido com FOR UPDATE SKIP LOCKED, filtrando leases ativos e contadores esgotados. Aquisições independentes são disjuntas sob contenção testada e ignoram linha elegível bloqueada por outra transação. Aquisição vazia significa nenhuma linha adquirida pela chamada, não ausência de backlog; SKIP LOCKED não é fila justa ou observação consistente geral. Observação é contrato separado, sem escrita, e inclui pending com lease/contador esgotado.

Tempo autoritativo precisa ser consultado **após obter locks**: espera pode ultrapassar lease. PostgreSQL now() fixa tempo inicial da transação; clock_timestamp() consulta tempo atual do servidor. Adapter primeiro consulta cutoff de seleção, obtém lock, restaura dados e consulta relógio decisório para revalidar elegibilidade e gerar timestamps. Completion/release bloqueiam por ID antes de consultar tempo e exigem pending, token correto e acquired_at <= tempo < expires_at. Igualdade com expiração rejeita; relógio anterior a acquired_at também. Sem garantia de relógio monotônico. Latência de commit/resposta consome lease; claim confirmado recebido não garante validade restante.

Falha pré-commit, conflito ordinário de posse e commit desconhecido são distintos. Dado selecionado inválido falha sem ignorar/reparar silenciosamente; candidato inválido pode impedir progresso repetidamente. Rejeição ordinária de COMMIT reportada pelo servidor é falha conhecida, demonstrada por trigger de constraint diferida isolada. Perda de confirmação pode esconder alteração confirmada: transporte/protocolo no commit e códigos de resultado desconhecido são conservadoramente CommitUncertain. Após aquisição incerta, não publicar por claim não confirmado; inspecionar posse durável ou recuperar após expiração com token novo. Após completion incerto, processed pode estar persistido; republicação cega ou interpretar conflito como sucesso anterior não se justifica. Cancelamento pode não retornar classificação; SQLx enfileira rollback de transação aberta descartada, mas não desfaz commit nem promete rollback imediato.

Escolhas específicas não são política universal: um evento por aquisição, token gerado no pedido, leases em microssegundos, leased permanecendo pending, contador de aquisições confirmadas limitado a i32::MAX, exclusão de contador esgotado, repetição retornando OwnershipLost e release preservando disponibilidade/diagnóstico sem calcular backoff. Completion persiste decisão de confirmação do chamador sem chamar broker. Prazos do pool, retry/DLQ e reconciliação/orquestração pertencem ao chamador/use case futuro.

### O que os testes demonstram e deixam aberto

Evidência PostgreSQL real cobre aquisições concorrentes disjuntas, SKIP LOCKED, rejeição de owners antigos/incorretos/ausentes/terminais/repetidos, substituição de token expirado, preservação de envelope/metadados, rollback por dado inválido/overflow de duração, contador esgotado, limpeza atômica, rejeição SQL imediata e COMMIT diferido rejeitado. Teste de expiração observa espera por row lock, atualiza snapshots de pg_stat_activity, confirma início transacional anterior à expiração, espera relógio alcançar expiração e libera lock; completion e release rejeitam. Cancelamento cobre future bloqueada antes de mutar e reutilização do pool. Lease de um microssegundo demonstra expiração quando aquisição confirmada é observada.

Igualdade exata da expiração é evidência determinística do modelo, não experimento de igualdade controlada no relógio real. Proxy de conexão isolado descarta CommandComplete COMMIT após observar conclusão no servidor em aquisição, completion e release: adapter retorna CommitUncertain e conexão independente observa estado confirmado. Prova que esse resultado incerto confirmado é possível, não que toda incerteza implica commit ou rollback. Serviços/tráfego compartilhados preservados. Cancelamento durante COMMIT continua não verificado. Caso anterior a acquired_at usa fixture com timestamp futuro, não reversão real do relógio. Testes não provam justiça, vazão, todos os schedules, perda de energia, CI remoto ou entrega ponta a ponta. Próximo 2.4 compõe um claim → publish → persistência do resultado; polling, worker Supervisor/reconexão, backoff/DLQ, produtores e idempotência do consumidor ficam para depois.

## Dossiê histórico — revisão estática de 2026-10-10

Seções restantes registram escopo anterior. Afirmações de SQL produtivo de posse ausente são históricas e substituídas pela atualização acima; limitações de broker/HTTP e operações produtivas continuam aplicáveis.

## Integração verificada do publisher

O adapter RabbitMQ chamável implementa o port `EventPublisher` da aplicação. Abre conexão/channel próprios, declara exchange direct durável e fila durável, vincula pela routing key configurada e habilita publisher confirms. Defaults são `relay.events`, `relay.local` e `event`. Serializa envelope em JSON, usa identidade estável do evento como message ID, envia mensagem persistente com roteamento mandatory e espera confirmação. Ack bem-sucedido sem retorno comprova aceitação pelo broker nesse contrato; não comprova consumidor, efeitos de negócio ou entrega ponta a ponta. Não há consumidor implementado.

`RabbitMqConfig` constrói URI AMQP escapada com campos separados de credencial/vhost, valida nomes/prazos e redige Debug. A configuração atual aceita `amqp`, não `amqps`; não há caminho TLS produtivo verificado. Autenticação usa credenciais/vhost do broker, não autenticação HTTP da aplicação ou cifra de payload. Compose local fornece armazenamento e endpoint de gestão; login de gestão é fronteira operacional distinta da publicação.

O mutex serializa uma publicação em andamento. Espera de admissão e publicação têm prazos separados; setup e fechamento também são limitados. Serialização/indisponibilidade, rejeição, ausência de rota e incerteza são resultados distintos. Timeout/erro/cancelamento após início do envio pode deixar aceitação desconhecida; o adapter aposenta o channel e exige reconexão explícita. Não faz retry automático. Token de lease do banco não é enviado como fencing ao broker e não impede envio externo de processo obsoleto.

Leitor PostgreSQL, ports de ownership e publisher são caminhos separados de biblioteca. `main` compõe apenas configuração/tracing/liveness HTTP. Não há transação de produtor, worker polling, SQL de aquisição/completion, efeito de consumidor ou integração de pagamento ligando-os. Aquisição → publicação → conclusão permanece orquestração hipotética. Um diagrama ligando adapters como worker em execução seria incorreto.

## Autoridade, diagnóstico e transporte

A API HTTP contém apenas `GET /health`, resposta fixa de liveness sem dependências ou login. Tracing JSON estruturado usa `RUST_LOG`. Erros de persistência/publicação expõem categorias sanitizadas em Display/Debug, mas conservam fontes tipadas. Imprimir essas fontes pode revelar conexão, SQL ou payload; formatação externa segura não é redação completa de logs. A revisão não leu credenciais reais ou linhas de aplicação.

Tokens de ownership autorizam futuras transições condicionais no banco, não sigilo de dados. UUID identifica evento estável entre retries; token identifica uma aquisição. Modelos puros rejeitam tokens zero/inválidos, horários incoerentes, owners antigos e transições na expiração exata. Campos nullable da migração precisam estar ausentes juntos ou formar lease pending coerente. Constraints validam formato da linha; não provam histórico de transição, relógio corretamente amostrado ou enforcement concorrente de ownership. Isso exige mutações produtivas e testes concorrentes PostgreSQL, atualmente ausentes.

Transações curtas e publicação fora dos locks são o projeto registrado no ADR 007. Futura completion/release precisa combinar ID, token, estado pending e lease não expirado usando horário do banco após adquirir lock. Publicação no broker é outra fronteira: o token não revoga envio já iniciado. Efeitos tolerantes a duplicatas exigiriam deduplicação do consumidor acoplada a alterações de negócio. É teoria futura, não consumidor implementado. AMQP atual tem transporte em texto puro; armazenamento durável e UUIDs não fornecem cifra de aplicação, assinatura de autenticação ou TLS produtivo.

## Implantação, observabilidade e lacunas de evidência

Compose fornece PostgreSQL, RabbitMQ e app de desenvolvimento gerenciado pelo Supervisor. O HTTP depende de configuração/tracing/listener; não cria PgPool nem RabbitMqPublisher. Health das dependências pode condicionar startup, mas `/health` continua liveness do processo. Supervisor permite 30 s de drain HTTP e Compose concede 35 s ao encerramento do gerenciador. Mudanças exigem stop/build/start; não há reload automático ou worker implantado. Bind/volume preserva recriações comuns, não perda do host/armazenamento.

Migrações SQLx são versionadas e aplicadas explicitamente, não pelo startup HTTP. Preserve IDs e conteúdo aplicado. A migração de ownership tem fonte e evidência isolada; o registro anterior informa que continuava pendente no banco compartilhado de desenvolvimento. Esta revisão não consultou esse banco nem atualizou seu estado. Down remove colunas de ownership; downs anteriores podem destruir outbox. Down e reaplicar schema não restauram linhas. Rollout real exige compatibilidade e backup/restore verificados separadamente, não reset destrutivo.

Testes padrão validam domínio, mapeamento e contratos, além de HTTP/socket. Testes PostgreSQL opt-in criam bancos de fixture com nomes exatos e verificam limpeza; testes de broker exercitam roteamento e incerteza. Alguns testes independentes do banco usam sockets locais, portanto independência não significa ausência de I/O. Workflow CI é evidência de configuração, não prova de execução remota. Resultados históricos continuam em testing/validation-results. Nenhum build/teste Rust, comando Docker, migração, chamada ao broker ou benchmark foi executado nesta revisão.

Desempenho tem limites de linhas e uma publicação em andamento, mas número de linhas não limita bytes de payload. `fetch_all` materializa lote; dado selecionado inválido falha o resultado inteiro e pode bloquear leituras repetidas. Não há quarentena, política de backpressure, frequência polling, medição de vazão, endpoint de métricas ou dimensionamento produtivo de pool entregue. Lacunas: SQL/concorrência de ownership, orquestração worker, experimentos de duplicata/recuperação, política de linha inválida, TLS/HA produtivo, retenção/restore e desempenho. Nada disso já foi comprovado por liveness verde.

## Evidência de apoio

- [integrations/rabbitmq-contract](../../../../rust-event-relay/docs/pt-BR/integrations/rabbitmq-contract.md)
- [security/diagnostic-and-authority-boundaries](../../../../rust-event-relay/docs/pt-BR/security/diagnostic-and-authority-boundaries.md)
- [operations/deployment-and-evidence](../../../../rust-event-relay/docs/pt-BR/operations/deployment-and-evidence.md)
- [Interview / Entrevista](../interviews/rust-event-relay.md)


## Marco 2.6 — Recuperação demonstrada, 2026-10-12

Experimentos Rust com PostgreSQL/RabbitMQ reais e processos próprios observaram pending após SIGKILL antes do envio e após confirmação; expiração real seguida de token novo/count 2 e processed. A segunda janela produziu duas mensagens com o ID original. Perder confirm AMQP deixou pending e Uncertain enquanto um observador independente já tinha a mensagem; o worker substituiu a conexão sem repetir o claim vivo. Perder resposta COMMIT de completion produziu CommitUncertain apesar de processed durável/count 1; reinício não adquiriu o evento.

Dois binários foram bloqueados em completion após publicar: tokens distintos duráveis e leases vivos sustentaram a afirmação de posse concorrente neste schedule. Owner antigo não concluiu/liberou após B adquirir; publisher anterior ainda conseguiu enviar. Banco protege autoridade de transição, não fencing externo. Rejeição/deadline SQL e cancelamento TERM preservaram pending recuperável; restauração/expiração/reinício concluíram. ACK do observador é só fixture, não efeito de negócio.

Esta evidência sustenta fechamento do escopo do Marco 2 como fundação pelo menos uma vez sob origem commitada, storage/contratos suportados, disponibilidade eventual, worker ativo e eventos válidos com falhas resolvíveis. Não prova entrega universal/exactly-once, fairness, ordenação, power loss, poison/rejeição permanente, contador esgotado ou HA/TLS produtivos. Rollout compartilhado permanece pendente/relay STOPPED. Próximo: decisões de retries duráveis/classificação/quarantine-dead-letter/replay auditável. Princípios são transferíveis sem alegar arquitetura privada de outro produto.

[Evidência e fronteiras](../../../../rust-event-relay/docs/pt-BR/architecture/milestone-2-6.md) | [Aceitação e premissas](../../../../rust-event-relay/docs/pt-BR/operations/milestone-2-review.md).


## Marco 3.1 — política escolhida

[Classification, scheduling, budgets, uncertainty, poison isolation and replay identity](durable-failure-policy.md). Princípios gerais separados das escolhas Rust; atualmente existem somente cálculos puros de política.

## Integração durável — Marco 3.3

[Decisões contextuais, jitter sem viés, pausas separadas, manutenção finita e cancelamento](durable-failure-policy.md). Integração implementada e testada em infraestrutura isolada; rollout compartilhado permanece pendente. Descrições anteriores mantêm escopo histórico. Scanning geral fica em 3.4, replay em 3.5 e fechamento em 3.6.

## Rollout local autorizado do relay — 2026-10-13

Supervisão de processos e persistência do broker têm donos diferentes: parar publisher não para broker gerenciado separadamente. Health de dependência condiciona startup, sem substituir autenticação, pré-requisitos de schema ou recuperação runtime. autostart vale no início do manager; autorestart=unexpected recupera falhas não zero após RUNNING, enquanto stop intencional mantém parado até start explícito ou novo início do manager. Tentativas de startup são finitas; schema/artefatos ausentes podem exigir reparo. Migrations continuam ações explícitas, sem efeitos repetidos no startup.

Reliable Event Relay agora inicia http/relay automaticamente pelo Supervisor. Dependências service_healthy de PostgreSQL/RabbitMQ preservadas; management permanece localhost:15672. Publisher existente declara exchange/fila/binding duráveis após autenticação, sem mensagens de demonstração. Duas migrations locais pendentes de ownership/retry autorizadas explicitamente, revisadas contra SQL/estado e aplicadas ao outbox vazio; as quatro agora instaladas. Somente app reconstruído/recriado; banco/broker/frontend e dados/credenciais preservados.

Verificações compartilhadas executadas: management host/topologia autenticados, controle direto/interativo pelos dois aliases, stop intencional do relay preservando HTTP/management/metadados e contagens observadas zero, recuperação após saída inesperada de ambos. Filas vazias não demonstram persistência de payload não vazio; nenhuma mensagem inventada. Worker smoke isolado verifica autostart com configuração real e recursos de entrega próprios do teste. Simulações frontend e semântica 3.3 preservadas. Registros anteriores pendentes/parados são históricos; rollout local não prova prontidão produtiva ou fechamento de 3.4–3.6.

[Procedimento e evidência atuais do projeto](../../../../rust-event-relay/docs/pt-BR/operations/local-relay-rollout.md). Library somente documentação; sem mudanças no Viva Bem, credenciais, aplicação/dependências runtime ou deployment público. Sem staging/commit/push.


## Marco 3.4 — descoberta limitada e isolamento seguro, 13/10/2026

Princípio geral: varredura observa dados, não concede autoridade de mutação. Travessia limitada por chave deve avançar além de linhas que exigem intervenção e revisitar alterações/inserções; lock atual e relógio do banco após lock estabelecem elegibilidade. Falha de decoder/representação não suportada não prova corrupção permanente. Preservar evidência original e histórico; não inventar dono para reparar identidade/metadados inseguros. Acknowledgement perdido exige observação durável independente, não repetição cega.

Implementação Rust: [matriz e contratos 3.4](../../../../rust-event-relay/docs/pt-BR/architecture/milestone-3-4.md). Cada descoberta lê até uma linha pending com UUID after/through e limite superior local. Worker admite no máximo uma unidade por segundo, antes da conexão do publisher; outage pausado do broker ainda permite manutenção de banco. Observação Valid fornece até uma sugestão de aquisição por ID, revalidada com autoridade atual, permitindo trabalho independente após prefixo inseguro. Isolamento mantém JSONB/envelope, ID e histórico vitalício em dead_letter com motivo/evidência e revisão verificada, protege dono ativo no orçamento final e relê invalidade na transação bloqueada. IDs configurados permanecem compatíveis/finitos; replay continua 3.5, fechamento 3.6.

Limite de linhas não prova limite de bytes, custo de consulta, justiça ou cobertura completa. Cursor reinicia com processo/retorno ao início; escrita externa não auditada de histórico não pode ser reconstruída. Não houve migration, reinício compartilhado, mudança de frontend ou idempotência de consumidor neste marco. Rollout local autorizado preservado. Atualização desta Library somente documental, mantendo edições anteriores. [Verificação datada](../../../../rust-event-relay/docs/pt-BR/testing/validation-results.md) separa testes determinísticos, falhas PostgreSQL isoladas e observações reais independentes do banco/broker; não alega execução de CI remoto.

## Marco 3.5 — replay autorizado, idempotente e auditável, 13/10/2026

Princípio transferível: identidade autenticada deriva de credencial validada no transporte; permissão verificada em todo caminho da aplicação, inclusive repetição e observação. String de ator/acesso ao banco não bastam para autorizar intenção. Identidade durável de request associa ator/escopo/campos explícitos; serializar request antes de bloquear evento e persistir ciclo/auditoria atomicamente. Intenção idêntica retorna recibo anterior após avanço; alteração conflita. Consulta negativa não exclui commit em andamento; incerteza preserva UUID original.

Rust concreto: API bearer local opt-in, escopo global outbox:replay, teto por ator e consulta de recibo restrita ao próprio ator; dead_letter preservado com validação atual, ciclo/revisão esperados/capacidade. Preservar identidade/conteúdo/timestamps/histórico vitalício; baseline marca novo ciclo, sem reparar conteúdo/metadados inseguros. Auditoria preserva evidência terminal anterior. Owner/superuser pode alterar objetos, logo imutabilidade de aplicação não significa storage à prova de adulteração. Recibo reabilita trabalho, sem publicar imediatamente, desfazer efeitos passados ou prometer outro efeito de consumidor.

[ADR 009](../../../../rust-event-relay/docs/pt-BR/adr/009-authorized-idempotent-replay.md), [operação e exemplos](../../../../rust-event-relay/docs/pt-BR/operations/replay.md), [implementação, validação e escopo exato 3.6](../../../../rust-event-relay/docs/pt-BR/architecture/milestone-3-5.md). Oito cenários PostgreSQL isolados, testes de credencial/aplicação e cenário broker/banco reais verificam atomicidade, concorrência, locks/estado obsoleto, conteúdo/capacidade, rejeição conhecida, COMMIT desconhecido e cancelamento com recibo observado independentemente. Configurar CI não prova execução remota; ACK da fixture não prova efeito de negócio.

Serviços compartilhados continuam rodando com quatro migrations; tarefa compilou artefatos separados sem restart compartilhado nem migration 5. Startup externo recente impede assumir que processo antigo nunca reiniciou. Migration 5/API privilegiada dependem de autorização separada. Marco 3.6 fecha matriz integrada 3.1–3.5, recuperação/incerteza/cleanup e status operacional final; reparo, idempotência do consumidor, frontend e prontidão produtiva ficam fora dessa aceitação. Library somente documental, sem runtime/produto ou mudanças no Viva Bem.
