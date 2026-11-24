# Prometheus: construção de consultas, cancelamento e duração dos recursos

`prometheus/prometheus` · `b2a602494b65bda38316eabaef7e0d834a6814dd`

CANDIDATE_FOR_SOURCE_REVIEW · sem aprovação do proprietário, sem Gold, fora dos dados de treinamento.

## Escopo e verificação

Este capítulo acompanha a revisão selecionada do Prometheus na construção de consultas PromQL, execução, cancelamento, liberação do leitor e finalização de resultados HTTP. O repositório já foi exposto em desenvolvimento; seus dezesseis registros anteriores de construção e bookkeeping pertencem a outro escopo de avaliação. A documentação foi escrita manualmente a partir das fontes, sem geração por modelo, consulta efetiva, banco de dados, inicialização de armazenamento, testes do projeto ou compilação Go. Trinta e três declarações completas foram extraídas pela ferramenta nativa de sintaxe Go com integridade verificada; os trechos abaixo foram selecionados separadamente, inclusive partes de funções maiores. Nenhum desses tipos de citação prova comportamento em execução.

## Interfaces de consulta separam responsabilidades

`QueryEngine` declara construtores instantâneo e por intervalo que retornam `Query` e um erro. `Query` declara separadamente `Exec`, `Close`, `Cancel`, `Statement`, `Stats` e `String`. O tipo concreto `query` armazena um provedor consultável, instrução analisada, estatísticas, matriz de resultado, função de cancelamento e referência ao engine. O comentário da interface permite executar apenas uma vez; o corpo de encaminhamento de `Exec` inspecionado não é uma guarda de uso único observada em execução. Esta inspeção não garante reutilização nem acesso concorrente.

[S1](#s1) [S2](#s2)

## A construção precede a avaliação

Ambos os construtores públicos chamam primeiro `newQuery`, depois entram na fila de consultas ativas, analisam e validam a expressão e fazem seu pré-processamento na instrução de avaliação. O caminho instantâneo usa início e fim iguais e intervalo zero. O caminho por intervalo rejeita ainda tipos de expressão diferentes de escalar ou vetor instantâneo. Esses caminhos selecionados não chamam `Exec` da consulta; também não foram estabelecidos como funções puras, pois colaboradores de análise, opções, rastreamento e encapsulamento podem ter efeitos. A construção pode falhar antes de retornar uma consulta.

[S4](#s4) [S5](#s5) [S6](#s6)

## Estado por consulta e política opcional de custo

`newQuery` fornece opções padrão quando elas faltam, escolhe a política de lookback e de timestamp inicial e cria o estado da instrução e das estatísticas. A conversão opcional de histogramas nativos encapsula o provedor consultável. Quando a verificação de custo está habilitada, lê tetos definidos pelo operador e sobrescritas opcionais por consulta, resolve limites efetivos e registra um prazo durante a construção. Sem essa funcionalidade, esse bloco não preenche os campos selecionados de limite de custo. Isso não especifica completamente todas as funcionalidades nem todos os encapsulamentos de armazenamento.

[S6](#s6)

## Uma solicitação zero herda o teto

`resolveUintLimit` retorna o teto quando o valor solicitado é zero. Caso contrário, um teto zero ou uma solicitação que não exceda o teto admite a solicitação; uma solicitação excessiva retorna `ErrLimitAboveCeiling`, em vez de reduzi-la silenciosamente ao teto. Portanto, solicitar zero não necessariamente desabilita um limite finito. `resolveDurationLimit` usa comparações análogas com durações não positivas. Na configuração de duração, um teto positivo configurado pode substituir o teto do timeout de inicialização; seria incorreto dizer genericamente que toda sobrescrita de duração apenas reduz esse timeout.

[S6](#s6) [S7](#s7)

## A execução cria seu contexto de cancelamento

`executionContext` usa o timeout do engine quando não há prazo armazenado na consulta; caso contrário, usa o prazo armazenado e uma causa explícita, escolhendo a causa de custo quando a duração máxima efetiva é positiva. Com a verificação de custo, os construtores usam e cancelam um contexto local, mantendo o prazo absoluto no estado da consulta. Depois, `Engine.exec` cria um contexto de execução, atribui sua função de cancelamento à consulta e adia seu cancelamento. Isso preserva uma fronteira de prazo na fonte; não mede latência de cancelamento nem estabelece interrupção imediata de colaboradores arbitrários.

[S3](#s3) [S4](#s4) [S5](#s5) [S8](#s8)

## Cancel sinaliza; não devolve buffers

`query.Cancel` invoca a função de cancelamento armazenada somente quando ela não é nula. Os construtores de consulta selecionados não inicializam essa função; a atribuição ocorre em `Engine.exec`. O teste de cancelamento inspecionado espera que cancelar antes da execução não tenha efeito, usando uma instrução sintética de teste. Esse caminho de fonte não mostra o cancelamento aguardando a consulta parar, devolvendo fatias do resultado ou tornando seguro o uso concorrente sem sincronização.

[S2](#s2) [S6](#s6) [S8](#s8) [S15](#s15) [S16](#s16)

## A admissão na fila tem uma função própria de liberação

`queueActive` retorna uma função de liberação sem ação quando não existe rastreador. Caso contrário, chama `Insert` do rastreador; em caso de sucesso, retorna uma função que chama `Delete` com o índice recebido. Os construtores e a execução adiam a liberação após admissão bem-sucedida. O ramo selecionado sem ação não prova um limite global de concorrência, e a fonte não estabelece que um rastreador arbitrário não possa bloquear ou falhar. Liberar a fila difere de devolver os buffers de resultado.

[S4](#s4) [S5](#s5) [S9](#s9) [S10](#s10)

## A execução encaminha valores, erros e avisos

`query.Exec` delega ao engine e constrói um `Result` com campos separados de erro, valor e avisos. `Engine.exec` registra métricas e tempos, admite a consulta, verifica seu contexto e despacha uma instrução de avaliação ou uma instrução de teste. Tipos de instrução não tratados chegam a um pânico explícito nessa função selecionada. O encaminhamento não promete que toda falha produza um valor sem erro nem que avisos desapareçam quando há erro. Os acessores de `Result` rejeitam um erro existente antes de verificar o tipo de valor solicitado.

[S2](#s2) [S8](#s8) [S9](#s9) [S23](#s23)

## O leitor de armazenamento tem duração própria

`execEvalStmt` calcula os limites temporais e solicita um `Querier` ao provedor consultável. Um erro retornado causa saída antes de instalar o fechamento adiado; após aquisição bem-sucedida, adia `querier.Close()` e avalia com esse leitor. A chamada adiada selecionada não propaga explicitamente um erro retornado pelo fechamento. A interface de armazenamento inclui `Close() error` por `LabelQuerier`. Essa liberação do leitor não é a operação posterior `query.Close` sobre fatias de resultado; o comportamento de provedores arbitrários não foi executado nem certificado.

[S11](#s11) [S21](#s21) [S22](#s22)

## A posse do resultado pode sobreviver a um erro tardio

O caminho de avaliação instantânea armazena uma matriz antes de convertê-la em vetor ou escalar ou de retornar uma matriz. Um resultado textual retorna antes, sem essa atribuição da matriz. O caminho por intervalo armazena sua matriz antes de uma verificação posterior de contexto e da ordenação. Assim, um erro retornado após essa atribuição não prova que a consulta esteja sem buffers de resultado. O código selecionado e o chamador HTTP mantêm a liberação separada do sucesso. Esses caminhos não provam que todo erro deixe buffers alocados nem que todo valor retornado seja uma cópia profunda independente.

[S12](#s12) [S19](#s19) [S20](#s20)

## Close devolve fatias de pontos aos pools

`query.Close` percorre a matriz armazenada e passa fatias de pontos de valores numéricos e de histogramas aos auxiliares dos respectivos pools. Esses auxiliares ignoram fatias nulas e, nos outros casos, devolvem ao pool uma visão com comprimento zero. O corpo selecionado não chama `Cancel`, não aguarda a execução, não fecha um leitor de armazenamento, não limpa a matriz nem protege contra chamadas repetidas. Portanto, este capítulo não promete idempotência, liberação imediata de memória ao sistema operacional, reutilização segura de resultados após fechar ou segurança concorrente.

[S2](#s2) [S13](#s13)

## A finalização HTTP acompanha o tratamento do resultado

Os manipuladores instantâneo e por intervalo selecionados instalam uma alternativa adiada após construir a consulta com sucesso: fechar a consulta se o resultado nomeado não tiver finalizador. Retornos normais de erro de execução e de sucesso carregam, em vez disso, `qry.Close` como finalizador do resultado. O encapsulamento registrado adia esse finalizador antes de chamar o caminho de tratamento de resposta ou erro. Portanto, os manipuladores não fecham simplesmente toda consulta antes de retornar seu valor ao chamador. A alternativa também cobre o desenrolamento sem finalizador atribuído; não prova recuperação de todo pânico nem conclusão de todo colaborador. Nenhuma requisição HTTP foi feita.

[S17](#s17) [S18](#s18) [S19](#s19) [S20](#s20)

## A validação HTTP não é um teorema sobre todo o engine

O manipulador HTTP por intervalo verifica fim anterior ao início, passo não positivo e quociente de resolução maior que 11.000 antes de construir uma consulta. São guardas selecionadas da camada de API; não se deve atribuir silenciosamente todas elas a `Engine.NewRangeQuery`. Da mesma forma, os finalizadores seguem o contrato deste encapsulamento HTTP registrado, e não de todo consumidor direto possível de `QueryEngine`. Não se afirma garantia global de validade do intervalo, limite de requisição ou comportamento de chamadores externos.

[S5](#s5) [S18](#s18) [S20](#s20)

## Fechar o engine é uma terceira operação

`Engine.Close` retorna nil para um engine nulo; caso contrário, fecha o rastreador de consultas ativas quando ele existe, retornando seu erro, ou retorna nil sem rastreador. Seu comentário exige que os chamadores garantam que o engine não esteja mais em uso. O corpo selecionado não é um laço que cancela todas as consultas ativas, libera a matriz de cada consulta ou fecha cada leitor de armazenamento. Não estabelece encerramento seguro enquanto há consultas ativas nem que o logger de consultas seja fechado por esse método.

[S14](#s14) [S25](#s25)

## Recuperação de erros e testes têm limites explícitos

`evaluator.Eval` adia um tratador de recuperação que converte valores selecionados de pânico no estado retornado de erro e avisos. Esse escopo não se estende automaticamente à construção, a todo ramo de instrução do engine, ao tratamento da resposta ou aos próprios colaboradores do tratador de recuperação. Os testes inspecionados de timeout e cancelamento usam `NewTestQuery`, que injeta um `parser.TestStmt`; o teste de cancelamento sincroniza canais e verifica separadamente o cancelamento antes de iniciar. Esses corpos foram inspecionados e analisados sintaticamente, sem execução, e não são evidência de latência real de cancelamento do armazenamento nem de testes de integração aprovados.

[S15](#s15) [S16](#s16) [S24](#s24)

## FAQ

### Cancel e Close são equivalentes?

Não. `Cancel` chama uma função de cancelamento instalada; `Close` devolve fatias da matriz armazenada aos pools. Nenhum dos corpos selecionados fornece a outra operação, e sinalizar cancelamento não é uma espera observada pela conclusão.

[S2](#s2) [S13](#s13)

### Cancelar antes da execução cancela permanentemente uma consulta nova?

Não no caminho selecionado de construção e cancelamento. O campo de cancelamento começa sem função atribuída e recebe seu valor na execução pelo engine; o teste sintético inspecionado espera que cancelar antes de executar não tenha efeito. Isso não é uma garantia de temporização concorrente para todo chamador.

[S2](#s2) [S6](#s6) [S8](#s8) [S16](#s16)

### Solicitar limite de custo zero desabilita um limite finito do operador?

Não. `resolveUintLimit` retorna o teto do operador quando a solicitação é zero. Uma solicitação positiva acima de um teto finito produz erro em vez de redução silenciosa ao teto. A política selecionada de custo por consulta depende da funcionalidade de custo.

[S6](#s6) [S7](#s7)

### Uma consulta com erro ainda pode exigir liberação do resultado?

Sim, a fonte permite isso: o caminho por intervalo atribui sua matriz antes de uma verificação posterior de erro de contexto. O resultado HTTP de erro de execução ainda carrega o finalizador de fechamento. Isso não significa que toda falha aloque buffers nem estabelece um vazamento observado em execução.

[S12](#s12) [S19](#s19) [S20](#s20)

### O manipulador HTTP de consulta precisa fechar antes de retornar seu resultado?

Os caminhos normais selecionados de sucesso e erro transferem `qry.Close` como finalizador, e o encapsulamento registrado o adia em torno do tratamento da resposta. A alternativa do manipulador fecha somente quando seu resultado nomeado não tem finalizador. Substituir isso por liberação antecipada incondicional descartaria essa distinção de posse; nenhuma alteração de código desse tipo foi feita.

[S17](#s17) [S18](#s18) [S19](#s19) [S20](#s20)

### Engine.Close garante que todo trabalho ativo tenha parado?

Essa garantia não foi estabelecida. O método fecha o rastreador ativo quando presente e exige que o engine não esteja mais em uso. Cancelamento por consulta, devolução de resultados aos pools e liberação do leitor são responsabilidades separadas.

[S2](#s2) [S11](#s11) [S14](#s14)

## Exemplo de reprodução somente para leitura

A recuperação Git equivalente com revisão fixada foi executada na aquisição. No checkout público do Prometheus, este comando apenas exibe fontes; não inicia serviço, avalia PromQL ou acessa armazenamento. As observações do parser nativo são apenas sintáticas e estão arquivadas separadamente com requisições, respostas e identidade do produtor.

```sh
git -c core.fsmonitor=false show b2a602494b65bda38316eabaef7e0d834a6814dd:promql/engine.go
```

## Referências às fontes, direitos e limites

<a id="s1"></a> [S1: promql/engine.go:165–196](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L165-L196)

<a id="s2"></a> [S2: promql/engine.go:313–393](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L313-L393)

<a id="s3"></a> [S3: promql/engine.go:397–434](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L397-L434)

<a id="s4"></a> [S4: promql/engine.go:788–831](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L788-L831)

<a id="s5"></a> [S5: promql/engine.go:835–881](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L835-L881)

<a id="s6"></a> [S6: promql/engine.go:886–968](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L886-L968)

<a id="s7"></a> [S7: promql/engine.go:976–1017](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L976-L1017)

<a id="s8"></a> [S8: promql/engine.go:1091–1146](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L1091-L1146)

<a id="s9"></a> [S9: promql/engine.go:1148–1183](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L1148-L1183)

<a id="s10"></a> [S10: promql/engine.go:1208–1219](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L1208-L1219)

<a id="s11"></a> [S11: promql/engine.go:1257–1315](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L1257-L1315)

<a id="s12"></a> [S12: promql/engine.go:1315–1397](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L1315-L1397)

<a id="s13"></a> [S13: promql/engine.go:3438–3462](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L3438-L3462)

<a id="s14"></a> [S14: promql/engine.go:750–762](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L750-L762)

<a id="s15"></a> [S15: promql/engine.go:1075–1085](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L1075-L1085)

<a id="s16"></a> [S16: promql/engine_test.go:159–226](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine_test.go#L159-L226)

<a id="s17"></a> [S17: web/api/v1/api.go:214–221](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/web/api/v1/api.go#L214-L221)

<a id="s18"></a> [S18: web/api/v1/api.go:443–465](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/web/api/v1/api.go#L443-L465)

<a id="s19"></a> [S19: web/api/v1/api.go:625–729](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/web/api/v1/api.go#L625-L729)

<a id="s20"></a> [S20: web/api/v1/api.go:1201–1331](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/web/api/v1/api.go#L1201-L1331)

<a id="s21"></a> [S21: storage/interface.go:109–139](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/storage/interface.go#L109-L139)

<a id="s22"></a> [S22: storage/interface.go:191–206](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/storage/interface.go#L191-L206)

<a id="s23"></a> [S23: promql/value.go:365–409](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/value.go#L365-L409)

<a id="s24"></a> [S24: promql/engine.go:1754–1787](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L1754-L1787)

<a id="s25"></a> [S25: promql/engine_test.go:5552–5573](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine_test.go#L5552-L5573)

A licença Apache-2.0 completa da raiz e os avisos originais dos arquivos foram preservados com as fontes. Isso não representa liberação geral por arquivo, para treinamento ou para publicação pública. Os artefatos da campanha permanecem material interno restrito de revisão. Nenhum dado ou fonte privada atual do Viva Bem foi usado como entrada de modelo.
