# Manutenção do Prometheus: política de timeout, ordem de estimativa e contexto do chamador

`prometheus/prometheus`: `5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4` → `80cd8d97bdfce88014a652d15723559d00a15902`

CANDIDATE_FOR_SOURCE_REVIEW · sem aprovação do proprietário, sem Gold, fora dos dados de treinamento.

## Uma revisão real da API, sem experimento de execução

Esta nota compara as revisões anterior e posterior selecionadas do Prometheus já exposto em desenvolvimento. O commit muda treze arquivos; dezoito arquivos selecionados de fontes, testes, documentação e licença foram preservados entre as duas revisões. Vinte e três citações nativas de declarações completas e quatro trechos de testes selecionados manualmente vinculam a análise às fontes. Não houve requisição efetiva, banco de dados, teste do projeto, benchmark ou compilação Go. As cláusulas pareadas foram escritas após a inspeção; não são previsões cegas nem resultado de um agente autônomo de manutenção.

## Timeout HTTP não é uma sobrescrita de limite de custo

Antes, `API.queryTimeout` rejeita uma solicitação positiva acima de um teto efetivo positivo. Depois, analisa o parâmetro e rejeita valores não positivos, mas não faz mais essa comparação com o teto. `max_query_duration` continua sendo uma sobrescrita diferente por consulta; quando a funcionalidade de custo está habilitada, a API posterior também rejeita explicitamente seus valores negativos. Com essa funcionalidade desabilitada, o extrator de opções selecionado ignora essas sobrescritas de custo. Depois desta revisão, os dois parâmetros não devem ser documentados como se compartilhassem a mesma regra de rejeição acima do teto.

## Aceitação na análise não desabilita prazos de execução

Um timeout HTTP positivo mais longo é aceito pela análise posterior; isso não promete execução ilimitada. O engine selecionado, que não mudou, ainda cria seu contexto de execução a partir de seu próprio timeout ou prazo armazenado. Pelo contrato padrão de contexto do Go, derivar um prazo posterior não estende um prazo anterior do contexto pai. O comportamento efetivo do servidor ainda depende da funcionalidade, da configuração e da implementação real do engine; o código de análise isolado não prova um teto global para colaboradores arbitrários.

## O estimador passa para antes da execução

Antes, um `Exec` bem-sucedido é seguido por `costComparison`. Depois, ambos os manipuladores registram `limitStart`, constroem a consulta, chamam `estimateForComparison` quando a comparação de custo está habilitada e só então chamam `Exec`. Mais tarde, `pendingCostComparison.finish` combina a estimativa com as estatísticas efetivas. Isso muda a orquestração do chamador embora o arquivo do engine seja idêntico byte a byte. A ordem posterior selecionada evita manter um resultado de consulta já concluído enquanto essa estimativa aguarda sua vaga; nenhuma melhoria de memória ou velocidade foi medida.

## Um início explícito difere de reiniciar o temporizador

Antes, o estimador deriva seu contexto de custo com `WithTimeout` quando começa. Depois, usa `WithDeadline` em `limitStart.Add(duration)`, com início registrado pelos manipuladores de consultas executadas antes da construção. Isso evita conceder uma nova duração completa à estimativa após construir a consulta. Timestamps da API e do engine são amostras separadas, e suas configurações podem diferir; esta revisão de fontes não iguala seus prazos exatos nem prova que todo colaborador pare na expiração.

## Um aviso de estimativa não garante sucesso da consulta

No caminho selecionado de execução bem-sucedida, `pendingCostComparison.finish` combina anotações do estimador e transforma um erro de estimativa em aviso sem comparação. Porém, `Exec` ainda roda com seu contexto de requisição e engine e pode falhar independentemente. Os retornos de erro de execução ocorrem antes dessa finalização e ali não combinam as anotações pendentes da estimativa. A declaração de teste alterada distingue uma falha de duração apenas da estimativa de um timeout ou cancelamento da requisição; a primeira pode preservar o sucesso nessa configuração de teste, que não instala o mesmo teto de duração no engine.

## A construção preserva categorias selecionadas de erro tipado

Antes, `queryConstructionError` trata especialmente um erro acima do teto e, nos demais casos, envolve o erro como parâmetro de consulta inválido. Depois, reconhece também `ErrQueryTimeout` e `ErrQueryCanceled` e delega esses casos ao `returnAPIError`, que não mudou. Isso não classifica todo erro bruto de contexto ou de um engine personalizado da mesma forma. A mudança na fonte sustenta documentar esses caminhos tipados selecionados; não é resultado observado de status HTTP.

## Funções chamadas inalteradas não implicam documentação inalterada

O arquivo do engine e as citações nativas completas de `queryCostCeilings`, `costRequested` e `returnAPIError` coincidem byte a byte entre essas revisões. Mesmo assim, seus chamadores mudam a validação de prazo, a ordem de estimativa e o encaminhamento de erros de construção. Cláusulas que descrevem essas políticas alteradas exigem `MODIFY`; referências de fonte também precisam mudar para um novo alvo. Não se deve inferir `NO-OP` do capítulo inteiro nem remover o capítulo apenas porque o auxiliar antigo `costComparison` desaparece e é substituído.

## A documentação existente mantém revisão delimitada

A comparação inicial preservou dezoito arquivos selecionados entre as revisões. Os rastreamentos posteriores H76–H79 agora abordam subtópicos selecionados de regras, estimativa remota, erros de duração e contagem de amostras com fontes congeladas separadamente. Não aprovam integralmente três páginas extensas nem estabelecem comportamento em execução. O inicializador de teste alterado fornece explicitamente `EnableQueryCost`; intenção escrita da configuração continua distinta de testes aprovados.

## Consultas de regras usam o engine configurado do servidor

Na conexão selecionada do servidor fora do modo agente, `rules.EngineQueryFunc` recebe o mesmo `queryEngine` cujas opções incluem `EnableQueryCost`. O callback de recarga aplica limites configurados apenas com essa funcionalidade habilitada. Regras de gravação e alerta invocam o callback de consulta fornecido; seu construtor passa opções nil, de modo que os padrões do engine selecionado mantêm os tetos do operador. Uma duração configurada não nula substitui o timeout de inicialização; zero mantém o valor de fallback. Isso rastreia o caminho padrão do chamador, não callbacks arbitrários injetados, modo agente ou execução observada de regras. [H76/R01–R18]

## Enumeração remota e amostragem de densidade são capacidades diferentes

O estimador selecionado abre o queryable comum para contar séries independentemente de seu `CostSamplingQueryable` opcional. Leitores remotos configurados fazem o fanout selecionado recusar a amostragem de densidade, enquanto a enumeração comum mantém um caminho de cliente remoto. Matchers remotos obrigatórios podem fazer um seletor específico retornar sem leitura pelo cliente. Sem amostrador, seletores com séries positivas usam o intervalo global de coleta fornecido e custo float `1.0` e adicionam `errCostSamplingFallback`. Porém, `Annotations.Add` usa `err.Error()` como chave: adições repetidas do mesmo fallback são deduplicadas. Não se deve prometer um aviso retornado separadamente identificável por seletor, tráfego efetivo de rede ou densidade precisa de histogramas. [H77/E01–E16]

## Um erro bruto de prazo pode não se tornar timeout tipado

O `contextErr` selecionado converte erros de contexto onde é chamado, mas a expansão de séries pode retornar um erro bruto de iterador ou contexto envolvido com `expanding series`. A recuperação preserva esse erro envolvido. `returnAPIError` reconhece `ErrQueryTimeout`, enquanto um prazo bruto envolvido sem esse tipo cai na classificação de execução. Assim, os status padrão diferem: timeout `503`, execução `422`; o `overrideErrorCode` opcional pode substituir os padrões. O contador selecionado de rejeições `max_duration` também exige timeout tipado e causa de duração de custo. São caminhos de fonte, não respostas HTTP observadas nem todos os casos de erro ou endpoint. [H78/T01–T12]

## Unidades de amostra do avaliador diferem de resultados e I/O físico

Avaliadores filhos selecionados compartilham `queryBudget`. Entrada float cobra uma unidade; entrada de histograma usa `HPoint.size()`, cuja fórmula selecionada é `(p.H.Size() + 8) / 16`. O consumo de subconsulta materializada passa um passo negativo para evitar nova cobrança desses pontos de entrada selecionados. Com o orçamento habilitado, a combinação selecionada também atribui trabalho filho fora das janelas do pai; um filho invariável no passo contribui leituras uma vez, mesmo quando as estatísticas de amostras totais se repetem. Esses ramos selecionados sustentam contagem de entrada do avaliador, não bytes transferidos, leituras físicas de armazenamento ou correção exaustiva do avaliador. [H79/S01–S13]

## FAQ

### Um timeout HTTP maior agora pode ignorar todo limite do servidor?

Não. A aceitação na análise difere dos limites selecionados do engine e do contexto pai. O engine inalterado ainda constrói um contexto de execução com limite; o comportamento efetivo exato exige considerar configuração e implementação do engine.

### timeout e max_query_duration são intercambiáveis?

Não. A análise posterior de timeout remove a rejeição acima do teto, mas continua exigindo valor positivo. Com a funcionalidade de custo habilitada, a sobrescrita mantém sua semântica de teto e ganha uma rejeição explícita de valor negativo na API; com a funcionalidade desabilitada, o extrator de opções selecionado ignora sobrescritas de custo. Não se deve aplicar silenciosamente a política de um parâmetro ao outro.

### Toda estimativa que falha deixa uma consulta bem-sucedida com aviso?

Não. A conversão em aviso ocorre após execução bem-sucedida. Cancelamento ou timeout da requisição ainda pode fazer a execução falhar, e o caminho de retorno de erro não chama a finalização da comparação pendente.

### A API e o engine agora compartilham um timestamp idêntico?

Isso não foi estabelecido. A API registra seu início antes da construção; o engine registra seu próprio prazo durante a construção. O cálculo explícito com início anterior restringe a estimativa, mas igualdade exata e tempo efetivo de parada não foram verificados.

### Um engine inalterado justifica manter todo parágrafo sobre o ciclo de vida?

Não. O chamador da API muda a ordem e o contexto de encaminhamento de erros em torno desse engine. Manter texto sobre a função chamada e modificar explicações sobre o chamador exige decisões separadas, com proveniência vinculada à revisão-alvo efetiva.

### Os testes ou a documentação existentes foram aprovados integralmente?

Não. Declarações de teste foram inspecionadas sem execução. Seis grupos iniciais de cláusulas e quatro subtópicos posteriores delimitados foram avaliados com limites explícitos; a aprovação integral das páginas continua não estabelecida. Esta nota tem revisão de fontes pelo mesmo agente, e não aprovação independente ou do proprietário.

### Uma chamada Add por seletor implica avisos retornados distintos?

Não. A mesma mensagem de erro de fallback é usada como chave do mapa, então adições duplicadas se condensam. A condição de séries positivas também importa; um seletor sem séries não entra nesse ramo de fallback. [H77/E02, E03, E15]

### Toda implementação de regras usa os limites inspecionados?

Isso não foi estabelecido. O rastreamento cobre a conexão padrão do servidor fora do modo agente e a funcionalidade de custo habilitada, não callbacks arbitrários de consulta injetados. [H76/R01–R18]

### Todo erro de duração é um timeout HTTP 503?

Não. Timeout tipado e erros brutos envolvidos de expansão podem seguir classificações diferentes, e um callback opcional pode substituir os status padrão. Nenhuma resposta foi medida. [H78/T01–T12]

### samplesRead mede bytes baixados do armazenamento remoto?

Essa afirmação não decorre da análise. Os contadores selecionados cobram unidades de entrada do avaliador e tamanho relativo de histogramas, com tratamento explícito de reutilização de resultados filhos; I/O físico está fora desta observação. [H79/S01–S13]

## Reprodução somente para leitura e referências às fontes

Uma comparação Git equivalente com revisões fixadas foi inspecionada. Este comando apenas exibe mudanças de fonte; não executa API, testes, armazenamento ou estimador.

```sh
git -c core.fsmonitor=false diff --no-ext-diff --no-renames 5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4 80cd8d97bdfce88014a652d15723559d00a15902 -- web/api/v1/api.go
```

[S1: after API.queryTimeout](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L919-L932)

[S2: after queryConstructionError](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L940-L951)

[S3: after API.estimateQueryCost](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L1002-L1022)

[S4: after API.queryCostCeilings](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L877-L889)

[S5: after API.estimateForComparison](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L966-L969)

[S6: after pendingCostComparison.finish](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L975-L997)

[S7: after API.costRequested](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L847-L860)

[S8: after returnAPIError](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L1371-L1399)

[S9: after API.query](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L625-L729)

[S10: after API.queryRange](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L1201-L1331)

[S11: after query.executionContext](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/promql/engine.go#L397-L406)

[S12: after Engine.newQuery](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/promql/engine.go#L877-L953)

[S13: after resolveDurationLimit](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/promql/engine.go#L990-L1002)

[S14: after Engine.Close](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/promql/engine.go#L744-L753)

[S15: before API.queryTimeout](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L919-L939)

[S16: before queryConstructionError](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L945-L950)

[S17: before API.estimateQueryCost](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L983-L1003)

[S18: before API.queryCostCeilings](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L872-L884)

[S19: before API.costComparison](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L957-L979)

[S20: before API.costRequested](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L842-L855)

[S21: before returnAPIError](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L1351-L1379)

[S22: before API.query](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L624-L727)

[S23: before API.queryRange](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L1182-L1311)

[S24: before func testEngine(](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api_test.go#L72-L91)

[S25: before func newQueryCostTestAPI(](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api_test.go#L5196-L5221)

[S26: after func newQueryCostTestAPI(](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api_test.go#L5219-L5252)

[S27: after func TestQueryCostEstimationQueueTimeout(](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api_test.go#L6116-L6160)

[R1: Go context deadline contract](https://pkg.go.dev/context#WithDeadline). Contrato primário atual da API; não é observação de execução do Prometheus.

A licença Apache-2.0 completa da raiz e os avisos dos arquivos foram preservados. Todos os artefatos da campanha permanecem material interno restrito de revisão, sem liberação geral por arquivo, para treinamento ou para publicação pública.
