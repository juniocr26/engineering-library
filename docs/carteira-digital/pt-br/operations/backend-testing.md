# Suíte backend atual e limites da verificação

[Sumário](../index.md) | [English](../../en/operations/backend-testing.md)

Revisado e executado em 2026-11-10. Público: mantenedores e revisores. A: código/asserções atuais; execução registrada separadamente. Nenhum teste, fixture, dependência, lógica ou infraestrutura foi alterado.

<!-- reading-section: harness -->
## Harness real e isolamento

`tests/TestCase.php` cria container Laravel mínimo, registra providers de banco/hash/cache/validação, usa cache array e conexão chamada mysql com SQLite :memory:. Cria schemas sintéticos transacao/saldo, sem providers ou migrations de produção. Bloqueia HTTP Laravel não simulado; operações externas exercitadas usam substitutos. Não valida locks/concorrência MySQL nem constitui sandbox de rede do sistema operacional.

`phpunit.xml` carrega vendor/autoload.php e descobre Unit/Feature. Nome da pasta não implica passagem de todo caso pelo kernel HTTP. Usa PHPUnit 11.5.56/Mockery e dependências locais existentes.

<!-- reading-section: scenarios -->
## Módulos existentes

| Arquivo | Contrato das asserções |
| --- | --- |
| `tests/Unit/SegurancaFinanceiraTest.php` | Conversão decimal/centavos estrita, rejeição de valores ambíguos e classificação sanitizada de falhas |
| `tests/Unit/ResultadoOperacaoTest.php` | Resultado público condicionado a effects_pending; rejeição de dono, destino e identidade emergencial |
| `tests/Feature/CompraAtendimentoSaldoTest.php` | Débito único por tentativa, rejeição de conteúdo conflitante e rollback por saldo insuficiente |
| `tests/Feature/ConclusaoFinanceiraTest.php` | Crédito único, proteção contra recusa tardia, esgotamento incerto, conversão tardia e composição do recebimento |
| `tests/Feature/RecuperacaoFinanceiraTest.php` | ACK de entrega antiga, espera sem consumir tentativa, reserva pré-consulta, esgotamento e idempotência na última tentativa |
| `tests/Feature/ApiFinanceiraTest.php` | Consulta pela rota/middleware/controller com claims, dono/ambiente/corpo e rejeição de campo extra |

<!-- reading-section: execution -->
## Resultado executado

Na raiz deste repositório:

```sh
composer test
```

Composer resolve para `php vendor/bin/phpunit --do-not-cache-result`. Saída 0 em PHP 8.3.27 / PHPUnit 11.5.56: **60 testes, 178 asserções**, todos aprovados. Sem serviço externo, credencial de produção ou banco implantado. Percentual de cobertura não medido.

<!-- reading-section: limits -->
## Lacunas, histórico e manutenção

Respostas Orders/Pix reais, transporte do provedor, confirmação broker, ciclo completo ACK/reject, observações Redis, corridas SQL e recuperação implantada permanecem não verificados. SQLite demonstra transições exercitadas, sem certificar isolamento de produção.

Guia de 2026-11-04 relatava 55/157 e listava arquivos ausentes no checkout. Relato é histórico, sem representar a suíte atual.

Fontes: composer.json, phpunit.xml, tests/TestCase.php e arquivos acima. Rever ambos os idiomas e coleção após mudanças em nomes, harness, contratos ou comandos. Suíte aprovada não é homologação ou completude documental. Novos testes ficam fora da tarefa documental.
