# Política dinâmica de novas tentativas: padrões, guardas de deadline e direção do intervalo

Correção escrita pelo Codex e revisada contra a fonte, pendente de aprovação do proprietário. Revisão congelada do Temporal SDK 7e0d845246d36fc7f62ade2af885554f94c29db9. Baselines reais: sdk-retry-function, sdk-retry-with-constants e sdk-contiguous-contract. Evidência ampliada: [trechos da fonte](source-excerpts.json). Nenhuma aplicação do SDK foi compilada ou executada.

A interpretação condicional da função predeclarada segue a [definição da linguagem Go](https://go.dev/ref/spec#Min_and_max).

## Uma política é construída antes de qualquer nova tentativa

A função `createDynamicServiceRetryPolicy` recebe ctx com o tipo escrito `context.Context` e retorna `backoff.RetryPolicy`. Seu corpo constrói e configura um objeto de política. Não contém callback de operação, espera, laço de tentativas nem invocação de um retrier. Uma afirmação sobre o comportamento posterior das novas tentativas exige, portanto, código de outro consumidor. Os baselines preservados do agente local misturaram configuração e execução, e uma resposta posterior interpretou incorretamente tanto a aritmética dos intervalos quanto as guardas do deadline.

Esta correção acrescenta explicitamente o construtor da política e os setters da mesma revisão congelada do SDK. A evidência adicional sustenta a passagem da configuração, mas não torna retroativamente correta uma afirmação anterior do modelo sem suporte. A implementação continua sendo documentação revisada contra a fonte, não uma execução medida do SDK nem melhoria de pesos neurais.

## As constantes divergem de um comentário da fonte

O intervalo inicial declarado é `200 * time.Millisecond`. O intervalo padrão de expiração declarado é `60 * time.Second`, e a constante de coeficiente é 2. O comentário explicativo próximo menciona 20ms, mas a atribuição usada pelo corpo referencia a constante declarada de 200 milissegundos. Um comentário pode ser contexto útil e ainda divergir da implementação. Copiar seu número menor perde o contrato literal.

A função primeiro atribui a constante de expiração a `timeout`. Não começa extraindo uma duração de um deadline incondicional do contexto. Inicializar `timeout`, decidir se ele será substituído e configurar a política resultante são três passos separados. Uma descrição completa precisa preservar tanto o caminho padrão quanto o caminho dependente do contexto.

## O ramo de deadline não calcula o mínimo com sessenta segundos

A guarda externa é `ctx != nil`. Dentro dela, o código obtém now com `time.Now()` e depois obtém expiration e ok de `ctx.Deadline()`. A substituição ocorre apenas quando `ok && expiration.After(now)`. Esse ramo atribui `expiration.Sub(now)` a `timeout`. Deadline ausente ou que não satisfaz o teste de futuro estrito deixa a duração inicializada sem alteração.

Não há comparação escolhendo o mais próximo entre esse deadline futuro e o padrão de sessenta segundos. Na interpretação comum das operações de tempo fornecidas, um deadline futuro mais distante que sessenta segundos pode, portanto, produzir duração configurada maior. A fonte não promete que toda implementação não nula do contexto conclua sua chamada Deadline com sucesso. A guarda é uma comparação escrita de interface, não prova de segurança para todas as implementações com ponteiro nulo tipado ou métodos arbitrários.

## Registre a expressão de máximo sem inverter sua direção

As atribuições seguintes definem `initialInterval` a partir da constante de intervalo inicial e `maximumInterval` a partir de `max(timeout/10, retryServiceOperationInitialInterval)`. O segundo operando é a mesma constante declarada de intervalo inicial. Não é um literal de vinte milissegundos. Sob o vínculo de `max` como função predeclarada do Go, a expressão escolhe o maior operando: o intervalo inicial funciona como piso desse valor calculado de configuração, em vez de teto para `timeout/10`. Na interpretação comum de duração, o padrão de sessenta segundos produz seis segundos nessa expressão.

A palavra `max` continua sendo um identificador cujo vínculo importa. O censo anterior sem filtragem recusou uma conclusão sobre o vínculo porque fontes importadas de time incluíam um pacote gerador ignorado. Um experimento opcional posterior com `go/build` inspecionou todos os 157 arquivos Go imediatos do pacote do SDK e censos completos dos três pacotes importados. Sob perfis explícitos Darwin/arm64 e Linux/arm64, 78 arquivos comuns do SDK estão ativos; a seleção oficial de build exclui o gerador, enquanto os nomes declarados reais dos imports e as declarações do pacote e locais deixam o nome simples sem sombreamento léxico. O [recibo de vínculo](../../go-build-binding-evaluation.json) e o [censo de fontes](../../go-build-binding-source-census.json) preservam a prova. Isso sustenta a interpretação predeclarada sob esses censos completos fornecidos e um build válido do pacote. Não prova verificação de tipos nem comportamento em execução, e o parser sintático de produção e o roteamento padrão do agente permanecem sem alteração.

## A sequência de setters armazena configuração

O corpo chama `backoff.NewExponentialRetryPolicy(initialInterval)`, depois `SetBackoffCoefficient`, `SetMaximumInterval` e `SetExpirationInterval` nessa ordem e, por fim, retorna policy. O construtor fornecido inicializa um ponteiro `ExponentialRetryPolicy` usando o argumento e padrões nomeados para outros campos. Os três setters fornecidos atribuem seus respectivos argumentos a campos e não têm resultado de retorno. Seus corpos não executam a operação, não limitam a duração recebida nem impõem um deadline de relógio.

O argumento externo de coeficiente vem da constante 2, o argumento de intervalo máximo é a expressão calculada e o argumento de expiração é `timeout`. Outros padrões do construtor não fundamentam limites numéricos ou contagens de tentativas inventados aqui. A passagem de dados na fonte explica o que é configurado e deixa cálculo posterior de atraso, elegibilidade de nova tentativa, cancelamento e atividade efetiva do serviço para seus próprios consumidores inspecionados. O capítulo corrigido em EN/PT permanece pendente de aprovação do proprietário e não é treinamento gold aprovado.

## FAQ de engenharia

<!-- reading-section: faq:initial-interval-comment-mismatch -->
### O intervalo inicial configurado é 20 ou 200 milissegundos?

A constante usada pelo corpo é de 200 milissegundos. O comentário próximo de 20 milissegundos diverge dessa declaração. A correção segue a constante escrita e preserva a divergência como evidência de revisão.

<!-- reading-section: faq:future-deadline-not-sixty-second-cap -->
### Um deadline futuro sempre encurta o padrão de sessenta segundos?

Somente um deadline estritamente futuro substitui o padrão, e a atribuição mostrada usa diretamente sua duração restante. Não calcula o mínimo com sessenta segundos. Deadlines ausentes ou não futuros preservam o caminho padrão, sujeito à conclusão normal dos métodos fornecidos.

<!-- reading-section: faq:policy-configuration-not-retry-schedule -->
### Criar a política realiza uma nova tentativa ou garante uma duração de espera?

A função construtora configura e retorna uma política. O consumidor fornecido `ComputeNextDelay` verifica separadamente tentativas e expiração, calcula e limita um intervalo e aplica jitter. Invocação real da operação, espera e cancelamento pertencem a outros consumidores. Nem o máximo armazenado nem o cálculo padrão isolado é um cronograma observado de novas tentativas do serviço.

A evidência opcional com filtragem de build agora sustenta o vínculo léxico da expressão de máximo sob dois perfis explícitos, condicionado a fontes completas e compilação válida. Não transforma configuração de política em cronograma observado de tentativas, prova completa de módulo e tipos ou aprovação do proprietário.
