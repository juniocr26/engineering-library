> Registro histórico de revisão. Contratos e verificação atuais estão ligados em [Arquitetura](../architecture/overview.md). Datas, revisões e resultados abaixo mantêm o escopo original.

# Revisão das fontes — Hub VivaBem

[English](../../en/operations/source-review.md) | [Português brasileiro](source-review.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `e0ab75952946bc3f764dcb4144e404097277933f`.

<!-- reading-section: scope -->

## Cobertura da inspeção

Árvore fonte inicialmente limpa. Leitura estática seletiva dos caminhos listados sustenta esta coleção; enumeração não é revisão integral. Símbolos/consumidores são identificados nos capítulos. Nenhum comando de aplicação, banco, broker ou deploy foi executado.

<!-- reading-section: sources -->

## Arquivos fonte

- `hub-vivabem/node-server/package.json`
- `hub-vivabem/node-server/src/app.js`
- `hub-vivabem/node-server/src/server.js`
- `hub-vivabem/node-server/src/config.js`
- `hub-vivabem/node-server/src/publisherPolicy.js`
- `hub-vivabem/node-server/src/publisherAuth.js`
- `hub-vivabem/node-server/src/redisEnvelope.js`
- `hub-vivabem/node-server/src/recipientRouting.js`
- `hub-vivabem/node-server/src/recipients.js`
- `hub-vivabem/node-server/src/subscriptions.js`
- `hub-vivabem/tests/node-server/subscriptions.test.js`

<!-- reading-section: history -->

## Reaproveitamento histórico e correções

O mapa antigo preserva a separação Pub/Sub/AMQP, recuperação por releitura e achados HUB por etapa. Descrições antigas de POST /events e Node condicionado ao RabbitMQ são históricas; app.js atual mantém apenas /health, server.js acrescenta /ready e registros HUB-06 posteriores substituem a narrativa anterior. Nenhuma contagem histórica de testes virou resultado desta tarefa.

Revision / Revisão: `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0`.

- `engineering-library_old/docs/pt-BR/architecture/hub-vivabem.md`
- `engineering-library_old/docs/pt-BR/interviews/hub-vivabem-interview.md`

<!-- reading-section: access -->

## Verificações e acesso ao código

Caminhos de código são referências apenas para checkout autorizado. São spans de código intencionalmente: nenhum snapshot/catálogo privado foi aprovado ou gerado, portanto o leitor não pode expandi-los. Navegação documental usa links de coleção. Não houve ingestão do catálogo no banco. Veja a revisão central para checks efetivamente executados.

<!-- reading-section: gaps -->

## Evidência ausente e trabalho restante

ACLs efetivas, overlays/bindings de produção, certificados/TLS, persistência/recuperação de brokers, fanout para clientes lentos e capacidade permanecem sem validação. Readiness Node não certifica fluxos AMQP. Nenhum teste de transporte ou comando de broker foi executado.

[Library review / Revisão da biblioteca](../../../engineering-library/pt-br/operations/vivabem-documentation-review.md)
