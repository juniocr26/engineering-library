# Rust Event Relay — Guia de Estudo para Entrevista Técnica

[English](../en/rust-event-relay.md) | [Português brasileiro](rust-event-relay.md)

Estudo de portfólio sobre entrega confiável sob falhas. Fontes: [README](../../../rust-event-relay/README.pt-BR.md), [arquitetura](../../../rust-event-relay/docs/pt-BR/architecture.md), [ownership](../../../rust-event-relay/docs/pt-BR/milestone-2-2.md) e código. Primeira pessoa descreve implementação, não produção. Alternativas são comparações de estudo; ADR 007 registra a decisão de ownership. Nenhuma verificação runtime foi executada nesta auditoria.

## 1. Visão geral e escopo

#### Pergunta: Já é um motor de entrega?

**Resposta modelo:** “O binário HTTP carrega configuração/tracing, atende liveness e encerra de forma graciosa. Módulos separados oferecem envelope, reader PostgreSQL, publisher RabbitMQ confirmado e modelos/contratos/schema de ownership. Não há worker ligando aquisição, publicação e conclusão. Entrega ponta a ponta, retries e dead-letter seguem futuros.”

2.1 entrega publisher; 2.2 entrega tipos/portas/migração. 2.3 mutações PostgreSQL, 2.4 orquestração, 2.5 worker/composição e 2.6 experimentos de crash são adiados. Documentação de estudo não altera os marcadores desses marcos.

## 2. Arquitetura e caminhos

`main.rs` → config/telemetry → listener TCP → `application::serve`. `/health` devolve `ok\n`; não conecta a banco/broker nem prova readiness. SIGINT/SIGTERM em Unix acionam shutdown. Future de shutdown injetado permite teste em socket efêmero sem estado global de sinais.

Caminho separado: `PgPool` injetado sustenta `PostgresOutboxRepository::read_eligible`, com SELECT parametrizado limitado e restauração validada. `RabbitMqPublisher` implementa `EventPublisher`, possui conexão/channel, declara topologia durável e publica JSON persistente com ID estável/confirm. Nenhum adaptador é chamado pelo HTTP.

[Contratos](../../../rust-event-relay/src/persistence/ownership.rs) usam futures Send nativos e despacho estático. SQLx/Lapin ficam na infraestrutura; domínio valida invariantes. Portas pequenas explicitam responsabilidades/testes, sem registry de plugins runtime. Despacho dinâmico poderia permitir escolha runtime com custo de alocação/dispatch; não está implementado.

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

Portas exigem tempo do banco após lock e aquisição confirmadamente commitada antes de devolver autoridade. **São contratos para mutações futuras, não concorrência SQL implementada no reader atual.** Migração 2.2 adiciona campos coerentes; constraints provam forma da linha, não histórico legal/token globalmente novo. `CommitUncertain` significa possível commit; `OwnershipLost`, ausência de autoridade. Nenhum é sucesso presumido.

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

PostgreSQL opt-in usa bancos isolados gerados para reads/migrações originais e ownership up/down. RabbitMQ real cobre roteamento/confirms e incerteza por timeout/cancelamento. CI possui jobs padrão/PostgreSQL/RabbitMQ; arquivo de workflow não prova execução remota aprovada. [Validação histórica](../../../rust-event-relay/docs/pt-BR/validation-results.md) registra execuções anteriores, sem repetição aqui. Modelos/fakes não provam concorrência de donos PostgreSQL antes de 2.3.

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
6. Testes/CI/evidência histórica; separar modelos/schema de mutações/orquestração ausentes.
7. Pré-requisitos 2.3–2.6 e idempotência, sem marcar entrega ou estudo concluídos.
