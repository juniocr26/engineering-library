# Cobra: validação de argumentos posicionais e execução de comandos

Candidato de pesquisa isolado. Somente revisão da fonte pelo autor; verificação separada e revisão do proprietário pendentes. Sem aprovação para publicação ou treino.

spf13/cobra @ `adbc8813901bba65827259daa8e22ff94ec1f30e`. Este capítulo cobre o contrato selecionado, não o repositório inteiro. Evidência: `source-freeze-v1.json`; critérios: `acceptance-protocol-v1.json`.

## Arquitetura e comportamento

**C01** — PositionalArgs é um tipo de função que recebe *Command e []string e retorna error. [C01: `args.go:22-22`]

**C02** — OnlyValidArgs verifica pertencimento somente quando Command.ValidArgs não está vazio; as entradas descartam a descrição após uma tabulação. [C02: `args.go:51-65`]

**C03** — NoDuplicateArgs retorna um erro no primeiro argumento posicional repetido. [C03: `args.go:68-79`]

**C04** — MinimumNArgs e MaximumNArgs impõem limites inferior e superior inclusivos; ExactArgs exige quantidade igual; RangeArgs aceita os dois extremos. [C04: `args.go:86-124`]

**C05** — MatchAll invoca validadores na ordem e retorna o primeiro erro; ExactValidArgs delega para MatchAll(ExactArgs(n), OnlyValidArgs). [C05: `args.go:126-144`]

**C06** — Nesse caminho de execução, um erro de ValidateArgs encerra a execução antes dos hooks persistent pre-run e pre-run. [C06: `command.go:968-1005`]

**C07** — Nesse caminho, a validação de flags obrigatórias e grupos de flags ocorre após os hooks pre-run e antes de RunE ou Run. [C07: `command.go:1007-1019`]

## Exemplo

Fragmento sintético de uso, não executado. Resolva dependências em um ambiente autorizado separadamente antes de executar. Nenhum comando de inicialização ou instalação está autorizado aqui.

```go
validator := cobra.MatchAll(cobra.ExactArgs(2), cobra.OnlyValidArgs)
cmd := &cobra.Command{ValidArgs: []string{"red", "blue"}}
err := validator(cmd, []string{"red", "blue"})
_ = err
```

## Evidências de testes e limitações

`args_test.go` está preservado como evidência de testes escritos. Nenhuma suíte externa, exemplo, instalação de dependências ou runtime foi executado. Asserções escritas não são resultados aprovados. Nenhum benchmark, garantia de concorrência ou compatibilidade de API entre releases foi estabelecido.

## FAQ

### Q001 — OnlyValidArgs exige uma lista de valores permitidos não vazia?

OnlyValidArgs verifica pertencimento somente quando Command.ValidArgs não está vazio; as entradas descartam a descrição após uma tabulação. [C02]

### Q002 — MatchAll coleta todos os erros de validação?

MatchAll invoca validadores na ordem e retorna o primeiro erro; ExactValidArgs delega para MatchAll(ExactArgs(n), OnlyValidArgs). [C05]

### Q003 — Todas as flags são validadas antes dos hooks pre-run?

Nesse caminho, a validação de flags obrigatórias e grupos de flags ocorre após os hooks pre-run e antes de RunE ou Run. [C07]

## Manutenção e direitos

Este clone raso não possui o pai de HEAD localmente. Uma decisão histórica MODIFY é INCONCLUSIVE sem uma fonte anterior verificada e documentação correspondente. Símbolos ausentes neste escopo selecionado não autorizam REMOVE. A documentação existente do projeto permanece sem alterações.

Apache-2.0 / LICENSE.txt. Os avisos estão preservados com o snapshot de fonte. Este artefato é somente para avaliação, excluído de treino e não aprovado pelo proprietário.
