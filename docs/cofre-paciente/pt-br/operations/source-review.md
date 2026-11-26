> Registro histórico de revisão. Contratos e verificação atuais estão ligados em [Arquitetura](../architecture/overview.md). Datas, revisões e resultados abaixo mantêm o escopo original.

# Revisão das fontes — Cofre Paciente

[English](../../en/operations/source-review.md) | [Português brasileiro](source-review.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `85edbcb16fd029235dc74eba12c7b14b164d3d62`.

<!-- reading-section: scope -->

## Cobertura da inspeção

Árvore fonte inicialmente limpa. Leitura estática seletiva dos caminhos listados sustenta esta coleção; enumeração não é revisão integral. Símbolos/consumidores são identificados nos capítulos. Nenhum comando de aplicação, banco, broker ou deploy foi executado.

<!-- reading-section: sources -->

## Arquivos fonte

- `cofre-paciente/composer.json`
- `cofre-paciente/routes/api.php`
- `cofre-paciente/app/Http/Middleware/JwtMiddleware.php`
- `cofre-paciente/app/Services/CofreRequestPolicy.php`
- `cofre-paciente/app/Repository/CartoesRepository.php`
- `cofre-paciente/app/Services/StoredFinancialReader.php`
- `cofre-paciente/app/UseCases/CartoesUseCase.php`
- `cofre-paciente/app/UseCases/LinksUseCase.php`
- `cofre-paciente/config/crypto.php`
- `cofre-paciente/config/services.php`
- `cofre-paciente/tests/Feature/F06AuthorizationTest.php`

<!-- reading-section: history -->

## Reaproveitamento histórico e correções

O mapa histórico fornece explicações de cifra seletiva, limpeza local/remota e fronteira Mongo. A API conta_bancarias e o exercício antigo de CAS bancário foram retirados, não são interfaces ativas. Explicação genérica de JWT de serviço é incompleta para a política atual de nove rotas. Descrições históricas de falha da lista inteira cedem ao indicador explícito de completude parcial.

Revision / Revisão: `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0`.

- `engineering-library_old/docs/pt-BR/architecture/cofre-paciente.md`
- `engineering-library_old/docs/pt-BR/interviews/cofre-paciente-interview.md`

<!-- reading-section: access -->

## Verificações e acesso ao código

Caminhos de código são referências apenas para checkout autorizado. São spans de código intencionalmente: nenhum snapshot/catálogo privado foi aprovado ou gerado, portanto o leitor não pode expandi-los. Navegação documental usa links de coleção. Não houve ingestão do catálogo no banco. Veja a revisão central para checks efetivamente executados.

<!-- reading-section: gaps -->

## Evidência ausente e trabalho restante

Concorrência Mongo real, auditoria completa de ciclo/índices de avaliações, handoff/recuperação de filas, aceite de conferência remota, restauração e ownership ponta a ponta ficam fora desta revisão seletiva. Nenhum Mongo, broker ou API externa foi contatado.

[Library review / Revisão da biblioteca](../../../engineering-library/pt-br/operations/vivabem-documentation-review.md)

Leitura adicional focada: `app/Services/GoogleMeetRemovalMessageProcessor.php`, `app/Services/ConfirmedRabbitMqPublisher.php`, `app/Console/Commands/ConsumirRemocaoGoogleMeetCommand.php`.

Leitura adicional focada: `app/Services/Avaliacoes/RatingLifecycleService.php`, `app/Services/Avaliacoes/EvaluationIndexMaintenance.php`.
