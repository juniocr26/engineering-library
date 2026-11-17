# API pública PHP e contrato estruturado de eventos

[Sumário](../index.md) | [English](../../en/api/contracts.md)

Revisado em 2026-11-10; A: API inspecionada. Público: chamadores PHP e consumidores de eventos. API local ao processo, sem autenticação HTTP, endpoints ou códigos de resposta. Autorização pertence à aplicação hospedeira. Consultar [instalação](../guides/installation.md), [privacidade](../security/context-and-diagnostics.md) e [confiabilidade](../operations/reliability.md).

<!-- reading-section: registrar -->
## Métodos do registrador e semântica de erros

`TracePaw\Registrador` recebe `Configuracao`, `Catalogo`, `Gravador`, `PoliticaRuido` opcional (padrão `PreservarEventos`), `SanitizadorContexto` opcional e `AgregadorTransitorios` opcional. Argumentos nomeados precisam preservar a grafia em português.

```php
public function registrar(
    string $codigo,
    array $contexto = [],
    array $tags = [],
    ?string $correlacao = null,
    ?string $requisicao = null,
    ?Resultado $resultado = null,
    ?\Throwable $excecao = null,
): ?string;

public function registrarFalhaInesperada(
    \Throwable $excecao,
    ?string $correlacao = null,
    ?string $requisicao = null,
): string;

public function descarregarRuido(): void;
```

`registrar` retorna UUID de ocorrência após sucesso do gravador, ou `null` para repetição agregada. Não retorna resultado booleano de negócio. Identificadores informados seguem `[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,127}`; vazio/quebras de linha são inválidos. Código desconhecido, tags contraditórias, resultado fixo contraditório e contexto aprovado inválido lançam `InvalidArgumentException`. Erros de tipo PHP continuam erros de tipo. Falhas de gravação propagam; não há envelope de sucesso ou retry automático.

`registrarFalhaInesperada` dispensa consulta ao catálogo com `library.unexpected_failure`, mensagem estática em português, `error`, `unexpected_defect`, contexto/tags vazios e resultado `unknown`, utilizando diagnóstico sanitizado. Ainda valida correlação/requisição e pode falhar ao gravar. Não é fallback automático para erro de digitação de código.

<!-- reading-section: definitions -->
## Definições e taxonomia controlada

Campos de `Dominio\DefinicaoEvento`, em ordem: `codigo`, `mensagem`, `severidade`, `classificacao`, `camposPermitidos=[]`, `tags=[]`, `impacto=null`, `resultado=Resultado::Desconhecido`, `acaoNecessaria=null`, `camposAgrupamento=null`. Código exige pelo menos dois segmentos minúsculos separados por ponto, iniciados por letra e compostos de letras/dígitos/underscore; máximo de 128 bytes. Mensagem é UTF-8 não vazia, até 2048 bytes; impacto opcional é UTF-8, até 256 bytes. Mensagens são conteúdo fixo do catálogo, sem interpolar payloads do chamador.

`Aplicacao\Catalogo(array $definicoes, array $taxonomia)` rejeita objetos inválidos, códigos duplicados, tags padrão não aprovadas e taxonomias inválidas. Dimensões permitidas são exatamente `domain`, `component`, `dependency`, `operation`, `failure_category` (`Dominio\Tags::DIMENSOES`). Cada dimensão aceita até 100 strings `[a-z][a-z0-9_]{0,63}`. `Tags` remove espaços das pontas e converte chave/valor para minúsculas, rejeita colisões de normalização ou valores não aprovados e ordena chaves. IDs e URLs ficam fora desse vocabulário de baixa cardinalidade; aprovação sintática não garante privacidade do catálogo.

| Severidade PHP | Severidade serializada |
| --- | --- |
| `Depuracao` | `debug` |
| `Informacao` | `info` |
| `Aviso` | `notice` |
| `Alerta` | `warning` |
| `Erro` | `error` |
| `Critico` | `critical` |
| `AcaoImediata` | `alert` |
| `Emergencia` | `emergency` |

Valores de `Classificacao`: `Esperado=expected`, `Transitorio=transient_failure`, `Recuperavel=recoverable_error`, `Recuperacao=confirmed_recovery`, `Defeito=unexpected_defect`, `Incidente=operational_incident`, `Seguranca=security_incident`. Valores de `Resultado`: `Desconhecido=unknown`, `Sucesso=success`, `Falha=failure`, `NovaTentativaAgendada=retry_scheduled`, `Esgotado=retry_exhausted`, `PossivelPerda=potential_data_loss`. São dimensões distintas. Definição com `unknown` permite seleção pelo chamador; resultado fixo não pode ser contradito. A biblioteca registra a afirmação do chamador; não verifica recuperação nem agenda retries.

<!-- reading-section: catalog -->
## Catálogo sintético e eventos gerados internamente

`Catalogo::exemplosSinteticos()` é vocabulário de exemplo, sem comprovar produtores implantados. A coluna de contexto lista campos opcionais aprovados; ausentes são omitidos.

| Código | Severidade / classificação | Contexto | Resultado fixo |
| --- | --- | --- | --- |
| `consumer.processing_started` | info / expected | attempt | unknown |
| `dependency.retry_scheduled` | notice / expected | attempt, retry_delay_ms, retry_scheduled (somente true) | retry_scheduled |
| `redis.connection_unavailable` | warning / transient_failure | attempt, duration_ms | unknown |
| `redis.connection_recovered` | info / confirmed_recovery | duration_ms | success |
| `rabbitmq.consumer_interrupted` | error / recoverable_error | attempt | unknown |
| `application.unexpected_failure` | error / unexpected_defect | duration_ms | unknown |
| `operation.retry_exhausted` | critical / operational_incident | attempt | retry_exhausted |

A taxonomia de exemplo define domain `messaging/application`, component `connection/consumer/runtime`, dependency `redis/rabbitmq`, operation `connect/consume/execute/publish/process/schedule_retry` e failure category `connection_unavailable/connection_interrupted/unexpected_failure/retry_exhausted`. Tags padrão estão em cada definição de `src/Aplicacao/Catalogo.php`; chamadores não podem substituí-las por valores conflitantes.

`library.unexpected_failure` é gerado somente pelo método explícito de falha inesperada. `library.transient_summary` é gerado pela agregação, sem resolução nesse catálogo. Resumo mantém severidade/tags/resultado/IDs de requisição e correlação originais, mas recebe UUID e timestamp próprios; `first_event_id` referencia a ocorrência original. Detalhes e contagens constam em [confiabilidade](../operations/reliability.md).

<!-- reading-section: schema -->
## Schema versão 1.1 e JSON Lines

`Dominio\Evento::paraArray` emite o contrato abaixo. `Infraestrutura\SerializadorJson::serializar` codifica Unicode/barras sem escape, preserva frações zero, substitui UTF-8 inválido e acrescenta exatamente uma quebra física de linha. Quebras em texto são escapes JSON. `tags` e `context` vazios são objetos JSON, não arrays.

| Campos | Tipo e significado |
| --- | --- |
| `schema_version` | string `1.1`; gravador aceita também registros de borda `1.0` |
| `event_id`, `timestamp` | UUID v4 do registrador; UTC `Y-m-dTH:i:s.uZ` |
| `project`, `service`, `environment` | strings configuradas do produtor |
| `severity`, `event_code`, `message`, `classification` | semântica do catálogo |
| `tags`, `context` | objeto controlado e objeto escalar sanitizado |
| `impact`, `action_required` | string anulável e booleano anulável da definição |
| `outcome` | string do enum, sem inferência pela severidade |
| `request_id`, `correlation_id` | identificadores anuláveis do chamador |
| `exception` | objeto diagnóstico opcional; omitido sem Throwable |
| `aggregation` | objeto de resumo opcional; omitido em eventos comuns |

`SerializadorJson($limiteBytes=65536)` aceita 4096–1048576 inclusive; terminador conta no limite em bytes. Eventos excessivos ou não serializáveis lançam `Dominio\FalhaGravacao`; erros JSON mantêm causa. Versão emitida e aceitação pelo gravador são contratos distintos: aceitar `1.0` nas bordas não converte registros nem garante suporte de todo consumidor a `1.1`.

Construir `Evento` diretamente contorna validação/sanitização do registrador. Gravadores serializam o objeto recebido; não são segunda validação de privacidade. Integrações comuns devem usar `Registrador` e definições revisadas.

<!-- reading-section: evidence -->
## Evidências e manutenção

Fontes: `src/Registrador.php`; `src/Dominio/{DefinicaoEvento,Tags,Severidade,Classificacao,Resultado,Evento}.php`; `src/Aplicacao/Catalogo.php`; `src/Infraestrutura/SerializadorJson.php`. Asserções existentes: `tests/Aplicacao/{CatalogoTest,RegistradorTest}.php`, `tests/Dominio/{EventoTest,TagsTest}.php`, `tests/Infraestrutura/SerializadorTest.php`. Resultados executados estão separados na verificação. Rever ambos os idiomas e leitores downstream quando parâmetros, enums, catálogo sintético, schema ou versões aceitas mudarem. Não foi executada matriz de pacotes publicados ou compatibilidade com coletor real.
