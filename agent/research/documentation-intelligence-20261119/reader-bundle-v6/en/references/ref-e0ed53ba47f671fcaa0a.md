# Evidence record: chapters / fastify-decoration-lookup.json

This is a dated raw research artifact. Findings and rejected model outputs retain their recorded status. Reading the record does not approve publication or training.

SHA-256: `e0ed53ba47f671fcaa0a29d49fd1a8a5e528361e84953bf3a94b9e29fbff158e`. Original bytes: `52954`.

Original path: `agent/research/documentation-intelligence-20261119/body-claim-bundles-v1/chapters/fastify-decoration-lookup.json`.

<!-- reading-section:reference:e0ed53ba47f671fcaa0a:consumers -->
## Referenced by

- [Per-chapter evidence review](../reviews/body-claims.md)

<!-- reading-section:reference:e0ed53ba47f671fcaa0a:artifact -->
## Original artifact

The fenced contents reproduce the exact UTF-8 artifact; a display-only terminal newline is added if the original lacks one.

<!-- artifact-body:e0ed53ba47f671fcaa0a29d49fd1a8a5e528361e84953bf3a94b9e29fbff158e:start -->
````json
{
  "chapter": "fastify-decoration-lookup",
  "derived_review_artifact_not_new_chapter_or_training_example": true,
  "document_language_spans": 30,
  "owner_approved": false,
  "prose_groups": 15,
  "records": [
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 3,
          "last_line": 3,
          "quote": "Codex-authored experimental correction reviewed against frozen source, pending human approval. Source: Fastify revision `825d7722e4932a39193729997c76535d0a963b6b`, `lib/decorate.js`. The actual local-agent baseline is `fastify-checkrequestexistence`. It contained only the request wrapper. This chapter explicitly expands the evidence to the reply wrapper, shared helpers, import names and export aliases from the same file. No Fastify module, HTTP server or inspected application source was executed.\n",
          "quote_sha256": "2f0f8ec3d0965eebef13e3824496a0924b7d09086586d5949f111e1678bd1784"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 3,
          "last_line": 3,
          "quote": "Correção experimental escrita pelo Codex e revisada na fonte congelada, pendente de aprovação humana. Fonte: Fastify na revisão `825d7722e4932a39193729997c76535d0a963b6b`, `lib/decorate.js`. O baseline real do agente local é `fastify-checkrequestexistence`. Ele continha somente o wrapper de requisição. Este capítulo amplia explicitamente a evidência para o wrapper de resposta, auxiliares compartilhados, nomes importados e aliases de exportação do mesmo arquivo. Nenhum módulo Fastify, servidor HTTP ou código de aplicação inspecionado foi executado.\n",
          "quote_sha256": "746763bdb25aff42fa3e1e5201e527d0e4d52c7ad41fc965f3e8551b084c1c9f"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [
        {
          "path": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/review.json",
          "role": "Dated review/inspection or historical owned language-probe result, not a new external application execution.",
          "sha256": "9bcd6b6580162c716e8d9f6d0e4bc441f41a74bdfa0fc4cf4155224812d90cd7"
        }
      ],
      "id": "fastify-decoration-lookup:body-paragraph:01",
      "manual_review_finding": "Frozenfile expansion beyond requestwrapper; no inspectedmodule/server execution.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-088",
        "source-span-089"
      ],
      "status": "PROVENANCE",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 7,
          "last_line": 7,
          "quote": "The function `checkRequestExistence` accepts a parameter named `name`. Its first condition is `name && hasKey(this[kRequest], name)`. A truthy result reaches the written return expression `true`. Only when that branch is not taken does the function reach the second condition, `name && hasInstanceProperty(this[kRequest], name)`. That branch also returns the written true expression when its condition is truthy.\n",
          "quote_sha256": "08344c5bf161fc7414fe10523219de20249ccc7a41eb87e5e34f0c618b791929"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 7,
          "last_line": 7,
          "quote": "A função `checkRequestExistence` recebe um parâmetro chamado `name`. Sua primeira condição é `name && hasKey(this[kRequest], name)`. Um resultado de valor lógico verdadeiro alcança a expressão escrita de retorno `true`. Somente quando esse ramo não é seguido a função alcança a segunda condição, `name && hasInstanceProperty(this[kRequest], name)`. Esse ramo também retorna a expressão true escrita quando sua condição tem valor lógico verdadeiro.\n",
          "quote_sha256": "7c093c9c5594e0c430d270e2dea5b81f7d42b24a678058568e0f26850d46d7c3"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [],
      "id": "fastify-decoration-lookup:body-paragraph:02",
      "manual_review_finding": "Twoorderedtruthy-name guards then explicitfallback; parameter is name.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-090"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 9,
          "last_line": 9,
          "quote": "The name participates in both short-circuit conditions. A falsy name prevents the corresponding helper operand from being evaluated in either guard. That observation does not determine the function's eventual result: there is still a final statement. It returns `checkExistence(this[kRequest].prototype, name)`. The wrapper has no unconditional false-return statement for an omitted name. The neural baseline invented exactly that fallback.\n",
          "quote_sha256": "a28bbb61a587a4abe32762af0f85ac3d201f55fa622d977bb814f6db11a0c693"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 9,
          "last_line": 9,
          "quote": "O nome participa das duas condições de curto-circuito. Um nome de valor lógico falso impede a avaliação do operando auxiliar correspondente em cada guarda. Essa observação não determina o resultado final da função: ainda existe uma instrução final. Ela retorna `checkExistence(this[kRequest].prototype, name)`. O wrapper não contém um retorno falso incondicional para um nome omitido. O baseline neural inventou precisamente essa alternativa.\n",
          "quote_sha256": "e76ebfcd9e532586d8ffb9e3e157ce2c552ca6146a7ad82bc013fe48924238f3"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [],
      "id": "fastify-decoration-lookup:body-paragraph:03",
      "manual_review_finding": "Falsyname skipsearlyhelpers but still reaches finalcall; no unconditionalfalse fallback.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-090"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 11,
          "last_line": 11,
          "quote": "The bracketed access is also part of the parameter-role distinction. The source does not pass a request object as the explicit argument to this function. It obtains a target through a property of the runtime receiver and passes the supplied name to helpers. The imported key's value and the actual receiver must not be inferred merely from the function's name.\n",
          "quote_sha256": "41d70b31f8e626e9e711b0111972fc1242f28c23fef40bcb247b7a267e53de02"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 11,
          "last_line": 11,
          "quote": "O acesso entre colchetes também faz parte da distinção de papéis. A fonte não passa um objeto de requisição como argumento explícito dessa função. Ela obtém um alvo por uma propriedade do receptor em execução e passa o nome fornecido aos auxiliares. O valor da chave importada e o receptor efetivo não devem ser inferidos apenas pelo nome da função.\n",
          "quote_sha256": "2729da0c77dbb0e97dfe6a721d684decf0b60a4479d8d48e7693c4dae5a55c36"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [],
      "id": "fastify-decoration-lookup:body-paragraph:04",
      "manual_review_finding": "Explicitnameargument differsfrom receiver-selectedtarget; actualkeyvalue/receiver needs separateevidence.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-090"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 15,
          "last_line": 15,
          "quote": "The function `checkReplyExistence` has the same sequence using `this[kReply]`. Its final call targets the corresponding prototype. This is useful corroboration of the written pattern, but it is one related decoration-lookup family. Two similarly shaped wrappers do not establish independent transfer or prove how every caller binds their receiver.\n",
          "quote_sha256": "9e5ad0727203671167d11f1c24328eea6d988b9a105eb8ed325eeb64b528c138"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 15,
          "last_line": 15,
          "quote": "A função `checkReplyExistence` tem a mesma sequência usando `this[kReply]`. Sua chamada final aponta para o protótipo correspondente. Isso corrobora o padrão escrito, mas pertence à mesma família de consulta de decorações. Dois wrappers semelhantes não estabelecem transferência independente nem provam como todo chamador vincula seus receptores.\n",
          "quote_sha256": "a614865edeae2f08e4b2dcdc8c325de5eaca37afadb7f0b6b61c6c97177f86e9"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [],
      "id": "fastify-decoration-lookup:body-paragraph:05",
      "manual_review_finding": "Replywrapper is samefamily/sibling shape, not independentevaluation or allcallers receiverproof.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-091"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 17,
          "last_line": 17,
          "quote": "The file obtains the two key names through a relative import and exports the wrappers under `existRequest` and `existReply`. These are explicit source relationships. The export aliases do not prove that a server has registered or invoked the functions in a particular runtime. This inspection neither loads the imported module nor creates requests or replies.\n",
          "quote_sha256": "34743493e0de6658bd39c8057b8b5cfe1c16c840e86180f1ea7bec2e294aea5d"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 17,
          "last_line": 17,
          "quote": "O arquivo obtém os dois nomes de chave por uma importação relativa e exporta os wrappers como `existRequest` e `existReply`. Essas são relações explícitas da fonte. Os aliases não provam que um servidor registrou ou chamou as funções em determinada execução. Esta inspeção não carrega o módulo importado nem cria requisições ou respostas.\n",
          "quote_sha256": "b211c4ca07f80e4ba7d703e00280d195591d8c60463e97c0939f804f6f4a32aa"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [],
      "id": "fastify-decoration-lookup:body-paragraph:06",
      "manual_review_finding": "Relativeimport plus exp_aliases are source relationships; not moduleload or invocationtrace.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-092",
        "source-span-093"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 21,
          "last_line": 21,
          "quote": "The helper `hasKey` checks the truthiness of a `props` property. When present, it calls that property's array-style search operation with a predicate comparing a stored key with the supplied name; otherwise, the written alternative result is false. The source does not validate that the property has every expected runtime method, and a property access or called operation is not automatically free of effects.\n",
          "quote_sha256": "7cb86ff0f259df363af0cafbf8c1394f55f0ca2b17f084916254e5b11da7fa7c"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 21,
          "last_line": 21,
          "quote": "O auxiliar `hasKey` verifica o valor lógico de uma propriedade `props`. Quando presente, chama a operação de busca no estilo de array dessa propriedade com um predicado que compara uma chave armazenada com o nome fornecido; caso contrário, a alternativa escrita é false. A fonte não valida que a propriedade tenha todos os métodos esperados em execução, e um acesso a propriedade ou uma operação chamada não é automaticamente livre de efeitos.\n",
          "quote_sha256": "dfa79b2dde9c365d09332a356d20971e855284e9275456b352d143563b9d444e"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [],
      "id": "fastify-decoration-lookup:body-paragraph:07",
      "manual_review_finding": "props truthiness and some predicate; no runtime-method or absence-of-getter-effects guarantee.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-094"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 23,
          "last_line": 23,
          "quote": "The helper `hasInstanceProperty` begins with a local cursor set to its first argument. While the cursor is truthy, it tests a property collection and its membership operation. A successful condition returns true. Otherwise, it assigns `k = k.parent` and continues; exiting the loop reaches false. This is a specific parent-field traversal. It is not interchangeable with automatically traversing JavaScript prototypes, and the body does not demonstrate cycle detection or guaranteed termination for arbitrary objects.\n",
          "quote_sha256": "06b747330f626a3bd28f96e66e555f732cb053887c20c755d6c09d9e9d5cffef"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 23,
          "last_line": 23,
          "quote": "O auxiliar `hasInstanceProperty` começa com um cursor local definido pelo primeiro argumento. Enquanto o cursor tem valor lógico verdadeiro, testa uma coleção de propriedades e sua operação de pertinência. Uma condição bem-sucedida retorna true. Caso contrário, atribui `k = k.parent` e continua; sair do laço alcança false. Essa é uma travessia específica de um campo de pai. Ela não equivale a percorrer automaticamente protótipos JavaScript, e o corpo não demonstra detecção de ciclos ou término garantido para objetos arbitrários.\n",
          "quote_sha256": "73fce3f0fde7d55941e372be6b55b76a324bdeb9f082672db1b2c846f0c4d27b"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [],
      "id": "fastify-decoration-lookup:body-paragraph:08",
      "manual_review_finding": "Explicitparentfield loop and membership, no generalprototype traversal/cycledetection/terminationproof.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-095"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 27,
          "last_line": 27,
          "quote": "The helper `checkExistence` distinguishes a truthy name from the other path. For a truthy name, it combines membership tests and a call to the stored-key helper. For the other path, the written expression is `instance in this`. That expression is not a constant false. Receiver validity and the point reached remain explicit preconditions.\n",
          "quote_sha256": "1559f50e0515678962f9eaa4ff19cf291af8f6b59bc1efa661813ba739551bd4"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 27,
          "last_line": 27,
          "quote": "O auxiliar `checkExistence` distingue um nome de valor lógico verdadeiro do outro caminho. Para o primeiro caso, combina testes de pertinência e uma chamada ao auxiliar de chaves armazenadas. No outro caminho, a expressão escrita é `instance in this`. Essa expressão não é a constante false. A validade do receptor e o ponto alcançado continuam como precondições explícitas.\n",
          "quote_sha256": "2053cefa041d4726de049b850bbd981103bb54d3a3f8092a7796f026f0fce964"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [],
      "id": "fastify-decoration-lookup:body-paragraph:09",
      "manual_review_finding": "Truthyname tests versus instance-in-this branch; finalexpression is not constantfalse.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-096"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 29,
          "last_line": 29,
          "quote": "If this branch is reached through the shown plain strict-mode call, `this` is `undefined`; applying `in` with that right operand raises `TypeError`. This is a conditional language-derived path, corroborated by an owned synthetic probe, not an observed Fastify execution. The language rules are specified by [strict this binding](https://tc39.es/ecma262/2026/multipage/ordinary-and-exotic-objects-behaviours.html#sec-ordinarycallbindthis) and [relational-operator evaluation](https://tc39.es/ecma262/2026/multipage/ecmascript-language-expressions.html#sec-relational-operators-runtime-semantics-evaluation).\n",
          "quote_sha256": "1405d428761904f8ff3cbcf70041de29ad6825fdd63623b5c5c28b1ca64a28e1"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 29,
          "last_line": 29,
          "quote": "Se esse ramo for alcançado pela chamada simples em modo estrito mostrada, `this` será `undefined`; aplicar `in` com esse operando à direita lança `TypeError`. Esse é um caminho condicional derivado da linguagem, corroborado por um exemplo sintético próprio, não uma execução observada do Fastify. As regras estão especificadas em [vínculo estrito de this](https://tc39.es/ecma262/2026/multipage/ordinary-and-exotic-objects-behaviours.html#sec-ordinarycallbindthis) e [avaliação de operadores relacionais](https://tc39.es/ecma262/2026/multipage/ecmascript-language-expressions.html#sec-relational-operators-runtime-semantics-evaluation).\n",
          "quote_sha256": "caf9d6afaa42a5e46aaded7cac37c6d91ad58d862750caac7d1041b9db4a7960"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [
        {
          "path": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/review.json",
          "role": "Dated review/inspection or historical owned language-probe result, not a new external application execution.",
          "sha256": "9bcd6b6580162c716e8d9f6d0e4bc441f41a74bdfa0fc4cf4155224812d90cd7"
        },
        {
          "path": ".local-backups/documentation-intelligence-20261119/chapter-body-claim-alignment-v2/historical-receipt-cuts/strict-receiver-language-probe.json",
          "role": "Dated review/inspection or historical owned language-probe result, not a new external application execution.",
          "sha256": "82289fe0a532d4a3faecd1d063265f166180e3d49bb6257eda12b2cb3ff5cc4e"
        }
      ],
      "id": "fastify-decoration-lookup:body-paragraph:10",
      "manual_review_finding": "Strictplaincall givesundefinedthis and in throwsif branchreached; corroboration is historicalownedsyntheticprobe, not executedFastify.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-097",
        "source-span-096",
        "source-span-090"
      ],
      "status": "CONDITIONAL_LANGUAGE_INTERPRETATION",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 31,
          "last_line": 31,
          "quote": "The wrappers perform no explicit assignment to the target request/reply structure in their own bodies. This does not prove global purity: helper calls, getters and runtime object behavior remain separate dependencies. The correction therefore preserves the order and exact fallback while keeping those boundaries visible.\n",
          "quote_sha256": "7f2790fcda179ac420eeb5ed1ff1a4acbbf100f16cf0a078189811ee7feacec6"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 31,
          "last_line": 31,
          "quote": "Os wrappers não fazem atribuição explícita à estrutura alvo de requisição ou resposta em seus próprios corpos. Isso não prova pureza global: chamadas auxiliares, getters e comportamento dos objetos em execução continuam como dependências separadas. A correção preserva a ordem e a alternativa exata, mantendo essas fronteiras visíveis.\n",
          "quote_sha256": "8360fc86f209e067e5ec3b63eda1f98145440fbb7f6627cc7e9a5b4ba92906ae"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [],
      "id": "fastify-decoration-lookup:body-paragraph:11",
      "manual_review_finding": "No explicittargetassignment in wrappers; helper/getter effects preventglobalpurity claim.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-098"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 33,
          "last_line": 33,
          "quote": "The standalone source producer now adds an optional ordered-guard packet for these wrappers. Its original first-guard paragraph is unchanged, and its new packet records written expressions rather than supplying missing helper semantics. The actual model baseline remains rejected; this chapter and the deterministic packet are separate artifacts, without neural training, publication or automatic promotion to approved training data.\n",
          "quote_sha256": "fbe4d513498485f28be1008ce7d099740ac5b70d7f06e9655d43ef4cc99a0f67"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 33,
          "last_line": 33,
          "quote": "O produtor independente de fonte agora acrescenta um pacote opcional de guardas ordenadas para esses wrappers. Seu parágrafo original da primeira guarda não mudou, e o pacote novo registra expressões escritas sem fornecer semântica ausente dos auxiliares. O baseline real do modelo continua rejeitado; este capítulo e o pacote determinístico são artefatos separados, sem treinamento neural, publicação ou promoção automática a dados de treinamento aprovados.\n",
          "quote_sha256": "8e3e0bb292481414a9a2be6d925d0023bc740309e823b5b02e355702d9e6615c"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [
        {
          "path": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/review.json",
          "role": "Dated review/inspection or historical owned language-probe result, not a new external application execution.",
          "sha256": "9bcd6b6580162c716e8d9f6d0e4bc441f41a74bdfa0fc4cf4155224812d90cd7"
        }
      ],
      "id": "fastify-decoration-lookup:body-paragraph:12",
      "manual_review_finding": "Optionalwritten-guardpacket doesnot resolve helpersemantics or change rejectedbaseline/trainingstatus.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-098"
      ],
      "status": "REVIEW_PROCESS_AND_SOURCE",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 37,
          "last_line": 37,
          "quote": "The frozen `fastify.js` imports `./lib/decorate` and assigns `hasRequestDecorator: decorator.existRequest` in the instance object. The export in `lib/decorate.js` connects that property value to `checkRequestExistence`. This is a concrete source-level consumer relationship, not a claim that every possible call preserves its receiver.\n",
          "quote_sha256": "c4805d7c2e5f272f7790cbaa694aa550fe85f7baa758c386bf5a4f591353bd07"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 37,
          "last_line": 37,
          "quote": "O `fastify.js` congelado importa `./lib/decorate` e atribui `hasRequestDecorator: decorator.existRequest` no objeto da instância. A exportação em `lib/decorate.js` liga o valor dessa propriedade a `checkRequestExistence`. Essa é uma relação concreta de consumo no código, não uma afirmação de que toda chamada possível preserva seu receptor.\n",
          "quote_sha256": "05ecec8949a8b345a6a53a97b80276ba0b6b2221c4de2f0880b8c1c608600561"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [],
      "id": "fastify-decoration-lookup:body-paragraph:13",
      "manual_review_finding": "Coreproperty plus exportalias establishesconsumer wiring, not allcallersreceiver preservation.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-099",
        "source-span-100",
        "source-span-093"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 39,
          "last_line": 39,
          "quote": "The `FastifyInstance` interface in `types/instance.d.ts` declares `hasRequestDecorator(decorator: string | symbol): boolean`. It declares a required identifier argument and a Boolean result on normal completion; a declaration does not prove that every runtime input returns normally. The implementation parameter `name` is that supplied identifier. By contrast, `kRequest: Symbol('fastify.Request')` in `lib/symbols.js` declares an internal target-selection key. The two roles must not be merged merely because either identifier can involve a symbol.\n",
          "quote_sha256": "eda629344e0aa6eb6e7c00067111dc2bfc563248ab992f47f63818e1a055347c"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 39,
          "last_line": 39,
          "quote": "A interface `FastifyInstance` em `types/instance.d.ts` declara `hasRequestDecorator(decorator: string | symbol): boolean`. Ela declara um argumento identificador obrigatório e um resultado booleano na conclusão normal; uma declaração não prova que toda entrada em execução termina normalmente. O parâmetro `name` da implementação é esse identificador fornecido. Em contraste, `kRequest: Symbol('fastify.Request')` em `lib/symbols.js` declara uma chave interna de seleção do alvo. Esses papéis não devem ser misturados apenas porque qualquer identificador pode envolver um símbolo.\n",
          "quote_sha256": "6df8d3d6913fb2bfd0764da4f293537543093864c454f105aa4e02b0bf1308d6"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [],
      "id": "fastify-decoration-lookup:body-paragraph:14",
      "manual_review_finding": "Requiredstring|symbol decorationidentifier differsfrom internaltargetselectionkey; normal Booleanresult not guaranteednormaltermination.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-101",
        "source-span-102",
        "source-span-090"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/en.md",
          "document_sha256": "73c08945e7761fd0b80f823f63720c630d1a0bd79af30c0c2a21b1b3650f36ea",
          "first_line": 41,
          "last_line": 41,
          "quote": "The instance object also initializes `[kRequest]: Request.buildRequest(Request, options.trustProxy)`. This establishes the visible factory delegation and configuration argument. The factory body was not inspected for this supplement, so its output construction, proxy behavior and execution effects remain outside the verified claim. No authentication, persistence, timeout or retry policy follows from the lookup's name or this call alone.\n",
          "quote_sha256": "ed70f95a1eecf5385f3195bcf3931585ccbe8552f83c16cdd849622ee178a6de"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/fastify-decoration-lookup/pt-br.md",
          "document_sha256": "f1ea7f3c9441072f22f3bc488d4fa609ea331a61f4e258377c03cba95450c9d1",
          "first_line": 41,
          "last_line": 41,
          "quote": "O objeto da instância também inicializa `[kRequest]: Request.buildRequest(Request, options.trustProxy)`. Isso estabelece a delegação visível à fábrica e o argumento de configuração. O corpo da fábrica não foi inspecionado neste suplemento; portanto, a construção de sua saída, o comportamento de proxy e seus efeitos em execução ficam fora da afirmação verificada. Nenhuma política de autenticação, persistência, timeout ou retry decorre apenas do nome da consulta ou dessa chamada.\n",
          "quote_sha256": "71e9409a2ca26fb99aaa536eee1ac106a4916855d03033c1d32c6f3b0500182a"
        }
      },
      "bilingual_review": "Complete paired prose manually read; guardorder, negations, ownership, return/error distinctions and limits checked; inline identifiers match.",
      "chapter": "fastify-decoration-lookup",
      "execution_or_inspection_receipts": [],
      "id": "fastify-decoration-lookup:body-paragraph:15",
      "manual_review_finding": "Factorydelegation and trustProxy argument visible; missingfactorybody prevents output/proxy/auth/persistence/retry claims.",
      "owner_approved": false,
      "scope": "Before firstFAQheading; prose paragraphs only. Headings, tables, fences and FAQs excluded.",
      "source_span_ids": [
        "source-span-103"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    }
  ],
  "schema": "chapter-specific-body-claim-review-v1",
  "scope": "Proseparagraphs beforefirstFAQheading only; titles,tables,fences,FAQ/trailingcontext andgenericatomicentailment are separate.",
  "source_spans": [
    {
      "first_line": 1,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/fastify/lib/decorate.js",
      "full_file_sha256": "d2b77abf8bbbb61286548a3188eb48f8d03a10308160b09e304c66d8e9fa6904",
      "id": "source-span-088",
      "last_line": 8,
      "quote": "'use strict'\n\nconst {\n  kReply,\n  kRequest,\n  kState,\n  kHasBeenDecorated\n} = require('./symbols.js')\n",
      "quote_sha256": "aa6e48e46dfe04cebdd5a44c83b22d5737b7d237a9efcb8fd1ef17abb979d996",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "lib/decorate.js"
    },
    {
      "first_line": 82,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/fastify/lib/decorate.js",
      "full_file_sha256": "d2b77abf8bbbb61286548a3188eb48f8d03a10308160b09e304c66d8e9fa6904",
      "id": "source-span-089",
      "last_line": 113,
      "quote": "function checkExistence (instance, name) {\n  if (name) {\n    return name in instance || (instance.prototype && name in instance.prototype) || hasKey(instance, name)\n  }\n\n  return instance in this\n}\n\nfunction hasKey (fn, name) {\n  return fn.props ? fn.props.some(p => p.key === name) : false\n}\n\nfunction hasInstanceProperty (konstructor, name) {\n  let k = konstructor\n  while (k) {\n    if (k.instanceProperties && k.instanceProperties.has(name)) return true\n    k = k.parent\n  }\n  return false\n}\n\nfunction checkRequestExistence (name) {\n  if (name && hasKey(this[kRequest], name)) return true\n  if (name && hasInstanceProperty(this[kRequest], name)) return true\n  return checkExistence(this[kRequest].prototype, name)\n}\n\nfunction checkReplyExistence (name) {\n  if (name && hasKey(this[kReply], name)) return true\n  if (name && hasInstanceProperty(this[kReply], name)) return true\n  return checkExistence(this[kReply].prototype, name)\n}\n",
      "quote_sha256": "641b46b8d7c569977bfbd43014d338ae23386679ad4872731d3457727c394171",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "lib/decorate.js"
    },
    {
      "first_line": 103,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/fastify/lib/decorate.js",
      "full_file_sha256": "d2b77abf8bbbb61286548a3188eb48f8d03a10308160b09e304c66d8e9fa6904",
      "id": "source-span-090",
      "last_line": 107,
      "quote": "function checkRequestExistence (name) {\n  if (name && hasKey(this[kRequest], name)) return true\n  if (name && hasInstanceProperty(this[kRequest], name)) return true\n  return checkExistence(this[kRequest].prototype, name)\n}\n",
      "quote_sha256": "2144dd84df44a02c578aca137b3dd5d0f9623d728311e9c021194980f581ce18",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "lib/decorate.js"
    },
    {
      "first_line": 109,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/fastify/lib/decorate.js",
      "full_file_sha256": "d2b77abf8bbbb61286548a3188eb48f8d03a10308160b09e304c66d8e9fa6904",
      "id": "source-span-091",
      "last_line": 113,
      "quote": "function checkReplyExistence (name) {\n  if (name && hasKey(this[kReply], name)) return true\n  if (name && hasInstanceProperty(this[kReply], name)) return true\n  return checkExistence(this[kReply].prototype, name)\n}\n",
      "quote_sha256": "879a4797c8947272cef3eb2825c99532616ac186145996ced4ee61b80ae0ae7f",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "lib/decorate.js"
    },
    {
      "first_line": 3,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/fastify/lib/decorate.js",
      "full_file_sha256": "d2b77abf8bbbb61286548a3188eb48f8d03a10308160b09e304c66d8e9fa6904",
      "id": "source-span-092",
      "last_line": 8,
      "quote": "const {\n  kReply,\n  kRequest,\n  kState,\n  kHasBeenDecorated\n} = require('./symbols.js')\n",
      "quote_sha256": "0bfead2696ba45b303bf4d046caf8c6272a69a50d2fe16dfc6ac400aed2488af",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "lib/decorate.js"
    },
    {
      "first_line": 151,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/fastify/lib/decorate.js",
      "full_file_sha256": "d2b77abf8bbbb61286548a3188eb48f8d03a10308160b09e304c66d8e9fa6904",
      "id": "source-span-093",
      "last_line": 161,
      "quote": "module.exports = {\n  add: decorateFastify,\n  exist: checkExistence,\n  existRequest: checkRequestExistence,\n  existReply: checkReplyExistence,\n  dependencies: checkDependencies,\n  decorateReply,\n  decorateRequest,\n  getInstanceDecorator,\n  hasKey\n}\n",
      "quote_sha256": "0257ae972cd951f4aad7a1f33bbc8128220f8087a6a2ae04920011978f648cc8",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "lib/decorate.js"
    },
    {
      "first_line": 90,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/fastify/lib/decorate.js",
      "full_file_sha256": "d2b77abf8bbbb61286548a3188eb48f8d03a10308160b09e304c66d8e9fa6904",
      "id": "source-span-094",
      "last_line": 92,
      "quote": "function hasKey (fn, name) {\n  return fn.props ? fn.props.some(p => p.key === name) : false\n}\n",
      "quote_sha256": "27676dd27e8466595d2d132d8f964ab2bc499f59b518288d6ed4d6d1936fdaca",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "lib/decorate.js"
    },
    {
      "first_line": 94,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/fastify/lib/decorate.js",
      "full_file_sha256": "d2b77abf8bbbb61286548a3188eb48f8d03a10308160b09e304c66d8e9fa6904",
      "id": "source-span-095",
      "last_line": 101,
      "quote": "function hasInstanceProperty (konstructor, name) {\n  let k = konstructor\n  while (k) {\n    if (k.instanceProperties && k.instanceProperties.has(name)) return true\n    k = k.parent\n  }\n  return false\n}\n",
      "quote_sha256": "3a39b3fc206d43f6e1ab6e6b7cf2e5adb6b7eec5f8877c403a99b92186e56392",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "lib/decorate.js"
    },
    {
      "first_line": 82,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/fastify/lib/decorate.js",
      "full_file_sha256": "d2b77abf8bbbb61286548a3188eb48f8d03a10308160b09e304c66d8e9fa6904",
      "id": "source-span-096",
      "last_line": 88,
      "quote": "function checkExistence (instance, name) {\n  if (name) {\n    return name in instance || (instance.prototype && name in instance.prototype) || hasKey(instance, name)\n  }\n\n  return instance in this\n}\n",
      "quote_sha256": "d2a8505dc42367846dea73f5327825cccd5462bdf33fc2ef571067cd6f345946",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "lib/decorate.js"
    },
    {
      "first_line": 1,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/fastify/lib/decorate.js",
      "full_file_sha256": "d2b77abf8bbbb61286548a3188eb48f8d03a10308160b09e304c66d8e9fa6904",
      "id": "source-span-097",
      "last_line": 1,
      "quote": "'use strict'\n",
      "quote_sha256": "77dec457bbc51a32f0d9161a78c42fd33db0f7b94c0fabc68d885e40415eaa68",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "lib/decorate.js"
    },
    {
      "first_line": 103,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/fastify/lib/decorate.js",
      "full_file_sha256": "d2b77abf8bbbb61286548a3188eb48f8d03a10308160b09e304c66d8e9fa6904",
      "id": "source-span-098",
      "last_line": 113,
      "quote": "function checkRequestExistence (name) {\n  if (name && hasKey(this[kRequest], name)) return true\n  if (name && hasInstanceProperty(this[kRequest], name)) return true\n  return checkExistence(this[kRequest].prototype, name)\n}\n\nfunction checkReplyExistence (name) {\n  if (name && hasKey(this[kReply], name)) return true\n  if (name && hasInstanceProperty(this[kReply], name)) return true\n  return checkExistence(this[kReply].prototype, name)\n}\n",
      "quote_sha256": "b9b6eae5ee0b5ace1185bae28f769557f43cdf3398dcc00b04ce165c5eea4df1",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "lib/decorate.js"
    },
    {
      "first_line": 40,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/source-expansions/fastify/fastify.js",
      "full_file_sha256": "c64c8e3fd61261e76a849fe545d8f5eb8f9ea6136445fc86f1b30730e3b41d25",
      "id": "source-span-099",
      "last_line": 45,
      "quote": "const { createServer } = require('./lib/server')\nconst Reply = require('./lib/reply')\nconst Request = require('./lib/request')\nconst Context = require('./lib/context.js')\nconst decorator = require('./lib/decorate')\nconst ContentTypeParser = require('./lib/content-type-parser.js')\n",
      "quote_sha256": "24049d09c8f9c66c3e6921ca82cd828e21a694bbe125c3c24a4769ae2b28a3fb",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "fastify.js"
    },
    {
      "first_line": 284,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/source-expansions/fastify/fastify.js",
      "full_file_sha256": "c64c8e3fd61261e76a849fe545d8f5eb8f9ea6136445fc86f1b30730e3b41d25",
      "id": "source-span-100",
      "last_line": 290,
      "quote": "    decorate: decorator.add,\n    hasDecorator: decorator.exist,\n    decorateReply: decorator.decorateReply,\n    decorateRequest: decorator.decorateRequest,\n    hasRequestDecorator: decorator.existRequest,\n    hasReplyDecorator: decorator.existReply,\n    getDecorator: decorator.getInstanceDecorator,\n",
      "quote_sha256": "e55d7b589ab7b462b35184d16c513930b20474fbd47de05e8d70edac5103b052",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "fastify.js"
    },
    {
      "first_line": 160,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/source-expansions/fastify/types/instance.d.ts",
      "full_file_sha256": "d131c9268b2c3d541743e376c439d8ca7611e04b187175bfb268d40724b7103f",
      "id": "source-span-101",
      "last_line": 164,
      "quote": "\n  hasDecorator(decorator: string | symbol): boolean;\n  hasRequestDecorator(decorator: string | symbol): boolean;\n  hasReplyDecorator(decorator: string | symbol): boolean;\n  hasPlugin(name: string): boolean;\n",
      "quote_sha256": "f4f8b14d117826f000bd8b378aa1943c80e57bcbd03ddf596d32276aa86deb27",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "types/instance.d.ts"
    },
    {
      "first_line": 27,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/source-expansions/fastify/lib/symbols.js",
      "full_file_sha256": "bddfadc6be13b7c28869ac052d499b0f400c6dacddc667500e3097cd7e6a4a6c",
      "id": "source-span-102",
      "last_line": 32,
      "quote": "  kSchemaErrorFormatter: Symbol('fastify.schemaErrorFormatter'),\n  kSchemaVisited: Symbol('fastify.schemas.visited'),\n  // Request\n  kRequest: Symbol('fastify.Request'),\n  kRequestPayloadStream: Symbol('fastify.RequestPayloadStream'),\n  kRequestAcceptVersion: Symbol('fastify.RequestAcceptVersion'),\n",
      "quote_sha256": "1fcab881cebab86baa4f53c77d3cadab6cf1aa7909d85a02421a3d26d5b64b09",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "lib/symbols.js"
    },
    {
      "first_line": 186,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/source-expansions/fastify/fastify.js",
      "full_file_sha256": "c64c8e3fd61261e76a849fe545d8f5eb8f9ea6136445fc86f1b30730e3b41d25",
      "id": "source-span-103",
      "last_line": 190,
      "quote": "    ),\n    [kReply]: Reply.buildReply(Reply),\n    [kRequest]: Request.buildRequest(Request, options.trustProxy),\n    [kFourOhFour]: fourOhFour,\n    [pluginUtils.kRegisteredPlugins]: [],\n",
      "quote_sha256": "3d85b204fad8ba1dd26eadb42db62e29c88b699e42e958378782081a17c0fcfc",
      "repository": "fastify",
      "revision": "825d7722e4932a39193729997c76535d0a963b6b",
      "source_path": "fastify.js"
    }
  ],
  "status": "CODEX_SOURCE_REVIEW_PENDING_OWNER",
  "training_gold": false
}
````
<!-- artifact-body:e0ed53ba47f671fcaa0a29d49fd1a8a5e528361e84953bf3a94b9e29fbff158e:end -->
