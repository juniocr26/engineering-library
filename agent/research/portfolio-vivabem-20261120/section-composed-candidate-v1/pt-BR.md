# Validadores posicionais do Cobra — candidato composto por seções

Saída gerada de pesquisa isolada; revisão pendente. Fonte: spf13/cobra, revisão adbc8813901bba65827259daa8e22ff94ec1f30e, args.go. Escopo: os cinco grupos de API selecionados, não o repositório inteiro ou o roteamento de comandos.

## simple

Essas funções verificam condições específicas na sequência de argumentos sem alterá-la.

Trechos de fonte: args.go:41-47, args.go:68-84.

## allowlist

OnlyValidArgs verifica se todos os argumentos posicionais são válidos e retorna um erro se não for o caso.

Trechos de fonte: args.go:49-65.

## bounds

As fábricas MinimumNArgs, MaximumNArgs, ExactArgs e RangeArgs retornam validadores que impõem limites inclusivos e incerteza ordenada desordenada. As condições de ramificação dessas fábricas são baseadas na quantidade de argumentos de entrada.

Trechos de fonte: args.go:86-124.

## composition

MatchAll permite combinar PositionalArgs para funcionar juntos, enquanto ExactValidArgs verifica os args posicionais exatos e a validade.

Trechos de fonte: args.go:126-144.

## legacy

O tipo de função PositionalArgs e as branches de controle da função legacyArgs são definidos. A função legacyArgs verifica se há subcomandos e valida os argumentos de acordo.

Trechos de fonte: args.go:22-39.

## Exemplo

Instruções sintéticas dentro de uma função Go existente, com github.com/spf13/cobra importado como cobra; sintaxe analisada pelo parser Go existente, sem verificação de tipos ou execução.

```go
validator := cobra.MatchAll(cobra.ExactArgs(2), cobra.OnlyValidArgs)
cmd := &cobra.Command{ValidArgs: []string{"red", "blue"}}
err := validator(cmd, []string{"red", "blue"})
_ = err
```

## Evidências de testes escritos

args_test.go existe no snapshot fixado de fonte; seus testes e este exemplo não foram executados. A presença de asserções não é um resultado aprovado.

## FAQ

### Q001 — Como as funções NoArgs, NoDuplicateArgs e ArbitraryArgs lidam com condições de ramificação?

A NoArgs retorna um erro se houver argumentos incluídos, enquanto NoDuplicateArgs retorna um erro se houver argumentos duplicados. A função ArbitraryArgs nunca retorna um erro. As condições de ramificação são verificadas usando if statements e retornando erros.

### Q002 — O que acontece se não houver argumentos válidos?

Se não houver argumentos válidos, OnlyValidArgs retorna um erro. Isso ocorre porque a função verifica se todos os argumentos são na lista de argumentos válidos. Se a lista estiver vazia, ela não pode determinar se um argumento é válido ou não. O erro é indicado que não há sugestões válidas para o comando.

### Q003 — Como as fábricas MinimumNArgs, MaximumNArgs, ExactArgs e RangeArgs lidam com o caso onde o número de argumentos é exatamente igual ao valor esperado?

A fábrica ExactArgs retorna nil quando o número de argumentos é exatamente igual ao valor esperado, indicando que a comando tem o número de argumentos necessário.

### Q004 — Qual é a diferença entre MatchAll e ExactValidArgs?

MatchAll permite combinar vários PositionalArgs para funcionar juntos, enquanto ExactValidArgs verifica exatamente N args posicionais e sua validade contra o campo `ValidArgs` do comando. ExactValidArgs é obsoleto e deve ser substituído por MatchAll com ExactArgs e OnlyValidArgs.

### Q005 — Como a função legacyArgs trata com comandos raízes com subcomandos?

A função legacyArgs verifica se o comando tem um pai e se há argumentos. Se o comando tem um pai e há argumentos, ela retorna um erro indicando um comando desconhecido. Caso contrário, ela retorna nil.

## Limitações e preservação

O clone raso não possui revisão pai local; por isso, MODIFY histórico permanece INCONCLUSIVE sem fonte anterior verificada e documentação correspondente. Símbolos ausentes em fonte parcial nunca autorizam REMOVE. Nenhuma garantia geral de runtime ou integração de produção foi testada. A documentação existente do projeto permanece sem alterações. Os avisos Apache-2.0 estão preservados com a fonte. Nenhuma aprovação do proprietário, publicação ou uso em treino está autorizado.
