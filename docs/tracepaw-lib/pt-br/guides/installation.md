# Instalação, configuração e primeiro evento

[Sumário](../index.md) | [English](../../en/guides/installation.md)

Revisado em 2026-11-10. Público: integradores PHP. Objetivo: instanciar a API real e produzir evento JSON Lines sintético em local descartável. A: API inspecionada; exemplo ilustrativo salvo execução registrada separadamente. Este guia não instala o pacote em aplicações do ecossistema.

<!-- reading-section: prerequisites -->
## Requisitos e identidade Composer

`composer.json` exige PHP `^8.2`, JSON e `psr/log ^3.0`; nome do pacote `parceiro-vivabem/tracepaw-lib`, namespace `TracePaw\`. Consumidores precisam de origem Composer privada aprovada pelo proprietário que disponibilize essa identidade. O repositório não estabelece URL pública de registry ou restrição de versão adequada para todas as aplicações. Não inventar esses valores nem inserir credenciais na configuração do projeto.

No consumidor autorizado, após configurar origem privada e política de versão aprovadas, o comando pelo nome do pacote é:

```sh
composer require parceiro-vivabem/tracepaw-lib:0.2.0
```

Altera manifesto/lockfile/vendor do consumidor e pode acessar a origem configurada; não foi executado nesta tarefa documental. Mantenedores do checkout utilizam o lockfile existente e `composer install` quando faltarem dependências. Instalação difere de verificação e é desnecessária quando `vendor/` já existe. Inspecionar versão resolvida antes de atribuir os contratos do checkout à aplicação implantada.

<!-- reading-section: configuration -->
## Contrato de configuração

`src/` inspecionado não lê dotenv/variável de ambiente diretamente. Chamadores fornecem argumentos; nomes de ambiente específicos da aplicação não são prescritos. Não presumir semântica ausente/vazio por convenção Laravel.

| Entrada / construtor de declaração | Padrão e validação | Significado operacional |
| --- | --- | --- |
| `Configuracao($projeto,$servico,$ambiente)` | Todos obrigatórios; `[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}` | Identidade estática não secreta; vazio rejeitado |
| `Catalogo($definicoes,$taxonomia)` | Ambos arrays obrigatórios; consultar API | Vocabulário revisado, sem payload arbitrário |
| `GravadorArquivoDiario($diretorio,$serializador)` | Diretório obrigatório; serializador padrão `new SerializadorJson()` | Construtor cria/inicializa armazenamento; caminho exclusivo |
| `SerializadorJson($limiteBytes)` | 65536; intervalo inclusivo 4096–1048576 | Bytes incluem terminador; excesso gera erro |
| `politica` do registrador | `new PreservarEventos()` | Agregação exige opção explícita |
| `sanitizador` do registrador | `new SanitizadorContexto()` | Diagnóstico padrão omite caminhos de origem |
| `AgregadorTransitorios($intervaloMs,$limiteRepeticoes,$limiteGrupos,$relogio)` | 60000 / 100 / 256 / `hrtime(true)` | Intervalos 1–3600000 ms, 1–10000 repetições, 1–1024 grupos |
| `DiagnosticoExcecao($raizAplicacao,$mensagensAprovadas,$limiteQuadros,$limiteCausas)` | null / [] / 12 / 3 | Se fornecido, diretório existente distinto da raiz; quadros 0–16; causas 1–4 |

`InvalidArgumentException` sinaliza identidades, limites ou diagnóstico inválidos. Inicialização do armazenamento pode lançar `FalhaGravacao` antes de qualquer evento. Caminhos e rótulos precisam ser valores aprovados não secretos. Canonicalização/checagem de identidade não substitui controle de acesso do host; permissões de diretório existente não são automaticamente restringidas pelo construtor.

<!-- reading-section: first-event -->
## Exemplo PHP sintético

Executar na raiz do checkout com dependências instaladas. O exemplo cria diretório temporário único e grava um registro sintético, sem acessar logs das aplicações. Exige permissão de escrita. Não copiar para handler de produção como estratégia de alocação de diretórios.

```php
<?php

declare(strict_types=1);
require getcwd() . '/vendor/autoload.php';

use TracePaw\Aplicacao\{Catalogo, Configuracao};
use TracePaw\Infraestrutura\GravadorArquivoDiario;
use TracePaw\Registrador;

$directory = sys_get_temp_dir() . '/synthetic-events-' . bin2hex(random_bytes(8));
$registrar = new Registrador(
    new Configuracao('synthetic-project', 'worker', 'testing'),
    Catalogo::exemplosSinteticos(),
    new GravadorArquivoDiario($directory),
);
$eventId = $registrar->registrar(
    'consumer.processing_started',
    ['attempt' => 0],
    correlacao: 'synthetic-operation-1',
    requisicao: 'synthetic-request-1',
);
```

Observação esperada: UUID não nulo, marcador `.tracepaw-lib-jsonl-v1` e `laravel-<data-UTC>.log` com objeto JSON terminado por newline, `schema_version: "1.1"`, código `consumer.processing_started` e `context.attempt: 0`. Prefixo do arquivo é convenção de armazenamento, sem comprovar integração Laravel. Verificar com parser JSON no arquivo descartável; não imprimir logs operacionais reais. Saída temporária do exemplo exige política local explícita de limpeza; o guia não contém comando de exclusão em produção.

<!-- reading-section: adapter -->
## Ligação PSR-3 e adoção Laravel

Para instância já aprovada de `Psr\Log\LoggerInterface`, injetar `new TracePaw\Infraestrutura\GravadorPsr($logger)` como gravador. `GravadorPsr::gravar` serializa, decodifica e chama `log($severity, $staticMessage, $structuredData)`. Preserva objetos aninhados. Exceções do logger são envolvidas em `FalhaGravacao` com causa; falhas de serialização precedem o despacho. O adaptador implementa `Gravador` da biblioteca, não `LoggerInterface`.

Logger externo controla formato, armazenamento, entrega e retenção. Chamada PSR-3 não garante JSON Lines, rotação diária, flush, confirmação remota ou privacidade equivalente para metadados extras acrescentados pelo logger. Sua configuração precisa de revisão separada. Construtores da biblioteca não exigem credenciais ou endpoint Datadog.

A adoção Laravel existe nos três consumidores por adaptadores PSR/Monolog. Catálogos, ciclo de vida, tratamento de falhas e retenção pertencem às aplicações. Implantação permanece não verificada; não reutilizar diretório de logs mistos no gravador exclusivo.

<!-- reading-section: troubleshooting -->
## Verificação, diagnóstico e manutenção

Código desconhecido: inspecionar `Catalogo::resolver` e definições selecionadas. Contexto inválido: conferir tipo, limites e listas, sem converter indiscriminadamente dados de negócio em strings. Tags inválidas: conferir taxonomia e padrões contraditórios. Falha de armazenamento: seguir [confiabilidade](../operations/reliability.md), preservando evidência. Evitar registrar recursivamente erros pelo mesmo gravador quebrado.

Fontes: `composer.json`, `src/Aplicacao/{Configuracao,Catalogo,AgregadorTransitorios,DiagnosticoExcecao}.php`, `src/Registrador.php`, `src/Infraestrutura/{GravadorArquivoDiario,GravadorPsr,SerializadorJson}.php`. Suite e exemplo executados constam na [verificação](../testing/verification.md). Mantenedores devem rever os dois idiomas após mudanças em construtores, requisitos, implantação ou adaptadores. Acesso ao registry privado e ligação em produção permanecem não verificados.

## Adoção atual — 11/11/2026

Os três consumidores Laravel usam a dependência `0.2.0` em declaração, lockfile e metadados instalados locais, com canal `tracepaw` e adaptador PSR/Monolog. O Hub Node.js não instala essa biblioteca PHP. O gravador interno exige diretório vazio/exclusivo e marcador `.tracepaw-lib-jsonl-v1`; Monolog não usa esse marcador. Implantação e publicação remota permanecem não verificadas; referências anteriores a adoção futura descrevem o escopo histórico da revisão isolada da biblioteca.
