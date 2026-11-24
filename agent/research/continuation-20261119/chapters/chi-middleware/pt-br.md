# Middlewares do chi: retorno de funções, trabalho adiado e propagação de panic

Estado: correção experimental escrita pelo Codex e revisada contra a fonte; aprovação humana pendente. O baseline foi gerado pelo agente local real. Este texto corrigido não foi fornecido ao baseline e não representa treinamento neural nem um manual publicado.

A revisão congelada do chi é `c64ed7d6635f33a8b2feaff7dcfa55677023ac7d`. Os contratos selecionados estão em `middleware/timeout.go` e `middleware/recoverer.go`. Os trechos exatos dos métodos, hashes das fontes e posições de linhas físicas acompanham este capítulo em `source-excerpts.json`.

## Construção e invocação são fases distintas

A declaração de `Timeout` retorna uma função com sintaxe `func(next http.Handler) http.Handler`. A chamada externa recebe uma duração e fornece essa função de middleware. A chamada da função retornada recebe o próximo handler e constrói `http.HandlerFunc(fn)`. O trabalho específico da requisição está no callback; retornar uma função literal não executa seu corpo.

Já `Recoverer` recebe o próximo handler em sua própria lista de parâmetros e retorna `http.HandlerFunc(fn)` diretamente. Dizer que ambas as funções externas simplesmente retornam um novo handler apaga a camada adicional de fábrica no primeiro contrato. O baseline neural de Timeout deixou essa distinção imprecisa. O perfil determinístico de sintaxe de retorno existente preserva a assinatura da função retornada e deixa explicitamente o corpo do callback sem análise; ele não pretende explicar todo o comportamento do middleware.

## Timeout: contexto derivado e verificação adiada do status

Dentro do callback de requisição, `context.WithTimeout(r.Context(), timeout)` produz o contexto e a função de cancelamento. O callback registra uma função adiada. Essa função chama primeiro `cancel()` e depois verifica `ctx.Err() == context.DeadlineExceeded`. Somente esse ramo de igualdade chama `w.WriteHeader(http.StatusGatewayTimeout)`.

Após registrar o defer, o callback atribui `r = r.WithContext(ctx)` e invoca `next.ServeHTTP(w, r)`. A chamada está escrita como uma chamada síncrona normal. O corpo selecionado não contém uma goroutine independente, uma goroutine de resposta por temporizador ou um select que interrompa à força o próximo handler. A propagação de contexto permite que o próximo handler acesse o contexto derivado; isso não prova que ele o observará ou respeitará.

A operação de status está no corpo adiado. Descrever a implementação como uma resposta incondicional que chega imediatamente quando um prazo vence acrescentaria um comportamento ausente dessa fonte. O código mostrado escreve um status sob uma condição específica; não constrói um corpo de resposta de timeout nem prova o que um cliente recebe após outras escritas da resposta. O comportamento das implementações de contexto e de response writer permanece fora desses métodos selecionados.

A ordem entre o cancelamento e a consulta do erro do contexto faz parte do contrato. Uma correção deve preservá-la, em vez de substituí-la pela afirmação genérica de que um timeout retorna um erro. O callback selecionado também não retorna um valor de erro Go a um chamador. Sua operação sobre a resposta e o erro do contexto consultado têm papéis distintos.

## Recoverer: inspeção adiada após o início da chamada ao próximo handler

O callback de requisição registra uma função adiada e depois invoca `next.ServeHTTP(w, r)`. Dentro da função adiada, `recover()` fornece o valor verificado por `rvr != nil`. Quando essa condição é falsa, o ramo selecionado de recuperação não executa. Quando é verdadeira, o primeiro caso especial é `rvr == http.ErrAbortHandler`; esse ramo executa `panic(rvr)` antes da seleção posterior de logging ou da escrita do status.

Para outro valor recuperado não nulo, o código atribui `logEntry := GetLogEntry(r)`. Uma entrada não nula leva a `logEntry.Panic(rvr, debug.Stack())`; caso contrário, chama `PrintPrettyStack(rvr)`. O getter e o método de logging são chamadas distintas com papéis diferentes. Esses trechos não mostram um uso adicional da entrada para registrar outros eventos do pipeline, nem declaram uma variável local chamada panic.

A condição final de resposta é `r.Header.Get("Connection") != "Upgrade"`. Somente esse ramo invoca `w.WriteHeader(http.StatusInternalServerError)`. A comparação escrita trata do valor retornado pelo header e da string exata mostrada. Isso não evidencia um classificador geral que reconheça todas as representações possíveis de uma conexão atualizada. O código também não promete substituir o corpo da resposta nem garantir o sucesso de toda escrita.

O baseline neural continha uma afirmação crítica de ordem invertida: dizia que o tratamento adiado de panic ocorre antes da chamada à próxima função. Uma instrução defer registra trabalho adiado; ela não executa imediatamente o corpo da função adiada. Aqui, a chamada direta ao próximo handler vem após o registro. A recuperação está vinculada à execução e ao desenrolar de panic desse callback; o código selecionado não estabelece proteção para trabalho arbitrário em outra goroutine.

## Por que o guard por palavras-chave foi rejeitado

Uma proposta de guard textual reconheceu a frase observada sobre tratar um panic antes do próximo handler. Ela também correspondeu a uma fonte sintética válida na qual uma função interna invocada imediatamente possui o defer e conclui a recuperação antes de a função externa chamar o próximo handler. Os dois trechos contêm defer e uma chamada ao próximo handler, mas os escopos das funções envolventes são diferentes.

Por isso, o candidato foi rejeitado sem alterar a validação de produção. Uma futura prova delimitada por AST precisaria identificar o callback envolvente exato, a chamada adiada e seus argumentos, além da chamada direta cuja ordem está sendo descrita. Encontrar algumas palavras na prosa e na fonte é insuficiente. O experimento rejeitado está preservado em `../../defer-guard-candidate.json`.

## Limites da revisão e autoridade da fonte

As respostas completas do baseline foram revisadas nas duas línguas. A resposta de Recoverer também inventou outros eventos de logging e repetiu descrições de variáveis sem sustentação. A aceitação pelo writer não foi tratada como aceitação factual. O capítulo corrigido preserva observações válidas da fonte e evita inferir implementações de auxiliares, resultados garantidos ao cliente ou segurança de concorrência.

A regra da linguagem sobre invocação adiada foi conferida na [especificação de Go](https://go.dev/ref/spec#Defer_statements). As implementações do projeto estão em [timeout.go](https://github.com/go-chi/chi/blob/c64ed7d6635f33a8b2feaff7dcfa55677023ac7d/middleware/timeout.go) e [recoverer.go](https://github.com/go-chi/chi/blob/c64ed7d6635f33a8b2feaff7dcfa55677023ac7d/middleware/recoverer.go), na revisão congelada. A procedência da licença upstream está preservada com os snapshots privados da fonte. Nenhum programa upstream ou servidor desses middlewares foi executado para esta revisão.
