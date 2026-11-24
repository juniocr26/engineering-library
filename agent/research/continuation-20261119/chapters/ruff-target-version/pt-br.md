# Um método Rust seleciona uma versão alvo Python

Correção escrita pelo Codex e revisada contra fonte fixada; pendente de aprovação do proprietário.

Repository: ruff; revision: 0222c19dd8e0c9a927f2e47bf3774a108431da25; baseline: ruff-target-version. [Exact source excerpts](source-excerpts.json).

## Linguagem de implementação e domínio do resultado

O baseline real do agente local associou corretamente o método a `FormatterSettings` e percebeu um helper baseado em caminho seguido de fallback. Ainda assim, descreveu uma versão alvo para um projeto Rust. A assinatura selecionada retorna explicitamente `PythonVersion`. Rust é a linguagem de implementação deste método; não é o domínio de versão nomeado pelo tipo de resultado. O mesmo erro de domínio apareceu nos dois idiomas gerados.

O método selecionado é `resolve_target_version(&self, path: &Path) -> PythonVersion`. Seu receptor é compartilhado e o argumento de caminho é emprestado. Essa declaração e o corpo curto identificam uma consulta às configurações. Não estabelecem uma execução do formatador, um módulo Python interpretado, um procedimento de detecção da linguagem do projeto ou uma invocação de compilador. Nenhum executável Ruff ou projeto Rust foi executado para este capítulo.

## O resultado do helper é seguido por fallback

O corpo chama `self.per_file_target_version.is_match(path)` e então aplica `unwrap_or(self.unresolved_target_version)`. A grafia importa: não há condicional local retornando um booleano nem literal numérico de versão neste método. Sob a interpretação comum de Option na cadeia de chamadas, um valor correspondente fornecido é usado; na ausência desse valor, o alvo não resolvido armazenado fornece o fallback.

Isso descreve o limite de seleção visível. Não revela o algoritmo de correspondência do helper. O pacote selecionado não inclui a implementação de `is_match`, portanto não estabelece precedência de globs, escolha da primeira ou última correspondência, normalização de caminhos, acesso ao sistema de arquivos ou reconciliação de regras sobrepostas. Um nome de método que sugere correspondência não basta para preencher essas lacunas com um algoritmo inventado.

## Configurações armazenadas não são padrões numéricos

O trecho de campos anexo declara `unresolved_target_version` como `PythonVersion` e `per_file_target_version` como `CompiledPerFileTargetVersionList`. Seus tipos distintos esclarecem os papéis: um armazena um valor de versão, enquanto o outro fornece resolução por arquivo através de um helper. O método selecionado os lê; o corpo não contém atribuição que atualize qualquer dos campos.

A palavra unresolved no nome do campo não deve ser traduzida como retorno de erro. O método declarado retorna `PythonVersion`, e a expressão visível fornece um fallback armazenado. Por outro lado, a presença de fallback não revela seu valor numérico nem prova que seja a versão Python mais recente suportada. Estabelecer um padrão configurado concreto exigiria evidências relevantes de construção e configuração, em vez de adivinhação pelo nome desse campo.

## Documente o resultado e preserve o limite do helper

Um resumo útil para o chamador é que o método resolve uma versão alvo Python para o caminho recebido usando busca por arquivo e o alvo não resolvido armazenado como fallback. Deve preservar o domínio de resultado `PythonVersion` e identificar a chamada ao helper sem prometer semânticas de correspondência não sustentadas. Isso informa mais que dizer apenas que resolve um alvo, mantendo o limite da evidência selecionada.

A correção reutiliza a resposta original concluída do modelo e sua fonte fixada; não repete um prompt rejeitado. O baseline inteiro continua sem aprovação apesar de suas subafirmações úteis. Hashes exatos da fonte, avisos de licença e registros de revisão bilíngue acompanham estes capítulos. Paridade de trechos de código verifica consistência da tradução, mas não prova sozinha verdade semântica, aprovação do proprietário, direitos de treinamento ou melhora do modelo local.

