# Registro de evidência: chapters / ruff-target-version.json

Este é um artefato bruto de pesquisa de um recorte datado. Resultados e saídas rejeitadas do modelo mantêm o status registrado. Ler o registro não aprova publicação nem treinamento.

SHA-256: `f75aa7917efe5e8ca1fcc77f32a9cf86aad45c4ce487ba6bf2e401d06a8981e0`. Bytes originais: `31259`.

Caminho original: `agent/research/documentation-intelligence-20261119/body-claim-bundles-v1/chapters/ruff-target-version.json`.

<!-- reading-section:reference:f75aa7917efe5e8ca1fc:consumers -->
## Referenciado por

- [Revisão de evidências por capítulo](../reviews/body-claims.md)

<!-- reading-section:reference:f75aa7917efe5e8ca1fc:artifact -->
## Artefato original

O bloco reproduz o artefato UTF-8 exato; acrescenta-se uma quebra final apenas para exibição se ela não existir no original.

<!-- artifact-body:f75aa7917efe5e8ca1fcc77f32a9cf86aad45c4ce487ba6bf2e401d06a8981e0:start -->
````json
{
  "chapter": "ruff-target-version",
  "derived_review_artifact_not_new_chapter_or_training_example": true,
  "document_language_spans": 20,
  "owner_approved": false,
  "prose_groups": 10,
  "records": [
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/en.md",
          "document_sha256": "5cc31c9bbb136d62da3f73b943b15f194afdb8e44dbf8f44cc8d292952435dbc",
          "first_line": 3,
          "last_line": 3,
          "quote": "Codex-authored correction reviewed against pinned source; pending owner approval.\n",
          "quote_sha256": "5183118486208939d931bd1952616e8990fad05963d3432fe88f73443478a456"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/pt-br.md",
          "document_sha256": "af65fcd22a8889ba7fc34a165660855dac2f6f40b24b0b5036a37af90b973867",
          "first_line": 3,
          "last_line": 3,
          "quote": "Correção escrita pelo Codex e revisada contra fonte fixada; pendente de aprovação do proprietário.\n",
          "quote_sha256": "2e3dac3bb0426a273dd86f93e3ed60bb02b5a0e7aa5acbcbd54f2a561665e25c"
        }
      },
      "bilingual_review": "Completepairedprose manuallycompared with physicalsource; resultdomain, intermediate/finalstate, flagparentbranches, bitwiseoperators and channel/loopboundaries preserved. Inlineidentifiers match.",
      "chapter": "ruff-target-version",
      "execution_or_inspection_receipts": [],
      "id": "ruff-target-version:body-paragraph:01",
      "manual_review_finding": "Authoredcorrection pendingownerapproval.",
      "owner_approved": false,
      "scope": "PreFAQprose only; headings,tables,fences andFAQ excluded.",
      "source_span_ids": [],
      "status": "EDITORIAL_STATUS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/en.md",
          "document_sha256": "5cc31c9bbb136d62da3f73b943b15f194afdb8e44dbf8f44cc8d292952435dbc",
          "first_line": 5,
          "last_line": 5,
          "quote": "Repository: ruff; revision: 0222c19dd8e0c9a927f2e47bf3774a108431da25; baseline: ruff-target-version. [Exact source excerpts](source-excerpts.json).\n",
          "quote_sha256": "6533bb07496791034dbf0fb41f1180c34b2f5d197026a0003313ce1260493f46"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/pt-br.md",
          "document_sha256": "af65fcd22a8889ba7fc34a165660855dac2f6f40b24b0b5036a37af90b973867",
          "first_line": 5,
          "last_line": 5,
          "quote": "Repository: ruff; revision: 0222c19dd8e0c9a927f2e47bf3774a108431da25; baseline: ruff-target-version. [Exact source excerpts](source-excerpts.json).\n",
          "quote_sha256": "6533bb07496791034dbf0fb41f1180c34b2f5d197026a0003313ce1260493f46"
        }
      },
      "bilingual_review": "Completepairedprose manuallycompared with physicalsource; resultdomain, intermediate/finalstate, flagparentbranches, bitwiseoperators and channel/loopboundaries preserved. Inlineidentifiers match.",
      "chapter": "ruff-target-version",
      "execution_or_inspection_receipts": [
        {
          "path": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/review.json",
          "role": "Dated review/inspection or historical owned language-probe result, not a new external application execution.",
          "sha256": "a2fde11870cf50486d20d06c7b59a56abe6830fef0582b07e02cc86645ce8ac4"
        }
      ],
      "id": "ruff-target-version:body-paragraph:02",
      "manual_review_finding": "PinnedRuffrevision and retainedbaseline.",
      "owner_approved": false,
      "scope": "PreFAQprose only; headings,tables,fences andFAQ excluded.",
      "source_span_ids": [
        "source-span-145"
      ],
      "status": "PROVENANCE",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/en.md",
          "document_sha256": "5cc31c9bbb136d62da3f73b943b15f194afdb8e44dbf8f44cc8d292952435dbc",
          "first_line": 9,
          "last_line": 9,
          "quote": "The actual local-agent baseline correctly associated the method with `FormatterSettings` and noticed a path-based helper followed by a fallback. It nevertheless described a target version for a Rust project. The selected signature explicitly returns `PythonVersion`. Rust is the implementation language of this method; it is not the version domain named by its result type. The same domain error appeared in both generated languages.\n",
          "quote_sha256": "95b406dab34b16dab798149176e53d3cdbfbf61b34345f8d313d390c5dd36194"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/pt-br.md",
          "document_sha256": "af65fcd22a8889ba7fc34a165660855dac2f6f40b24b0b5036a37af90b973867",
          "first_line": 9,
          "last_line": 9,
          "quote": "O baseline real do agente local associou corretamente o método a `FormatterSettings` e percebeu um helper baseado em caminho seguido de fallback. Ainda assim, descreveu uma versão alvo para um projeto Rust. A assinatura selecionada retorna explicitamente `PythonVersion`. Rust é a linguagem de implementação deste método; não é o domínio de versão nomeado pelo tipo de resultado. O mesmo erro de domínio apareceu nos dois idiomas gerados.\n",
          "quote_sha256": "db7e18b0ee23af0b81cb6e73438b4a632f1ebc4d30d4c14ee4f5c31626bcef79"
        }
      },
      "bilingual_review": "Completepairedprose manuallycompared with physicalsource; resultdomain, intermediate/finalstate, flagparentbranches, bitwiseoperators and channel/loopboundaries preserved. Inlineidentifiers match.",
      "chapter": "ruff-target-version",
      "execution_or_inspection_receipts": [
        {
          "path": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/review.json",
          "role": "Dated review/inspection or historical owned language-probe result, not a new external application execution.",
          "sha256": "a2fde11870cf50486d20d06c7b59a56abe6830fef0582b07e02cc86645ce8ac4"
        }
      ],
      "id": "ruff-target-version:body-paragraph:03",
      "manual_review_finding": "PythonVersionresultdomain differsfromRustimplementationlanguage; helper/fallback usefulsubclaims retained.",
      "owner_approved": false,
      "scope": "PreFAQprose only; headings,tables,fences andFAQ excluded.",
      "source_span_ids": [
        "source-span-145"
      ],
      "status": "REVIEW_PROCESS_AND_SOURCE",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/en.md",
          "document_sha256": "5cc31c9bbb136d62da3f73b943b15f194afdb8e44dbf8f44cc8d292952435dbc",
          "first_line": 11,
          "last_line": 11,
          "quote": "The selected method is `resolve_target_version(&self, path: &Path) -> PythonVersion`. Its receiver is shared and its path argument is borrowed. This declaration and the short body identify a settings lookup. They do not establish a formatter run, a parsed Python module, a project-language detection procedure or a compiler invocation. No Ruff executable or Rust project was run for this chapter.\n",
          "quote_sha256": "e16a3c07b344971bbd1934aca235a2936deec67dd8a7938db82a96283792c140"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/pt-br.md",
          "document_sha256": "af65fcd22a8889ba7fc34a165660855dac2f6f40b24b0b5036a37af90b973867",
          "first_line": 11,
          "last_line": 11,
          "quote": "O método selecionado é `resolve_target_version(&self, path: &Path) -> PythonVersion`. Seu receptor é compartilhado e o argumento de caminho é emprestado. Essa declaração e o corpo curto identificam uma consulta às configurações. Não estabelecem uma execução do formatador, um módulo Python interpretado, um procedimento de detecção da linguagem do projeto ou uma invocação de compilador. Nenhum executável Ruff ou projeto Rust foi executado para este capítulo.\n",
          "quote_sha256": "5001b46e88bb8d182ffd13e1c2c357b27820b11eeb0d2dcbf8655ee5145c110e"
        }
      },
      "bilingual_review": "Completepairedprose manuallycompared with physicalsource; resultdomain, intermediate/finalstate, flagparentbranches, bitwiseoperators and channel/loopboundaries preserved. Inlineidentifiers match.",
      "chapter": "ruff-target-version",
      "execution_or_inspection_receipts": [],
      "id": "ruff-target-version:body-paragraph:04",
      "manual_review_finding": "Borrowedsharedreceiver/path andPythonVersionresult implythislookupbody, not formatter/compilerexecution orprojectlanguage detection.",
      "owner_approved": false,
      "scope": "PreFAQprose only; headings,tables,fences andFAQ excluded.",
      "source_span_ids": [
        "source-span-145"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/en.md",
          "document_sha256": "5cc31c9bbb136d62da3f73b943b15f194afdb8e44dbf8f44cc8d292952435dbc",
          "first_line": 15,
          "last_line": 15,
          "quote": "The body calls `self.per_file_target_version.is_match(path)` and then applies `unwrap_or(self.unresolved_target_version)`. The spelling is important: there is no local conditional returning a Boolean and no numeric version literal in this method. Under the ordinary Option interpretation of the call chain, a supplied matching value is used; absent that value, the stored unresolved target supplies the fallback.\n",
          "quote_sha256": "ff9d6ee04bba39a20fb1bdab76af68eb1f682b36cd5df5ccf7918f0a1ef3823c"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/pt-br.md",
          "document_sha256": "af65fcd22a8889ba7fc34a165660855dac2f6f40b24b0b5036a37af90b973867",
          "first_line": 15,
          "last_line": 15,
          "quote": "O corpo chama `self.per_file_target_version.is_match(path)` e então aplica `unwrap_or(self.unresolved_target_version)`. A grafia importa: não há condicional local retornando um booleano nem literal numérico de versão neste método. Sob a interpretação comum de Option na cadeia de chamadas, um valor correspondente fornecido é usado; na ausência desse valor, o alvo não resolvido armazenado fornece o fallback.\n",
          "quote_sha256": "a50c5cf9614ce4588caa6bd184898786a9935f4dd163e5daf5de7e49f397a71a"
        }
      },
      "bilingual_review": "Completepairedprose manuallycompared with physicalsource; resultdomain, intermediate/finalstate, flagparentbranches, bitwiseoperators and channel/loopboundaries preserved. Inlineidentifiers match.",
      "chapter": "ruff-target-version",
      "execution_or_inspection_receipts": [],
      "id": "ruff-target-version:body-paragraph:05",
      "manual_review_finding": "is_match followedbyunwrap_or storedfallback; Optionnormalinterpretation, not Boolean/numericliteral result.",
      "owner_approved": false,
      "scope": "PreFAQprose only; headings,tables,fences andFAQ excluded.",
      "source_span_ids": [
        "source-span-145",
        "source-span-146"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/en.md",
          "document_sha256": "5cc31c9bbb136d62da3f73b943b15f194afdb8e44dbf8f44cc8d292952435dbc",
          "first_line": 17,
          "last_line": 17,
          "quote": "That describes the visible selection boundary. It does not reveal the helper's matching algorithm. The original selected packet did not include the implementation of `is_match`, so it did not establish glob precedence, first-versus-last match behavior, path normalization, filesystem access or reconciliation of overlapping rules. The additional source reviewed below establishes a narrower compiled-list selection order. A method name suggesting a match is not enough to fill those gaps with an invented algorithm.\n",
          "quote_sha256": "8f18e803f98ed5bc0af0411a7f46d0342b816bdfeb53ae20a0ca61a163f3c1fb"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/pt-br.md",
          "document_sha256": "af65fcd22a8889ba7fc34a165660855dac2f6f40b24b0b5036a37af90b973867",
          "first_line": 17,
          "last_line": 17,
          "quote": "Isso descreve o limite de seleção visível. Não revela o algoritmo de correspondência do helper. O pacote selecionado original não incluía a implementação de `is_match`, portanto não estabelecia precedência de globs, escolha da primeira ou última correspondência, normalização de caminhos, acesso ao sistema de arquivos ou reconciliação de regras sobrepostas. A fonte adicional revisada abaixo estabelece uma ordem de seleção mais restrita na lista compilada. Um nome de método que sugere correspondência não basta para preencher essas lacunas com um algoritmo inventado.\n",
          "quote_sha256": "f5745e8b337b363474d7ce101e401b18a7e4b35b8e51d2b19484a866f48fee7a"
        }
      },
      "bilingual_review": "Completepairedprose manuallycompared with physicalsource; resultdomain, intermediate/finalstate, flagparentbranches, bitwiseoperators and channel/loopboundaries preserved. Inlineidentifiers match.",
      "chapter": "ruff-target-version",
      "execution_or_inspection_receipts": [],
      "id": "ruff-target-version:body-paragraph:06",
      "manual_review_finding": "Originalcaller didnotshowalgorithm; addedcompiledlist source supportsnarroworder only, not inventednormalization/filesystem/generalglobbehavior.",
      "owner_approved": false,
      "scope": "PreFAQprose only; headings,tables,fences andFAQ excluded.",
      "source_span_ids": [
        "source-span-145",
        "source-span-147",
        "source-span-146"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/en.md",
          "document_sha256": "5cc31c9bbb136d62da3f73b943b15f194afdb8e44dbf8f44cc8d292952435dbc",
          "first_line": 21,
          "last_line": 21,
          "quote": "The accompanying field excerpt declares `unresolved_target_version` as `PythonVersion` and `per_file_target_version` as `CompiledPerFileTargetVersionList`. Their distinct types make the roles clearer: one stores a version value, while the other supplies per-file resolution behavior through a helper. The selected method reads them; the body contains no assignment that updates either field.\n",
          "quote_sha256": "e1cd40de284022d07d2593a85d0ccbe9129910c3048442f5d5dec95c72b97b9a"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/pt-br.md",
          "document_sha256": "af65fcd22a8889ba7fc34a165660855dac2f6f40b24b0b5036a37af90b973867",
          "first_line": 21,
          "last_line": 21,
          "quote": "O trecho de campos anexo declara `unresolved_target_version` como `PythonVersion` e `per_file_target_version` como `CompiledPerFileTargetVersionList`. Seus tipos distintos esclarecem os papéis: um armazena um valor de versão, enquanto o outro fornece resolução por arquivo através de um helper. O método selecionado os lê; o corpo não contém atribuição que atualize qualquer dos campos.\n",
          "quote_sha256": "c2e8466892298364f650df0030d0151ad65388562dc2f523e2db1de86280cdc0"
        }
      },
      "bilingual_review": "Completepairedprose manuallycompared with physicalsource; resultdomain, intermediate/finalstate, flagparentbranches, bitwiseoperators and channel/loopboundaries preserved. Inlineidentifiers match.",
      "chapter": "ruff-target-version",
      "execution_or_inspection_receipts": [],
      "id": "ruff-target-version:body-paragraph:07",
      "manual_review_finding": "Distinctversion andcompiledlist fieldtypes, readwithoutassignment.",
      "owner_approved": false,
      "scope": "PreFAQprose only; headings,tables,fences andFAQ excluded.",
      "source_span_ids": [
        "source-span-148",
        "source-span-145"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/en.md",
          "document_sha256": "5cc31c9bbb136d62da3f73b943b15f194afdb8e44dbf8f44cc8d292952435dbc",
          "first_line": 23,
          "last_line": 23,
          "quote": "The word unresolved in the field name must not be translated into an error return. The declared method returns `PythonVersion`, and the visible expression supplies a stored fallback. Conversely, the presence of a fallback does not reveal its numeric value or prove it is the latest supported Python release. Establishing a concrete configured default would require the relevant construction and configuration evidence, rather than a guess from this field name.\n",
          "quote_sha256": "765ee67a4cdee96d4eae8ed1358df59deea3daec699a81d1635ce2ed8a0eebfa"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/pt-br.md",
          "document_sha256": "af65fcd22a8889ba7fc34a165660855dac2f6f40b24b0b5036a37af90b973867",
          "first_line": 23,
          "last_line": 23,
          "quote": "A palavra unresolved no nome do campo não deve ser traduzida como retorno de erro. O método declarado retorna `PythonVersion`, e a expressão visível fornece um fallback armazenado. Por outro lado, a presença de fallback não revela seu valor numérico nem prova que seja a versão Python mais recente suportada. Estabelecer um padrão configurado concreto exigiria evidências relevantes de construção e configuração, em vez de adivinhação pelo nome desse campo.\n",
          "quote_sha256": "43e66c03285100df2d66d23cc0724da16f1d27a91240a09a5c9d822c411917ad"
        }
      },
      "bilingual_review": "Completepairedprose manuallycompared with physicalsource; resultdomain, intermediate/finalstate, flagparentbranches, bitwiseoperators and channel/loopboundaries preserved. Inlineidentifiers match.",
      "chapter": "ruff-target-version",
      "execution_or_inspection_receipts": [],
      "id": "ruff-target-version:body-paragraph:08",
      "manual_review_finding": "Unresolvedfieldname is not errorreturn orproofoflatestnumericdefault; configurationconstruction remainsneeded.",
      "owner_approved": false,
      "scope": "PreFAQprose only; headings,tables,fences andFAQ excluded.",
      "source_span_ids": [
        "source-span-148",
        "source-span-145"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/en.md",
          "document_sha256": "5cc31c9bbb136d62da3f73b943b15f194afdb8e44dbf8f44cc8d292952435dbc",
          "first_line": 27,
          "last_line": 27,
          "quote": "A useful caller-facing summary is that the method resolves a Python target version for the supplied path using a per-file lookup and the stored unresolved target as fallback. It should retain the `PythonVersion` result domain and identify the helper call without promising unsupported matching semantics. This is more informative than saying only that it resolves a target, while remaining within the selected evidence.\n",
          "quote_sha256": "a4476b6d8c35974bee1b559efd54b3914e8a1fb0f4ae1ad859513e296fbf65ca"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/pt-br.md",
          "document_sha256": "af65fcd22a8889ba7fc34a165660855dac2f6f40b24b0b5036a37af90b973867",
          "first_line": 27,
          "last_line": 27,
          "quote": "Um resumo útil para o chamador é que o método resolve uma versão alvo Python para o caminho recebido usando busca por arquivo e o alvo não resolvido armazenado como fallback. Deve preservar o domínio de resultado `PythonVersion` e identificar a chamada ao helper sem prometer semânticas de correspondência não sustentadas. Isso informa mais que dizer apenas que resolve um alvo, mantendo o limite da evidência selecionada.\n",
          "quote_sha256": "08b833123083b196bae5921fe4ac4d1e9a2feebc4a4aed0dadbc6c0e1aeae7d2"
        }
      },
      "bilingual_review": "Completepairedprose manuallycompared with physicalsource; resultdomain, intermediate/finalstate, flagparentbranches, bitwiseoperators and channel/loopboundaries preserved. Inlineidentifiers match.",
      "chapter": "ruff-target-version",
      "execution_or_inspection_receipts": [],
      "id": "ruff-target-version:body-paragraph:09",
      "manual_review_finding": "Caller-facingPythonpathlookup withstoredfallback retains helperboundary; no extraalgorithm inferred.",
      "owner_approved": false,
      "scope": "PreFAQprose only; headings,tables,fences andFAQ excluded.",
      "source_span_ids": [
        "source-span-145"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/en.md",
          "document_sha256": "5cc31c9bbb136d62da3f73b943b15f194afdb8e44dbf8f44cc8d292952435dbc",
          "first_line": 29,
          "last_line": 29,
          "quote": "The correction reuses the original completed model response and its pinned source; it does not rerun a rejected prompt. The whole baseline remains unapproved despite its useful subclaims. Exact source hashes, license notices and bilingual review records accompany these chapters. Code-span parity checks translation consistency, but cannot by itself prove semantic truth, owner approval, training rights or improvement in the local model.\n",
          "quote_sha256": "656409929d1ec551c62216be2b6087c6d3fec7168db6d2810e724996d0e37dbc"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/pt-br.md",
          "document_sha256": "af65fcd22a8889ba7fc34a165660855dac2f6f40b24b0b5036a37af90b973867",
          "first_line": 29,
          "last_line": 29,
          "quote": "A correção reutiliza a resposta original concluída do modelo e sua fonte fixada; não repete um prompt rejeitado. O baseline inteiro continua sem aprovação apesar de suas subafirmações úteis. Hashes exatos da fonte, avisos de licença e registros de revisão bilíngue acompanham estes capítulos. Paridade de trechos de código verifica consistência da tradução, mas não prova sozinha verdade semântica, aprovação do proprietário, direitos de treinamento ou melhora do modelo local.\n",
          "quote_sha256": "5914045b7e1cb9c145757e7372beecfd6ed8a3820bcf984347be6335dea4d467"
        }
      },
      "bilingual_review": "Completepairedprose manuallycompared with physicalsource; resultdomain, intermediate/finalstate, flagparentbranches, bitwiseoperators and channel/loopboundaries preserved. Inlineidentifiers match.",
      "chapter": "ruff-target-version",
      "execution_or_inspection_receipts": [
        {
          "path": "agent/research/documentation-intelligence-20261119/chapters/ruff-target-version/review.json",
          "role": "Dated review/inspection or historical owned language-probe result, not a new external application execution.",
          "sha256": "a2fde11870cf50486d20d06c7b59a56abe6830fef0582b07e02cc86645ce8ac4"
        }
      ],
      "id": "ruff-target-version:body-paragraph:10",
      "manual_review_finding": "Priorcompletedresponse reusedwithoutreprompting; source/parity/license review not ownerapproval,trainingrights orneuralimprovement.",
      "owner_approved": false,
      "scope": "PreFAQprose only; headings,tables,fences andFAQ excluded.",
      "source_span_ids": [
        "source-span-145"
      ],
      "status": "REVIEW_PROCESS_AND_SOURCE",
      "training_gold": false
    }
  ],
  "schema": "chapter-specific-body-claim-review-v1",
  "scope": "Proseparagraphs beforefirstFAQheading only; titles,tables,fences,FAQ/trailingcontext andgenericatomicentailment are separate.",
  "source_spans": [
    {
      "first_line": 264,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/ruff/crates/ruff_workspace/src/settings.rs",
      "full_file_sha256": "1cd5c228eaefa5d798d70c049ae79ec378ffc0cb3cb2d44858eef49cbdd9eff0",
      "id": "source-span-145",
      "last_line": 268,
      "quote": "    pub fn resolve_target_version(&self, path: &Path) -> PythonVersion {\n        self.per_file_target_version\n            .is_match(path)\n            .unwrap_or(self.unresolved_target_version)\n    }\n",
      "quote_sha256": "d2c21f84473438271b8a2f2548f58c8b7dc62a0795769e96ea8372b028afdc03",
      "repository": "ruff",
      "revision": "0222c19dd8e0c9a927f2e47bf3774a108431da25",
      "source_path": "crates/ruff_workspace/src/settings.rs"
    },
    {
      "first_line": 987,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/ruff/crates/ruff_linter/src/settings/types.rs",
      "full_file_sha256": "de4bcea28a982a9c98951baf4404523ba2cafb27083e4d5e942639ea4f794121",
      "id": "source-span-146",
      "last_line": 996,
      "quote": "    pub fn is_match(&self, path: &Path) -> Option<ast::PythonVersion> {\n        if self.0.is_empty() {\n            return None;\n        }\n\n        self.0\n            .iter_matches(path, \"Setting Python version\")\n            .next()\n            .copied()\n    }\n",
      "quote_sha256": "428949abaebf05b3bc67d5aa1607c1dcf3b7d315e683033995577222f4359c13",
      "repository": "ruff",
      "revision": "0222c19dd8e0c9a927f2e47bf3774a108431da25",
      "source_path": "crates/ruff_linter/src/settings/types.rs"
    },
    {
      "first_line": 827,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/ruff/crates/ruff_linter/src/settings/types.rs",
      "full_file_sha256": "de4bcea28a982a9c98951baf4404523ba2cafb27083e4d5e942639ea4f794121",
      "id": "source-span-147",
      "last_line": 884,
      "quote": "impl<T: std::fmt::Debug> CompiledPerFileList<T> {\n    /// Return an iterator over the entries in `self` that match the input `path`.\n    ///\n    /// `debug_label` is used for [`debug!`] messages explaining why certain patterns were matched.\n    pub(crate) fn iter_matches<'a, 'p>(\n        &'a self,\n        path: &'p Path,\n        debug_label: &'static str,\n    ) -> impl Iterator<Item = &'p T>\n    where\n        'a: 'p,\n    {\n        let file_name = path.file_name().expect(\"Unable to parse filename\");\n        let basename = Candidate::new(file_name);\n        let absolute = Candidate::new(path);\n        self.inner.iter().filter_map(move |entry| {\n            if entry.basename_matcher.is_match_candidate(&basename) {\n                if entry.negated {\n                    None\n                } else {\n                    debug!(\n                        \"{} for {:?} due to basename match on {:?}: {:?}\",\n                        debug_label,\n                        path,\n                        entry.basename_matcher.glob().regex(),\n                        entry.data\n                    );\n                    Some(&entry.data)\n                }\n            } else if entry.absolute_matcher.is_match_candidate(&absolute) {\n                if entry.negated {\n                    None\n                } else {\n                    debug!(\n                        \"{} for {:?} due to absolute match on {:?}: {:?}\",\n                        debug_label,\n                        path,\n                        entry.absolute_matcher.glob().regex(),\n                        entry.data\n                    );\n                    Some(&entry.data)\n                }\n            } else if entry.negated {\n                debug!(\n                    \"{} for {:?} due to negated pattern matching neither {:?} nor {:?}: {:?}\",\n                    debug_label,\n                    path,\n                    entry.basename_matcher.glob().regex(),\n                    entry.absolute_matcher.glob().regex(),\n                    entry.data\n                );\n                Some(&entry.data)\n            } else {\n                None\n            }\n        })\n    }\n}\n",
      "quote_sha256": "500d164e845d3def5b7952bf2a9341eef59df5e07d89a2d00256f7a92e57716d",
      "repository": "ruff",
      "revision": "0222c19dd8e0c9a927f2e47bf3774a108431da25",
      "source_path": "crates/ruff_linter/src/settings/types.rs"
    },
    {
      "first_line": 187,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/ruff/crates/ruff_workspace/src/settings.rs",
      "full_file_sha256": "1cd5c228eaefa5d798d70c049ae79ec378ffc0cb3cb2d44858eef49cbdd9eff0",
      "id": "source-span-148",
      "last_line": 195,
      "quote": "    /// See [`FormatterSettings::resolve_target_version`] for a way to obtain the Python version for\n    /// a given file, while respecting the overrides in `per_file_target_version`.\n    pub unresolved_target_version: PythonVersion,\n    /// Path-specific overrides to `unresolved_target_version`.\n    ///\n    /// See [`FormatterSettings::resolve_target_version`] for a way to check a given [`Path`]\n    /// against these patterns, while falling back to `unresolved_target_version` if none of them\n    /// match.\n    pub per_file_target_version: CompiledPerFileTargetVersionList,\n",
      "quote_sha256": "32e004245f0c7267f8df69fc4293a706fbbd84cd11b00b1c2c5576605c0b3fec",
      "repository": "ruff",
      "revision": "0222c19dd8e0c9a927f2e47bf3774a108431da25",
      "source_path": "crates/ruff_workspace/src/settings.rs"
    }
  ],
  "status": "CODEX_SOURCE_REVIEW_PENDING_OWNER",
  "training_gold": false
}
````
<!-- artifact-body:f75aa7917efe5e8ca1fcc77f32a9cf86aad45c4ce487ba6bf2e401d06a8981e0:end -->
