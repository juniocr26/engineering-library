> Registro histórico de revisão. Contratos e verificação atuais estão ligados em [Arquitetura](../architecture/overview.md). Datas, revisões e resultados abaixo mantêm o escopo original.

# Revisão das fontes — VivaBem

[English](../../en/operations/source-review.md) | [Português brasileiro](source-review.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `f0b884ca536a26996d40bf4187981d8c7506d0d7`.

<!-- reading-section: scope -->

## Cobertura da inspeção

Árvore fonte inicialmente limpa. Leitura estática seletiva dos caminhos listados sustenta esta coleção; enumeração não é revisão integral. Símbolos/consumidores são identificados nos capítulos. Nenhum comando de aplicação, banco, broker ou deploy foi executado.

<!-- reading-section: sources -->

## Arquivos fonte

- `vivabem/composer.json`
- `vivabem/app/Services/DashboardReadService.php`
- `vivabem/app/Services/BalanceReader.php`
- `vivabem/app/Services/ExternalPosterCofrePaciente.php`
- `vivabem/app/Services/ExternalPosterDigitalWallet.php`
- `vivabem/app/Services/CofreRequestPolicy.php`
- `vivabem/app/Services/RedisAuthenticationSession.php`
- `vivabem/app/Services/OfficialAppRequestDetector.php`
- `vivabem/app/Services/HubEventSigner.php`
- `vivabem/app/Services/AuditExecutor.php`
- `vivabem/config/cofre-paciente.php`
- `vivabem/config/carteira-digital.php`
- `vivabem/config/android.php`
- `vivabem/config/crypto.php`
- `vivabem/config/services.php`
- `vivabem/tests/Feature/BalanceReaderTest.php`

<!-- reading-section: history -->

## Reaproveitamento histórico e correções

A arquitetura/entrevista antigas fornecem ownership, recuperação de avisos perdidos, limites de transação e raciocínio do dashboard. Descrições de consultas/repasses/outbox financiados por Stripe são históricas após retirada financeira. O cliente específico de saldo atual não pode ser confundido com adaptador genérico indisponível. Registros de política legada mantêm semântica limitada própria; política atual de 60 dias e exclusão de atividade passiva substituem afirmações genéricas de TTL. Suporte CLI a diretório selecionado não prova uso pelo Portal.

Revision / Revisão: `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0`.

- `engineering-library_old/docs/pt-BR/architecture/vivabem.md`
- `engineering-library_old/docs/pt-BR/interviews/vivabem-interview.md`

<!-- reading-section: access -->

## Verificações e acesso ao código

Caminhos de código são referências apenas para checkout autorizado. São spans de código intencionalmente: nenhum snapshot/catálogo privado foi aprovado ou gerado, portanto o leitor não pode expandi-los. Navegação documental usa links de coleção. Não houve ingestão do catálogo no banco. Veja a revisão central para checks efetivamente executados.

<!-- reading-section: gaps -->

## Evidência ausente e trabalho restante

Esta revisão amostra dashboard, transporte entre pares, saldo/autenticação e auditoria. Máquina completa de estados/recuperação de consultas, ciclo de conferências, entrega de e-mail/FCM, recuperação de filas, acessibilidade, concorrência de banco e aceitação de startup/restauração de produção permanecem sem validação aqui. A documentação detalhada na fonte exige reconferência nessas implementações antes de ampliar afirmações.

[Library review / Revisão da biblioteca](../../../engineering-library/pt-br/operations/vivabem-documentation-review.md)

Leitura adicional focada: `routes/web.php`, `app/UseCases/AtendimentoUseCase.php`, `app/UseCases/AtendimentoEmergencialUseCase.php`, `app/Http/Controllers/TransacaoController.php`, `app/Jobs/ProcessarBuscaAtendimentoEmergencial.php`, `app/Services/AtendimentoGoogleMeetLinkService.php`, `app/Services/AtendimentoMensalGoogleMeetCleanupService.php`.
