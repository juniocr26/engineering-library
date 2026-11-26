# Testes existentes e evidências de verificação

[Sumário](../index.md) | [English](../../en/testing/verification.md)

Revisado e executado em 2026-11-10. Público: revisores e mantenedores. Escopo: suíte existente e verificações documentais. Registro de resultados observados, sem substituir relatórios históricos por certificação de produção. Nenhum teste, fixture, runner, código ou dependência foi criado ou alterado.

<!-- reading-section: suite -->
## Suíte existente e isolamento

`composer.json` define `test: phpunit`; `phpunit.xml` carrega `tests/bootstrap.php`, descobre `tests/` e reprova warnings/testes arriscados. Bootstrap carrega Composer e hooks existentes de operações de filesystem no namespace. `tests/Suporte/TesteIsolado.php` cria diretórios temporários privados aleatórios e remove apenas árvore pertencente ao teste. Hooks de `OperacoesArquivo.php` simulam falhas; testes de processo usam `proc_open` e `tests/Suporte/processo.php` existentes nesses diretórios. Não acessam logs ou bancos das aplicações.

| Área de teste existente | Contratos verificados pelas asserções |
| --- | --- |
| `tests/Dominio/CampoContextoTest.php` | Tipos estritos, limites, listas, forma abreviada |
| `tests/Dominio/TagsTest.php` | Normalização, dimensões, rejeição de colisões/valores |
| `tests/Dominio/EventoTest.php` | Schema completo, UTC, omissão de opcionais |
| `tests/Aplicacao/CatalogoTest.php` | Catálogo extensível, definições/identidade inválidas, desconhecidos |
| `tests/Aplicacao/RegistradorTest.php` | UUID, identidade, fallback protegido, entradas contraditórias |
| `tests/Aplicacao/ContextoTest.php` | Remoção de sensíveis/desconhecidos, UTF-8, escalares, ausente/null/zero/false |
| `tests/Aplicacao/DiagnosticoTest.php` | Redação, ausência de argumentos, caminhos relativos, causas/quadros limitados |
| `tests/Aplicacao/RuidoTest.php` | Elegibilidade, primeira escrita, limites, correlação, flush falho, grupos limitados |
| `tests/Infraestrutura/SerializadorTest.php` | JSON Lines, bytes, erros de não finitos |
| `tests/Infraestrutura/PsrTest.php` | Mapeamento de severidades, contexto estruturado, causas |
| `tests/Infraestrutura/ArquivoDiarioTest.php` | Rotação UTC, permissões, bordas, links, escritas parciais/restauração |
| `tests/Integracao/ContratoRegistroTest.php` | Resumo de recuperação até arquivo e exclusão de mensagens privadas |
| `tests/Integracao/ProcessosTest.php` | Quatro escritores/300 eventos, bloqueio, encerramento abrupto |

Testes de processo verificam concorrência delimitada, sem medir vazão. Término abrupto cobre resumo pendente em memória, sem cobrir todo ponto de falha ou queda elétrica.

<!-- reading-section: execution -->
## Comando executado e resultado

Diretório: raiz da biblioteca, com `vendor/` preexistente. Runtime do host foi usado para este pacote PHP independente; biblioteca inspecionada não contém definição de container. Comando desabilita escrita de cache de resultados:

```sh
composer test -- --do-not-cache-result
```

Resultado real: saída 0; PHP 8.3.27; PHPUnit 11.5.57; **210 testes, 1323 asserções**, todos aprovados em 2026-11-10. Tempo 1.896 segundos e memória 12 MB são observações do runner nessa execução, sem representar desempenho da aplicação. Não houve indicação de testes ignorados. Não foi solicitada/produzida medição de cobertura. Aprovação no PHP 8.3 não certifica toda versão aceita por `^8.2` ou todo filesystem/plataforma.

O exemplo PHP executável completo do guia passou em `php -l` e execução real em diretório descartável próprio em 2026-11-10: foram verificados registro JSON Lines único, UUID correspondente, schema `1.1`, código e contexto numérico. Código dos exemplos inglês/português era idêntico. O exemplo de agregação opcional do capítulo operacional também passou em lint PHP e execução: primeiro ID presente, ID repetido nulo, dois registros, contagem `1`, motivo `explicit_flush` e último contexto verificados; ambos os idiomas usam código idêntico. Fences de declarações da API são assinaturas, não programas autônomos. Comandos/resultados exatos das verificações documentais pertencem ao relatório da tarefa; paridade estrutural não substitui revisão semântica bilíngue.

<!-- reading-section: limitations -->
## Limites da validação e manutenção

Não executados: instalação por registry privado, binding Laravel, entrega Datadog, aplicações reais, filesystem/coletor de produção, backup/restore, matriz de releases, benchmark ou revisão visual do frontend. Socket Docker da Engineering Library estava indisponível nesta sessão; nenhum serviço foi criado, iniciado ou reconfigurado. Sincronização do catálogo altera banco e não foi executada.

`tools/check_catalog.py` integral inclui manifesto histórico de inventário fixo/procedência. Nova coleção pode causar divergência de inventário até reconciliação deliberada da política de procedência. A tarefa não regenera histórico ou snapshots para silenciar a verificação. Verificações delimitadas em memória podem validar caminhos, âncoras, chaves bilíngues e alcance separadamente; relatório final precisa identificar quais foram executadas.

Mantenedores devem reexecutar suíte existente após mudanças contratuais e registrar data/runtime/resultado, sem apresentar resultado antigo como novo. Atualizar ambos os idiomas quando nomes, escopo, isolamento ou comando mudar. Testes/scaffolding novos exigem autorização separada; esta documentação não os cria. Fontes: `composer.json`, `phpunit.xml`, testes acima e helpers existentes. Aprovação permanece com proprietário/revisor técnico designado.

## Evidência atual — 11/11/2026

Suíte local da biblioteca em `4b99743`: `php vendor/bin/phpunit --do-not-cache-result`, exit 0, PHP 8.3.27, PHPUnit 11.5.57, **210 testes, 1323 asserções**. Não certifica publicação, implantação ou integração de produção. Nenhum teste foi alterado nesta manutenção documental.
