# Suplemento do código atual: identificadores de exceção entre crases

Candidato técnico isolado;não publicado,aprovado pelo proprietário ou gold de treinamento.

Este texto complementa o [capítulo histórico congelado](../../../../.local-backups/documentation-intelligence-20261119/dataset-v10-reference-blobs/sha256/bc0e4f63854e99f30b0f6040b1a2c480d27a3c50dd4db98e5598ee53da5f2a43). Seus bytes originais e seu recorte de fonte permanecem intactos; este é um novo recorte dos arquivos de trabalho, não uma reescrita histórica.

O código atual do chamador declara `VERSION = '1.9.42'`. O planejador, a manutenção e o auxiliar opcional inspecionados declaram `0.3.6`, `0.1.5` e `0.1.3`, respectivamente. Os hashes exatos dos arquivos de trabalho identificam este recorte; o HEAD Git observado, isoladamente, não afirma que os novos bytes do chamador estão commitados. [source:E6] [source:E7] [source:E8] [source:E9]

`evidence_cards` usa `source_units` para seleções explícitas de unidades. O modo estrutural Python usa `python_fragments`; outros cartões podem omitir metadados AST de captura. O caminho `infer` inspecionado continua chamando `call_model(source_model_request(files, skills))`. Este suplemento não transforma pesquisa com o auxiliar opcional em roteamento autônomo de ferramentas. [source:E1] [source:E2] [source:E10] [source:E11]

`caught_exception_identifiers` percorre a subárvore AST lexical da função selecionada e coleta nomes estáticos limitados das cláusulas de captura. Pode registrar nomes simples, cadeias de atributos e elementos diretos de tuplas. Não resolve classes de exceção nem estabelece qual corpo aninhado é executado. Capturas sem tipo e expressões dinâmicas de tipo não viram fatos de classes resolvidas. [source:E5]

`quoted_caught_identifier_mismatch?` atua para um identificador de captura da fonte entre crases e exige sua grafia admitida nas explicações dos dois idiomas. A grafia qualificada da fonte e seu nome terminal podem concordar quando não há ambiguidade. Nomes qualificados distintos com o mesmo terminal exigem os mesmos conjuntos de referências nomeadas entre os idiomas; um proprietário não sustentado é recusado. [source:E3] [source:E4]

Essa recusa depende da presença de metadados AST no cartão. Não é um validador geral para prosa sem identificadores da fonte entre crases, chaves de código, todas as expressões de exceção, ordem de execução ou equivalência factual. Integridade de citações, preservação de identificadores e revisão semântica completa são obrigações separadas. [source:E1] [source:E3] [source:E4] [source:E5]

## Candidatos de perguntas frequentes

<!-- reading-section: faq:quoted-exception-preservation -->
### Citações corretas da fonte, sozinhas, provam que os nomes de exceções foram preservados na tradução?

`quoted_caught_identifier_mismatch?` atua para um identificador de captura da fonte entre crases e exige sua grafia admitida nas explicações dos dois idiomas. A grafia qualificada da fonte e seu nome terminal podem concordar quando não há ambiguidade. Nomes qualificados distintos com o mesmo terminal exigem os mesmos conjuntos de referências nomeadas entre os idiomas; um proprietário não sustentado é recusado. [source:E3] [source:E4]

<!-- reading-section: faq:ast-card-coverage -->
### A nova recusa cobre todos os modos de evidência e todos os tipos de prosa?

Essa recusa depende da presença de metadados AST no cartão. Não é um validador geral para prosa sem identificadores da fonte entre crases, chaves de código, todas as expressões de exceção, ordem de execução ou equivalência factual. Integridade de citações, preservação de identificadores e revisão semântica completa são obrigações separadas. [source:E1] [source:E3] [source:E4] [source:E5]

## Referências físicas da fonte

- [source:E1] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 658–675; SHA-256 `6b0d819901f39438fab987d213664f96c1120b942a96602fdbd031e17fc10baa`.

- [source:E2] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 704–737; SHA-256 `6b0d819901f39438fab987d213664f96c1120b942a96602fdbd031e17fc10baa`.

- [source:E3] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 1110–1130; SHA-256 `6b0d819901f39438fab987d213664f96c1120b942a96602fdbd031e17fc10baa`.

- [source:E4] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 1254–1254; SHA-256 `6b0d819901f39438fab987d213664f96c1120b942a96602fdbd031e17fc10baa`.

- [source:E5] [backend/lib/documentation/python_structure.py](../../../../backend/lib/documentation/python_structure.py), lines 1–51; SHA-256 `27f2eed6c6dd5ccaacaec36d1e98fb7c0fc6160d7b788ee76cdfc8aab88f3e5a`.

- [source:E6] [agent/tools/documentation_lifecycle.py](../../../tools/documentation_lifecycle.py), lines 20–20; SHA-256 `fe6ef693fdbfe0f793960cc10430cb012ff44a00a10efdcfa0d6c803902ed2ee`.

- [source:E7] [agent/tools/documentation_maintenance.py](../../../tools/documentation_maintenance.py), lines 29–29; SHA-256 `23ace94042542517b2a01e03e43cb0e6dfcb90ebb19814a0e8804ae69753f6ed`.

- [source:E8] [agent/tools/documentation_retrieval.py](../../../tools/documentation_retrieval.py), lines 21–21; SHA-256 `afc77b34d46d95f3ec251ac837ce91495f7b2518cd98e80e1305c5c19339030c`.

- [source:E9] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 18–18; SHA-256 `6b0d819901f39438fab987d213664f96c1120b942a96602fdbd031e17fc10baa`.

- [source:E10] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 789–791; SHA-256 `6b0d819901f39438fab987d213664f96c1120b942a96602fdbd031e17fc10baa`.

- [source:E11] [backend/lib/documentation/command.rb](../../../../backend/lib/documentation/command.rb), lines 799–828; SHA-256 `6b0d819901f39438fab987d213664f96c1120b942a96602fdbd031e17fc10baa`.
