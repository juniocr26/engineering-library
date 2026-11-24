# Throttling: orçamentos de admissão, espera e devolução adiada

Correção escrita pelo Codex e revisada contra a fonte; pendente de aprovação do proprietário.

chi revision c64ed7d6635f33a8b2feaff7dcfa55677023ac7d; middleware/throttle.go. Actual local-agent baseline: chi-throttle-workflow. [Exact source evidence](../references/ref-fe7353b4cadf7acc814c.md).

## A construção valida dois intervalos diferentes

O baseline real do agente local disse que o limite de processamento deve ser maior que zero, o que corresponde à primeira guarda. Também disse que o limite de backlog deve ser positivo. Essa segunda afirmação segue a mensagem de pânico, em vez da condição: a guarda escrita é `opts.BacklogLimit < 0`. Zero é permitido por essa guarda. Trata-se de erro crítico de fronteira repetido em inglês e português, embora a resposta cite os dois IDs de evidência selecionados.

A função selecionada primeiro executa panic quando `opts.Limit < 1` e então executa panic para um limite negativo de backlog. Copia o status configurado e substitui por `http.StatusTooManyRequests` somente quando esse status é zero. As verificações mostradas não validam toda capacidade, duração ou condição de overflow de inteiros concebível. Um chamador não pode inferir validação completa da configuração apenas pelos dois ramos explícitos de pânico.

## Dois orçamentos de canais são compartilhados pelo middleware retornado

O throttler local possui um canal de tokens de processamento com capacidade `opts.Limit` e um canal de tokens de backlog com capacidade `opts.Limit+opts.BacklogLimit`. O laço de inicialização preenche o canal de processamento para as primeiras entradas correspondentes ao limite e preenche o canal de backlog para toda a contagem combinada. Esses canais têm papéis diferentes: a admissão consome um token de backlog, enquanto invocar o próximo handler também exige um token de processamento.

A função externa retorna `func(next http.Handler) http.Handler`. Aplicar essa função retornada produz `http.HandlerFunc(fn)`; isso não executa por si só uma requisição. O throttler capturado e seus canais pertencem a essa instância construída de middleware. A implementação selecionada não contém identificador de usuário ou bucket de taxa por usuário. Seu temporizador de espera não deve ser confundido com uma cota fixa de requisições por janela de tempo.

## Admissão, processamento imediato e caminho de espera

O callback de requisição obtém `r.Context()` e entra em um select externo. Seu caso de contexto concluído chama o helper de cabeçalho com true e então chama `http.Error` com o texto de cancelamento e o status configurado. Seu caso default chama o helper com false e relata capacidade excedida. Adquirir um token de backlog, por sua vez, registra um envio adiado que devolve esse token quando o trabalho adiado do callback é executado.

Após a admissão, um select interno primeiro tenta receber um token de processamento sem esperar. No sucesso, registra uma devolução adiada do token de processamento, chama `next.ServeHTTP(w, r)` e retorna. Esse caminho não cria o temporizador posterior. Se esse recebimento imediato não está disponível, o ramo default prossegue para `time.NewTimer(t.backlogTimeout)` e um select separado de espera.

O select de espera distingue expiração do temporizador, conclusão do contexto e recebimento de token de processamento. A expiração relata timeout com false passado ao helper de cabeçalho. A conclusão do contexto para explicitamente o temporizador e relata cancelamento com true. Receber um token de processamento agenda um defer que para o temporizador e devolve o token de processamento, e então chama o próximo handler. O defer do token de backlog continua fazendo parte do caminho de saída do callback envolvente.

## A devolução adiada não interrompe o próximo handler

O envio do token de processamento está escrito dentro de uma função adiada, enquanto a invocação do próximo handler é uma chamada síncrona direta. Descrever o token como devolvido antes de o handler executar inverte a ordem mostrada. As duas chamadas de limpeza são registradas antes da chamada ao próximo handler. No retorno normal dele, a limpeza de processamento registrada depois executa antes da limpeza de backlog registrada antes, quando o callback envolvente retorna. Essa é uma descrição da fonte sobre agendamento da limpeza, não uma medição de conclusão de requisições concorrentes.

O temporizador governa a espera por um token de processamento. O código mostrado do select de temporizador não continua executando ao lado do próximo handler depois que esse token é adquirido. Portanto, não estabelece interrupção forçada de um handler bloqueado. Da mesma forma, se vários casos de select estão prontos, essa fonte não estabelece preferência determinística pelo cancelamento em vez da admissão. O código contém ramos de cancelamento, não garantia universal de que toda requisição já cancelada seja rejeitada antes de qualquer chamada ao handler.

## O helper de cabeçalho de retry tem contrato condicional próprio

O helper primeiro retorna quando o callback de retry configurado é nulo. Caso contrário, chama esse callback com o booleano de contexto concluído recebido. Divide a duração retornada por `time.Second`, limita uma duração negativa a zero segundos e incrementa um resultado não negativo quando resta uma fração de segundo. Então define `Retry-After` usando uma string decimal. Segundos positivos inteiros exatos não são aumentados pelo ramo de resto.

Essas operações descrevem o helper quando suas chamadas concluem normalmente; não provam que um callback configurado arbitrário não possa entrar em pânico ou bloquear. O capítulo expande as observações úteis do baseline sobre cabeçalho para o fluxo envolvente de admissão e devolução, e corrige a fronteira de backlog zero. Os trechos adicionais de opções e campos de estado foram lidos para esta correção, em vez de serem atribuídos falsamente ao contexto original selecionado do modelo. Este candidato bilíngue revisado contra a fonte aguarda aprovação do proprietário e não foi publicado nem promovido a gold de treinamento.

## Configuração no ponto de entrada real

Os wrappers e o construtor por opções não possuem comportamento padrão idêntico. O arquivo congelado completo mostra que `Throttle` fornece explicitamente um timeout de backlog de 60 segundos. `ThrottleBacklog` encaminha seu argumento de duração. `ThrottleWithOpts` copia `opts.BacklogTimeout` diretamente; essa função não substitui zero pelo padrão daquele wrapper.

| Opção | Regra sustentada pela fonte em ThrottleWithOpts |
| --- | --- |
| Limit | Valores abaixo de 1 executam panic antes da criação dos canais. |
| BacklogLimit | Valores negativos executam panic; zero passa por essa guarda. |
| BacklogTimeout | Copiado diretamente; não há guarda de positividade mostrada. |
| StatusCode | Zero torna-se a constante de excesso de requisições; outro valor é copiado. |
| RetryAfterFn | Nil pula o corpo do helper de cabeçalho; outro valor é chamado nos caminhos de rejeição. |

## FAQ de engenharia

<!-- reading-section: faq:concurrency-not-per-user-rate -->
### Este é um limite de taxa de requisições por usuário?

Os canais capturados limitam admissão e processamento concorrentes para a instância do middleware. Não há identificador por usuário, mapa de buckets por usuário ou reposição periódica nesta implementação selecionada. O temporizador limita a espera por um token de processamento.

<!-- reading-section: faq:zero-backlog -->
### Backlog zero desativa todas as requisições?

Não. Com um limite positivo válido, a capacidade do canal de backlog é a soma desse limite com zero. Backlog zero passa pela guarda de validação explícita; tokens de admissão e processamento continuam com papéis distintos.

<!-- reading-section: faq:retry-header-not-execution -->
### Definir RetryAfterFn faz a requisição ser tentada novamente automaticamente?

O helper define `Retry-After` quando seu callback conclui normalmente. Não invoca o próximo handler novamente nem implementa retry no cliente. Durações negativas tornam-se zero; uma fração positiva de segundo é arredondada para cima, enquanto um segundo inteiro exato é preservado.

A ordem da linguagem e os limites dos casos prontos seguem as [regras de defer de Go](https://go.dev/ref/spec#Defer_statements) e as [regras de select](https://go.dev/ref/spec#Select_statements), reconferidas nesta revisão. Nenhum middleware upstream foi executado.
