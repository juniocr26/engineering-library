# Builder do Prometheus: inclusão, substituição e registro de exclusão

Estado: correção experimental escrita pelo Codex e revisada contra a fonte. A aprovação humana está pendente. Este capítulo não é uma resposta gerada pelo modelo, um exemplo aprovado para treinamento, um manual publicado ou evidência de melhoria nos pesos do modelo.

A fonte é a revisão `b2a602494b65bda38316eabaef7e0d834a6814dd` do Prometheus, arquivo `model/labels/labels_common.go`. O contrato delimitado compreende `Builder.Set` e `Builder.Del`. As respostas originais do agente local e os critérios de avaliação congelados de forma independente estão preservados no workspace privado da continuação. A resposta que recebeu somente o chamador foi recusada; a resposta que recebeu os dois métodos passou pelas verificações estruturais, mas omitiu o auxiliar e os retornos. Esta correção trata diretamente dessas omissões.

## Set escolhe o ramo pelo valor

O método recebe um nome e um valor, ambos strings, e retorna um ponteiro para o builder. Sua primeira condição é `v == ""`. A condição trata do valor, não de um nome vazio, da ausência de rótulos no builder ou da existência prévia de um rótulo. Nesse ramo, a implementação executa imediatamente `return b.Del(n)`. Portanto, delega ao auxiliar de exclusão e retorna o resultado dele. As instruções posteriores de busca e inclusão não são alcançadas nesse ramo.

Para um valor não vazio, o método percorre `b.add`. Cada iteração compara `a.Name == n`. Na primeira entrada correspondente, atribui `b.add[i].Value = v` e executa `return b`. A coleção pesquisada é a slice de inclusões pendentes. Dizer apenas “atualiza um rótulo existente” perde essa distinção e pode sugerir que o método pesquisa ou reescreve diretamente a coleção base.

Se a busca terminar sem correspondência, o método atribui `b.add = append(b.add, Label{Name: n, Value: v})` e executa `return b`. O novo elemento usa o nome e o valor recebidos. O método não ordena as inclusões nesse corpo. Os dois caminhos de valor não vazio retornam a mesma expressão do receptor; o caminho de valor vazio retorna o resultado da chamada ao auxiliar.

## Del registra a exclusão e ajusta inclusões pendentes

O auxiliar recebe `ns ...string`. Ele visita os nomes recebidos na ordem fornecida. Para cada nome, percorre `b.add` e verifica `a.Name == n`. Em uma correspondência, a atualização de slice escrita é `b.add = append(b.add[:i], b.add[i+1:]...)`. Após essa busca interna, executa `b.del = append(b.del, n)`. Ao terminar o laço externo, executa `return b`.

O registro de uma exclusão solicitada não depende de encontrar uma inclusão. Assim, um nome pode ser acrescentado à slice de exclusões mesmo quando a busca interna não encontra uma inclusão pendente correspondente. Não existe uma verificação de duplicidade antes desse acréscimo. O código não mostra que solicitações repetidas do mesmo nome sejam normalizadas em um único marcador de exclusão. Por outro lado, uma chamada sem nomes não entra no laço externo e alcança o retorno.

Essas observações descrevem os laços e as atualizações escritos. Elas não estabelecem comportamento para slices internas arbitrariamente malformadas, não provam conclusão normal para todo estado possível do receptor nem estabelecem segurança de concorrência. O código selecionado não contém bloqueio ou validação independente que justifique essas garantias.

## Por que o auxiliar muda o que pode ser documentado

Com somente o chamador disponível, um autor pode identificar a delegação para valor vazio, a busca nas inclusões, o ramo de substituição, o ramo de acréscimo e os retornos escritos. Sua evidência não inclui como o auxiliar registra exclusões. Conhecer o nome de um auxiliar é diferente de dispor de sua implementação.

Com os dois métodos disponíveis, a atualização da slice de exclusões pode ser inspecionada diretamente. A explicação pode distinguir uma solicitação de exclusão de uma modificação imediata da coleção base, explicar a expressão de remoção nas inclusões pendentes e identificar o retorno do auxiliar. Acrescentar essa fonte só ajuda se a explicação final realmente a utilizar corretamente. Neste experimento, a resposta neural com o auxiliar continuou citando apenas o chamador e omitiu o contrato do auxiliar. Portanto, o contexto adicional não demonstrou uma melhoria factual completa.

## Limites deste capítulo

Os métodos selecionados não atribuem a `b.base`. Também não removem entradas de `b.del` no caminho de valor não vazio. Este capítulo não infere como outro método combina posteriormente a base, as inclusões e as exclusões. Isso exige sua própria fonte, incluindo a variante de build pertinente. Também não infere validação de nomes, operações de banco, erros, tempo de execução, garantias de alocação de memória ou sincronização automática a partir desses dois métodos.

Preservar o comportamento de retorno importa mesmo quando a descrição de inclusão ou substituição parece plausível. O baseline mencionou o retorno de um builder; a resposta com o contexto do auxiliar perdeu esse fato. Uma intervenção deve preservar os fatos já corretos e acrescentar os que faltam. A aceitação estrutural pelo writer, a equivalência bilíngue e a recuperação bem-sucedida de fonte são verificações distintas dessa exigência de contrato completo.

## Referências e revisão

Os trechos exatos selecionados, linhas físicas, hash da fonte e identidade do produtor estão em `source-excerpts.json`. A fonte upstream é [labels_common.go na revisão congelada](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/model/labels/labels_common.go). O código está sob a Apache License 2.0; a licença original foi preservada privadamente com o snapshot. O programa fonte não foi executado para esta revisão. Identificadores e condições de código em EN/PT-BR são verificados separadamente das respostas neurais, e nenhuma língua recebe aprovação automática para publicação.

## FAQ de engenharia e um consumidor verificado

<!-- reading-section: faq:deferred-deletion-bookkeeping -->
### Um valor vazio reescreve imediatamente os labels base?

`Builder.Set` delega para `Builder.Del`. Esses métodos selecionados ajustam adições pendentes e o registro de exclusões; nenhum atribui a coleção base. Um valor vazio não evidencia delete em banco ou substituição imediata da representação base.

<!-- reading-section: faq:addition-precedence -->
### Por que um Set posterior pode ter precedência sem limpar a slice de exclusões?

A fonte adicional revisada aqui é `Builder.Get`. Ela pesquisa primeiro as adições pendentes e retorna um valor correspondente. Só depois dessa pesquisa verifica a slice de exclusões e, caso contrário, delega ao getter da base. Essa é uma ordem de consulta escrita e verificada, não a afirmação de que Set remove marcas de exclusão.

<!-- reading-section: faq:deletion-no-synchronization-proof -->
### Del garante unicidade ou sincronização?

Seu corpo selecionado acrescenta cada nome solicitado sem uma guarda de deduplicação. Nenhum lock é mostrado nesses métodos. Validade do receptor, variantes de build do pacote e uso concorrente exigem evidências separadas.

O corpo adicional de `Builder.Range` copia adições e exclusões antes de seus callbacks, filtra os labels base visitados contra essas cópias e então visita as adições pendentes. A representação final dos labels e a implementação do percurso da base continuam contratos separados. Esses métodos extras foram revisados para este candidato, não fornecidos à resposta neural histórica.
