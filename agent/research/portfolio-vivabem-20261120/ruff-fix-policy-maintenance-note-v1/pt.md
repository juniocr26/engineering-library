# Manutenção do Ruff: presença da explicação, conteúdo e limites da política de correções

`astral-sh/ruff`: `47a28e3a2e2cfcc711f6f68eb7267731478e4a81` → `0e1bf0d2f6bf100ec93f164efcd98514fb12b348`

READY_FOR_OWNER_REVIEW · somente fontes · sem aprovação do proprietário, Gold, inferência neural ou treinamento.

## Uma revisão real, com conclusões delimitadas

Esta nota de manutenção revisada manualmente compara uma revisão local e sua revisão anterior no Ruff já exposto em desenvolvimento. O commit muda dez arquivos; o pacote preservado contém onze arquivos selecionados em cada revisão. Cinco dependências alteradas foram lidas junto aos arquivos inalterados de política de correções. Não houve execução de compilador Rust, saída gerada de macros, aplicação Ruff, testes do projeto, vinculador ou experimento de tamanho de binário. As cláusulas EN/PT abaixo foram escritas após a inspeção; não são previsões cegas nem resultado de um agente autônomo de manutenção.

## A interface da explicação muda

Antes: `ViolationMetadata::explain` retorna `Option<&'static str>`. Depois: retorna `&'static str`. O gerador de metadados selecionado deixa de envolver a documentação coletada em `Some` e passa a emiti-la diretamente, enquanto a assinatura gerada de `Rule::explanation` muda de forma correspondente. Uma cláusula que documente o retorno opcional precisa ser modificada para a revisão posterior. É uma mudança de interface na fonte, e não uma falha de compilação observada em um consumidor.

## A construção da URL deixa de consultar a explicação

Antes: `Rule::url` retorna `Option<String>` e constrói a URL sob a condição `self.explanation().is_some()`. Depois: retorna `String` usando o mesmo padrão de formatação com página inicial e nome da regra, sem consultar a explicação. O auxiliar de diagnóstico muda de forma correspondente: deixa de passar `rule.url()` e passa a fornecer `Some(rule.url())`. Não se demonstrou que a API de armazenamento opcional tenha se tornado obrigatória. O comentário da fonte aponta evitar a retenção de textos de documentação como motivação; esta campanha não mediu alocação, vinculação, tamanho de binário ou velocidade.

## Retornar texto não prova conteúdo não vazio

A implementação de `get_docs` inspecionada começa com texto vazio, acrescenta atributos de documentação reconhecidos e retorna o texto acumulado. Sem esses atributos, o corpo selecionado não rejeita um resultado vazio. Antes, o gerador selecionado já envolvia esse texto em `Some`, que ainda pode conter texto vazio. O teste do registro deixa de consultar `is_some()` e passa a verificar `!trim().is_empty()`. Isso fortalece a asserção inspecionada sobre o conteúdo, mas o teste não foi executado e não estabelece que a documentação de todas as regras atuais tenha passado.

## Corpos inalterados de política sustentam uma cláusula local mantida

Os arquivos completos que definem `Fix`, `fix_file`/`apply_fixes` e `FixSafetyTable` são idênticos byte a byte entre essas revisões. O arquivo de configurações também é idêntico entre elas; seu enum e implementação selecionados de `UnsafeFixes` correspondem ainda à captura posterior de HEAD, embora o arquivo completo posterior de configurações seja diferente. Portanto, a cláusula delimitada às fontes sobre `Enabled` selecionar `Unsafe` e `Disabled`/`Hint` selecionarem `Safe` pode manter o texto nesse par. Isso não prova equivalência comportamental do programa inteiro nem alcance inalterado das chamadas.

## Ações de manutenção dependem da cláusula exata

Para uma cláusula sobre a assinatura de retorno da explicação ou da URL, a ação é `MODIFY`. Para a descrição do corpo selecionado do limiar de correções, a ação sobre o texto semântico é `NO-OP` dentro desse escopo limitado às fontes. Se o documento deve citar a nova revisão-alvo, sua referência de revisão e as evidências vinculadas ainda precisam mudar mesmo quando o texto permanece. O capítulo inteiro não deve ser classificado como inalterado somente porque arquivos selecionados de correções coincidem. Não se infere dessas cláusulas escritas nenhuma afirmação de `ADD` ou `REMOVE`, decisão efetiva de agente ou pontuação independente.

## FAQ

### O gerador anterior necessariamente retornava None quando faltava documentação?

Não. Sua saída selecionada envolve o texto coletado em `Some`; o corpo de coleta pode produzir texto vazio. Opcionalidade e conteúdo não vazio são propriedades diferentes.

### A nova assinatura de texto garante que toda documentação seja não vazia?

Não. O tipo de retorno isolado não expressa conteúdo não vazio. O teste fortalecido do registro verifica conteúdo após remover espaços das extremidades, mas esta campanha apenas inspecionou sua declaração.

### O armazenamento da URL do diagnóstico perdeu seu tipo opcional?

Isso não decorre da mudança. O chamador selecionado agora envolve explicitamente a URL retornada em `Some`. Esta nota não estabelece migração do esquema de armazenamento nem executa um consumidor.

### Os arquivos de aplicação de correções mudaram neste commit?

Os arquivos completos selecionados `fix.rs`, `fix/mod.rs` e da tabela de segurança não mudaram. Outros arquivos mudaram, incluindo interfaces de metadados e consumidores; igualdade local não é equivalência do commit inteiro.

### Texto inalterado pode manter referências desatualizadas à revisão?

Não quando o contrato de documentação exige a nova revisão. Manter uma cláusula semântica e atualizar sua proveniência são decisões separadas de manutenção; os hashes precisam vincular os bytes efetivos do alvo.

### O benefício alegado sobre retenção de documentação foi medido?

Não. O caminho de chamada alterado e seu comentário foram inspecionados. Não houve compilação, observação do vinculador, comparação de binários ou benchmark; o benefício pretendido permanece sem medição aqui.

## Evidência e reprodução

Foram realizadas recuperação Git somente para leitura e inspeção de diferenças. O JSON de trechos preserva dezoito excertos vinculados a arquivos e intervalos de linhas nativas; o manifesto preserva vinte e dois arquivos selecionados, incluindo ambas as licenças completas da raiz e avisos de terceiros. Os comandos abaixo inspecionam a mudança de interface e não executam o Ruff.

```sh
git -c core.fsmonitor=false diff --no-ext-diff --no-renames 47a28e3a2e2cfcc711f6f68eb7267731478e4a81 0e1bf0d2f6bf100ec93f164efcd98514fb12b348 -- crates/ruff_linter/src/violation.rs
```

[before: crates/ruff_linter/src/violation.rs](https://github.com/astral-sh/ruff/blob/47a28e3a2e2cfcc711f6f68eb7267731478e4a81/crates/ruff_linter/src/violation.rs)

[before: crates/ruff_macros/src/violation_metadata.rs](https://github.com/astral-sh/ruff/blob/47a28e3a2e2cfcc711f6f68eb7267731478e4a81/crates/ruff_macros/src/violation_metadata.rs)

[before: crates/ruff_linter/src/registry.rs](https://github.com/astral-sh/ruff/blob/47a28e3a2e2cfcc711f6f68eb7267731478e4a81/crates/ruff_linter/src/registry.rs)

[before: crates/ruff_macros/src/map_codes.rs](https://github.com/astral-sh/ruff/blob/47a28e3a2e2cfcc711f6f68eb7267731478e4a81/crates/ruff_macros/src/map_codes.rs)

[before: crates/ruff_linter/src/message/mod.rs](https://github.com/astral-sh/ruff/blob/47a28e3a2e2cfcc711f6f68eb7267731478e4a81/crates/ruff_linter/src/message/mod.rs)

[after: crates/ruff_linter/src/violation.rs](https://github.com/astral-sh/ruff/blob/0e1bf0d2f6bf100ec93f164efcd98514fb12b348/crates/ruff_linter/src/violation.rs)

[after: crates/ruff_macros/src/violation_metadata.rs](https://github.com/astral-sh/ruff/blob/0e1bf0d2f6bf100ec93f164efcd98514fb12b348/crates/ruff_macros/src/violation_metadata.rs)

[after: crates/ruff_linter/src/registry.rs](https://github.com/astral-sh/ruff/blob/0e1bf0d2f6bf100ec93f164efcd98514fb12b348/crates/ruff_linter/src/registry.rs)

[after: crates/ruff_macros/src/map_codes.rs](https://github.com/astral-sh/ruff/blob/0e1bf0d2f6bf100ec93f164efcd98514fb12b348/crates/ruff_macros/src/map_codes.rs)

[after: crates/ruff_linter/src/message/mod.rs](https://github.com/astral-sh/ruff/blob/0e1bf0d2f6bf100ec93f164efcd98514fb12b348/crates/ruff_linter/src/message/mod.rs)

Artefato interno de revisão; direitos e independência permanecem restritos conforme os registros da campanha.
