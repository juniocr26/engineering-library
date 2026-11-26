# Gravação, ciclo de ruído e recuperação operacional

[Sumário](../index.md) | [English](../../en/operations/reliability.md)

Revisado em 2026-11-10. Público: operadores e mantenedores de workers PHP persistentes. A: comportamento inspecionado; testes mapeados na [verificação](../testing/verification.md). Escopo: gravador local e ruído local ao processo, sem certificação de recuperação em produção. Operadores da aplicação respondem por permissões, retenção, coleta e decisões de incidente.

<!-- reading-section: storage -->
## Diretório exclusivo e arquivos diários JSON Lines

`Infraestrutura\GravadorArquivoDiario` inicializa diretório exclusivo e marcador `.tracepaw-lib-jsonl-v1` com `tracepaw-lib/jsonl/1\n`. Se o marcador estiver vazio, inicialização exige diretório contendo apenas esse marcador; logs legados não são migrados. Marcador válido inicializado permite reutilização posterior. O construtor altera o filesystem antes de registrar eventos; não usar diretório de produção em smoke check.

Saída: `tracepaw-YYYY-MM-DD.log`, escolhendo data UTC do timestamp do evento, sem usar timezone do host ou data local de São Paulo. Não há implementação de rotação por rename, retenção, compressão ou envio. Prefixo `tracepaw-` não instala a biblioteca no Laravel. Diretórios novos solicitam `0700`; inicialização do marcador e arquivos diários novos vazios usam `0600`. Permissões de diretório/arquivo não vazio existentes exigem inspeção operacional.

Em cada append, o gravador serializa primeiro, verifica inode/device do diretório, rejeita links inseguros/destinos não regulares, cria exclusivamente ou reabre arquivo regular com verificações, obtém `flock(LOCK_EX)` bloqueante e confere identidade entre arquivo aberto e caminho. Arquivos existentes são verificados no primeiro/último registro: terminador newline, JSON válido, schema `1.0/1.1` aceito e ID/código/timestamp textuais. É verificação de bordas, sem validação completa do schema ou auditoria dos registros internos. A suíte preserva explicitamente corrupção intermediária como limitação documentada.

Append ocorre sob o mesmo lock, completa escritas parciais e chama `fflush`/`fsync`. Exceção de escrita/sincronização tenta truncar para tamanho anterior e sincronizar; restauração falha gera `FalhaGravacao` explícita exigindo inspeção. Lock e recurso são liberados em `finally`. Processos cooperantes são serializados pelo lock; não há timeout ou garantia para filesystem distribuído. Custo de lock/sync é síncrono e não medido. Falha abrupta de processo/host não tem garantia transacional de exatamente uma vez.

<!-- reading-section: eligibility -->
## Elegibilidade de supressão e preservação da primeira falha

`PreservarEventos` padrão registra tudo; `AgregarTransitorios` solicita agregação, mas elegibilidade do registrador continua obrigatória. Todas as condições precisam ocorrer simultaneamente:

- Classificação `Transitorio`.
- Severidade `Depuracao`, `Informacao`, `Aviso` ou `Alerta`.
- Resultado `NovaTentativaAgendada`.
- `acaoNecessaria !== true` e `impacto === null`.
- Correlação validada não nula e ausência de Throwable.

Eventos error/críticos, incidentes operacionais/de segurança, recuperação confirmada, resultados desconhecidos, possível perda e eventos exigindo ação nunca são elegíveis. O evento sintético de retry agendado é `Esperado`; não se torna suprimível apenas pelo resultado `retry_scheduled`.

`AgregadorTransitorios::confirmarPrimeiro` cria grupo somente após primeira gravação bem-sucedida. Falha inicial não habilita supressão. Com capacidade esgotada, grupos novos não são rastreados e eventos continuam gravados; grupos já rastreados ainda podem agregar. Padrões: 60 segundos, 100 repetições suprimidas e 256 grupos; intervalos constam na [configuração](../guides/installation.md).

<!-- reading-section: groups -->
## Identidade de grupo, resumos e flush

Chave do grupo é hash do evento estruturado sem `event_id/timestamp`. Por padrão inclui contexto sanitizado completo, identidade de requisição/correlação e outros metadados: mudar `attempt` normalmente cria outro grupo. `DefinicaoEvento::camposAgrupamento` opcional seleciona campos aprovados para agrupar; `null` mantém todos, `[]` nenhum. Requisição/correlação continuam participando. Campo ausente e null explícito permitido permanecem distintos. Selecionar menos campos melhora agregação e remove deliberadamente essas diferenças da identidade; revisar por evento.

Com agrupamento explícito, contexto do resumo mantém somente os últimos `attempt`, `duration_ms` e `retry_delay_ms` aprovados presentes no último evento suprimido. Sem agrupamento explícito fica vazio. Contexto estável permanece consultável por `first_event_id`; resumos não copiam todo contexto original. Campos de `aggregation`: `source_event_code`, `first_event_id`, `suppressed_count`, `first_seen`, `last_seen`, `duration_ms` monotônico e `reason`. Duração mede última repetição observada desde a primeira, sem representar duração total da indisponibilidade até recuperação.

Motivos: `threshold`, `interval`, `operation_event`, `explicit_flush`. Expiração usa `hrtime` monotônico, avaliada somente durante registro/flush; não há timer. Checagem do limite após contagem pode emitir resumo em chamada que retorna `null`. Resumo possui UUID e timestamp UTC próprios. Contagem suprimida exclui o primeiro evento individual; totais devem combinar primeiros eventos e contagens, sem contar apenas linhas JSON.

`descarregarRuido()` descarrega todos os grupos pendentes. Resumos gravados confirmam/removem grupos; flush repetido bem-sucedido não duplica registros no ciclo em memória observado. Resumos falhos mantêm estado para retry enquanto o processo vive. Não há destrutor/hook de encerramento, persistência, agregação entre processos ou replay. Encerramento abrupto pode perder contagens pendentes, preservando primeira ocorrência gravada com sucesso. Configuração de agregador injetada é clonada com grupos zerados por registrador.

Evento não elegível encerra grupos da mesma `(project, service, environment, correlation_id)`, sem usar código, dependência ou request ID nessa correspondência. Recuperação/escalada com essa correlação descarrega grupos pertinentes, sem comprovar recuperação de todas as dependências. Escopo de correlação é decisão de integração que exige responsabilidade clara.

<!-- reading-section: example -->
## Exemplo sintético de agregação opcional

Executar na raiz da biblioteca com dependências instaladas. Cria diretório descartável único. Catálogo usa deliberadamente nenhum campo contextual na identidade para que mudar tentativa/atraso não divida o grupo; produtor/correlação/requisição continuam participando. Registra afirmação de retry agendado sem executar retry.

```php
<?php

declare(strict_types=1);
require getcwd() . '/vendor/autoload.php';

use TracePaw\Aplicacao\{AgregarTransitorios, Catalogo, Configuracao};
use TracePaw\Dominio\{Classificacao, DefinicaoEvento, Resultado, Severidade};
use TracePaw\Infraestrutura\GravadorArquivoDiario;
use TracePaw\Registrador;

$directory = sys_get_temp_dir() . '/synthetic-noise-' . bin2hex(random_bytes(8));
$catalog = new Catalogo([
    new DefinicaoEvento(
        'synthetic.connection_unavailable',
        'Synthetic dependency unavailable; retry scheduled.',
        Severidade::Alerta,
        Classificacao::Transitorio,
        ['attempt', 'retry_delay_ms'],
        resultado: Resultado::NovaTentativaAgendada,
        camposAgrupamento: [],
    ),
], []);
$registrar = new Registrador(
    new Configuracao('synthetic-project', 'worker', 'testing'),
    $catalog,
    new GravadorArquivoDiario($directory),
    new AgregarTransitorios(),
);
$firstId = $registrar->registrar(
    'synthetic.connection_unavailable',
    ['attempt' => 1, 'retry_delay_ms' => 100],
    correlacao: 'synthetic-operation-1',
);
$repetitionId = $registrar->registrar(
    'synthetic.connection_unavailable',
    ['attempt' => 2, 'retry_delay_ms' => 200],
    correlacao: 'synthetic-operation-1',
);
$registrar->descarregarRuido();
```

Resultado esperado: `$firstId` não nulo, `$repetitionId` nulo e flush explícito produz segundo registro JSON Lines com código `library.transient_summary`, `suppressed_count: 1`, `reason: explicit_flush` e última tentativa/atraso `2/200`. Não se afirma recuperação. Exemplo usa janela padrão de 60 segundos; executar chamadas cruzando sua expiração pode criar nova ocorrência. Descartar somente saída temporária pertencente ao exemplo após inspeção. Chamador precisa tratar exceções; consultar contrato de falha parcial abaixo.

<!-- reading-section: partial-failure -->
## Falha parcial e diagnóstico seguro

Resumos pendentes precedem evento atual. Se resumo falhar, o registrador tenta gravar evento atual mesmo assim e relança erro do resumo. Exceção não comprova ausência do evento atual. Se a gravação atual também falhar, seu erro propaga em lugar do anterior. Não há rollback de registros já escritos. Repetir cegamente o registro pode criar outro UUID; não há chave idempotente fornecida pelo chamador ou garantia de exatamente uma vez. Repetir flush explícito difere de repetir operação de negócio.

| Sintoma | Diagnóstico seguro / fronteira de recuperação |
| --- | --- |
| Diretório legado/incompatível | Preservar logs; selecionar destino vazio exclusivo aprovado; sem conversão automática |
| Diretório ausente/substituído ou link inseguro | Inspecionar propriedade, mounts e inodes; preservar alvos; não contornar verificações |
| Evento excessivo | Rever campos e limite; não despejar payload rejeitado sensível no diagnóstico |
| Registro de borda inválido/incompleto | Suspender presunção de append saudável; preservar arquivo para inspeção autorizada; não truncar como validação rotineira |
| Falha de escrita/sync/restauração | Conferir espaço, permissões e saúde do filesystem; restauração falha exige investigar integridade |
| Chamada demorada | Verificar lock bloqueante e I/O síncrono; não há timeout configurado |
| Resumo final ausente | Conferir ciclo de processo, flush explícito e término abrupto; ausência não comprova zero repetições |
| Erro após evento atual persistido | Inspecionar evidência sintética/autorizada e resultado do adaptador antes do retry; entrega pode ser parcial |

Não registrar recursivamente falha pelo mesmo gravador. Aplicações precisam de fronteira de falha aprovada separadamente que preserve semântica de negócio e privacidade. Esta tarefa não adiciona fallback ou recuperação. Operadores devem organizar backup/retenção privados conforme política da instalação; nenhum backup/restore foi executado, e restauração com escritores ativos não foi validada.

<!-- reading-section: evidence -->
## Evidências e manutenção

Fontes: `src/Infraestrutura/{GravadorArquivoDiario,SerializadorJson,GravadorPsr}.php`, `src/Registrador.php::{registrarDefinicao,gravarResumos,descarregarRuido}`, `src/Aplicacao/{AgregadorTransitorios,AgregarTransitorios,PreservarEventos}.php`. Asserções: `tests/Aplicacao/RuidoTest.php`, `tests/Infraestrutura/ArquivoDiarioTest.php`, `tests/Integracao/{ContratoRegistroTest,ProcessosTest}.php`. Rever ambos os idiomas quando agrupamento, identidade/lock, flush, aceitação de arquivo ou ciclo da aplicação mudar. Testes locais de processo não certificam filesystem de rede, queda elétrica, armazenamento de produção, envio Datadog ou vazão.

## Migração da identidade de armazenamento

Novos arquivos usam `tracepaw-YYYY-MM-DD.log` em UTC e o gravador próprio usa `.tracepaw-lib-jsonl-v1`. Logs históricos `datadog-YYYY-MM-DD.log` permanecem intocados: não renomear, reescrever, converter marcadores ou introduzir leitores de compatibilidade. A retenção do Monolog nos consumidores não elimina automaticamente arquivos do prefixo antigo. Retenção e arquivamento desses arquivos pertencem aos operadores.
