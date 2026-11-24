# Interrupção real: o que foi recuperado e o que permanece incerto

Este é um diagnóstico da ocorrência observada, não uma implementação de Harness, MCP ou nova rota de ferramentas. A autorização posterior do proprietário acrescentou aproximadamente duas horas à janela original da campanha. A instrução e sua interpretação estão preservadas em `private-research://continuation-20261119/owner-extension-20261119.json`.

## Evidência observada

Os containers de backend e Ollama apresentaram `StartedAt` em 19/11/2026 às 19:01:54 UTC. O handle anterior deixou de existir, o processo Ruby anterior estava ausente e `ollama ps` não mostrava modelo ativo na primeira inspeção. Esses dados comprovam que o pedido anterior não continuava em um processo vivo observado. Não medem o instante exato do desligamento nem sua duração.

O workspace temporário sobreviveu e foi copiado integralmente para `remaining-chapters-v1/interrupted-workspace`. O caso chi tinha uma resposta completa, auditoria e documentos. O caso SQLx tinha um evento `model_request`, mas nenhum `model_response` ou `outcome.json`. O evento do cliente acontece antes do transporte: sozinho, ele não comprova recebimento ou conclusão pelo servidor. A busca filtrada nos logs Docker não encontrou uma conclusão HTTP retida; essa ausência tampouco comprova que o servidor nunca executou a inferência.

A contagem mantém essa tentativa como **resultado desconhecido**, separada das respostas concluídas e dos tokens gerados conhecidos. Não foi atribuída uma resposta fictícia, nem uma duração de servidor estimada. A reconciliação está em `private-research://continuation-20261119/power-restart-reconciliation.json`.

Após comprovar ausência do processo antigo e receber a autorização de recuperação, uma única tentativa nova foi congelada com outro identificador. Antes do transporte, o runner exigiu igualdade integral entre a nova requisição preparada e o preflight original. A tentativa anterior permaneceu intacta. A nova resposta concluiu normalmente no servidor, foi preservada e acabou recusada pelo writer por uma exigência de nome qualificado. A revisão de fonte encontrou também erros factuais independentes dessa recusa.

## Recuperação de ambiente e limites

O runtime voltou com Ruby 3.4.11, Nokogiri 1.19.4, Action Pack 8.1.4 e Ollama 0.40.16. O digest aprovado permaneceu `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`. Uma primeira verificação parou na integridade documental: o README já havia mudado desde o manifesto anterior. Essa recusa não era evidência de dano aos pesos. A atualização preservou o manifesto anterior, verificou 252 arquivos operacionais e manteve o objeto de identidade do modelo exatamente igual ao baseline. A verificação seguinte confirmou conhecimento e grafo original do modelo.

Os artefatos locais e o índice Git sobreviveram. A extensão da campanha não autoriza staging, commits, uploads ou mudanças nos repositórios externos. A imagem preservada e as gems recuperadas reduzem dependências da recuperação, mas não demonstram um boot frio em outro computador. Veja [recuperação das dependências](backend-runtime-recovery.json) e [arquivo-base e inferência recuperada](capsule-preservation-recovery.json).

## Lacuna arquitetural confirmada

O [cliente atual](../../../backend/lib/documentation/command.rb) prepara a inferência em `infer`, verifica identidade e faz o transporte em `call_model`; `audit` oferece eventos. O runner desta pesquisa acrescenta persistência com `flush` e `fsync` por evento. Isso permitiu recuperar o que já tinha sido recebido. Não equivale a um protocolo de idempotência do servidor nem a um diário de pedido pendente universalmente consumido pelo agente.

A recuperação de arquivos de saída em `recover` e o diário de assembly do [coordenador](../../../backend/lib/documentation/project_command.rb) tratam outra fronteira: arquivos sob propriedade do pipeline. Uma transação de arquivos recuperável não prova que uma inferência remota pendente será executada uma única vez. `api/tags` confirma identidade instalada; não recupera o corpo de uma requisição perdida.

## Proposta de próxima aceitação, sem implementação

Um eventual diário de inferência deve distinguir `PREPARED`, `DISPATCHING`, `RESPONSE_PERSISTED`, `VALIDATED`, `OUTPUTS_COMMITTED` e `UNCERTAIN`. Persistir `DISPATCHING` antes da escrita no socket ainda deixa uma janela incerta; chamar esse estado de sucesso ou afirmar execução exatamente uma vez seria incorreto. A proposta não pressupõe suporte a chave de idempotência no endpoint Ollama atual.

Se houver resposta integral persistida e verificável, a recuperação pode revalidá-la antes de decidir por uma nova inferência. Sem resposta e com o processo antigo comprovadamente encerrado, a política precisa de um fallback previamente autorizado e limitado: uma tentativa nova vinculada à anterior, orçamento contado por tentativas, nenhuma exclusão da evidência incerta. Aqui essa autorização veio explicitamente do proprietário. Ela não constitui autorização permanente para retries sem limite.

O plano de avaliação deve cortar a execução em cinco pontos: antes do transporte, depois de o servidor poder ter recebido o pedido, depois da resposta persistida, antes da publicação de EN/PT e durante uma escrita já coberta pelo diário de arquivos. Cada corte deve verificar estado, hashes, ausência de duplicação silenciosa e preservação de conteúdo humano. Este documento define a aceitação; esses cortes não foram artificialmente executados contra os serviços reais.

Instruções embutidas em código recuperado não podem aumentar orçamento, alterar autorização ou escolher retry. O modelo continua responsável por texto candidato; aplicação e eventual Harness precisam controlar identidade, estado, orçamento e efeitos. A decisão de implementar esse diário ou uma capacidade de retrieval permanece separada da pesquisa autorizada. Nenhum servidor MCP, plugin, novo Harness ou roteamento de produção foi instalado.
