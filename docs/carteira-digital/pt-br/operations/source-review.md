> Registro histórico de revisão. Contratos e verificação atuais estão ligados em [Arquitetura](../architecture/overview.md). Datas, revisões e resultados abaixo mantêm o escopo original.

# Revisão das fontes — Carteira Digital

[English](../../en/operations/source-review.md) | [Português brasileiro](source-review.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `9a6b795b6ebc16f0390e0fbdbf711f257e42fa2a`.

<!-- reading-section: scope -->

## Cobertura da inspeção

Árvore fonte inicialmente limpa. Leitura estática seletiva dos caminhos listados sustenta esta coleção; enumeração não é revisão integral. Símbolos/consumidores são identificados nos capítulos. Nenhum comando de aplicação, banco, broker ou deploy foi executado.

<!-- reading-section: sources -->

## Arquivos fonte

- `carteira-digital/composer.json`
- `carteira-digital/routes/api.php`
- `carteira-digital/app/Http/Controllers/TransacaoController.php`
- `carteira-digital/app/Http/Controllers/MercadoPagoWebhookController.php`
- `carteira-digital/app/Services/BalanceReader.php`
- `carteira-digital/app/Services/MercadoPagoEnvironment.php`
- `carteira-digital/app/Services/RuntimeCryptoConfiguration.php`
- `carteira-digital/config/crypto.php`
- `carteira-digital/config/services.php`
- `carteira-digital/database/migrations/2025_08_31_143316_transacao.php`
- `carteira-digital/tests/Feature/BalanceReaderTest.php`

<!-- reading-section: history -->

## Reaproveitamento histórico e correções

A arquitetura/entrevista históricas explicam ownership, identidades de idempotência, resultados incertos do provedor e limites de transação local. Contas Stripe/Connect, outbox/inbox de repasses e execução com lotes estornados são descrições retiradas. Controllers e migration atuais prevalecem. A recepção assinada Mercado Pago é apenas fundação, com 503 em vez de confirmação de aceite.

Revision / Revisão: `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0`.

- `engineering-library_old/docs/pt-BR/architecture/carteira-digital.md`
- `engineering-library_old/docs/pt-BR/interviews/carteira-digital-interview.md`

<!-- reading-section: access -->

## Verificações e acesso ao código

Caminhos de código são referências apenas para checkout autorizado. São spans de código intencionalmente: nenhum snapshot/catálogo privado foi aprovado ou gerado, portanto o leitor não pode expandi-los. Navegação documental usa links de coleção. Não houve ingestão do catálogo no banco. Veja a revisão central para checks efetivamente executados.

<!-- reading-section: gaps -->

## Evidência ausente e trabalho restante

Inbox/consumidor durável Mercado Pago, execução financeira, conciliação, aceitação de produção, upgrade/migração de schema e concorrência MySQL real permanecem pendentes. O schema de nove campos foi inspecionado, não aplicado aqui.

[Library review / Revisão da biblioteca](../../../engineering-library/pt-br/operations/vivabem-documentation-review.md)

## Entrega de resultados e observação operacional — revisão de 2026-11-10

IMPLEMENTED: `CasoDeUsoComprarAtendimentoSaldo` bloqueia o saldo do titular antes da busca idempotente e verifica titular, valor, tipo, ambiente, finalidade, atendimento e duração. Tentativa aprovada repetida retorna sem novo débito. Saldo insuficiente reverte a operação recém-criada. Débito e `debit_applied` são confirmados juntos; execução interrompida verifica a aprovação persistida antes de decidir por nova tentativa. A entrega continua como obrigação independente `effects_pending`.

`AdaptadorOrdersMercadoPago::situacao` exige ordem e pagamento `processed/accredited` para aprovar; `failed/processing_error` continua pendente. Recusa exige combinações terminais reconhecidas, não qualquer erro HTTP. A tradução verifica referência externa opaca, vendedor configurado, identidade da ordem, restrições BRL/BRA, centavos exatos, um pagamento e identidade de método/pagamento. Pagador retornado deve corresponder; pagador omitido não é inventado. Aprovação também exige valores efetivamente pagos exatos. A submissão usa a chave idempotente existente, sem redirecionamentos e com timeouts limitados. Limitação 423/429 reconhecida preserva o prazo de retentativa; respostas ambíguas permanecem incertas.

`AdaptadorResultadoCompraPortal` envia resultado criptografado para `/api/internal/balance-purchases/results` com JWT HS256 válido por 60 segundos, com escopo e vínculo a POST/caminho/corpo/sujeito. Sucesso HTTP sem `persisted=true` gera erro de efeitos não confirmados. Aprovação SQL não comprova conclusão das notificações ou aplicação do atendimento no Portal. A operação deve preservar identidades de transação/tentativa/evento e investigar efeitos pendentes em vez de criar nova cobrança.

`ObservabilidadeReconciliacao` registra compras externas suportadas, excluindo identidades Pix sintéticas. Separa eventos de tentativa, consulta ao provedor, retentativa, início de crédito, confirmação após commit e resultado observado. `credito_iniciado` explicitamente não comprova saldo creditado. O esquema versão 1 correlaciona eventos à transação; titular/valor/identificadores do provedor são metadados operacionais sensíveis que não devem aparecer em exemplos públicos. O registro adiado ocorre após commit MySQL quando cabível; falhas de preparação/armazenamento são contidas e registradas sem alterar o processamento financeiro.

`AdaptadorObservabilidadeReconciliacaoRedis` usa Lua com verificação de tipos e pré-verificação de ACL quando disponível. Acrescenta eventos sequenciais por transação, substitui metadados e mantém índice ordenado por titular. Metadados/eventos/índice expiram em 604800 segundos (sete dias), renovados por gravações; entradas antigas do índice são removidas. Esta projeção temporária do Cockpit não é razão financeiro imutável, prova de liquidação ou fonte para reconstruir SQL ausente. Nenhum teste real de Redis/ACL/provedor foi executado aqui.

Fontes: `app/UseCases/CasoDeUsoComprarAtendimentoSaldo.php`, `app/Adapters/AdaptadorOrdersMercadoPago.php`, `app/Adapters/AdaptadorResultadoCompraPortal.php`, `app/Services/ObservabilidadeReconciliacao.php`, `app/Adapters/AdaptadorObservabilidadeReconciliacaoRedis.php`. Gatilho de manutenção: mudanças em estados, confirmação de entrega, esquema de eventos, retenção ou classificação de retentativa exigem atualização conjunta dos idiomas e da coleção curada.
