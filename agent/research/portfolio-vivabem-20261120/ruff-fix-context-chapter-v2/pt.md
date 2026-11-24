# Ruff: da disponibilidade declarada às edições selecionadas

`astral-sh/ruff` · `0222c19dd8e0c9a927f2e47bf3774a108431da25`

Status: CANDIDATE_FOR_SOURCE_REVIEW; sem aprovação do proprietário, sem Gold, fora dos dados de treinamento.

## Escopo e evidência

Este capítulo descreve a revisão selecionada do Ruff, sem generalizar para todas as versões lançadas. Ele acompanha metadados de regras, armazenamento de diagnósticos, política de correções e reconstrução do texto entre crates distintos. O repositório já foi exposto em desenvolvimento. Todas as conclusões abaixo são inferências das fontes; não houve compilação Rust, expansão de macros, execução do Ruff, execução dos testes do projeto ou alteração de seus arquivos.

## Metadados têm uma interface separada

`ViolationMetadata` declara identidade, explicação, status, categoria, arquivo e linha de declaração da regra. O gerador `violation_metadata` selecionado emite esses métodos e exige metadados de status e categoria, retornando `syn::Error` quando algum falta. Sua saída selecionada não anexa um `Fix` nem implementa `FIX_AVAILABILITY`. A afirmação se limita a esse gerador; não significa que correções estejam ausentes em todo o projeto.

[S1](#s1) [S2](#s2)

## Disponibilidade descreve uma regra

`FixAvailability` possui `Sometimes`, `Always` e `None`. `Violation::FIX_AVAILABILITY` tem padrão `None`; `fix_title` também retorna `None` por padrão. A implementação abrangente para `AlwaysFixableViolation` define disponibilidade `Always` e envolve seu título em `Some`. Essas declarações, por si, não constroem o conteúdo das edições nem armazenam uma correção em cada diagnóstico.

[S1](#s1)

## Converter uma violação não anexa uma correção

`Violation::into_diagnostic` chama `create_lint_diagnostic` com argumento de correção `None`, mesmo quando há título. `Diagnostic::new` inicializa sua correção com `None`; o auxiliar chama `set_fix` somente quando seu argumento opcional de correção é `Some`. Portanto, nesse caminho selecionado, um título de ajuda e uma coleção de edições anexada são coisas distintas.

[S1](#s1) [S3](#s3) [S5](#s5)

## Operações de armazenamento têm significados diferentes

`Diagnostic::fix` retorna uma referência opcional à correção. `set_fix` atribui `Some(fix)` por `Arc::make_mut` e contém `debug_assert!` exigindo um span primário. Essa asserção não deve ser descrita como validação incondicional em modo release. `set_optional_fix(None)` não faz nada e não apaga uma correção existente; `remove_fix` armazena `None` explicitamente.

[S4](#s4)

## Construtores classificam e organizam edições

`Fix` armazena edições, aplicabilidade e isolamento. Os construtores de correções seguras, inseguras e apenas para exibição atribuem a classificação correspondente e o isolamento padrão; os construtores de múltiplas edições ordenam por início e fim. `applicable_edit` e `applicable_edits` recebem a classificação explicitamente. Esses corpos armazenam dados; não executam as edições nem provam que o autor escolheu a classificação semântica correta.

[S6](#s6) [S7](#s7)

## A guarda de diagnóstico da AST acrescenta política

`DiagnosticGuard::set_fix` consulta primeiro `should_fix(self.rule)`. Quando falso, remove a correção do diagnóstico e retorna. Caso contrário, resolve a aplicabilidade pela tabela de configurações e anexa a correção reclassificada. Esse é um caminho selecionado do verificador de AST; não prova que toda chamada direta a `Diagnostic::set_fix` passe pela mesma política.

[S9](#s9)

## A construção falível ainda chama sua função

`try_set_fix` invoca `func()` antes de analisar seu resultado. `Ok(fix)` delega a `set_fix`; `Err` registra uma mensagem de depuração. Logo, a consulta de seleção de regra dentro de `set_fix` não estabelece que a função de construção deixe de ser chamada. `try_set_optional_fix` também mantém o estado atual em `Ok(None)`. Aqui não se afirma observação de efeitos dessa função nem recuperação de pânico.

[S9](#s9)

## Sobrescritas de segurança preservam correções apenas para exibição

`FixSafetyTable::resolve_applicability` preserva `DisplayOnly`. Para uma entrada `Safe` ou `Unsafe`, consulta primeiro a classificação forçada como insegura, depois a forçada como segura e, na ausência delas, mantém a entrada. Isso descreve o corpo do resolvedor; não certifica que a reclassificação valide a semântica das edições nem que os dois conjuntos possam conter a mesma regra pela construção normal.

[S10](#s10)

## Aplicabilidade usa um limiar ordenado

`Applicability` deriva `Ord` e `PartialOrd`, com discriminantes implícitos na ordem de declaração: `DisplayOnly < Unsafe < Safe`. `Fix::applies` compara a classificação armazenada com o argumento usando `>=`. A ordenação decorre do contrato oficial do Rust para ordenação derivada de enums, e não de uma observação de compilador local. Isoladamente, o método admitiria uma correção apenas para exibição com limiar de apenas exibição.

[S6](#s6) [S8](#s8)

## O chamador selecionado restringe o domínio do limiar

`UnsafeFixes::required_applicability` retorna `Unsafe` para `Enabled` e `Safe` para `Disabled` e o padrão `Hint`. Assim, a política selecionada de `fix_file` admite correções seguras nos três modos, também inseguras no modo habilitado e nenhuma apenas para exibição. Trata-se de um filtro de admissão; sobreposição e isolamento ainda podem impedir a seleção das edições. Não se generaliza isso para todo chamador possível de `applies`.

[S8](#s8) [S11](#s11) [S12](#s12)

## A função selecionada constrói um resultado

`fix_file` filtra diagnósticos com correção anexada e admitida. Sem nenhum, retorna `None`; caso contrário, retorna `Some(apply_fixes(...))`. `FixResult` contém texto reconstruído, contagens de correções e um mapa de origem. Embora o comentário próximo mencione gravação em disco, o corpo selecionado não faz uma gravação no sistema de arquivos. Persistência externa e iterações de análise e correção ficam fora deste capítulo.

[S12](#s12) [S13](#s13)

## Ordenação, edições duplicadas e conflitos

`apply_fixes` ordena correções por `cmp_fix`, incluindo precedência especial de regras, posição inicial e desempates selecionados. Remove edições já presentes no conjunto de edições aplicadas antes de verificar se resta uma primeira edição nova. Para essa primeira edição, verifica o grupo de isolamento e então rejeita a posição inicial quando `last_pos >= first.start()`. Essa condição de fronteira não deve ser reduzida a um teorema genérico de sobreposição de intervalos, nem implica que todo diagnóstico admitido altere o texto.

[S13](#s13) [S14](#s14)

## A reserva do grupo precede a rejeição por posição

Para uma correção com edição nova e `IsolationLevel::Group(id)`, o código insere o identificador do grupo antes de consultar `last_pos`. Uma rejeição posterior por posição não remove esse identificador no corpo selecionado. Portanto, a fonte não sustenta uma descrição simplificada segundo a qual os grupos só são reservados após aplicar uma edição com sucesso. Essa observação de ordem não é um contraexemplo executado nem uma avaliação da política pretendida pelos mantenedores.

[S13](#s13)

## Reconstrução não é verificação semântica

Para as edições selecionadas, a implementação acrescenta trechos intactos, conteúdo de substituição ou uma substituição vazia, registra marcadores do mapa de origem e avança `last_pos` até o fim da edição. Depois da correção, amplia o conjunto de edições aplicadas e incrementa uma contagem de diagnóstico; ao final, acrescenta o restante da fonte. Contar um diagnóstico difere de contar novas edições emitidas, inclusive quando todas as suas edições eram duplicadas. Esses corpos não estabelecem a correção do programa Python resultante.

[S13](#s13)

## Testes existentes e observações efetivas

O módulo selecionado contém um módulo de testes `#[cfg(test)]`, um auxiliar que constrói diagnósticos e o teste `empty_file`, que verifica saída vazia, contagens zeradas e mapa de origem vazio. São declarações de testes inspecionadas, e não resultados de aprovação obtidos nesta campanha. As observações efetivas foram recuperação de fontes por Git somente para leitura e acompanhamento editorial das fontes. A busca por `rustc` no PATH do host não encontrou comando; isso não estabelece a ausência de toda instalação Rust ou de ferramentas em contêineres. Não se tentou instalar ferramentas nem compilar o repositório.

[S15](#s15)

## FAQ

### Always significa que todo diagnóstico já tem edições?

Não. A implementação abrangente define disponibilidade da regra e título, enquanto `into_diagnostic` passa `None` como correção. Uma correção anexada é um estado opcional separado.

[S1](#s1) [S3](#s3) [S5](#s5)

### Safe prova correção ou garante aplicação?

Não. Os construtores atribuem uma classificação sem verificação semântica, e o consumidor ainda verifica admissão, isolamento e posição. A classificação expressa política e intenção do autor; não é prova observada de correção.

[S7](#s7) [S12](#s12) [S13](#s13)

### Correções apenas para exibição podem passar por applies?

O método isolado retorna verdadeiro com limiar `DisplayOnly`. O chamador `fix_file` selecionado obtém somente `Safe` ou `Unsafe` de `required_applicability`, excluindo ali correções apenas para exibição. É necessário distinguir o domínio do método do domínio do chamador.

[S6](#s6) [S8](#s8) [S11](#s11) [S12](#s12)

### try_set_fix evita a construção quando a correção está desabilitada?

O corpo selecionado não estabelece isso. Ele invoca `func()` primeiro e só delega um resultado `Ok` a `set_fix`, onde ocorre a consulta de seleção da regra. Um erro é registrado em vez de ser anexado como correção.

[S9](#s9)

### Um conflito de posição ignorado deixa o grupo sem reserva?

Não necessariamente no corpo selecionado. Quando resta uma edição nova, a inserção do grupo precede a consulta de posição, e essa rejeição posterior não tem remoção correspondente do grupo. É uma observação da ordem na fonte, e não um cenário executado no Ruff.

[S13](#s13)

### Esta campanha executou correções, testes ou gravações por fix_file?

Não. Corpos de fontes e testes foram inspecionados sem executar o Ruff. O corpo selecionado de `fix_file` constrói um resultado opcional; não grava um arquivo por si. Esta revisão não sustenta afirmações de testes aprovados, expansão de macros, persistência ou semântica do programa completo.

[S12](#s12) [S15](#s15)

## Exemplo de reprodução somente para leitura

A recuperação Git equivalente foi executada na aquisição das fontes. Execute no checkout do Ruff apenas para exibir a fonte fixada; o comando não invoca o programa. Não é exemplo Rust nem resultado de teste.

```sh
git -c core.fsmonitor=false show 0222c19dd8e0c9a927f2e47bf3774a108431da25:crates/ruff_linter/src/fix/mod.rs
```

## Referências às fontes e direitos

<a id="s1"></a> [S1: crates/ruff_linter/src/violation.rs:14–117](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/violation.rs#L14-L117)

<a id="s2"></a> [S2: crates/ruff_macros/src/violation_metadata.rs:8–60](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_macros/src/violation_metadata.rs#L8-L60)

<a id="s3"></a> [S3: crates/ruff_db/src/diagnostic/mod.rs:60–80](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_db/src/diagnostic/mod.rs#L60-L80)

<a id="s4"></a> [S4: crates/ruff_db/src/diagnostic/mod.rs:373–402](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_db/src/diagnostic/mod.rs#L373-L402)

<a id="s5"></a> [S5: crates/ruff_linter/src/message/mod.rs:82–135](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/message/mod.rs#L82-L135)

<a id="s6"></a> [S6: crates/ruff_diagnostics/src/fix.rs:8–55](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_diagnostics/src/fix.rs#L8-L55)

<a id="s7"></a> [S7: crates/ruff_diagnostics/src/fix.rs:57–141](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_diagnostics/src/fix.rs#L57-L141)

<a id="s8"></a> [S8: crates/ruff_diagnostics/src/fix.rs:143–185](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_diagnostics/src/fix.rs#L143-L185)

<a id="s9"></a> [S9: crates/ruff_linter/src/checkers/ast/mod.rs:3889–3933](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/checkers/ast/mod.rs#L3889-L3933)

<a id="s10"></a> [S10: crates/ruff_linter/src/settings/fix_safety_table.rs:23–42](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/settings/fix_safety_table.rs#L23-L42)

<a id="s11"></a> [S11: crates/ruff_linter/src/settings/types.rs:125–168](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/settings/types.rs#L125-L168)

<a id="s12"></a> [S12: crates/ruff_linter/src/fix/mod.rs:20–51](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/fix/mod.rs#L20-L51)

<a id="s13"></a> [S13: crates/ruff_linter/src/fix/mod.rs:53–128](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/fix/mod.rs#L53-L128)

<a id="s14"></a> [S14: crates/ruff_linter/src/fix/mod.rs:130–170](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/fix/mod.rs#L130-L170)

<a id="s15"></a> [S15: crates/ruff_linter/src/fix/mod.rs:172–213](https://github.com/astral-sh/ruff/blob/0222c19dd8e0c9a927f2e47bf3774a108431da25/crates/ruff_linter/src/fix/mod.rs#L172-L213)

[R1: Rust derived enum ordering](https://doc.rust-lang.org/std/cmp/trait.Ord.html#derivable). Referência primária atual da linguagem; não é evidência de execução de ferramenta histórica.

A LICENSE completa da raiz, incluindo avisos de terceiros, foi preservada com as fontes. O repositório selecionado usa licença MIT na raiz; não se infere autorização geral por arquivo, para treinamento ou para publicação pública. Os artefatos da campanha permanecem material interno restrito de revisão.
