# Rust Event Relay: dossiê da implementação

Código revisado em 2026-10-18 em `6e5e64fbffea1eb3ec50b828648f3fa9e708cf6c`. Referência autossuficiente do escopo local final. Aceite registrado em 2026-10-17 na base `18893c865eba506e7d4a2124864920d82ce6237d`; não foi reexecutado. Mudanças posteriores em startup/token/ferramentas impedem tratar sucesso histórico como certificação da revisão presente. CI remoto não verificado; prontidão de produção não estabelecida.

## Propósito e composição

Demonstra como um fato de negócio confirmado chega ao broker e produz um efeito local de estoque apesar de transporte duplicado. Rust/Axum/Tokio compõem três processos no Supervisor: HTTP, worker relay e consumidor. PostgreSQL armazena fatos, outbox/retry/posse e efeitos. RabbitMQ transporta envelopes canônicos. Vue oferece operações locais reais e animações educacionais identificadas. Não há integração de runtime comprovada com outro repositório do portfólio.

Um Compose principal executa app, frontend, PostgreSQL e RabbitMQ. O launcher suportado valida configuração local derivada de exemplo, constrói artefatos locked, verifica histórico e realiza backup protegido/restauração descartável antes de migrations forward necessárias. Compose direto não equivale a esse procedimento sobre armazenamento retido. `compose.demo.yaml` é histórico, não segunda stack permanente. Padrões: frontend localhost:5173, HTTP localhost:8080, PostgreSQL localhost:5433 e management localhost:15672. Readiness/métricas internas de HTTP/relay/consumidor ficam em 9100/9101/9102; `/health` só demonstra liveness HTTP.

## Produtor e outbox no mesmo commit local

Intenção fixa contém identidade estável da requisição e cenário suportado. A transação insere execução, fixture de estoque 10, fato de recebimento e envelope outbox com quantidade 5. Mesma identidade/intenção retorna evidência existente; conteúdo diferente gera conflito. `demo.goods_receipts` prova o fato do produtor, não que o consumidor somou cinco unidades. Falha de resposta após COMMIT pode ocultar sucesso; recuperação inspeciona a mesma requisição sem criar outra identidade.

`relay.outbox_events` armazena evento canônico, identidade/conteúdo imutáveis e estado de publicação mutável. Aquisição usa relógio do banco, locks curtos e `FOR UPDATE SKIP LOCKED`. Estado pending, disponibilidade, expiração e orçamento limitam elegibilidade. Aquisição confirmada incrementa `attempt_count` vitalício e revisão, inclusive com crash antes do envio. Ciclos registram baseline/máximo sem apagar histórico. Token/revisão/lease protegem transições, mas não impedem processo expirado de publicar externamente.

## Aceitação e conclusão durável são separadas

Publisher envia envelope original com ID estável e mandatory, observando confirms/returns. Unroutable/rejeição conhecidos diferem de incerteza. Falta de confirm pode ocultar aceitação; perda da resposta de conclusão SQL pode ocultar processed. Nova aquisição pode republicar após aceitação e antes de conclusão. Trocar conexão repara o ciclo do publisher, não decide o resultado do envio anterior.

Retry durável persiste próxima elegibilidade e diagnóstico sanitizado, com equal jitter exponencial limitado (teto inicial 1 segundo, máximo 5 minutos). Sleep do worker apenas espaça admissão. Terminal `dead_letter` preserva trabalho esgotado/irrecuperável no SQL. Descoberta limitada fornece candidatos de manutenção; snapshot não autoriza mutação, que relê e exige autoridade atual. Replay autorizado usa operador, identidade de requisição, estado/revisão esperados e auditoria durável. Novo ciclo preserva evento e contador vitalício; pode gerar duplicata no consumidor. Credenciais demo e autoridade de replay são contratos distintos.

## Um efeito local sob o contrato de deduplicação

Consumidor valida envelope/message identity e intenção de estoque. Em READ COMMITTED tenta primeiro inserir recibo único `(consumer_name,event_id)`, depois atualiza estoque e completa recibo atomicamente. Inserção conflitante espera vencedor; novo snapshot lê seu recibo confirmado. Duplicate compara conteúdo imutável restaurado do modelo, não apenas ID. BYTEA versionado evita perda por normalização de números/timestamps em JSONB. Envelope diferente com mesma identidade não vira duplicata válida silenciosamente.

Constraints diferidas exigem recibo completo no commit; guards protegem identidade/conteúdo concluídos contra alteração/remoção comum. Não protegem contra proprietário privilegiado do banco. Entrega normal muda 10 → 15 com um recibo. Duplicata igual e concorrente mantêm 15 e um efeito. A garantia cobre efeito SQL local suportado com identidade retida; email, pagamento ou outro efeito externo não integra essa transação automaticamente.

Após processamento durável, consumidor tenta ACK manual. Aceitação do broker, conclusão outbox, commit do consumidor, envio local de ACK e recebimento pelo broker são cinco observações. Consumidor pode confirmar antes de observar conclusão do relay. Sucesso no envio não prova recebimento; reentrega permanece possível. Não há promessa de transporte exatamente uma vez.

Entrada inválida/não suportada/conflitante usa quarentena da aplicação: preserva conteúdo suportado com publicação confirmada antes do ACK da origem. Se falha ou não representa exatamente a entrada dentro dos limites, mantém a origem sem ACK. Terminal SQL é diferente da fila de quarentena. Padrão: direct durável `relay.events`, chave `event`, fila `relay.local`, vhost `relay`; quarentena `relay.quarantine`, chave `inventory`, fila `relay.quarantine.inventory`.

## UI real, ações limitadas e evidência honesta

Cenários reais: entrega normal, duplicata, duplicata concorrente e uma rejeição antes do envio por execução seguida de retry durável. Ações republicam envelope original em fila/chave `relay.demo.<UUID da ação>` com consumidores temporários limitados. Publicações/classificações correlacionam ação/execução/evento; gráficos agregados não estabelecem essa relação. Contagens têm caps e são limites inferiores.

Rejeição controlada não é indisponibilidade nem NACK do broker. Animações de crash, corrida e perda de confirmação/ACK ilustram janelas distribuídas sem manipular infraestrutura. Kill/reconexão, corrida de lease, COMMIT ambíguo e falhas do consumidor reais pertencem a testes isolados. Simulações tornam incerteza temporal compreensível sem atribuir essas falhas à UI.

Vue usa HTTP pelo proxy, não AMQP por WebSocket. POST `/demo/runs` e `/demo/actions` criam trabalho fixo; GET de evidência/histórico/configuração nunca republica. GET `/demo/runs` seleciona execuções bem-sucedidas. Credencial Bearer separada, origem/header de cliente e limites de corpo/taxa/concorrência/prazo restringem a demonstração local. Token só em memória do navegador; session storage retém identificadores. Esses controles não são TLS ou criptografia da aplicação.

Histórico inclui pending/unknown/terminal e ações. `observed_at` identifica snapshot, stale após 15 segundos. Refresh falho preserva observação anterior; GET não reenvia trabalho desconhecido. Polling sequencial dura até 60 segundos, com timeout browser de nove. Fechar/recarregar termina observação, não commits. Snapshot não prova que efeito ausente nunca será confirmado.

## Registros, limites e operação

`demo` controla execuções, fatos, ações, publicações, observações e falhas controladas. `relay` controla outbox e replay. `consumer` controla estoque/recibos. `public._sqlx_migrations` controla histórico do schema. Acompanhe evento por consultas filtradas somente leitura: fato → status/contador/revisão outbox → recibo/estoque → observações da ação/publicação/Duplicate. Inspecione fila da ação separadamente. Processed não prova consumo; gráfico não substitui recibo.

Limites: 100 execuções retidas, 100 ações totais, três por execução, quatro execuções/ações ativas, um worker de ação, dois contextos temporários, 1–3 chamadas de publicação por ação e 32 observações de publicação/32 de consumo por execução. Rejeitar capacidade preserva histórico. Não há retenção automática ou reparo geral de ação desconhecida. Nunca remova recibos enquanto houver reentrega possível. Backup PostgreSQL não cobre filas RabbitMQ. Restauração protegida, HA/TLS multi-host, desastre do broker e capacidade maior são trabalhos de produção separados.

## Aceite, alternativas e roteiro

Manifesto final registra 243 entradas Rust únicas aprovadas (241 substantivas, dois helpers), 27 verificações browser reais, instalação limpa separada com 24 e nove migrations. Pertencem à base/data registrada, não a esta revisão; detalhes e medições limitadas permanecem na evidência original. Não cabe gráfico novo ou extrapolação. Em 2026-10-18 o proprietário confirmou que o antigo PDF não existe mais e pode ser desconsiderado; hash registrado permanece apenas proveniência.

Transação SQL única para origem/efeito é mais simples se ambos pertencem ao mesmo banco/processo; outbox/broker demonstra entrega independente durável ao custo de duplicatas/incerteza. Leases reduzem tempo de coordenação, mas não fazem fencing externo. Recibos trocam armazenamento/retenção por segurança contra repetição local. Conteúdo imutável versionado detecta reutilização de identidade com custo de schema/validação. São consequências/alternativas, não motivações originais inventadas.

Estude transação produtora, aquisição/token/revisão, confirms, retry/descoberta/replay, consumidor/quarentena e evidência browser. Para cada fronteira cite registro, resultado desconhecido e teste de um agendamento. [Roteiro do projeto](../../../../rust-event-relay/docs/pt-BR/guides/implementation-study.md), [ADRs](../../../../rust-event-relay/docs/pt-BR/index.md#adr), [aceite](../../../../rust-event-relay/docs/pt-BR/operations/final-audit.md), [manifesto](../../../../rust-event-relay/docs/audit/2026-10-17/manifest.json) e [entrevista](../interviews/rust-event-relay.md) oferecem proveniência/aprofundamento. [Revisões anteriores](../operations/rust-historical-reviews.md) preservam marcos originais; declarações de consumidor/API ausentes são históricas.
