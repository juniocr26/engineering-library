# Redis: o limite exato do predicado de expiração

Este capítulo experimental descreve `checkAlreadyExpired` na revisão de código congelada registrada na evidência correspondente. Ele corrige um baseline real do agente local preservado da campanha anterior. A correção foi escrita e revisada contra o código pelo Codex; aguarda aprovação do proprietário e não é documentação publicada nem dado de treinamento aprovado. O Redis não foi executado nesta revisão. A função selecionada responde a uma pergunta delimitada sobre um instante de expiração e o estado do servidor, tornando essencial distinguir seu retorno das operações realizadas em outros lugares.

## A guarda do cliente atual vem primeiro

A primeira instrução executável testa `server.current_client` e depois suas flags contra `CLIENT_MASTER`. A condição externa usa conjunção lógica, que protege o acesso ao campo do cliente quando não existe cliente atual. A expressão das flags é um teste de pertencimento com operação bit a bit. Quando a condição combinada é verdadeira, a função retorna `0` imediatamente. A comparação temporal posterior não é alcançada nesse caminho. Essa guarda trata das flags do cliente atual; substituí-la pela afirmação vaga de que o servidor está em certo modo mestre perde o proprietário e a condição reais.

Se a guarda não retornar, a função avalia `when <= commandTimeSnapshot() && !server.loading && !server.masterhost`. A comparação inclui igualdade: um instante igual ao resultado do helper satisfaz o primeiro operando. Um instante estritamente anterior também o satisfaz. A função só pode retornar verdadeiro por essa expressão quando a comparação passa e os dois campos negados seguintes do servidor também são verdadeiros. Portanto, o instante isolado não determina o resultado. Qualquer uma das condições do servidor pode impedir que a expressão se torne verdadeira.

## Ordem de avaliação e incerteza sobre o helper

A conjunção lógica usa curto-circuito. Ao alcançar a segunda instrução, a comparação temporal é avaliada primeiro. Uma comparação falsa pula os dois operandos posteriores; um operando falso referente ao carregamento pula o último operando. A função fornecida original chamava `commandTimeSnapshot()` sem mostrar sua implementação; esta campanha acrescenta esse helper separadamente abaixo. Aquele trecho original isolado não estabelecia implementação de relógio, unidade, política de cache, comportamento entre threads ou atualização do horário de parede. O helper acrescentado abaixo identifica um snapshot armazenado e seu tipo documentado em milissegundos; momento de atualização e garantias do relógio em execução ainda exigem evidência separada. A comparação e a ordem explícitas dos desvios continuam diretamente inspecionáveis.

O tipo de retorno é inteiro, enquanto a expressão lógica final fornece um valor de verdade segundo as regras de expressões de C. O inteiro `0` antecipado e a expressão final falsa produzem resultado falso, mas surgem de caminhos de controle diferentes. O primeiro evita completamente a chamada ao helper temporal. Uma explicação sustentada pelo código deve preservar essa diferença ao discutir avaliação, instrumentação ou um teste controlado futuro. O predicado selecionado original não estabelecia o comportamento do chamador; o trecho adicional abaixo agora separa seus ramos de mutação do resultado do predicado.

## Justificativa do comentário e operações reais

O comentário do código discute instantes de expiração passados, carregamento de um arquivo de append-only, contexto de replicação e espera por uma exclusão explícita enviada pelo mestre. Ele explica a razão da guarda e das condições de estado. O corpo da função não insere uma chave, exclui uma chave, propaga um comando, configura uma expiração nem espera uma mensagem de rede. Transformar essa justificativa em promessa de que a própria função realiza essas operações foi um erro crítico do baseline histórico. O contrato corrigido descreve o predicado e mantém o fluxo de banco ao redor fora da evidência selecionada.

## Comparação e estado da revisão

O baseline reconheceu em termos gerais uma verificação de expiração, mas omitiu o retorno antecipado do cliente atual e confundiu os papéis do servidor. Também perdeu a comparação exata e a guarda final de estado, apresentando a justificativa do comentário como comportamento. Esta correção restaura essas condições sem afirmar que o modelo local as aprendeu. As duas versões preservam as mesmas expressões técnicas e limites. Hashes exatos, linhas físicas das citações, resposta original, identidade histórica do caller e achados da revisão continuam nos artefatos correspondentes; essas verificações de integridade ajudam a revisão, mas não substituem a aprovação do proprietário.

## FAQ de engenharia e responsabilidade real do chamador

<!-- reading-section: faq:predicate-versus-key-deletion -->
### O próprio predicado exclui uma chave já expirada?

Seu corpo retorna uma decisão. O chamador inspecionado separadamente testa essa decisão e então invoca `dbGenericDelete` no ramo verdadeiro, atualiza o estado dirty, reescreve o comando do cliente e emite notificações e uma resposta. O ramo falso invoca `setExpire` e sua própria sequência de atualização e notificação. Essas são operações do chamador, não operações ocultas realizadas pelo predicado.

<!-- reading-section: faq:inclusive-expiry-boundary -->
### Um instante igual é considerado além da fronteira?

A comparação escrita inclui igualdade, mas só depois que a guarda de retorno antecipado do cliente atual não disparou. As condições loading e masterhost ainda participam da conjunção final. A comparação temporal isolada é insuficiente.

<!-- reading-section: faq:clock-snapshot-value -->
### Qual valor temporal o getter inspecionado fornece?

A implementação adicional retorna diretamente `server.cmd_time_snapshot`; sua declaração usa o tipo temporal em milissegundos. Não lê um relógio novo nesse corpo. Cronograma exato de atualização, todos os chamadores, confiabilidade do relógio e acesso concorrente permanecem fora desta revisão delimitada.

Esses trechos adicionais resolvem o getter nomeado e um chamador real sem transformar comentários sobre replicação ou carregamento de AOF em operações dentro do predicado. Nenhum comando, servidor, mutação de chave ou fluxo de replicação Redis foi executado.
