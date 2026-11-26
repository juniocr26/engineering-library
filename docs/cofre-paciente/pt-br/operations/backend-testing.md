# Suíte backend atual e limites da verificação

[Sumário](../index.md) | [English](../../en/operations/backend-testing.md)

Revisado e executado em 2026-11-10. Público: mantenedores e revisores. A: código/asserções atuais; execução registrada separadamente. Nenhum teste, fixture, dependência, lógica ou infraestrutura foi alterado.

<!-- reading-section: harness -->
## Harness real e isolamento

`tests/TestCase.php` cria aplicação Laravel mínima com SQLite em memória e providers de validação/tradução/FormRequest, JWT sintético e logger/view simulados. Bloqueia HTTP Laravel não simulado e limpa Carbon, timestamp/leeway JWT, models e facades. Cenários substituem repositórios Mongo, criptografia e dependências remotas. Não utiliza o harness removido tests/TesteIsolado.php.

`phpunit.xml` carrega vendor/autoload.php e descobre Unit/Feature. Nome da pasta não implica passagem de todo caso pelo kernel HTTP. Usa PHPUnit 11.5.56/Mockery e dependências locais existentes.

<!-- reading-section: scenarios -->
## Módulos existentes

| Arquivo | Contrato das asserções |
| --- | --- |
| `tests/Unit/IdentificadoresCartoesTest.php` | Rejeição de chaves Mongo, caminhos diagnósticos seguros e referência mínima/ambiente |
| `tests/Unit/ProcessadorMensagemRemocaoGoogleMeetTest.php` | ACK somente na conclusão, reject condicionado a pendência persistida, entrada inválida e falha de dependência |
| `tests/Unit/RetencaoAvaliacoesTest.php` | Flag de contabilização, data/corte estritos e rejeição de datas inválidas |
| `tests/Feature/AutorizacaoLinksApiTest.php` | Router/middleware/controller/caso de uso locais com crypto/repositório simulados; negação antes de decifrar claims/corpo/query inválidos |
| `tests/Feature/CartoesTest.php` | Redação de token legado, listas incompletas/ilegíveis e exclusão por dono/valor observado |
| `tests/Feature/AvaliacoesTest.php` | Estrelas inteiras 1–5, duplicidade, IDs normalizados e respostas agregadas |
| `tests/Feature/RecuperacaoLinksTest.php` | Idempotência de exclusão ausente e continuação após falha individual |

<!-- reading-section: execution -->
## Resultado executado

Na raiz deste repositório:

```sh
composer test
```

Composer resolve para `php vendor/bin/phpunit --do-not-cache-result`. Saída 0 em PHP 8.3.27 / PHPUnit 11.5.56: **58 testes, 156 asserções**, todos aprovados. Sem serviço externo, credencial de produção ou banco implantado. Percentual de cobertura não medido.

<!-- reading-section: limits -->
## Lacunas, histórico e manutenção

Índices/atomicidade MongoDB implantados, remoção real no provedor, controller completo de débito, transporte retry/DLQ e limpeza real de conferência permanecem não verificados. Teste do processador valida ação retornada, sem ACK em broker real.

Relato anterior 21/52 e três arquivos citados são obsoletos como inventário atual. Resultados antigos permanecem atribuídos àquela execução.

Fontes: composer.json, phpunit.xml, tests/TestCase.php e arquivos acima. Rever ambos os idiomas e coleção após mudanças em nomes, harness, contratos ou comandos. Suíte aprovada não é homologação ou completude documental. Novos testes ficam fora da tarefa documental.
