# rust-event-relay: dossiê de implementação

[English](../../en/architecture/rust-event-relay.md) | [Português brasileiro](rust-event-relay.md)

Revisão estática: 2026-10-10. Este projeto independente não tem chamadas runtime verificadas a outro repositório do portfólio. Links de evidência sustentam as explicações completas abaixo.

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
