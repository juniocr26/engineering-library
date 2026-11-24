# Suplemento do código atual: preservação limitada de referências de identificadores

Candidato técnico isolado;não publicado,aprovado pelo proprietário ou gold de treinamento.

Este texto complementa o [capítulo histórico congelado](../../../../.local-backups/documentation-intelligence-20261119/dataset-v10-reference-blobs/sha256/bc0e4f63854e99f30b0f6040b1a2c480d27a3c50dd4db98e5598ee53da5f2a43). Seus bytes originais e seu recorte de fonte permanecem intactos; este é um novo recorte dos arquivos de trabalho, não uma reescrita histórica.

O código atual do chamador declara `VERSION = '1.9.43'`. O planejador, a manutenção e o auxiliar opcional inspecionados declaram `0.3.6`, `0.1.5` e `0.1.3`, respectivamente. Os hashes exatos dos arquivos de trabalho identificam este recorte; o HEAD Git observado, isoladamente, não afirma que os novos bytes do chamador estão commitados. [source:E6] [source:E7] [source:E8] [source:E9]

`evidence_cards` usa `source_units` para seleções explícitas de unidades. O modo estrutural Python usa `python_fragments`; outros cartões podem omitir metadados AST de captura. O caminho `infer` inspecionado continua chamando `call_model(source_model_request(files, skills))`. Este suplemento não transforma pesquisa com o auxiliar opcional em roteamento autônomo de ferramentas. [source:E1] [source:E2] [source:E10] [source:E11]

`caught_exception_identifiers` percorre a subárvore AST lexical da função selecionada e coleta nomes estáticos limitados das cláusulas de captura. Pode registrar nomes simples, cadeias de atributos e elementos diretos de tuplas. Não resolve classes de exceção nem estabelece qual corpo aninhado é executado. Capturas sem tipo e expressões dinâmicas de tipo não viram fatos de classes resolvidas. [source:E5]

`quoted_caught_identifier_mismatch?` atua para um identificador de captura da fonte entre crases e exige sua grafia admitida nas explicações dos dois idiomas. A grafia qualificada da fonte e seu nome terminal podem concordar quando não há ambiguidade. Nomes qualificados distintos com o mesmo terminal exigem os mesmos conjuntos de referências nomeadas entre os idiomas; um proprietário não sustentado é recusado. [source:E3] [source:E4] [source:E12]

Essas recusas exigem metadados AST suportados no cartão. Elas não certificam direção dos pares do mapa, papéis das referências, identificadores novos arbitrários, toda chave de código, dicionários aninhados ou mistos, vinculações em execução, ordem de execução nem equivalência factual completa EN/PT. O auxiliar compartilhado verifica a presença de referências da fonte na explicação; ele não é um analisador semântico completo de cada trecho de código. Integridade das citações, preservação das referências e revisão semântica continuam sendo obrigações separadas. [source:E1] [source:E3] [source:E4] [source:E5]

`direct_return_mapping_identifiers` registra referências ASCII limitadas de nomes/atributos quando instruções diretas de retorno contêm dicionários literais inteiramente formados por essas referências. O perfil permite até 32 pares e 64 referências únicas; mapas com expansão, mistos, apenas aninhados ou grandes demais ficam fora da cobertura. Ele registra grafia lexical, em vez de identidades de classes resolvidas ou um valor de retorno executado. [source:E5]

`quoted_return_mapping_identifier_mismatch?` envia as referências conhecidas do mapa para `quoted_identifier_reference_mismatch?`; a entrada existente de referências de captura usa o mesmo auxiliar. Uma referência conhecida entre crases aciona uma verificação de presença entre idiomas e de proprietário admitido. Quando grafias distintas da fonte compartilham um terminal, ambas as explicações devem preservar o mesmo conjunto de referências nomeadas. Isso não verifica qual referência é a chave ou o valor do dicionário. [source:E3] [source:E4] [source:E12] [source:E13]

## Candidatos de perguntas frequentes

<!-- reading-section: faq:quoted-exception-preservation -->
### Citações corretas da fonte, sozinhas, provam que os nomes de exceções foram preservados na tradução?

`quoted_caught_identifier_mismatch?` atua para um identificador de captura da fonte entre crases e exige sua grafia admitida nas explicações dos dois idiomas. A grafia qualificada da fonte e seu nome terminal podem concordar quando não há ambiguidade. Nomes qualificados distintos com o mesmo terminal exigem os mesmos conjuntos de referências nomeadas entre os idiomas; um proprietário não sustentado é recusado. [source:E3] [source:E4] [source:E12]

<!-- reading-section: faq:ast-card-coverage -->
### A nova recusa cobre todos os modos de evidência e todos os tipos de prosa?

Essas recusas exigem metadados AST suportados no cartão. Elas não certificam direção dos pares do mapa, papéis das referências, identificadores novos arbitrários, toda chave de código, dicionários aninhados ou mistos, vinculações em execução, ordem de execução nem equivalência factual completa EN/PT. O auxiliar compartilhado verifica a presença de referências da fonte na explicação; ele não é um analisador semântico completo de cada trecho de código. Integridade das citações, preservação das referências e revisão semântica continuam sendo obrigações separadas. [source:E1] [source:E3] [source:E4] [source:E5]

<!-- reading-section: faq:returned-map-reference-profile -->
### Quais referências de dicionários retornados os novos metadados cobrem?

`direct_return_mapping_identifiers` registra referências ASCII limitadas de nomes/atributos quando instruções diretas de retorno contêm dicionários literais inteiramente formados por essas referências. O perfil permite até 32 pares e 64 referências únicas; mapas com expansão, mistos, apenas aninhados ou grandes demais ficam fora da cobertura. Ele registra grafia lexical, em vez de identidades de classes resolvidas ou um valor de retorno executado. [source:E5]

<!-- reading-section: faq:mapping-direction-limit -->
### Preservar nomes de referências do mapa estabelece sua direção entre chave e valor?

`quoted_return_mapping_identifier_mismatch?` envia as referências conhecidas do mapa para `quoted_identifier_reference_mismatch?`; a entrada existente de referências de captura usa o mesmo auxiliar. Uma referência conhecida entre crases aciona uma verificação de presença entre idiomas e de proprietário admitido. Quando grafias distintas da fonte compartilham um terminal, ambas as explicações devem preservar o mesmo conjunto de referências nomeadas. Isso não verifica qual referência é a chave ou o valor do dicionário. [source:E3] [source:E4] [source:E12] [source:E13]

## Referências físicas da fonte

- [source:E1] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 658–700; SHA-256 `086c11b2d10972111cfcfb23c49b70e67f4d30f1d5de39f768c46b23748cdb2b`.

- [source:E2] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 704–733; SHA-256 `086c11b2d10972111cfcfb23c49b70e67f4d30f1d5de39f768c46b23748cdb2b`.

- [source:E3] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 1111–1113; SHA-256 `086c11b2d10972111cfcfb23c49b70e67f4d30f1d5de39f768c46b23748cdb2b`.

- [source:E12] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 1121–1140; SHA-256 `086c11b2d10972111cfcfb23c49b70e67f4d30f1d5de39f768c46b23748cdb2b`.

- [source:E13] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 1117–1119; SHA-256 `086c11b2d10972111cfcfb23c49b70e67f4d30f1d5de39f768c46b23748cdb2b`.

- [source:E4] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 1264–1265; SHA-256 `086c11b2d10972111cfcfb23c49b70e67f4d30f1d5de39f768c46b23748cdb2b`.

- [source:E5] [backend/lib/documentation/python_structure.py](../../../../backend/lib/documentation/python_structure.py), lines 1–88; SHA-256 `d9d7da9ad2662f39c9b43a424bfb6b934f4c755032c2d3a1c04bc77f7b1f376f`.

- [source:E6] [agent/tools/documentation_lifecycle.py](../../../tools/documentation_lifecycle.py), lines 20–20; SHA-256 `fe6ef693fdbfe0f793960cc10430cb012ff44a00a10efdcfa0d6c803902ed2ee`.

- [source:E7] [agent/tools/documentation_maintenance.py](../../../tools/documentation_maintenance.py), lines 29–29; SHA-256 `23ace94042542517b2a01e03e43cb0e6dfcb90ebb19814a0e8804ae69753f6ed`.

- [source:E8] [agent/tools/documentation_retrieval.py](../../../tools/documentation_retrieval.py), lines 21–21; SHA-256 `afc77b34d46d95f3ec251ac837ce91495f7b2518cd98e80e1305c5c19339030c`.

- [source:E9] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 18–18; SHA-256 `086c11b2d10972111cfcfb23c49b70e67f4d30f1d5de39f768c46b23748cdb2b`.

- [source:E10] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 790–792; SHA-256 `086c11b2d10972111cfcfb23c49b70e67f4d30f1d5de39f768c46b23748cdb2b`.

- [source:E11] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 800–829; SHA-256 `086c11b2d10972111cfcfb23c49b70e67f4d30f1d5de39f768c46b23748cdb2b`.
