# Cobra: validadores posicionais no contexto do comando

Este capítulo isolado cobre contratos escritos selecionados de `spf13/cobra` em `adbc8813901bba65827259daa8e22ff94ec1f30e`. Conecta factories de validadores, seleção de comando e o caminho ordinário de execução. O código público exato e os avisos Apache-2.0 estão preservados. Revisão do código, análise nativa de sintaxe Go e aprovação do proprietário são coisas diferentes; nenhum código ou teste do Cobra foi executado.

## Validadores e factories

`PositionalArgs` é o tipo de função que recebe um ponteiro de comando e um slice de strings e retorna um erro (`args.go:22`). `OnlyValidArgs` executa suas verificações de pertencimento sob a condição escrita `len(cmd.ValidArgs) > 0`. Mantém a parte de cada entrada da lista permitida anterior à primeira tabulação e depois verifica os argumentos fornecidos. Fora desse bloco condicionado, retorna `nil`; uma lista permitida vazia não produz, por si só, um erro de validação. O helper `stringInSlice` compara strings por igualdade. Evidência: `args.go:51–66`, `cobra.go:225–232`.

`ExactArgs(n)` retorna uma função `PositionalArgs`. Essa função retornada verifica `len(args) != n` quando é invocada; chamar a factory não é validar um slice de argumentos posterior. Os validadores correspondentes de mínimo e máximo rejeitam comprimentos abaixo ou acima de seus limites, e o validador de intervalo rejeita valores fora de seus dois extremos. Evidência: `args.go:87–124`.

`MatchAll` retorna outro validador. Seu laço invoca os validadores fornecidos em ordem e retorna imediatamente no primeiro erro diferente de `nil`; não coleta todos os erros. `ExactValidArgs(n)` delega a `MatchAll(ExactArgs(n), OnlyValidArgs)` e está marcado como obsoleto no comentário do código selecionado. `NoDuplicateArgs` mantém um conjunto de itens vistos e retorna no primeiro ramo de argumento repetido. Esses são contratos selecionados do código, não garantias sobre callbacks arbitrários ou ponteiros de comando inválidos. Evidência: `args.go:69–79,127–144`.

## Dois caminhos distintos do comando

`Command.ValidateArgs` retorna `ArbitraryArgs(c, args)` quando `c.Args == nil`; caso contrário, chama `c.Args(c, args)`. O corpo selecionado de `ArbitraryArgs` retorna `nil`. Seria incorreto descrever `legacyArgs` como o ramo padrão desse método. Evidência: `command.go:1172–1177`, `args.go:82–84`.

Separadamente, depois de sua busca interna de comando, `Command.Find` chama `legacyArgs(commandFound, stripFlags(a, commandFound))` quando `commandFound.Args == nil`. O `legacyArgs` selecionado retorna antecipadamente quando o comando não tem subcomandos. Caso contrário, seu ramo escrito de erro exige tanto `!cmd.HasParent()` quanto `len(args) > 0`. Os dois helpers consultados retornam, respectivamente, `c.parent != nil` e `len(c.commands) > 0`. Isso não estabelece todo chamador ou comportamento de remoção de flags. Evidência: `command.go:757–779,1601–1603,1677–1679`, `args.go:28–39`.

## Ordem da validação e dos hooks

No caminho selecionado de `Command.execute`, a análise das flags ocorre antes da verificação dos argumentos posicionais; erros nessa análise podem retornar antes. O método depois chama seu helper inicializador `preRun`, em minúsculas, e agenda `postRun` com defer. Esse helper inicializador percorre `initializers`; é distinto dos campos de hook `PreRun` e `PersistentPreRun`. Evidência: `command.go:919–922,955–970,1047–1051`.

Um erro retornado por `ValidateArgs` encerra o caminho antes dos blocos seguintes de hooks persistentes de pré-execução e de pré-execução. Quando o controle continua, a validação de flags obrigatórias e de grupos de flags ocorre depois desses blocos de hooks e antes do ramo `RunE`/`Run`. Retornos anteriores e erros dos hooks ainda importam. Isso não afirma que todo tipo de tratamento de flags aguarde até depois dos hooks ou que todos os hooks necessariamente executem. Evidência: `command.go:968–1019`.

## Um fragmento ilustrativo

O fragmento próprio abaixo cria e invoca um validador diretamente. Não executa um comando, não registra hooks e não demonstra o caminho completo da CLI.

```go
validator := cobra.MatchAll(cobra.ExactArgs(2), cobra.OnlyValidArgs)
cmd := &cobra.Command{ValidArgs: []string{"red", "blue"}}
err := validator(cmd, []string{"red", "blue"})
_ = err
```

O fragmento é analisado sintaticamente depois de ser envolvido por uma função própria com a importação do Cobra. A declaração do módulo identifica `github.com/spf13/cobra`. As importações não foram resolvidas, e o fragmento não passou por verificação de tipos nem foi executado. Nenhum comando de instalação, inicialização ou execução é proposto aqui.

## Testes escritos

`TestOnlyValidArgs` e `TestOnlyValidArgs_WithInvalidArgs` contêm chamadas a helpers de sucesso e de argumento inválido em torno de `executeCommand` (`args_test.go:155–165`). São evidências escritas de testes, não observações de aprovação nesta campanha.

`TestMatchAll` compõe `ExactArgs(3)` com um validador que verifica comprimentos de dois bytes por argumento. Sua tabela inclui um caso de sucesso, um caso de contagem incorreta e um caso de comprimento em bytes incorreto; depois verifica se os erros correspondem ao indicador esperado de falha (`args_test.go:477–523`). Isso ilustra a cobertura pretendida da composição; não prova todo ramo, comportamento de callbacks arbitrários ou o resultado do exemplo em runtime.

## FAQ

### Q001 — Uma lista ValidArgs vazia, por si só, rejeita entradas?

Não. No corpo selecionado de `OnlyValidArgs`, a validação de pertencimento fica dentro da condição de lista não vazia, e o retorno seguinte é `nil`.

[A01: `args.go:51–66`]

### Q002 — Construir ExactArgs valida um slice posterior?

Não. A fábrica retorna um validador; sua função retornada faz a comparação de comprimento quando é chamada.

[A02: `args.go:107–114`]

### Q003 — O que ValidateArgs usa quando Args é nil?

O método selecionado chama `ArbitraryArgs`, cujo corpo selecionado retorna `nil`. A chamada de `legacyArgs` no caminho de `Find` é separada.

[A03: `command.go:1172–1177`]

### Q004 — MatchAll continua depois que um validador retorna um erro?

O corpo selecionado de legacyArgs retorna nil se não há subcomandos. Caso contrário, seu ramo de erro exige tanto !cmd.HasParent() quanto len(args) > 0.

[A04: `args.go:28–39`]

### Q005 — Toda validação de flags precisa preceder os hooks de pré-execução?

Não. Seu laço retorna esse primeiro erro antes das iterações posteriores.

[A05: `args.go:127–136`]

## Manutenção e limites

O inventário inicial registrou um clone shallow sem seu pai local de HEAD. Nenhuma revisão ausente foi buscada, e nenhuma alteração histórica é inventada aqui. Símbolos ausentes de um escopo selecionado não autorizam remoção. A análise das declarações Go estabelece sintaxe, identidade léxica e citações físicas; os contratos selecionados foram revisados separadamente. Isso não é verificação de tipos, prova de vínculos em runtime, análise completa do projeto ou verificador semântico geral. Este capítulo é um candidato de pesquisa, excluído de treinamento e publicação ativa; aprovação do proprietário e gold de treinamento permanecem falsos.
