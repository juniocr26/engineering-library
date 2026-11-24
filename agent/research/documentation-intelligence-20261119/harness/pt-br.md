# Harness documental limitado: arquitetura atual e interoperabilidade

Este corte de pesquisa fundamentado em fonte é separado da integração de produção.
O core Ruby permanece no HEAD45c3cd0 do proprietário; APIs opcionais novas são
executadas somente em pesquisa/testes. O PDF de estudo não foi encontrado nos
escopos locais verificados ou em duas buscas atuais de metadados no Drive; o
[recibo de escopo](../pdf-plan-access-current.json) não afirma ausência em todo lugar.

## Fluxo existente e responsabilidade

O ramo comum de modelo é dirigido pela aplicação: configuração do proprietário
seleciona a fonte; Command.process confere propriedade e prepara evidência,
contexto fixo de skills e identidade; no-op/reuso exato podem evitar inferência;
senão call_model invoca Ollama e valida o envelope. Checagens de parágrafos/fonte
e releitura da fonte antecedem aplicação do rascunho próprio. ProjectCommand
coordena seções declaradas e montagem. Esses caminhos não despacham chamadas de
ferramenta escolhidas pelo modelo.

O ramo de pesquisa adiciona chamadas HelperRetrieval congeladas pelo operador
antes de um pedido ao modelo. Fornece citações de fonte, não permissão ou semântica
de helper verificada. A comparação do adaptador não melhorou a cobertura do modelo.
Correção de registro/recibo e revisão EN/PT do contrato completo seguem gates separados.

| Capacidade | Status | Constatação atual | Fonte de evidência |
|---|---|---|---|
| Orquestração dirigida pela aplicação | CONFIRMED | Command.process e ProjectCommand.process controlam seleção, cache/inferência, validação e saída própria. Não se infere planejador escolhido pelo modelo. | backend/lib/documentation/command.rb, backend/lib/documentation/project_command.rb |
| Identidade do modelo antes/depois da inferência | CONFIRMED | verify_model_identity confere modelo e hashes das skills ativas contra tags; call_model confere envelopes completos. | backend/lib/documentation/command.rb |
| Despacho de ferramentas pelo modelo nos pedidos comuns | ABSENT | source_model_request fornece mensagens/prompt, schema e opções, sem loop de despacho tools. Seleção de helpers na pesquisa é congelada pelo operador. | backend/lib/documentation/command.rb |
| API opcional de helpers executada na pesquisa | CONFIRMED | A versão0.1.2 tem37 testes e9 casos de fonte real. Não está conectada à inferência Ruby comum. | agent/tools/documentation_retrieval.py |
| Proveniência exata e limitada de fonte | CONFIRMED | Registro, revisões, hashes, citações físicas e identidade do produtor nativo são verificados em seus perfis explícitos. | agent/tools/documentation_retrieval.py, agent/tools/go_source_ast.py, backend/lib/documentation/go_ast_command.rb |
| Compreensão de dependências e vínculos | PARTIAL | Fatos fechados e prova Go opcional filtrada por build cobrem casos restritos. Semântica geral de helpers importados e vínculos em execução seguem não resolvidos. | agent/tools/documentation_lifecycle.py, agent/tools/documentation_retrieval.py |
| Três contextos fixos de instrução | CONFIRMED | skill_context lê exatamente os blocos ingleses evidence, authoring e review no modo skills; baseline retorna contexto vazio. | backend/lib/documentation/command.rb, agent/skills/evidence/SKILL.md, agent/skills/authoring/SKILL.md, agent/skills/review/SKILL.md |
| Descoberta/ativação de skills portáveis | PARTIAL | Os arquivos fixos não têm frontmatter YAML name/description. Não foi encontrado caminho de descoberta/ativação por metadados no loader inspecionado. | backend/lib/documentation/command.rb, agent/skills/evidence/SKILL.md, agent/skills/authoring/SKILL.md, agent/skills/review/SKILL.md |
| MCP no runtime documental | ABSENT | Os caminhos inspecionados usam HTTP Ollama e subprocessos verificados; nenhum dispatcher/servidor MCP foi adicionado. Conectores do host Codex são outro ambiente. | backend/lib/documentation/command.rb, agent/tools/documentation_retrieval.py |
| Conformidade com Agent Plugins | NOT VERIFIED | Não foi executado teste de conformidade de pacote/cliente compatível. Apenas o nome SKILL.md não caracteriza pacote de plugin conforme. | agent/skills/evidence/SKILL.md |
| Orçamentos de job completo | PARTIAL | Limites de fonte/resposta são explícitos; orçamento de tentativas/citações é por instância. Orçamento global persistente de ferramentas não foi implementado. | backend/lib/documentation/command.rb, agent/tools/documentation_retrieval.py |
| Cancelamento e deadlines | PARTIAL | Workers usam deadlines de subprocesso de3/20 segundos; transporte tem timeout de pedido. Cancelamento completo da inferência remota não foi verificado. | agent/tools/documentation_retrieval.py, backend/lib/documentation/command.rb |
| Supressão de duplicatas de helpers por journal | CONFIRMED | Pedidos/resultados/recibos são exclusivos; recibo ausente ou dado antigo nunca inicia nova extração automática. | agent/tools/documentation_retrieval.py |
| Conclusão ambígua de inferência | PARTIAL | Pedidos/respostas brutos são preservados. Uma inferência desconectada pode ter concluído remotamente; não há prova geral de reconciliação do servidor. | backend/lib/documentation/command.rb |
| Permissões de ferramentas e saída | PARTIAL | A API opcional confia em registros de leitura fornecidos pelo operador; fonte segue somente leitura enquanto registros privados de auditoria são gravados. Não há serviço de autorização multiusuário. | agent/tools/documentation_retrieval.py, agent/tools/documentation_maintenance.py |
| Instruções recuperadas continuam dados | PARTIAL | Allowlists e schemas restringem efeitos; rótulos de fonte não garantem obediência do modelo. Uma falsa REMOVE crítica está preservada. | agent/tools/documentation_retrieval.py, backend/lib/documentation/command.rb |
| Fronteira de propriedade de conteúdo humano | CONFIRMED | Checagens de propriedade do caller e manutenção isolada recusam escrita sem propriedade ou obsoleta; recomendações não concedem aprovação de publicação. | backend/lib/documentation/command.rb, agent/tools/documentation_maintenance.py |
| Evidência e recuperação locais | CONFIRMED | Restauração independente de código/modelo e137 testes restaurados passaram em Mac/Linux; perda remota e estado de treinador não foram verificados. | agent/recovery/bootstrap.py, agent/recovery/bundle.py |
| Treinador automático ou ingestão de arquivo de pesquisa | ABSENT | Não há execução de otimizador ou loader automático do dataset de pesquisa no caminho de autoria inspecionado. Gates de treino seguem fechados. | backend/lib/documentation/command.rb |

## Padrões e fronteiras propostas

A revisão MCP consultada é2026-07-28. O core usa pedidos autocontidos e informação
de capacidades por pedido; pressupostos de conexão de versões anteriores não
podem ser copiados sem análise.
[Especificação principal](https://modelcontextprotocol.io/specification/2026-07-28)

MCP define contratos de schema de entrada/saída e erros de protocolo/ferramenta
separados. Anotações exigem confiança; compatibilidade de transporte não autoriza
acesso ao filesystem. Nosso mapeamento futuro de status seria convenção da
aplicação, não garantia de precisão.
[Ferramentas](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)

O binding de transporte carrega metadados e delimita mensagens. Uma ponte futura
precisa vincular jobs autorizados independentemente da conexão; criar ferramenta
interna nova por pedido reiniciaria seu orçamento atual por instância. Esta é
inferência de projeto a partir do código e protocolo.
[Transportes](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports)

Cancelamento varia por transporte e pode chegar depois da conclusão. Timeout
não prova rollback nem permite repetir inferência de resultado desconhecido.
[Cancelamento](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/cancellation)

Agent Skills exige metadados em SKILL.md. Os três contextos fixos não têm esses
metadados; o nome do arquivo é insuficiente para conformidade. Descoberta
progressiva é capacidade distinta de loader.
[Formato](https://agentskills.io/specification),
[orientação de cliente](https://agentskills.io/client-implementation/adding-skills-support)

Agent Plugins1.0.0 padroniza plugin.json na raiz e componentes fixos opcionais.
Contenção de pacote não cria sandbox para seu subprocesso. Um pacote reutilizável
futuro exigiria validação de cliente/permissões além de envolver esses arquivos.
[Especificação](https://agent-plugins.org/specification)

## Compare três abordagens para o mesmo helper

| Dimensão | API interna | Exposição MCP local | Distribuição por skill/plugin |
|---|---|---|---|
| Potencial factual | Fonte ausente exata; qualidade da citação medida | Mesma evidência em outra interface | Procedimento isolado não fornece fonte ausente |
| Proveniência | Fonte/hash/seletor registrados e recibos | Preservar checagens e identidade de wire | Preservar proveniência de componentes e ferramenta subjacente |
| Complexidade | Já implementada em pesquisa | Novo ciclo de cliente/servidor/versão/processo | Novo loader/pacote compatível e revisão de permissão |
| Dependências | Python existente e produtor Go empacotado | Implementação/runtime de protocolo não selecionados | Cliente compatível e runtime de recuperação |
| Segurança | Fonte somente leitura; grava journal próprio | Mesma política e controle de job/transporte autorizado | Confiança no pacote e contenção/política de ferramenta |
| Interoperabilidade | API privada da aplicação | Fronteira padronizada após testes de conformidade | Procedimento/pacote portável após teste de cliente |
| Latência/recursos | Deadlines de worker3/20s; sem ganho controlado alegado | Não implementada ou medida | Custo de contexto/descoberta não medido |
| Manutenção | Contratos restritos de fonte/recibo | Compatibilidade de protocolo adicional | Compatibilidade de cliente/pacote adicional |
| Estado atual | Executada em pesquisa, fora do roteamento comum | Somente proposta | Somente proposta |

Podem se complementar: a mesma implementação interna poderia ser exposta por MCP
e distribuída com skill procedural. Empacotar isoladamente não demonstrou melhoria factual.

## Próximo trabalho por risco e decisões

1. Alto: exigir fonte/vínculo completos e preservar desconhecidos. A falsa REMOVE
   e explicação incorreta com helper justificam checagens semânticas independentes.
2. Alto: vincular versões atuais de referência antes de pontuar ou curar dados.
   A reconciliação V1/V3 é diagnóstico real, coberto por849 checagens de referência.
3. Alto: manter instruções recuperadas fora da autoridade de permissão. O modelo
   ainda pode interpretar mal um comentário mesmo com acesso somente leitura imposto.
4. Médio: adicionar ledger de passos/deadline do job pertencente ao operador antes
   de roteamento autônomo. Limites atuais são por instância, não orçamento global durável.
5. Médio: reconciliar conclusão desconhecida de inferência antes de nova tentativa.
6. Adiado: aprovar SDK/versão MCP, transporte, raízes permitidas, artefatos retidos,
   permissões, cancelamento/reinício e testes de conformidade específicos.
7. Adiado: aprovar separadamente empacotamento/carregamento de plugin e qualquer
   rota de prompt/ferramenta em produção. Esta nota não instala servidor ou pacote.

O [experimento medido](../owned-adapter-helper-comparison.json) e a
[regressão da ferramenta](../helper-cache-integrity-evaluation.json) respondem
questões distintas: acesso ao helper é viável e recuperável; melhoria da arquitetura
gerada não foi demonstrada. Rollback é omitir a chamada opcional e preservar
journals; o roteamento Ruby comum não mudou.

O relato da Anthropic motiva handoffs duráveis incrementais; seu fluxo com
escritas Git é inaplicável às restrições deste proprietário.
[Relato de engenharia](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)
O relato da OpenAI motiva evidência legível e feedback imposto pelo repositório;
seus resultados relatados não estabelecem qualidade do modelo local.
[Relato de engenharia](https://openai.com/index/harness-engineering/)

Pesquisa concluída: mapa atual, matriz de capacidades, comparação primária e
fronteiras de decisão. Experimento interno executado; integração MCP/plugin de
produção não realizada; treinamento neural não realizado.
