# `Builder.Keep`: inclusão, retornos do callback e registro de exclusões

Correção escrita pelo Codex e revisada contra a fonte; pendente de aprovação do proprietário.

Prometheus revision b2a602494b65bda38316eabaef7e0d834a6814dd; actual preserved baseline: prometheus-keep-bookkeeping. [Exact source excerpt](../references/ref-8e32e3c5ff290286d9d7.md).

## Nomes para manter, não uma coleção de namespaces

A declaração selecionada é `func (b *Builder) Keep(ns ...string) *Builder`. O receptor é um ponteiro de builder, e `ns` é um parâmetro variádico de strings. O baseline do agente local inventou uma coleção de namespaces e inverteu a direção do filtro. Sua observação útil de que o método atualiza o registro de exclusões não corrige esses erros. A resposta original continua preservada como diagnóstico rejeitado.

O callback testa `slices.Contains(ns, l.Name)`. Um nome incluído nessa lista recebida segue o return antecipado do callback. Um nome não incluído alcança o append em `b.del`. Descrever isso como excluir os nomes fornecidos inverte o predicado mostrado. O identificador `ns` é uma abreviação no nome de um parâmetro, não evidência de que essa API gerencie objetos de namespace ou um registro de namespaces.

## O return do callback não retorna de `Keep`

`Keep` chama `b.base.Range` com uma função que recebe um `Label`. O return dentro dessa função não possui expressão de resultado. Ele encerra aquela invocação do callback para um label visitado cujo nome está incluído. Não é o retorno de ponteiro do método externo e não mostra, por si só, que todo o percurso de `Range` pare após o primeiro label incluído.

Depois que a chamada a `Range` conclui normalmente, o método alcança `return b`. Isso retorna o mesmo ponteiro de receptor escrito no método, em vez de um builder recém-alocado, uma lista de labels filtrados ou um booleano. O corpo selecionado não possui guarda explícita de receptor nulo. A conclusão bem-sucedida de `Range` e das operações de seu callback não deve ser convertida silenciosamente em garantia sobre toda entrada possível em execução.

## Registrar exclusões é mais restrito que excluir labels armazenados

Para cada nome visitado que falha no teste de inclusão, a operação escrita é `b.del = append(b.del, l.Name)`. Ela acrescenta à fatia de exclusões existente. O corpo não limpa essa fatia antes do percurso, não deduplica os nomes acrescentados e não desfaz uma marca de exclusão anterior quando o teste de inclusão atual tem sucesso. Um nome correspondente apenas evita o caminho de append desta invocação.

O método selecionado não contém atribuição a `b.add` ou `b.base`. Ele não reescreve diretamente a coleção base nem filtra adições pendentes no corpo mostrado. Uma formulação antiga da fila descrevia incorretamente filtragem de adições; essa premissa precisa ser corrigida antes que experimentos futuros a usem como resposta esperada. A materialização final de um builder é um contrato separado que exige sua própria evidência de fonte.

## Casos de fronteira úteis e seus limites de evidência

Sob o comportamento comum da operação importada `slices.Contains`, uma lista de nomes recebida vazia não contém nenhum nome visitado, portanto cada nome visitado alcança o append de registro de exclusões. Repetir um nome na lista recebida não cria uma invocação adicional de callback neste corpo. Essas são consequências derivadas da fonte do teste e callback escritos, não execuções observadas do Prometheus.

O trecho não estabelece a ordem interna de iteração de `Range`, segurança entre threads, custo assintótico ou conteúdo de um conjunto de labels materializado posteriormente. Por isso, a correção diz “nomes base visitados” e “registro de exclusões”, em vez de afirmar uma exclusão global executada. Reutiliza um baseline concluído do agente local na campanha anterior, sem repetir inferência. Inglês e português preservam o mesmo predicado, receptor, limite de callback e resultado final. O capítulo continua candidato revisado contra a fonte e pendente de aprovação do proprietário, com licença e avisos retidos e sem autorização automática para treinamento ou publicação.

## FAQ de engenharia

<!-- reading-section: faq:keep-does-not-restore-deletion -->
### Keep pode restaurar um nome já marcado para exclusão?

Para um nome visitado incluído, o callback retorna sem acrescentar uma nova marca de exclusão. Não remove uma marca antiga de `b.del`. Preservar um teste de inclusão e desfazer um registro anterior são operações distintas.

<!-- reading-section: faq:keep-addition-preservation -->
### Keep removerá uma adição que não esteja na lista de nomes fornecida?

O método selecionado visita a base e não atribui `b.add`. Esse corpo não permite documentá-lo como filtro de adições pendentes. O `Builder.Range` inspecionado separadamente visita as adições pendentes depois de processar os labels base contra seu estado copiado.

<!-- reading-section: faq:callback-return-scope -->
### Por que um return antecipado não encerra o método externo?

O return está dentro do callback passado ao percurso da base. Depois que esse percurso conclui normalmente, o `Keep` externo ainda alcança `return b`. Conclusão do callback, conclusão do percurso e retorno externo do ponteiro devem permanecer distintos nas duas línguas.

A fonte adicional de `Builder.Get` também mostra por que apenas o registro de exclusões não descreve o resultado completo: ela verifica adições pendentes antes das marcas de exclusão e depois o getter da base. Essas observações dos consumidores não selecionam uma variante de build do pacote nem executam o Prometheus.
