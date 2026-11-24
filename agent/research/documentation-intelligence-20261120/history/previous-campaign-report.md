# Engineering Library — campanha de inteligência documental

**RELATÓRIO FINAL: CAMPANHA CONCLUÍDA.** Este arquivo registra o trabalho realizado,
a duração efetiva e os limites das evidências; não transforma tempo de calendário em tempo de inferência.

| Marco | Observação real |
|---|---|
| Início | 2026-11-19T22:49:10.847824+00:00 / 2026-11-19 19:49:10 -03 |
| Atualização deste relatório | 2026-11-20T10:56:15.805072+00:00 / 2026-11-20 07:56:15 -03 |
| Tempo decorrido de calendário | 12h 7min 4s |
| Alvo aproximado de 12 horas | 2026-11-20T10:49:10.847824+00:00 / 2026-11-20 07:49:10 -03 |
| Encerramento efetivo | 2026-11-20T10:56:15.805072+00:00 / 2026-11-20 07:56:15 -0300 |

Tempo de calendário, tempo de servidor do modelo e trabalho humano/automático
não são a mesma medida. Nenhum sleep artificial ou inferência de preenchimento
foi utilizado. Disponibilidade futura do host não é prometida.

## 1. Repositório, autorização e estado Git

Repositório exato: **engineering-library**, em /Users/juniorosa/Documents/Projetos/Projeto VivaBem/engineering-library.
Remoto real: https://github.com/parceiro-vivabem/engineering-library.git. Branch inicial: main.
HEAD preservado: 45c3cd00c528cf2075ceec56e97ab2a0b6ad387a. O checkout estava limpo no início.
Hash inicial do índice: 0dbf02d8eff9893bb3d8495143c1021ea7e418f30143fb28c0827697719aa8e8; checkpoints e comparação dos
metadados Git o verificam sem alterações.

A [comparação final somente de leitura](agent/research/documentation-intelligence-20261119/closing-git-preservation-v1.json)
conferiu 810 nós de metadados Git sem diferença, inclusive após os comandos.
11 checkouts externos mantêm HEAD e status anteriores; 208 fontes selecionadas
continuam iguais aos bytes congelados. As outras três famílias são snapshots
públicos preservados localmente, sem inventar worktrees Git ou executar aplicações.


Todas as mudanças permanecem fora do staging. Nenhum commit, push, reset, clean,
rebase, stash, cherry-pick ou reescrita de histórico foi executado. Os comandos
LFS clean/smudge descritos adiante são filtros locais de dados; não são git clean.
Nenhum repositório externo foi modificado. Nenhum serviço, credencial, payload
financeiro real ou código privado do Viva Bem foi utilizado.

O backend original continua parado: seu entrypoint faria preparação de banco e
sincronização de catálogo. A campanha usa somente o container Ollama já existente
e diretórios temporários próprios; não cria novos containers, listeners ou serviços.

## 2. Continuidade e baseline histórico

O baseline foi conferido no checkout atual: caller documental em Ruby, versão
1.9.40 do componente, coordenador de projeto 1.0.8 e produtor Go AST 1.6.1. Os 24 pares experimentais e a fila anterior
de 273 tarefas foram localizados; o histórico append-only permanece preservado.
Foram acrescentadas 27 tarefas DLI; a fila atual tem 300 tarefas e 531 eventos, sem apagar o prefixo histórico.

O relatório antigo removido pelo proprietário antes desta campanha não foi
recriado na raiz. Sua cópia histórica foi recuperada e explicitamente reconciliada
em [histórico](agent/research/documentation-intelligence-20261119/historical-report-reconciliation.json).
Observações antigas não foram apresentadas como novas inferências.

## 3. ADD, MODIFY, REMOVE, NO-OP e INCONCLUSIVE

O planejador opcional 0.3.5 trabalha com perfis fechados de afirmações/fonte,
recalcula fatos e produz recomendações técnicas. Não entende prosa arbitrária e
não publica documentos. A aplicação em memória e em workspace próprio é separada,
com propriedade, hashes, fonte física, histórico e par EN/PT verificados.

A [regressão atual](agent/research/documentation-intelligence-20261119/lifecycle-current-regression-v4.json)
acertou **22/24** ações na matriz de
desenvolvimento corrigida V3: duas entradas JavaScript continuam INCONCLUSIVE
no roteamento padrão Python/Go. O observador JavaScript é opt-in; um caso com
seletor acrescentado é uma entrada diferente, não prova de 24/24 na mesma matriz.

As demonstrações de [workspace](agent/research/documentation-intelligence-20261119/lifecycle-filesystem-demonstration.json)
e [FAQ](agent/research/documentation-intelligence-20261119/faq-maintenance-evaluation.json)
preservam originais, históricos e bytes humanos. Ausência isolada nunca prova
remoção. NO-OP não regenera o documento; os controles comparam bytes e mtime.

O [ensaio de lotes com duas operações](agent/research/documentation-intelligence-20261119/workspace-batch-coverage-evaluation-v1.json)
congelou oito pedidos sintéticos antes das chamadas ao CLI. Quatro lotes prepararam
candidatos: dois MODIFY, a ordem inversa desses MODIFY, ADD com MODIFY e NO-OP
com MODIFY. Quatro foram recusados sem criar raiz: alteração com INCONCLUSIVE,
NO-OP cujo bloco físico estava desatualizado, identidade duplicada e hash PT-BR
inválido após outra operação válida. As 64 identidades/hash/modos/tempos de arquivos
originais ficaram intactas; oito guias, 16 históricos e oito notas preservadas
foram conferidos. Inverter as operações independentes produziu os mesmos bytes.
São controles de integração de desenvolvimento; não alteram a matriz 22/24,
não somam testes à suíte de 278 e não provam atomicidade do sistema de arquivos.
A preparação inline inicial falhou ao analisar Python, antes de criar fixtures
ou chamar o componente; a receita corrigida foi salva antes de congelar o protocolo.
Este estudo é posterior ao selo V6 e integra a camada de fechamento.

## 4. Matriz de confusão do baseline local

O baseline teve 24 chamadas reais, 9 ações exatas coincidentes e 15 falsas
modificações. Todas as previsões foram MODIFY. Referências corrigidas antes da
pontuação permanecem versionadas; isto não é holdout independente.

| Referência / previsto | ADD | MODIFY | REMOVE | NO-OP | INCONCLUSIVE |
|---|---:|---:|---:|---:|---:|
| ADD | 0 | 2 | 0 | 0 | 0 |
| MODIFY | 0 | 9 | 0 | 0 | 0 |
| REMOVE | 0 | 1 | 0 | 0 | 0 |
| NO-OP | 0 | 6 | 0 | 0 | 0 |
| INCONCLUSIVE | 0 | 6 | 0 | 0 | 0 |

O antigo número zero de mudanças perdidas mede apenas sinal de mudança; não
significa ação correta. Houve perda de duas ações ADD, uma REMOVE e decisões
desnecessárias sobre seis NO-OP e seis casos insuficientes. A
[clarificação](agent/research/documentation-intelligence-20261119/lifecycle-metric-clarification.json)
preserva essa distinção. Nenhuma aprovação de capítulo inteiro decorre de JSON válido.

## 5. Novos experimentos do modelo e regressões críticas

Foram concluídas **56 chamadas** nesta campanha: 24 do baseline, duas do adaptador,
16 da comparação pareada, seis controles literais/aritméticos, quatro respostas
sobre fatos fechados e quatro sobre representações da prova de entrada/imports.
O [ledger bruto reconciliado](agent/research/documentation-intelligence-20261119/inference-current-ledger-v3.json)
verifica 5.640 tokens gerados e 1.956,070655435 segundos de servidor, cerca de 32,6 minutos.
Os seis controles não são exemplos documentais adicionais. O dataset V2 conserva
seu recorte de 42 diagnósticos; o V3 preserva os 56 em categorias explícitas.
Este tempo não representa a duração da campanha. Não há chamada pendente ou
resultado incerto novo contado como sucesso.

A [decomposição por predicados](agent/research/documentation-intelligence-20261119/decomposed-decision-evaluation.json)
não demonstrou melhoria. Ação direta: 4/8, três falsas MODIFY e **uma falsa REMOVE
crítica** sobre função Go cujo retorno 456 permaneceu igual. Predicados: 1/8,
todas as respostas declararam evidência insuficiente e cinco mudanças necessárias
foram abstidas. Diversos motivos PT-BR estão corrompidos.

O cenário Go continha comentário adversarial. A causalidade de prompt injection
não foi isolada; o resultado não é uma taxa geral de ataques. A resposta foi
preservada e nunca aplicada. Ambas as variantes continuam restritas à pesquisa.

A [calibração estruturada](agent/research/documentation-intelligence-20261119/structured-output-calibration-evaluation.json)
produziu seis objetos válidos no formato, mas apenas três respostas inteiramente
corretas. Houve true explícito, refutando a hipótese de impossibilidade universal
nesse formato. Incluir o schema no prompt não demonstrou ganho: cada braço acertou
um de dois controles. Isto não mede entendimento de código.

A [nova comparação com fatos fechados](agent/research/documentation-intelligence-20261119/closed-fact-documentation-evaluation.json)
terminou quatro chamadas. O controle sem helper absteve corretamente nos dois
casos; o braço com fato verificado também absteve nos dois e alegou, incorretamente,
que o fato estava ausente. Os quatro pares EN/PT preservam o mesmo sentido, mas
todos omitem a ressalva de bindings em runtime solicitada. Não houve melhoria
na explicação produzida nem aplicação de documentação.

## 6. Correções efetivas de compreensão de fonte

- Defaults com delimitador explícito preservam dígitos no nome do parâmetro.
  A forma antiga limit12 é recusada se puder significar limit=12 ou limit1=2.
  Defaults keyword-only e remoção de default de parâmetro existente são distinguidos.
- Um registro literal e uma função não podem ocupar silenciosamente o mesmo nome
  no observador Python. O caso antes recomendado como REMOVE agora é INCONCLUSIVE.
  Parâmetros duplicados também são recusados.
- O produtor JavaScript opcional extrai somente mapeamentos de campos admitidos,
  com identidade do parser/runtime e citação UTF-8 exata.
- O novo produtor Go usa censo completo virtual e seleção oficial de build.
  O max do SDK fica lexicalmente sem sombreamento em Darwin/arm64 e Linux/arm64,
  condicionado a censo completo e pacote válido. Não houve type-check ou execução do SDK.

Os recibos [default](agent/research/documentation-intelligence-20261119/default-claim-ambiguity-evaluation.json),
[binding Python](agent/research/documentation-intelligence-20261119/python-registry-binding-evaluation.json)
e [binding Go](agent/research/documentation-intelligence-20261119/go-build-binding-evaluation.json)
retêm versões anteriores, falhas, controles e limites. São melhorias de código e
protocolo, não aprendizado neural.

O [observador Python de dependências fechadas](agent/research/documentation-intelligence-20261119/python-closed-dependency-evaluation-v2.json)
resolveu seis fatos inteiros e recusou seis cenários insuficientes/dinâmicos,
12/12 referências de desenvolvimento. Quatro cadeias antes inconclusivas no perfil
apenas do arquivo raiz passam a ter fato condicional. Mudança apenas no helper
invalida a chave de evidência; formatação preserva a chave restrita do contrato.
Dezenove fontes mantiveram bytes, inode, mtime e ctime. O perfil não suporta
pacotes gerais, argumentos, classes ou bindings reais; não decide REMOVE.

A [fronteira JSON/arquivo](agent/research/documentation-intelligence-20261119/packet-json-boundary-evaluation.json)
foi endurecida na versão0.3.4. A versão anterior aceitava chaves repetidas e podia
recomendar REMOVE após um segundo current_source ocultar uma definição presente.
A nova recusa o pacote ambíguo antes de criar candidato. Um FIFO que bloqueava a
leitura antiga é recusado; arquivos não regulares, symlinks finais, crescimento,
troca de inode, Unicode inválido e valores não finitos também são controlados.
As 24 entradas canônicas mantêm22ações exatas, sem alteração das referências.
A fronteira protege o CLI bruto; um chamador que já descartou duplicatas ao criar
um dicionário deve aplicar sua própria admissão estrita.

A [auditoria das 56 respostas](agent/research/documentation-intelligence-20261119/strict-model-json-audit.json)
confirmou JSON lexicalmente inequívoco e todos os oito tipos de restrição de schema
usados nessas requisições. Isso não corrige os erros factuais, ressalvas ausentes
ou português ruim. A validação cobre esses schemas observados, não JSON Schema
genérico. As versões anteriores de fonte/dataset são preservadas por conteúdo em
[source-cut evolution](agent/research/documentation-intelligence-20261119/source-cut-evolution.json).


O [experimento de representação da prova](agent/research/documentation-intelligence-20261119/bound-proof-representation-evaluation.json)
acrescentou quatro respostas: prova completa e fato compacto, em dois casos já
expostos. Nenhuma respondeu corretamente ao fato presente; todas omitiram a
ressalva pedida. Somadas às duas falhas anteriores com fato, são seis falhas em
seis respostas que receberam o fato, além de dois controles root-only seguros.
A linha de novas tentativas de apresentação foi encerrada. Não se atribui a falha
a overflow de contexto ou ao defeito posterior de mutação de registro.

O [FAQ fechado](agent/research/documentation-intelligence-20261119/closed-return-faq-evaluation.json)
preparou oito pares condicionais e recusou seis controles, sem inferência ou escrita
de documento. Esses pares são fixtures, separados dos 77 pares de FAQ dos capítulos.
O observador atual 0.1.2 acrescenta identidade da entrada, provas de imports e
proteção do registro; a recuperação 0.1.3 também fixa configuração por operação.
O [estudo de mutação](agent/research/documentation-intelligence-20261119/frozen-registry-guard-evaluation.json)
preserva dois defeitos reais anteriores e controles de correção.


O [sinalizador de revisões Python](agent/tools/documentation_revision_signals.md)
0.1.1 compara ASTs escritos e comentários de tipo em snapshots explícitos, com
worker de três segundos e citações físicas. Não executa fontes nem escolhe ação
documental. Mudança apenas no helper ou no módulo ao redor exige revisão mesmo
quando a declaração selecionada permanece igual. Quinze controles passaram.
Na [comparação real cachetools](agent/research/documentation-intelligence-20261119/cachetools-real-evolution-evaluation.json),
duas revisões fixas mostram dois retornos alterados, uma nova função exportada e
duas afirmações escritas que permanecem corretas. São referências manuais de dois
MODIFY, um ADD e dois NO-OP, pendentes de revisão. O sinalizador correspondeu às
cinco referências estruturais; o planejador restrito existente ficou INCONCLUSIVE
nos cinco módulos completos. Portanto não se reivindica acerto de ações em código
real nem aplicação automática dessas propostas. A [regressão atual](agent/research/documentation-intelligence-20261119/revision-signals-current-evaluation.json)
preserva a versão anterior e a evolução para comentários de tipo. A família já
havia sido exposta durante desenvolvimento; isso não é um novo holdout.

A [avaliação em more-itertools](agent/research/documentation-intelligence-20261119/more-itertools-revision-signals-evaluation.json)
congelou a ferramenta antes da nova fonte e correspondeu a seis seletores mais uma
recusa de módulo acima de 64 KiB. Uma mudança só em docstring e uma mudança de
implementação produziram sinais escritos distintos, sem escolher ação documental.
A fonte declara derivação das receitas CPython; novo repositório não comprova
família disjunta. As duas revisões, avisos e esse limite de ancestralidade estão
preservados. Nenhuma biblioteca externa foi importada ou executada.

A [avaliação dos snapshots por chamada](agent/research/documentation-intelligence-20261119/typed-input-snapshot-evaluation-v2.json)
reproduziu e corrigiu seis falhas controladas de mutação pelo chamador. Operações,
pacotes, documentos, hashes e especificações agora são fixados antes da validação.
O planejador 0.3.5 e as APIs de candidatos, manutenção e FAQ 0.1.1 passaram 238
testes. Uma operação alterada para REMOVE após validação antes causava remoção
indevida somente na cópia em memória; nenhum documento original foi removido.
Os cortes antigos continuam recuperáveis, mas não são recomendados para essa
fronteira de entradas mutáveis. Os snapshots não são uma sandbox de Python nem
uma transação atômica do sistema de arquivos.

A [admissão de especificações de manutenção](agent/research/documentation-intelligence-20261119/maintenance-spec-boundary-evaluation.json)
foi corrigida em0.1.2 após reproduzir um bloqueio FIFO na0.1.1. A leitura atual
usa descritores, arquivo regular estável,2MiB e JSON limitado/inequívoco. Recusa
symlinks ancestrais; aliases de caminho devem usar sua forma física. Seis controles
novos passaram. Nenhuma semântica do classificador original mudou.

A [revisão condicional de FAQ](agent/research/documentation-intelligence-20261119/conditional-faq-revision-evaluation-v1.json)
0.1.0 recomenda deltas somente para o registro exato do renderizador fechado.
Suas16 referências de desenvolvimento corresponderam:1ADD,2MODIFY,3NO-OP e10
INCONCLUSIVE. Helper alterado pode mudar a resposta mesmo com entrada idêntica.
Mantém a ressalva de runtime em EN/PT e nunca recomendaREMOVE. Não edita Markdown
livre; exige propriedade/inventário, hashes e rechecagem dos dois recortes. Aquela
suíte local datada passou264 testes. Não é melhoria neural nem ganho na mesma matriz24 casos.

A [nova família de repositório ItsDangerous](agent/research/documentation-intelligence-20261119/itsdangerous-revision-signals-evaluation.json)
foi lida após congelar o sinalizador0.1.1. Seis referências estruturais coincidiram:
uma declaração igual,quatro diferentes e uma recusa por sobrecargas. Parte das
diferenças vem de anotações; não implica contrato de runtime alterado. A ancestralidade
completa não foi certificada; avisos BSD primários e correções de nomes de licença
estão preservados no [suplemento](agent/research/documentation-intelligence-20261119/source-license-provenance-supplement-v4.json).


A [vinculação física de NO-OP](agent/research/documentation-intelligence-20261119/noop-document-binding-evaluation-v1.json)
reproduziu duas declarações incorretas: fonte e pacote diziam retorno2,enquanto
os documentos físicos ainda diziam1. A API de candidatos0.1.2 agora exige bloco
endereçado,hash esperado e texto correspondente à afirmação do pacote antes de
certificar NO-OP. Os dois casos congelados são recusados; sete controles novos
passaram e INCONCLUSIVE continua preservando sem certificar correção.

A [conferência real das saídas](agent/research/documentation-intelligence-20261119/candidate-output-closure-evaluation-v1.json)
reproduziu cinco falsos sucessos na manutenção0.1.3:raiz substituída,conteúdo
ativo/histórico corrompido,arquivo inesperado e resultado persistido alterado.
A versão0.1.4 revalida identidades,inventários,bytes,modo/mtime preservados,
precondições,índice e resultado antes de entregar sucesso. Cinco mutações
novas equivalentes agora são recusadas; o controle válido prepara candidato.
Sete controles novos distinguem a versão antiga. Evidência parcial e arquivos
humanos de substituição ficam preservados. A existência de result.json não
significa conclusão após uma recusa posterior; as conferências são sequenciais,
sem promessa de atomicidade contra mudanças depois da última verificação.
O código atual passou278 testes nas restaurações macOS/Linux.

A [cobertura de preparação](agent/research/documentation-intelligence-20261119/lifecycle-candidate-coverage-evaluation-v1.json)
mede outra etapa:24 casos de desenvolvimento receberam envoltórios sintéticos
com propriedade explícita;48 chamadas de idioma produziram seis alterações
pareadas, seis NO-OP, oito INCONCLUSIVE e quatro recusas. As alterações foram
umADD,quatroMODIFY e umREMOVE; os originais e bytes humanos permaneceram intactos.
Raises escritos,retornos string e substituição de caminho atual ainda não têm
gramática positiva admitida; conteúdo humano também foi recusado corretamente.
As entradas derivadas acrescentam metadados de propriedade, portanto não são
outra pontuação22/24com os mesmos bytes,holdout independente ou novos dados gold.


A [cobertura do CLI de workspace](agent/research/documentation-intelligence-20261119/workspace-candidate-coverage-evaluation-v1.json)
executou16 casos físicos admitidos:seis candidatos preparados,seis NO-OP sem
novo diretório e quatro recusas sem edição. Os oito casos INCONCLUSIVE em memória
ficam explicitamente fora desse subconjunto. Os 96 arquivos originais mantiveram
hash,modo,mtime,ctime,dispositivo e inode;24 documentos ativos e24cópias históricas
foram comparados, e 12 notas humanas mantiveram bytes,modo e mtime no candidato.
As guias preparadas coincidem exatamente com os candidatos anteriores em memória;
campos do resultado persistido conferem com a resposta do CLI. Nenhuma fonte
inspecionada ou aplicação externa foi executada. É integração em fixtures próprias,
não homologação de publicação,transação contra crashes ou métrica24/24.

## 7. Arquitetura e adaptador de integração

O exemplo próprio contém porta de domínio, serviço consumidor, adaptador,
interface de cliente, mapeador e fake. O [capítulo EN](agent/research/documentation-intelligence-20261119/owned-adapter/en.md)
e [PT-BR](agent/research/documentation-intelligence-20261119/owned-adapter/pt-br.md)
incluem diagrama, configuração, transformação de dados, erros, cinco FAQs e
exemplo executável. Oito testes da fonte publicada e o exemplo passaram.

O timeout 2.0 pertence ao adaptador e é encaminhado ao cliente; o serviço não o
configura. GatewayUnavailable é traduzido com causa; erros do mapeador estão
fora desse handler. O tipo inteiro exato rejeita booleanos; moeda é apenas string
de três caracteres, sem validação ISO ou maiúsculas. Cliente HTTP concreto,
retentativas internas, TLS, autorização, cache e persistência permanecem desconhecidos.

Na [comparação de helpers](agent/research/documentation-intelligence-20261119/owned-adapter-helper-comparison.json),
a resposta sem helpers atribuiu incorretamente o timeout ao serviço. A resposta
com helpers não usou suas citações adicionais. Não foi demonstrada melhoria neural.


Os [traços executados da fixture própria](agent/research/documentation-intelligence-20261119/owned-adapter-execution-traces-evaluation-v1.json)
acrescentam15 sondagens nativas,sem repetir os oito testes anteriores ou aumentar
artificialmente os 278 testes documentais. Os sete caminhos de sucesso correspondem
às seis arestas observáveis entre componentes nos dois diagramas preservados;
as setas internas não são tratadas como novas chamadas observadas. Houve zero
tentativas de criar socket. Um GatewayUnavailable do cliente foi traduzido com
causa; a mesma classe numa leitura de payload durante o mapeamento propagou sem
tradução. A chave currency ausente foi lida antes da validação de amount booleano,
produzindo KeyError. Três caracteres Unicode de sete bytes e valor negativo foram
aceitos; uma subclasse de int foi recusada. Timeout negativo,token vazio e caractere
de query foram encaminhados ao fake como escritos,sem inferir semântica HTTP,
autorização ou deadline real. Payload com outro account_id não substituiu o
identificador do chamador. Código próprio foi executado com instrumentação em
memória; fontes externas,rede,modelo e navegador não foram executados. Os sete
arquivos de código/exemplo e os dois capítulos mantiveram seus hashes.

## 8. Revisão dos 24 pares experimentais

Todos os originais foram lidos, cotejados com fontes e preservados. Resultado
original: 23 VERIFIED_WITH_LIMITATIONS e um REQUIRES_CORRECTION. Os 24 novos pares
estão prontos para revisão do proprietário, mantendo limites explícitos.
O capítulo de adaptador acrescenta um par novo; não é o 25º original revisado.

| Capítulo | Estado do original | Recomendação do candidato |
|---|---|---|
| chi-middleware | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| chi-throttle-workflow | REQUIRES_CORRECTION | READY_FOR_OWNER_REVIEW |
| documentation-agent-contracts | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| duckdb-boolean-factory | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| fastify-decoration-lookup | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| go-image-animation | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| go-image-compression-flow | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| go-image-configuration | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| go-image-dimensions | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| go-image-frontend-dimensions | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| go-image-quality | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| opencv-depth-coercion | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| opencv-shape-contract | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| prometheus-builder | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| prometheus-keep-bookkeeping | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| rails-request-methods | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| redis-expiry-predicate | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| redis-ttl-replies | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| ruff-target-version | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| sdk-dynamic-retry-policy | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| sqlx-in-expansion | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| sqlx-map-argument-binding | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| starlette-server-error-flow | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |
| starlette-task-and-iteration | VERIFIED_WITH_LIMITATIONS | READY_FOR_OWNER_REVIEW |

A [QA V11](agent/research/documentation-intelligence-20261119/chapter-review-integrity-v11.json)
confirma 95 arquivos originais inalterados, 131 citações exatas, 88 links locais e
paridade de identificadores nos 48 arquivos dos 24 pares. Hash e citação corretos
não substituem revisão factual. Aprovação do proprietário e treinamento gold: zero.

## 9. FAQs e deduplicação

Há 72 pares novos de FAQ nos capítulos revisados e cinco no adaptador, totalizando
77 perguntas bilíngues. Suas identidades foram atribuídas depois de comparação
manual do sentido, sem inferir tradução pela posição do heading.

A rotina automática é mais restrita: um tipo de pergunta sobre retorno inteiro,
inventário explícito e blocos próprios. Dez demonstrações acertaram as decisões,
com vinte originais preservados e três pares candidatos alterados. Duplicata
registrada, conflito humano, referência obsoleta ou evidência insuficiente impedem
edição. Isso não equivale a deduplicar paráfrases livres.

## 10. Exemplos, comandos, tabelas, diagramas e navegação

O exemplo do adaptador e seu comando de testes foram executados com fake, sem rede.
Comandos/código EN/PT coincidem. Tabelas documentam parâmetros e limites reais.
Nenhuma captura de tela ou imagem de origem desconhecida foi inventada.

As funções reais e inalteradas de Markdown/navegação foram executadas em catálogo
temporário com cinquenta candidatos. Identidades compartilhadas das FAQs passaram
de 0/77 para 77/77 sem mudança no código visual ou no catálogo ativo.

No primeiro corte, dois diagramas de sequência passaram no parser Mermaid e
quatro fluxogramas ficaram bloqueados por ausência de DOM no Node, com
DOMPurify.addHook indisponível. Essa falha ambiental foi preservada. Posteriormente,
os seis diagramas foram renderizados e inspecionados no navegador, conforme
o recibo citado na seção15. As 42 referências incompatíveis eram daquele primeiro
corte isolado; a proposta V8 mais recente verifica392 arestas/carregamentos, sem
ativação do catálogo ou nova renderização dos corpos inalterados.

## 11. Harness e recuperação controlada

HelperRetrieval 0.1.3 aceita seis campos, registro explícito, revisão/hash e
seletor lexical. Impõe arquivo de 64 KiB, citação completa de 6.144 bytes, resposta
de 16 KiB, quatro tentativas e 24.576 bytes de citação por instância por padrão.
Workers têm deadlines; estados incertos não são repetidos automaticamente.

Resultados/recibos conferem pedido, registro, extrator e citação contra a fonte
física. Uma duplicata não reinjeta a citação. Versões antigas e gravações sem
recibo são preservadas para revisão. Recibos por hash não são assinaturas nem
histórico autenticado. Concorrência na mesma instância não ultrapassa o orçamento.

A [avaliação real de helpers](agent/research/documentation-intelligence-20261119/helper-new-families-evaluation.json)
teve seis citações completas e três recusas esperadas em nove casos. Método
herdado ou atributo dinâmico não foi inventado como declaração. Nenhum ecossistema
MCP, servidor genérico ou roteamento autônomo de produção foi instalado.

## 12. Dados candidatos e qualidade de linhagem

O [dataset atual V10](agent/research/documentation-intelligence-20261119/datasets/v10/manifest.json)
contém 305 registros: 50 deltas de documentos (25 pares), 154 linhas de FAQ (77 pares),
24 referências de ciclo documental, 56 diagnósticos, nove referências estruturais
anteriores e 12 controles cachetools separados como TEST_ONLY. São 16 famílias de
desenvolvimento e uma família externa reservada à avaliação estrutural. Categorias,
idiomas e versões se sobrepõem; não são 305 exemplos independentes para treinar.

A [auditoria V10](agent/research/documentation-intelligence-20261119/dataset-current-lineage-audit-v10.json)
passou 1.271 verificações diretas de arquivo/hash e comparações de identidades EN/PT.
As referências diretas usam cópias locais por conteúdo, preservando o caminho de
origem. As fontes físicas aninhadas continuam dependentes da cápsula/CAS de evidência.
Há 56 respostas e 55 pedidos de conteúdo distinto: dois controles root-only têm
pedidos deliberadamente idênticos, com respostas brutas distintas. Isso não cria
independência adicional. Os recortes V1, V2 e V3 permanecem preservados, incluindo as
três correções de rótulo ligadas à matriz efetiva V3. Não houve inferência adicional
para corrigir rótulos nem qualquer treino.

Todos os candidatos de desenvolvimento continuam em quarentena. Os 12 controles
externos são TEST_ONLY, sem autorização de treinamento, publicação ou certificação
de holdout neural. Enriquecimento de capítulo com fonte fixa não recebe rótulo de
evolução de código; respostas erradas são diagnósticos, não targets.


A [proposta de leitura V8](agent/research/documentation-intelligence-20261119/reader-bundle-evaluation-v8.json)
contém192 documentos derivados:50capítulos,dois índices de revisão,138vistas exatas
de 69 artefatos e dois índices raiz. Os 392 destinos efetivamente carregados correspondem
a todas as 392 arestas locais da AST,sem lacunas. As 77 identidades FAQ e os bytes fora
das URLs dos 52 documentos de entrada permanecem preservados. Não houve nova
renderização dos seis diagramas, alteração de catálogo ativo, UI ou banco.
Os recortesV1–V7 permanecem datados. Um contador inicial doV6 esperava378 arestas
por erro de contagem; sua falha e correção para376foram preservadas. NoV7,uma
leitura prematura da saída ainda vazia foi recusada; as chamadas terminaram depois,
sem nova execução. Esses erros de orquestração não foram tratados como falhas das
fontes ou como novas inferências.

Os [25 pacotes limitados por capítulo](agent/research/documentation-intelligence-20261119/body-claim-bundles-evaluation-v3.json)
particionam exatamente os 294 registros e 279 intervalos únicos de fonte do
mapeamento global de parágrafos. Cada JSON tem menos de 1 MiB; o maior tem
299.017 bytes. Vinte e quatro pacotes filhos são herdados byte a byte por seus caminhos antigos;
só o pacote do próprio agente foi refeito. Dois índices bilíngues conectam capítulos, pacotes e manifesto.
São comprovantes para leitura, não novos capítulos ou exemplos de treinamento.

A [conferência separada de tabelas e blocos cercados](agent/research/documentation-intelligence-20261119/document-tables-fences-audit-v3.json)
cobre seis tabelas bilíngues, 28 linhas de dados pareadas e 12 blocos físicos:
seis Mermaid, quatro instâncias de comandos e duas de saída JSON. Foram usados
27 intervalos físicos de fonte. Corpos de diagramas e capturas anteriores foram
conferidos por hash; recibos existentes de comandos foram relidos sem nova execução.
Duas falhas do avaliador foram preservadas: escapes Unicode contados indevidamente
como números e diferença explícita de um LF final entre AST e corpo físico.
As correções não alteraram fontes ou valores de referência.

O [estudo de canários de fonte](agent/research/documentation-intelligence-20261119/conditional-faq-source-canaries-evaluation-v1.json)
congelou a implementação antes de 12 casos próprios: cinco MODIFY, um NO-OP e
seis INCONCLUSIVE corresponderam às referências; 48 arquivos de fonte ficaram
intactos. Nenhum canário entrou nas respostas candidatas e nenhum marcador de
execução foi criado. Não houve LLM, execução de fontes ou escrita em documentos.
Isso verifica somente o perfil determinístico fechado, sem alegar resistência
geral de LLM a injeção de prompt ou avaliação independente de família.

O [suplemento V7 do Harness](agent/research/documentation-intelligence-20261119/harness/current-supplement-v7.json)
registra estes escopos e suas sobreposições, preservando as matrizes anteriores.
Nenhum novo servidor MCP, plugin ou roteamento padrão foi instalado.

O [alinhamento granular atual de FAQ](agent/research/documentation-intelligence-20261119/faq-claim-alignment-audit-v11.json)
cobre os 77 pares existentes dos 25 capítulos, com 143 intervalos físicos e quatro
referências a recibos de execução/revisão. As 154 identidades/hash de perguntas,
fontes preservadas e hashes dos documentos atuais foram conferidos. Todas as 154
linhas FAQ do dataset V10 referenciam sua anotação exata. A cobertura manual não é
um motor de implicação semântica, revisão humana independente ou aprovação de treino.
As versões anteriores das anotações permanecem intactas.

A [revisão de precisão em português](agent/research/documentation-intelligence-20261119/portuguese-precision-review.json)
preservou os textos anteriores e corrigiu duas expressões: acervo de pesquisa em
vez de arquivo isolado, e chamada ao cliente simulado em vez de chamada falsa.
Perguntas, IDs, código, diagramas e fonte não mudaram.

O [suplemento de licenças](agent/research/documentation-intelligence-20261119/source-license-provenance-supplement-v2.json)
retém os dois avisos MIT das revisões cachetools. O [histórico de exposição](agent/research/documentation-intelligence-20261119/cachetools-family-exposure-ledger.json)
distingue a avaliação do helper congelado antes da leitura da família do novo
sinalizador desenvolvido após essa leitura. Nenhuma delas certifica independência
do pré-treinamento neural ou autorização de uso em treino.

O V10 herda cinco arquivos JSONL do V4 através dos manifestos intermediários por caminho/hash, sem copiá-los. Das 50
linhas de capítulos, 48 permanecem byte a byte iguais ao V9; somente as duas
versões de idioma do capítulo do próprio agente foram atualizadas. Nenhuma pergunta ou resposta FAQ mudou. Cada uma das 154
linhas FAQ referencia agora um blob imutável do respectivo par, evitando que uma
alteração de pergunta não relacionada invalide todas as referências. São 149
registros com versão original V4, 148 V5 e oito V10, sob política explícita de herança.

Além das FAQs, o [alinhamento atual dos corpos](agent/research/documentation-intelligence-20261119/chapter-body-claim-alignment-audit-v9.json)
cobre os25corpos candidatos anteriores à primeira FAQ:294 grupos de parágrafos,
588 trechos bilíngues,279 intervalos físicos de fonte e 109 referências a recibos.
São grupos de prosa, possivelmente com múltiplas afirmações atômicas; títulos,
tabelas,fences,FAQs e contexto posterior têm outros escopos. Não se afirma
implicação semântica genérica ou aprovação humana independente. Os recortes
V1–V8 permanecem preservados, e os 263 grupos anteriores não foram reescritos.

A leitura completa identificou um qualificador histórico ausente no português
do próprio agente:0.1.1 já era um recorte anterior em inglês, mas ainda aparecia
como atual em PT. A [correção preservada](agent/research/documentation-intelligence-20261119/self-bilingual-history-precision-v2.json)
alinha o tempo verbal e traduz archive como acervo de pesquisa. Perguntas,
respostas,IDs,versões literais e código não mudaram. Aquele V8 conservou148 linhas FAQ
e 49 linhas de capítulos byte a byte; apenas seis metadados FAQ e um capítulo PT
foram atualizados, sem gerar novos exemplos ou inferência.

O primeiro export V8 parou por um caminho de recibo público ausente. Os sete
auditores tinham mantido nomes privados distintos, mas repetiam o nome público
V1. A [reparação de caminhos](agent/research/documentation-intelligence-20261119/body-audit-version-routing-repair.json)
recuperou cada recibo original por versão/hash e preservou a saída parcial. Nenhum
resultado ou histórico foi perdido; a nova auditoria V10 passou1.271checagens.

## 13. Fine-tuning e direitos

A [revisão atual](agent/research/documentation-intelligence-20261119/training-readiness-current.json)
mantém **zero dos nove gates totalmente satisfeitos**. Apenas o deployment GGUF
está comprovado, sem par train-ready de modelo/tokenizer validado; não há targets
aprovados, holdout certificado, piloto de memória/treinador, serialização de estado
de treino ou rollback de otimizador verificados.

Foram observados M1 Pro, 16 GiB, dez CPUs e Docker com 8.321.515.520 bytes de memória.
Treze módulos inspecionados não são descobertos no host e no Python recuperado.
Isso não prova ausência em todos os ambientes possíveis nem no backend parado.
Nenhum framework foi importado/instalado para treinar.

O levantamento inicial preservou treze licenças/avisos primários em onze repositórios
e a proveniência do actionpack. Isso não é autorização legal ou do proprietário para treinamento.
Treinos, passos de otimizador e adaptadores neurais criados: **zero**.


A [revisão de sobreposição](agent/research/documentation-intelligence-20261119/dataset-overlap-review-v1.json)
confere102 pares de tarefas bilíngues e 154 respostas FAQ integralmente contidas nos
respectivos capítulos. Há64 referências de entrada para32pacotes exatos e 27 pares
de fonte reconhecidos;56diagnósticos usam55conteúdos de pedido. Dezesseis
explicações diagnósticas não têm source_input_ref explícito e seus prompts não
foram interpretados heuristicamente. Os 17 grupos conservadores mantêm as famílias
existentes; não certificam ancestralidade disjunta,holdout ou305exemplos positivos
independentes. Tarefas de capítulo/FAQ podem ser intencionalmente complementares,
mas ponderação ou máscara exige decisão futura. Nenhum registro,split,flag de
aprovação ou peso de amostragem foi modificado. Cachetools continua TEST_ONLY
estrutural já exposto em desenvolvimento,não holdout neural certificado.

## 14. Preservação, LFS e recuperação

A [cápsula operacional V7](agent/research/documentation-intelligence-20261119/operational-recovery-current-v7.json)
restaurou1.713 arquivos e verificou1.712 itens de conhecimento. Os 278 testes passaram
no macOS Python 3.14.7 em8,756s e no Linux ARM64 Python 3.11.2 existente em4,273s.
Inclui candidatos0.1.2 e manutenção0.1.4. A V6 preserva o corte271anterior ao
readback; a V5 preserva264 testes anteriores à falha de NO-OP físico. Sucessos
históricos de recuperação não certificam defeitos descobertos depois.
Os recibos públicos de bundles/leitor estavam com nomes antigos nesse corteV7;
a reparação posterior preserva e restaura seus bytes por versão, sem invalidar
os 278 testes de código ou reescrever a cápsula. O deltaV5,descrito abaixo,
inclui os caminhos corrigidos e os novos textos/dados daquela captura.


A [cápsula operacional V3](agent/research/documentation-intelligence-20261119/operational-recovery-current-v3.json)
restaurou 809 arquivos, verificou conhecimento e passou 228 testes no macOS 3.14.7
e Linux ARM64 3.11.2. Uma primeira seleção do Python 3.9.6 no diretório restaurado
teve uma falha, preservada; o código não foi alterado para passar. A cápsula V3 inclui o sinalizador 0.1.1; textos e recibos posteriores são novos
recortes datados. A cápsula V2 anterior, de 796 arquivos e 213 testes, fica preservada. O [catálogo privado](agent/research/documentation-intelligence-20261119/private-artifact-catalog-receipt-v1.json)
pinou individualmente 4.907 arquivos regulares, um symlink e dois manifestos de
runtime selado; checkpoints têm inventários próprios, sem recursão.


O [catálogo privado V2](agent/research/documentation-intelligence-20261119/private-artifact-catalog-receipt-v2.json)
conferiu6.947 arquivos regulares,3.905.125.532 bytes,finalidade por arquivo e dois
FIFOs apenas por metadados. Aponta23 manifestos de checkpoints e os manifestos de
dois runtimes/sete árvores restauradas,sem recursão de cópias. A conferência detectou
que a árvore operacional V1 recebeu depois um store de modelo; o
[complemento das árvores vivas](agent/research/documentation-intelligence-20261119/private-restored-tree-artifact-catalog-receipt-v1.json)
inventariou7.666 arquivos regulares e um symlink:7.651 arquivos correspondem aos
cortes de código, sete são seus próprios manifestos e oito foram acrescentados
após a extração. Os dados recuperados do modelo estavam presentes e foram
explicitamente incluídos,sem perda,limpeza ou inicialização do store.

O [grafo recuperado](agent/research/documentation-intelligence-20261119/restored-model-catalog-graph-v1.json)
confere sete blobs,wrapper legado e namespace nativo. O wrapper tem digest
a52a4a87c5affc63e344f4974f75bcc5b478b40e641df57d0f40941dfc406c94 e inclui o
manifesto nativo a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72
como descritor adicional; seus papéis e hashes não são intercambiáveis.
A [comparação de fechamento](agent/research/documentation-intelligence-20261119/model-components-closing-v1.json)
validou os sete artefatos e 14 partes ordenadas contra original,snapshot local e
store recuperado. Os pesos de 2.019.377.376 bytes permanecem dde5aa3fc5ffc17176b5e8bdc82f587b24b2678c6c66101bf7da77af9f7ccdff.
Foram lidos6.058.184.920 bytes novos; o hash do store recuperado foi reutilizado
somente após conferir identidade,inode,tamanho,mtime ectime do nó recém-catalogado.
Não houve novo store,inferência,treino ou upload. Os caminhos efetivos das partes
continuam em agent/recovery/model-bundle.json e storage do manifesto; localização
remota aprovada permanece ausente.

O [teste de interrupções](agent/research/documentation-intelligence-20261119/interrupted-workspace-recovery-evaluation-v1.json)
encerrou somente três processos próprios recém-criados após gravações concluídas
de precondições,índice e resultado. As raízes parciais de1/9/10 arquivos permaneceram
inalteradas. Três novas tentativas no mesmo caminho foram recusadas; três pedidos
explícitos em novas raízes prepararam candidatos e preservaram os históricos.
Um result.json preparado existiu sem resposta concluída do CLI. Sua presença não
prova conclusão ou aprovação. Não houve desligamento do host,queda física de
energia ou prova de durabilidade contra crash do sistema de arquivos.

Uma cápsula anterior datada restaurou 485 arquivos operacionais mais manifesto. Seus
137 testes passaram a partir da cópia restaurada no macOS e no Linux existente.
O modelo original foi reconstruído em destino novo a partir de catorze partes;
o grafo completo restaurado e o original passaram na verificação de hashes.
O novo store não foi servido, e não houve nova inferência de recuperação.

O primeiro restore recusou ausência do diretório pai; logs foram preservados,
o pai foi criado e a nova tentativa em destino ainda ausente passou. Uma verificação
prematura também ficou registrada. Nenhum store existente foi substituído.

Git LFS privado 3.8.1 fez roundtrip local da cápsula de 16.507.451 bytes com pointer
canônico e comparação de 810 arquivos de metadados Git inalterados. Não houve
instalação de hooks, configuração global/repo, staging ou uploads.

Os runtimes Ruby e Markdown/Mermaid possuem arquivos selados com hashes; fontes,
prompts, respostas, rejeições, checkpoints e pesos originais continuam preservados.
A cápsula de código é um corte datado: não contém todos os arquivos privados nem
recibos criados depois dela. Recuperação remota, cold boot e Windows permanecem
não comprovados. Persistência de deployment não é checkpoint de treinamento.

A [cápsula privada de fontes/evidências](agent/research/documentation-intelligence-20261119/source-evidence-recovery.json)
restaurou independentemente 1.958 arquivos,358.351.090 bytes de conteúdo, de um
arquivo local de315.908.501 bytes. Inclui fontes completas de citações e históricos;
não duplica os 2 GB de pesos, já recuperados separadamente. É um recorte datado,
não o checkout inteiro mais recente nem recuperação remota.

A [preservação por conteúdo do dataset](agent/research/documentation-intelligence-20261119/dataset-reference-preservation.json)
verificou1.104 referências,370 identidades caminho/hash e357 blobs únicos,
4.472.581 bytes. Cópias históricas explicitamente indicadas e fontes de terceiros
foram resolvidas no escopo correto, sem tratar um LICENSE externo como o da raiz.
A [restauração independente](agent/research/documentation-intelligence-20261119/dataset-reference-recovery.json)
resolve as referências do dataset sem ler os caminhos originais e recupera uma
versão anterior mesmo após mudar uma cópia isolada. Nenhuma linha foi promovida
a gold, alterada ou ingerida por trainer.

A [recompilação Go com cache novo](agent/research/documentation-intelligence-20261119/go-build-binding-reproduction.json)
produziu os mesmos bytes nos dois alvos. O manifesto registra o diretório canônico
de build, relevante à identidade de pacote com GO111MODULE=off.

A [cadeia base + deltaV2 + deltaV3](agent/research/documentation-intelligence-20261119/source-evidence-delta-recovery-v3.json)
restaurou6.359 arquivos,1.255 itens de conhecimento,305 registros e 1.269 referências.
Os 83 arquivos de código/testes coincidem com o corte de 264 testes já exercitado
nas duas plataformas. O delta novo tem7.082.627 bytes e não recopia pesos,imagem
ou novas cápsulas operacionais seladas. Esse corte é anterior ao mapeamento de
25corpos e à correção PT/datasetV8; esses novos artefatos exigem delta posterior.


A [cadeia com deltaV4](agent/research/documentation-intelligence-20261119/source-evidence-delta-recovery-v4.json)
acrescentou7.859.580 bytes e restaurou7.056 arquivos em diretório independente,
preservando53 sobreposições anteriores por conteúdo. Confere305 registros V8,
1.271 referências,77 pares FAQ/143citações e os25corpos/276 intervalos/584 trechos,
além de 105 referências a recibos,27 intervalos de tabelas,12blocos cercados,
25pacotes limitados e 184 documentos do leitor com 376 arestas. Os 83 arquivos
executáveis/de testes coincidem com o corte264testado. Não foram reexecutados
os 264 testes, comandos de exemplos ou navegador por essa restauração de dados.
A receita foi incluída no próprio delta antes de selar; recibos restaurados
não foram sobrescritos. Ainda é recuperação no mesmo host, com imagem e pesos
separados, anterior à correção posterior da vinculação física deNO-OP.



A [cadeia com deltaV5](agent/research/documentation-intelligence-20261119/source-evidence-delta-recovery-v5.json)
acrescentou11.767.034 bytes e restaurou8.549 arquivos,preservando70 sobreposições
anteriores por conteúdo. Sua receita já estava dentro do delta antes de selar.
Conferiu1.935 itens de conhecimento,305 registros V10/1.271 referências,77 pares FAQ,
279 intervalos de corpo/588 trechos/109 recibos,25pacotes limitados e o leitorV8
com 192 documentos/392 arestas. Os 49 recibos versionados e 19 referências do Harness
foram verificados na cópia restaurada, assim como48 entradas/40 saídas do estudo
em memória e 48 fontes dos canários. Os 83 arquivos executáveis/de testes coincidem
com o corte278testado. Não houve nova suíte ampla,comando de exemplo,navegador,
inferência ou treino nessa restauração. Os 16 casos de CLI posteriores são anexos
novos,preservados separadamente até o próximo delta/checkpoint.

As reparações [dos bundles](agent/research/documentation-intelligence-20261119/body-claim-bundle-audit-version-routing-repair.json)
e [do leitor](agent/research/documentation-intelligence-20261119/reader-audit-version-routing-repair.json)
recuperaram recibos exatos de versões anteriores nas cápsulas seladas. Scripts
derivados haviam mudado entradas sem atualizar o nome público de saída. O Harness
recusou as referências ausentes antes de gravar seu suplemento; essas falhas foram
preservadas. Nenhuma avaliação,extração AST,navegação ou inferência foi repetida.
A [auditoria de roteamento por versão](agent/research/documentation-intelligence-20261119/versioned-receipt-routing-audit-v2.json)
confere49 recibos de sete famílias; o primeiro corte confere19 referências dos suplementos,
e o novo corteV2 confere28 referências V5/V6/V7,além dos 83 arquivos
executáveis/de testes idênticos ao corte278testado. As versões públicas agora
correspondem aos próprios manifestos; observações de caminhos mutáveis antigos
continuam exigindo seu recorte datado preservado.

A [cadeia atual com delta V6](agent/research/documentation-intelligence-20261119/source-evidence-delta-recovery-v6.json)
foi selada às 09:59 UTC e restaurou 8.920 arquivos em diretório independente,
preservando 77 sobreposições por conteúdo. O delta acrescenta 3.315.397 bytes,
com 378 arquivos novos/atualizados; exige os cinco componentes anteriores na ordem.
A cópia conferiu 1.951 itens de conhecimento, os 305 registros V10 e suas 1.271
referências, 77 pares FAQ, 279 intervalos de fonte/588 trechos de corpo e o leitor
V8 de 192 documentos/392 arestas. Também verificou os 49 caminhos por versão,
28 referências imutáveis do Harness, os 16 casos de CLI, 20 arquivos parciais das
três interrupções e 12 pares documentais dos replanejamentos explícitos.
Os 17 grupos de sobreposição e as 154 contenções FAQ/capítulo permanecem exatos;
as 15 sondagens do adaptador foram preservadas como recibos, sem reexecutá-las.
Os 83 arquivos executáveis/de testes continuam iguais ao corte dos 278 testes.

Os catálogos privados também estão dentro dessa cadeia: o principal V3 contém
6.979 entradas, das quais 6.968 arquivos regulares, e o complemento das sete árvores
restauradas contém 7.666 regulares e um symlink. A restauração verifica os próprios
catálogos e as 14 identidades de partes no recibo do modelo; não apresenta os pesos
ou a imagem como payload dessa cápsula de fontes. A [observação final do runtime](agent/research/documentation-intelligence-20261119/runtime-closing-observation-v1.json)
consultou apenas três endpoints GET do container existente: versão 0.40.16, tag e
digest aprovados coincidentes, modelo descarregado da memória e zero inferências.
Recibos de criação/restauração e o fechamento do relatório, necessariamente
posteriores ao selo, ficam em checkpoints e no suplemento final de metadados;
não são retroativamente atribuídos ao conteúdo V6.

O roteiro bilíngue de [retomada local](agent/research/documentation-intelligence-20261119/recovery-handoff-v1/pt-br.md)
lista os seis arquivos selados, hashes, ordem e limites do ensaio V6, além dos
componentes separados de pesos/imagem. Distingue recibos de conclusão de arquivos
parciais e explica que arquivos ignorados pelo Git não estão em um backup remoto.
É um guia posterior ao selo, sem disparar nova restauração ou aprovar publicação.

O [catálogo complementar de fechamento](agent/research/documentation-intelligence-20261119/private-artifact-catalog-late-delta-receipt-v1.json)
registra o estado das 10:32 UTC: 239 caminhos privados novos e dois arquivos menores
alterados após o catálogo V3, com finalidade individual e hashes. Outros 6.955
arquivos menores foram relidos e permaneceram iguais. As identidades de 11
componentes grandes são herdadas explicitamente; não foram novamente calculadas
por esse suplemento. Dois FIFOs ficam apenas em metadados, sem abertura. Edições
posteriores de receitas preservam seus bytes anteriores; recibos finais e o
relatório atualizado são metadados posteriores, guardados no último checkpoint.

A [camada final V7 de fontes/evidências](agent/research/documentation-intelligence-20261119/source-evidence-delta-recovery-v7.json)
foi selada após a janela autorizada e restaurou 9.200 arquivos, preservando 83 sobreposições anteriores. O novo delta tem 2.925.825 bytes
e SHA-256 `bdaace271dea04600692c78304175a84831763b163a13f2b61b8f5c4955bfa22`; requer base e V2–V6 na ordem.
Conferiu 1962 itens de conhecimento, os mesmos 305 registros/1.271 referências,
os oito lotes posteriores e suas 64 fontes/documentos originais, oito guias,
16 históricos e oito notas; a síntese das mesmas 19 capacidades também foi verificada.
O relatório de FECHAMENTO está no payload recuperado. O recibo dessa restauração e
esta atualização posterior do relatório ficam fora do próprio selo e são
preservados no checkpoint de fechamento, sem cadeia circular de hashes.
O ensaio guardado inicial usa `.local-backups/documentation-intelligence-20261119/restore_final_with_open_scope_v1.py`.

A primeira auditoria recusou a ausência de logs brutos da restauração V6: o
filtro de diretórios anteriores incluía JSONs, mas deixou de fora o stdout
do restore e o stdout de conhecimento. Ambos continuavam preservados no disco.
O primeiro suplemento e a segunda recusa também foram conservados. O suplemento
completo V2 contém 19 arquivos, 368.372 bytes, SHA-256
`cee44a46a3bf788e9bb0758d809793f6ca2342a1ef929055b522dddffa1686c5`. Ele é requisito adicional
à cadeia original, cujo arquivo V7 não foi reescrito. A análise prévia verificou
que todos os 241 hashes do catálogo seriam resolvidos antes da conclusão.
A retomada usa a cópia já extraída e repete apenas as conferências de leitura;
não repete extração, suíte, fixture ou modelo. O PASS do filho de conhecimento
original foi reutilizado após conferir os 1.962 arquivos fixados; nenhuma
nova execução desse filho foi contada. A receita de conclusão é
`.local-backups/documentation-intelligence-20261119/resume_final_recovery_log_supplement_v2.py`,
com protocolo explícito para a pasta preservada. Uma nova recuperação exige
um novo protocolo para o destino, preservando os protocolos e falhas históricos.

A [observação de isolamento das leituras](agent/research/documentation-intelligence-20261119/independent-recovery-source-isolation-v1.json)
impôs a política de aberturas Python no processo principal e no filho de
conhecimento. Duas leituras-canário de uma fonte original foram recusadas;
não houve abertura inesperada do checkout original. Arquivos selados e a
receita própria foram entradas permitidas; as provas de conteúdo vieram da
cópia restaurada. Isso observa eventos Python, não constitui sandbox de
kernel/código nativo e não comprova recuperação remota ou queda de energia.


## 15. Verificações e resultados realmente executados

| Verificação | Resultado e limite |
|---|---|
| Python novo, último recorte da árvore atual | 278 testes passaram; inclui 15 controles de sinalização de revisões e os controles anteriores |
| Python, cópia restaurada macOS 3.14.7 | 278 passaram na cápsula V7 com NO-OP físico e readback de saídas |
| Python, cópia restaurada Linux 3.11.2 | 278 passaram na cápsula V7 no runtime recuperado |
| Go opcional novo | 23 testes principais + 11 subtestes passaram; dois executáveis ARM64 verificados |
| JavaScript/CJS | 41 testes novos e sessenta controles existentes passaram em runtime recuperado |
| Ruby existente | 262 testes, 1.787 asserções; recuperação documenta adaptação de caminho e falhas ambientais anteriores |
| Capítulos originais | 24 pares; 131 citações; 95 originais preservados; zero problemas na QA V11 |
| Modelo original/restaurado | Hashes de pesos, metadados e namespace verificados; nenhuma troca de modelo |
| Git | Índice, HEAD e 810 metadados comparados sem mudanças |

As execuções de parser e testes próprios não são execução de aplicações externas.
As suítes Ruby/CJS inalteradas não são repetidas sem nova preocupação de regressão.

Os [seis diagramas exatos](agent/research/documentation-intelligence-20261119/mermaid-browser-evaluation.json)
foram renderizados no Edge157/Mermaid12.2.0 e as seis imagens foram inspecionadas.
Caixas,setas e rótulos ficaram legíveis e dentro dos recortes naturais capturados;
os três pares mantêm condições e direções equivalentes. O teste usa páginas locais
de QA e pipes CDP, sem listener TCP, catálogo ativo ou mudança de UI. Não é captura
do leitor em execução nem homologação em tela estreita. As tentativas anteriores
com DOMPurify ausente e dump-dom ainda PENDING permanecem preservadas.

O [mapa bilíngue do Harness](agent/research/documentation-intelligence-20261119/harness/pt-br.md)
registra19 capacidades e distingue fluxo Ruby, APIs de pesquisa e ferramentas deste
host. MCP2026-07-28, Agent Skills e Agent Plugins1.0.0 foram consultados em fontes
primárias. O [plano de interoperabilidade](agent/research/documentation-intelligence-20261119/harness/proposed-interop-evaluation.json)
é apenas desenho: nenhum servidor, pacote de plugin ou novo roteamento foi instalado.
O PDF de estudo não apareceu nos escopos locais e duas buscas atuais de metadados
Drive; não se presume ausência global.

Uma [camada opcional de orçamento por trabalho](agent/research/documentation-intelligence-20261119/helper-job-budget-evaluation.json)
reserva limites persistentes antes do helper. Novas instâncias/processos não
reiniciaram o teto de duas chamadas; seis processos concorrentes o respeitaram.
Resultados tardios, falhas de auditoria e conclusão incerta não expuseram citações
nem causaram retry. O custo reservado é conservador,6.144 bytes por chamada.
A camada não limita tokens do modelo, não cancela inferência remota, não é lock
distribuído e não protege contra rollback consistente de todo o diário confiado.
Chamadores diretos continuam com os limites anteriores por instância.

Uma [proposta separada de leitura](agent/research/documentation-intelligence-20261119/reader-bundle-evaluation.json)
contém102 documentos:50cópias de capítulos,50vistas de 25 artefatos brutos e dois
índices EN/PT. A cópia anterior usada no catálogo isolado tinha54links de artefato
não suportados e seis rotas sem destino. Na proposta,164links carregam o destino
real,77 identidades de FAQ permanecem compartilhadas e só URLs mudam nos corpos
dos capítulos. Isto não descreve defeitos do catálogo ativo: os50originais,
a UI e o banco continuam intactos. Os apêndices brutos preservam status e hashes;
não criam novas famílias de treinamento. Paginação e telas estreitas seguem sem
homologação. A primeira proposta e o datasetV2 são recortes anteriores ao CLI0.3.4.

A [imagem local do runtime Ollama](agent/research/documentation-intelligence-20261119/ollama-runtime-image-preservation.json)
foi salva em 2.872.640.512 bytes e teve as quatro camadas conferidas pelos hashes
comprimidos e diff IDs descomprimidos. O índice e a cadeia Linux/arm64 estão
preservados; a variante amd64 anunciada no índice não está incluída. Não houve
image load, novo contêiner, novo servidor, cópia do volume original ou inferência
de restauração. Verificar conteúdo da imagem não equivale a testá-la servindo o
modelo em outro host.

## 16. Inventário obrigatório por repositório

O [inventário por arquivo](agent/research/documentation-intelligence-20261119/repository-file-inventory.json)
lista cada criação, modificação e fonte inspecionada com finalidade. Hashes de
baseline são diferenciados de revisão semântica. Arquivos operacionais ignorados
estão nos manifestos privados/checkpoints, com origem e papel de recuperação.

| Repositório exato | Remoto | HEAD congelado | Alterações da campanha |
|---|---|---|---|
| engineering-library | https://github.com/parceiro-vivabem/engineering-library.git | 45c3cd00c528cf2075ceec56e97ab2a0b6ad387a | 1653 criados; 2 modificados; excluídos: Nenhum |
| chi | https://github.com/go-chi/chi.git | c64ed7d6635f33a8b2feaff7dcfa55677023ac7d | sem alterações; criados/modificados/excluídos: Nenhum |
| go-image-optimizer | https://github.com/juniocr26/go-image-optimizer.git | 48476de6e4450294b7769ab7af90805100bb21b5 | sem alterações; criados/modificados/excluídos: Nenhum |
| prometheus | https://github.com/prometheus/prometheus.git | b2a602494b65bda38316eabaef7e0d834a6814dd | sem alterações; criados/modificados/excluídos: Nenhum |
| fastify | https://github.com/fastify/fastify.git | 825d7722e4932a39193729997c76535d0a963b6b | sem alterações; criados/modificados/excluídos: Nenhum |
| starlette | https://github.com/encode/starlette.git | 271c277da0ff64e2048a4d46ecc812b9d61db5f6 | sem alterações; criados/modificados/excluídos: Nenhum |
| sdk-go | https://github.com/temporalio/sdk-go.git | 7e0d845246d36fc7f62ade2af885554f94c29db9 | sem alterações; criados/modificados/excluídos: Nenhum |
| sqlx | https://github.com/jmoiron/sqlx.git | 41dac167fdad5e3fd81d66cafba0951dc6823a30 | sem alterações; criados/modificados/excluídos: Nenhum |
| opencv | https://github.com/opencv/opencv.git | 5d0660acfed08650cafec4876b4792a369a20601 | sem alterações; criados/modificados/excluídos: Nenhum |
| redis | https://github.com/redis/redis.git | 1a9eb051aa243f9d0e5a8a8afa6c4801bf52a9fb | sem alterações; criados/modificados/excluídos: Nenhum |
| duckdb | https://github.com/duckdb/duckdb.git | e41515de6f7efb19b43293ab49cb967cd64ab9f9 | sem alterações; criados/modificados/excluídos: Nenhum |
| ruff | https://github.com/astral-sh/ruff.git | 0222c19dd8e0c9a927f2e47bf3774a108431da25 | sem alterações; criados/modificados/excluídos: Nenhum |
| tkem/cachetools | https://github.com/tkem/cachetools.git | c403f9f4185e58090b904c1915345b9ba46d5a08 | sem alterações; criados/modificados/excluídos: Nenhum |
| more-itertools/more-itertools | https://github.com/more-itertools/more-itertools.git | 7e46c39ea5d73b80f36ef2faf266e10108029b02 | sem alterações; criados/modificados/excluídos: Nenhum |
| pallets/itsdangerous | https://github.com/pallets/itsdangerous.git | 096c8d42545d3b68ea21a4f890fb2b2d8979c0bd | sem alterações; criados/modificados/excluídos: Nenhum |

Na engineering-library, os arquivos modificados já existentes são agent/README.md
(suplemento datado) e agent/recovery/manifest.json (identidades/inventário/estado
local de armazenamento). Excluídos: Nenhum. Mudanças pré-existentes: Nenhum.
Cada ferramenta/teste/recibo/candidato novo está individualizado no inventário.

Nos catorze repositórios externos: criados Nenhum; modificados Nenhum; excluídos
Nenhum; **sem alterações**. Só houve leitura de Git/fontes/licenças, congelamento
de evidência na própria biblioteca e análise de trechos. Suítes e aplicações
externas executadas: Nenhum. actionpack, Go e CPython instalados são fontes de
pacote/runtime com hashes próprios, sem inventar HEAD Git.

## 17. Falhas, recusas e limitações preservadas

O histórico inclui falsos positivos do modelo, falsa remoção crítica, motivos
PT-BR corrompidos, falha de propriedade de registro Python corrigida, deriva de
versão de referência corrigida, falhas ambientais Ruby, diretório pai ausente no
restore, recusas de escopo/quote e parser Mermaid sem DOM. Nenhuma foi apagada
ou retroativamente descrita como sucesso.

As capacidades novas são limitadas e opcionais. Censos declarados não provam
integridade de toda uma aplicação; extração AST não resolve todos os imports,
tipos, decoradores ou efeitos em execução. Não há promessa de aprovação documental
autônoma ou de qualidade geral medida fora destas famílias de desenvolvimento.

O [suplemento datado V7 do harness](agent/research/documentation-intelligence-20261119/harness/current-supplement-v7.json)
registra as correções físicas, recuperação de 278 testes, preparação de candidatos
e os recortes atuais de corpos,leitor e dados. Suas linhas refinam capacidades sobrepostas; não devem ser somadas à
matriz anterior como novas capacidades independentes.


A [síntese atual consolidada do Harness](agent/research/documentation-intelligence-20261119/harness/consolidated-current-pt-br-v1.md)
retoma os mesmos 19 IDs e status da matriz inicial, sem somar suplementos como
novas capacidades independentes. Nove constatações incorporam resultados posteriores;
dez mantêm seu texto, com três delas vinculadas à fonte atual do helper revisada.
Hashes históricos e atuais ficam explícitos. A primeira guarda recusou justamente
um hash antigo desse helper, antes de criar a síntese; a revisão preservada
confirmou o escopo das três constatações sem reescrever a matriz anterior.
O orçamento persistente opcional não se torna orçamento global de tokens, nem
as validações de pesquisa passam a ser roteamento Ruby/MCP de produção. Esta
síntese e o ensaio de lotes são posteriores ao leitor V8, que permanece datado.

## 18. Encerramento e escopos futuros

A janela autorizada foi cumprida. As linhas de pesquisa realizadas e as recusas permanecem preservadas; os pontos abaixo distinguem fechamento verificado de trabalho futuro.
O delta V6 já fecha código, dados e evidências recentes em uma cópia restaurada;
os catálogos privados e as partes do modelo foram conferidos. A leitura crítica e a conferência de fontes foram concluídas; a camada V7 registra
o ensaio final. O checkpoint de fechamento preserva os metadados produzidos
depois do selo. O inventário vivo distingue esses recortes.
A linha de representação do modelo permanece encerrada, sem tentativas de preenchimento.

Metas ainda não demonstradas ficam explícitas: treinamento aprovado, holdout
independente certificado, edição de prosa arbitrária, resolução geral de dependências,
completude semântica geral e recuperação fora desta máquina.

## 19. Continuação segura e aprovação final

Ler primeiro os handoffs em .local-backups/documentation-intelligence-20261119/,
o último checkpoint, a fila append-only e os recibos de chamadas. Conferir processos
pendentes antes de qualquer inferência; não repetir resultado incerto automaticamente.
Não iniciar o backend, apagar pesos/históricos ou fazer operações Git proibidas.

As alterações permanecem propostas para revisão do proprietário. Publicação,
dados gold e commits não decorrem deste relatório. Sugestões de Conventional Commit
serão apresentadas apenas na resposta final para o único repositório alterado.

## 20. Próxima campanha recomendada

Priorizar aprovação humana dos candidatos e direitos de fonte antes de qualquer
treinamento; manter os nove gates explícitos. Ampliar a revisão humana independente dos25
corpos já mapeados, conferir implicações semânticas que excedem os perfis fechados
e medir a revisão condicional em famílias ainda não expostas. Claims positivos
para raise/string/caminho exigem novo perfil e prova de endereço físico,sem
confundir recomendação com preparação. Evolução de Go módulos/tipos e imports
Python gerais exige novas provas, sem ampliar rótulos de remoção por ausência.
Testar recuperação remota somente com destino/custo aprovados; verificar cold
boot do modelo e o consumidor real antes de alegar deployment reproduzível.
Interoperabilidade MCP continua uma alternativa a comparar, sem instalar um
ecossistema para substituir APIs locais que já atendem ao experimento limitado.

Encerramento registrado em 2026-11-20T10:56:15.805072+00:00. As alterações continuam sem staging e dependem de revisão do proprietário para publicação ou commit.
