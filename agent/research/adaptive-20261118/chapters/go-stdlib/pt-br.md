# Comparação, valores zero e busca em fatias Go

Capítulo experimental de correção escrito pelo Codex após revisão estática da fonte. A aprovação humana factual e bilíngue está pendente. Este texto não é saída inalterada do modelo nem dado aprovado para treinamento. Nenhum programa-fonte foi executado.

Provedor da fonte: imagem Go 1.27.4 Linux ARM64 em cache `golang@sha256:0a5f7fe796599ff487605987432e7619ae45beeb2fba4c2ce0b907879932aebf`. Nenhuma revisão Git é inferida. Bytes exatos da fonte, faixas e valores SHA-256: [source-excerpts.json](source-excerpts.json). Licença: [licença Go no estilo BSD](source/LICENSE).

## Comparação e exceções de ponto flutuante

`Less[T Ordered](x, y T) bool` retorna `(isNaN(x) && !isNaN(y)) || x < y`. A expressão escrita trata um NaN detectado à esquerda como menor somente quando o lado direito não é NaN; dois NaNs detectados não satisfazem esse primeiro termo. Esse comportamento difere de apenas retornar `x < y`.

Unidade-fonte: `Less`, `cmp/cmp.go:28-30`. [Citação exata](source-excerpts.json).

`Compare[T Ordered](x, y T) int` calcula `xNaN` e `yNaN` primeiro. Quando `xNaN` é verdadeiro, retorna `0` se `yNaN` também for verdadeiro e `-1` no outro caso. Quando apenas `yNaN` é verdadeiro, retorna `+1`. Esses ramos antecedem as comparações comuns `x < y` e `x > y`.

Unidade-fonte: `Compare`, `cmp/cmp.go:40-59`. [Citação exata](source-excerpts.json).

Os ramos restantes de `Compare` retornam `-1` para `x < y`, `+1` para `x > y` e depois `0`. O auxiliar citado `isNaN[T Ordered](x T) bool` retorna `x != x`; seu comentário diz que o resultado é falso para tipos sem ponto flutuante. Essas funções não escrevem uma distinção entre categorias de NaN com sinal.

Unidade-fonte: `isNaN`, `cmp/cmp.go:63-65`. [Citação exata](source-excerpts.json).

## Seleção variádica pelo valor zero

`Or[T comparable](vals ...T) T` declara `var zero T`, percorre `vals` em ordem e retorna o primeiro `val` para o qual `val != zero`. Ao terminar o laço, retorna `zero`. Uma sequência vazia de argumentos alcança esse retorno final sem entrar no laço.

Unidade-fonte: `Or`, `cmp/cmp.go:69-77`. [Citação exata](source-excerpts.json).

A assinatura de `Or` usa a restrição `comparable` e o parâmetro variádico `...T`; não usa `Ordered`, uma assinatura de dois argumentos nem a restrição irrestrita `any`. A comparação ocorre com o valor zero de `T`, e não com um predicado universal limitado a nulo. O corpo não ordena os valores.

Unidade-fonte: `Or`, `cmp/cmp.go:69-77`. [Citação exata](source-excerpts.json).

## Busca binária retorna posição e presença

`BinarySearch[S ~[]E, E cmp.Ordered](x S, target E) (int, bool)` declara dois resultados. O comentário exige a fatia ordenada em ordem crescente. O corpo inicializa `n := len(x)` e `i, j := 0, n`; não ordena a entrada antes de pesquisar.

Unidade-fonte: `BinarySearch`, `slices/sort.go:126-143`. [Citação exata](source-excerpts.json).

Enquanto `i < j`, `BinarySearch` calcula `h := int(uint(i+j) >> 1)`. Se `cmp.Less(x[h], target)` for verdadeiro, atribui `i = h + 1`; caso contrário, atribui `j = h`. O índice retornado é `i`, e não obrigatoriamente `len(x)` para todo alvo ausente.

Unidade-fonte: `BinarySearch`, `slices/sort.go:126-143`. [Citação exata](source-excerpts.json).

O booleano final é `i < n && (x[i] == target || (isNaN(x[i]) && isNaN(target)))`. Ele verifica o limite do índice e a igualdade ou a condição de ambos serem NaN. Em uma fatia vazia, o laço é ignorado e o resultado é `0, false`. As fontes dos auxiliares `cmp.Less` e `isNaN` precisam ser consideradas ao explicar seus casos especiais.

Unidade-fonte: `BinarySearch`, `slices/sort.go:126-143`. [Citação exata](source-excerpts.json).

## Mínimo pelo comparador é uma varredura

`MinFunc[S ~[]E, E any](x S, cmp func(a, b E) int) E` verifica `len(x) < 1` e chama `panic("slices.MinFunc: empty list")` nesse ramo. Caso contrário, inicializa `m := x[0]` e percorre os índices a partir de `1`. Sua assinatura retorna um `E`, e não um índice e um booleano.

Unidade-fonte: `MinFunc`, `slices/sort.go:79-90`. [Citação exata](source-excerpts.json).

Para cada elemento restante, `MinFunc` atribui `m = x[i]` somente quando `cmp(x[i], m) < 0`. Um resultado `0` do comparador mantém o `m` atual; o comentário descreve a escolha do primeiro elemento mínimo. O corpo escreve seu acumulador local e não contém atribuição a elemento da fatia nem chamada de ordenação. Efeitos colaterais do comparador e consistência da ordenação permanecem suposições externas.

Unidade-fonte: `MinFunc`, `slices/sort.go:79-90`. [Citação exata](source-excerpts.json).

## Escopo e uso

Estes contratos são limitados à fonte. Validade de tipos genéricos, comportamento do compilador, pureza de callbacks e desempenho não foram estabelecidos por execução destes arquivos. O capítulo é preservado para revisão do proprietário e não é carregado automaticamente nos prompts do modelo nem em algum treinador.
