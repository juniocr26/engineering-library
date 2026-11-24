"""Root-only measured handoff; final mode refuses an unmet eleven-hour window."""
import argparse
import datetime
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--phase', choices=['active', 'final'], required=True)
args = parser.parse_args()
baseline = json.loads((P / 'baseline.json').read_text())
now = datetime.datetime.now(datetime.timezone.utc)
start = datetime.datetime.fromisoformat(baseline['start_utc'])
minimum = datetime.datetime.fromisoformat(baseline['minimum_target_utc'])
elapsed = (now - start).total_seconds()
if args.phase == 'final' and now < minimum:
    raise SystemExit('Finalization refused: measured eleven-hour minimum has not elapsed.')
final = args.phase == 'final'
local = now.astimezone(ZoneInfo('America/Sao_Paulo'))
hours, remainder = divmod(int(elapsed), 3600)
minutes, seconds = divmod(remainder, 60)
duration = f'{hours}h {minutes:02d}min {seconds:02d}s'
status = 'JANELA CONCLUÍDA — LIMITES TÉCNICOS EXPLÍCITOS' if final else 'ATIVA — CONSOLIDAÇÃO EM ANDAMENTO'
evidence = json.loads((P / 'final-evidence-integrity-v1.json').read_text())
model = json.loads((P / 'current-model-call-summary-v8.json').read_text())
faq = json.loads((P / 'faq-identity-overlap-audit-v8.json').read_text())
index = json.loads((P / 'current-documentation-candidate-index-v1.json').read_text())
recovery = json.loads((P / 'recovery-delta-receipt-v6.json').read_text())
manifest_sha = hashlib.sha256((ROOT / 'agent/recovery/manifest.json').read_bytes()).hexdigest()
assert manifest_sha == evidence['manifest_sha256']
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'), text=True).strip() == baseline['head']
assert hashlib.sha256((ROOT / '.git/index').read_bytes()).hexdigest() == baseline['index_sha256']
assert model['active_model_calls'] == model['optimizer_steps'] == model['gold'] == 0

def link(name):
    return '[' + name + '](agent/research/continuation-20261120/' + name + ')'

time_block = f"""Estado: **{status}**. Registro medido: **`{local.isoformat()}`** / `{now.isoformat()}`.

Início desta continuação: **20/11/2026,08:57:10 America/Sao_Paulo** (`{baseline['start_utc']}`). Janela mínima: **19:57:10.273488** (`{baseline['minimum_target_utc']}`). Tempo medido neste registro: **{duration}** ({elapsed:.3f} segundos). As46min36s da campanha anterior não entram nesta duração.

Onze horas atingidas: **{'SIM, por medição real' if final else 'NÃO; a campanha continua e este documento não autoriza encerramento antecipado'}**. Nenhuma exaustão de quota, cancelamento ou término de host foi observado como motivo de parada. O recibo técnico de fechamento registra seu próprio instante posterior de preservação e verificação; este cabeçalho identifica o corte medido do relatório.
"""

main = f"""# Engineering Library — relatório consolidado da continuação

{time_block}
## 1. Início efetivo

`{baseline['start_utc']}` / `{baseline['start_local']}`. Baseline limpa,HEAD `{baseline['head']}`,3444arquivos rastreados. A solicitação autorizada e o checkpoint inicial estão preservados em `agent/research/continuation-20261120/`.

## 2. Encerramento efetivo

{'Corte de encerramento deste relatório: '+now.isoformat()+'. A preservação técnica subsequente tem timestamp próprio no recibo de fechamento.' if final else 'Ainda não registrado. O mínimo não foi atingido; nenhuma conclusão é inferida de testes, relatórios ou tarefas já prontas.'}

## 3. Duração medida

**{duration}**,calculada do relógio UTC real e do início preservado. O recibo de fechamento complementa este registro com a duração efetiva de sua última verificação.

## 4. Cumprimento das11horas

**{'Mínimo atingido neste corte.' if final else 'Ainda pendente; execução permanece ativa.'}** Não foram usados sleeps artificiais, inferências sem hipótese ou timestamps futuros para cumprir a janela. Esperas de threads foram apenas dependências reais dos controles,limitadas por eventos e timeouts.

## 5. Motivo de término ou continuação

{'Encerramento após o mínimo medido e a consolidação autorizada,com limitações do produto mantidas explícitas. Não houve término antecipado.' if final else 'Continuar a consolidação e as verificações autorizadas até o mínimo medido. Não há motivo externo observado para parar antes.'}

## 6. Estado atual do repositório

Somente **engineering-library** foi alterado. Quatro arquivos rastreados modificados: `backend/lib/documentation/command.rb`,`backend/lib/documentation/python_structure.py`,`agent/tools/documentation_retrieval.py` e `agent/recovery/manifest.json`. Cinco cópias redundantes de relatórios anteriores foram removidas depois da preservação exata e da verificação de referências/recuperação. Os3435demais arquivos rastreados mantêm os bytes da baseline; HEAD,index e modos rastreados permanecem inalterados. Não houve staging,commit,push,reset,clean,rebase,stash,cherry-pick ou reescrita de histórico.

Versões dos arquivos-fonte: chamador **1.9.43**,HelperRetrieval **0.1.5**,planejador **0.3.6**,manutenção **0.1.5**. Os dois últimos não tiveram código alterado. Manifest operacional atual: `{manifest_sha}`. Seus1964itens são válidos e o objeto do modelo continua idêntico ao da baseline.

Isso não certifica a versão já carregada no processo Rails. O campo herdado `runtime.caller_version=1.9.30` é metadado histórico preservado; o bootstrap de runtime mede Ollama/modelo,e não esse processo Ruby. Nenhum serviço foi reiniciado ou publicado. Inventário individual completo: [AI_TRAINING_FILE_INVENTORY.md](AI_TRAINING_FILE_INVENTORY.md).

## 7. Comparação com a baseline histórica

| Item | Histórico relatado | Verificação atual |
|---|---|---|
| Python do agente |312passando |312testes existentes passam após helper0.1.5;68deles também passam no Linux3.11 |
| Ruby |262testes/1787assertions |Última execução relevante após chamador1.9.43 passa |
| JavaScript |101controles relatados |Resultado real100/102;duas falhas em entradas/fontes não alteradas |
| Avaliação pública original |0/8,todos inconclusivos |Permanece0/8no planejador de produção;oracle congelado intacto |
| Matriz de desenvolvimento |22/24 |Resultado histórico preservado,não convertido em generalização pública |
| Dados e gold |305registros/gold0 |Mesmos305registros,com bytes preservados nos sete arquivos;gold aprovado0 |
| Fine-tuning |NO-GO |NO-GO,zero de nove requisitos integralmente satisfeitos |

A análise das duas falhas frontend verifica140hashes de fonte e os dados que já existiam; não é uma execução separada em checkout pristine. O candidato isolado de links Go produz três referências disponíveis por idioma,mas não foi aplicado ao catálogo.

## 8. Resultados sobre fontes reais

| Família/escopo | Resultado verificado e limite |
|---|---|
| JMESPath |Fachada/parser/visitor,cache de classe e exceções documentados por fonte;capítuloV3com9afirmações/6FAQ |
| go-geom |Pacote raiz compilado offline,sete conjuntos de métodos e exemplo compilado;sem execução do pacote |
| Totalist |Declarações,README,exports e limites Git/distribuição;sem inventar arquivos dist ausentes ou identidade npm instalada |
| Boltons |Oito casos originais diagnosticados;dois trechos selecionados executados sob facades próprias;outros contratos permanecem escritos/limitados |
| HTTPX/httpcore |Fronteiras de construção,pool,iteração,close/contexto e tradução;21casos/70assertions repetidos em dois Python e seis casos próprios adicionais,não somados como independentes |
| go-humanize |36casos congelados por revisão;35previsões exatas coincidem. A divergência de ponto flutuante é erro da expectativa própria,preservado. Tipos/inicializadores e exemplo compilado sem executá-lo |
| backoff |30casos compartilhados por revisão+8casos da API atual;seis formas de consumo compiladas por revisão. Relógios/timers próprios,sem espera real de retry |
| p-limit/yocto-queue |Módulos exatos observados;16casos runtime,16tipos e12formatos mantidos separados. Limpar fila não prova cancelamento das operações ativas |
| cachetools |Família já exposta.23observações nativas em14grupos coincidem em Mac3.14/Linux3.11;um caso adicional sem armazenamento computa duas vezes sequencialmente,com pico de concorrência1 |
| MLX-LM/MLX |Código e metadados fixados;construtor puro de argumentos e adapters puros selecionados observados. Nenhum framework completo,tokenizer real,modelo,tensor,trainer ou otimizador foi executado |

Os repositórios e materiais externos foram usados **sem alterações**,com snapshots,commits,citações físicas e avisos de licença preservados. A lista completa distingue aliases locais e nomes remotos no inventário.

## 9. Decisões de ciclo de vida

O planejador original continua **0/8**,com a primeira recusa na admissão de módulo completo/imports. Apenas permitir imports não resolveria os demais limites. O protótipo de gramática fechada para helpers alcança8/8nos casos Boltons já expostos;isso é desenvolvimento,não holdout independente nem integração de produção. O perfil isolado de pares literais com papel/polaridade alcança23/23controles próprios contra14/23do perfil anterior,e sete verificações HTTPX;anotações,prosa geral de runtime e a transição cujo helper antigo está ausente continuam inconclusivas.

Cachetools produziu sete **referências manuais**:ADD1,MODIFY2,REMOVE1,NO-OP2,INCONCLUSIVE1. Não são sete acertos de classificador. REMOVE está restrito à entrada atual de `MRUCache`/`func.mru_cache`,com aviso primário explícito de retirada,exportações completas selecionadas e observação de namespace;histórico preservado. Não houve remoção de capítulo ou catálogo publicado.

## 10. Melhorias concretas de compreensão e validação

O chamador preserva referências citadas de exceções capturadas e de mapas literais diretos,com limites explícitos. O guard compartilhado verifica nomes/presença/proprietários entre idiomas;**não verifica direção de pares ou verdade de toda prosa**. Seis fatos incorretos conhecidos ainda são renderizados nos controles de limite.

HelperRetrieval0.1.5reconstrói a unidade lexical Python/Go esperada antes de aceitar evidência nova ou cacheada. Controles próprios:Python2/7→7/7;Go2/9→9/9. Os dois casos Go válidos esperamDUPLICATE,a regra original da API;uma expectativa inicial errada foi corrigida em novo oracle antes do candidato,sem reescrever resultados antigos. Journals legados permanecem para revisão explícita,sem migração ou reembolso automático de budget. A validação Go requer a ferramenta local de extração.

## 11. Avaliação factual do modelo

**Nove chamadas concluídas**,mesmo `llama3.2:3b`,digest `{model['same_digest']}`:sete tarefas de geração/julgamento de fonte e duas condições de um único probe de cópia. **8140tokens gerados/4085.059segundos de servidor**,zero chamadas ativas. Nenhuma entrega completa solicitada foi aceita;contagens heterogêneas não são denominador de acurácia.

Capítulos/FAQ falharam por fatos inventados,identificadores traduzidos,idioma ausente,cortes em imports ou repetição. HTTPX acertou9/16rótulos,mas nenhum registro cumpriu integralmente os critérios de resposta. Cachetools retornou JSON completo com10INSUFFICIENT,e apenas1/10rótulos coincide com a referência. Os probes de cópia falharam estritamente,embora o programa inglês com aspas tenha sido copiado em um objeto filho diagnóstico;isso refuta a impossibilidade geral de representar imports escapados,não explica a causa dos cortes longos. Não houve retry nem promoção de fragmentos a gold. {link('current-model-call-summary-v8.json')}

## 12. Candidatos de documentação

Índice corrente isolado: **9capítulos/18arquivos de idioma,113afirmações revisadas por fonte,255trechos físicos**;três exemplos auxiliares também têm identidade conferida. O leitor com raiz explícita verificou94arquivos distintos. Isso comprova bytes,posições e caminhos,não entailment geral de prosa. O ledger MLX-LMV3corrige dois caminhos absolutos da versão anterior,com os mesmos documentos;seis controles do leitor existente confirmam raiz restaurada e recusam caminho absoluto/travessia/cut errado.

O pacote cachetools tem27arquivos preservados:documentos próprios anteriores/candidatos,diffs EN/PT e manifest. Seus24documentos presentes/quatro ausências esperadas e dois diffs foram reconstruídos no restoreV6. Nenhum documento humano ativo foi usado ou removido. O applier de produção não foi ampliado para esses perfis de pesquisa.

## 13. Qualidade EN/PT-BR

O censo atual confere286linhas de idioma/143pares:77pares congelados+66atuais. Não há divergências nos code spans atuais. O novo capítulo MLX-LM possui14revisões de linguagem pelo agente;isso não é revisão humana independente ou certificação semântica. A preservação lexical não prova equivalência de negações,quantificadores,escopo ou todos os fatos.

## 14. FAQ e manutenção

Dos66pares atuais,60derivam de capítulos e seis são FAQ standalone relacionadas às mesmas fontes. Versões antigas não são somadas. O suplemento da própria Engineering Library foi atualizado de helper0.1.3para0.1.5em versão nova:10afirmações/seisFAQ/95verificações,com os quatro pares antigos preservados. Seus24trechos históricos foram vinculados a bytes exatos atuais ou a três preimages preservados,sem reescrever capítulos antigos. A revisão permanece pendente do proprietário.

## 15. Linhagem e dados

Os **305registros originais**,em sete arquivos,não foram alterados nem exportados para treino. Há42grupos de linhagem/17famílias declaradas,396referências congeladas e13registros de licença/aviso em11repositórios;integridade não é autorização de uso. Gold aprovado0. Propostas suplementares de revisão/revisão de metadados não reescrevem esses dados.

O diagnóstico hipotético de partição por linha separa28tarefas bilíngues e15famílias;por linhagem ainda separa quatro famílias;por família declarada elimina somente as sobreposições medidas. Não foi criado split train/valid/eval real,nem independência de pré-treinamento certificada. Exclusões append-onlyV2→V11e default-deny retêm os novos derivados fora de treino.

## 16. Prontidão de fine-tuning

**NO-GO:0/9requisitos plenamente satisfeitos.** O GGUF implantado não estabelece disponibilidade de checkpoint/tokenizer treináveis compatíveis. O plano futuro é somente dados,sem comando executável/autorização de lançamento. Contagens condicionais de adapters e nomes de wheels não medem memória,Metal,resolução de dependências ou treino. Relatório dos nove requisitos: [AI_FINE_TUNING_READINESS.md](AI_FINE_TUNING_READINESS.md).

## 17. Testes e verificações executados

| Verificação existente | Resultado e escopo |
|---|---|
| Agente,MacPython3.14 |312testes passam após helper0.1.5 |
| Subconjunto helper/job,LinuxPython3.11 |68testes existentes passam;estão contidos nos312,não são68novos |
| BackendRuby |262testes/1787assertions passam após o último código de chamador alterado |
| BackendPython,linhas físicas |3controles passam |
| Frontend |100/102;duas falhas explícitas de catálogo/links em entradas não alteradas |
| Recuperação operacional/modelo |1964itens/seis blobs pequenos;hashes completos do store e Ollama0.40.16/digest verificados após a nona inferência |

Nenhum arquivo de teste permanente,fixture permanente ou infraestrutura de teste foi alterado. Matrizes próprias,repetições em outros ambientes e contagens de citações não são somadas como novos testes ou acurácia independente.

## 18. Hipóteses rejeitadas e falhas próprias preservadas

- Gramáticas de helper muito amplas aceitaram fluxos que interrompiam o caminho;versões posteriores restringem a admissão escrita,sem prometer comportamento geral.
- Um guard ingênuo de pares com dois-pontos recusava anotação e negação verdadeiras;foi rejeitado e não implantado.
- As nove entregas neurais completas foram rejeitadas. A causa dos cortes em capítulos permanece desconhecida;parâmetros de stop preservados não contêm regra de aspas/import.
- A previsão numérica própria de go-humanize estava errada em um caso;fonte/oracle e divergência permanecem preservados.
- O primeiro censo GoMatchFile duplicava capacidade já existente;nenhuma nova capacidade de binding é atribuída a esse estudo.
- Erros próprios de seletores,indentação,namespace de anotação,ID de fila,forma de schema,status e campos diagnósticos têm originais/recibos preservados;correções não são falhas do projeto externo.
- Comprimentos brutos,offsets de template,source hashes e flags de metadados não substituem tokens reais,alinhamento,semântica ou aprovação. O probe sem armazenamento limita a interpretação exactly-once.
- O ledger MLX-LMantigo tinha caminhos absolutos;foi preservado e substituído no índice corrente por vínculo relativo explícito. Journals antigos não foram tornados portáveis por essa correção.

## 19. Recuperação comprovada

O corteV6restaurou **21534arquivos efetivos** e preservou todos os hashes antes/depois do bootstrap. O helper carregado do restore fez GoFOUND,DUPLICATE e REFUSEDpara uma substituição coordenada própria,e PythonFOUNDpara uma fonte real. O pacote de revisão foi consumido sem modificar o restore. {link('recovery-delta-receipt-v6.json')} / {link('restored-research-consumption-v6.json')}.

O fechamento associa o corte incremental mais recente e um envelope posterior dos relatórios/inventário/recibos,com hashes e regra explícita de não autorreferência. Consulte `agent/research/continuation-20261120/closing-receipt-v1.json` quando emitido. Arquivos posteriores aoV6não são retroativamente declarados dentro dele. Store/modelos e assets históricos permanecem separados e preservados;nenhum cold boot,backup remoto ou recuperação de estado de treinamento foi testado.

## 20. Trabalho restante

Integrar compreensão mais ampla de módulos/helpers somente após critérios claros;manter as recusas seguras. Avaliar famílias/tarefas realmente independentes sem confundir exposição prévia com holdout. Resolver as duas falhas frontend sob escopo próprio. Rever candidatos/citações/FAQs com o proprietário antes de publicação. Continuar os nove requisitos de treino,sem usar respostas rejeitadas como gold nem assumir viabilidade a partir de aritmética ou inferência GGUF.

## 21. Aprovações futuras necessárias

Nenhuma confirmação adicional foi usada para interromper a campanha autorizada. Fora desta campanha,permanecem necessários:aprovação de alvos/direitos,gold e partição independente;escolha e aquisição autorizada de checkpoint/tokenizer;ambiente/framework e orçamento de piloto medido;autorização explícita de qualquer treino;revisão de publicação/integração de catálogo e de novos testes permanentes. Nenhuma dessas ações foi executada por inferência de autorização.

## 22. Continuação segura exata

Ler [AI_TRAINING_RESUME.md](AI_TRAINING_RESUME.md),o recibo de fechamento,o índice corrente de candidatos e a fila materializada. Verificar HEAD/index e pins antes de novas alterações. Reconstruir baseline+overlay e deltas efetivos na ordem registrada;arquivos históricos separados não devem sobrescrever cortes novos. Aplicar o envelope posterior conforme o recibo,verificar hashes e executar `python3 agent/recovery/bootstrap.py knowledge`. Criar registries explícitos para uma nova raiz;preservar journals/budgets antigos,sem rebase textual ou retry automático. Não reexecutar produtores não reentrantes nos mesmos diretórios. Não iniciar fine-tuning,publicação ou operações Git de escrita.

## Histórico cronológico preservado

"""

gates = [
    ('Modelo/tokenizer compatíveis', 'BLOQUEADO', 'GGUF verificado;pesos/tokenizer treináveis compatíveis não disponíveis/verificados localmente. Metadados comunitários não são checkpoint.'),
    ('Alvos aprovados e direitos', 'BLOQUEADO', '305registros intactos,gold0;avisos primários preservados não aprovam treino ou qualidade dos alvos.'),
    ('Avaliação independente', 'PARCIAL', 'Famílias/tarefas expostas agrupadas;diagnóstico de partição não cria split nem certifica independência neural.'),
    ('Viabilidade de hardware', 'PARCIAL', 'M1Pro/16GiB/10CPU observado;sem treino,memória/throughput/Metal não medidos. Contagens de adapters são condicionais.'),
    ('Framework e ambiente', 'BLOQUEADO', 'Framework/tokenizer não instalados. Wheels cp314nominais não resolvem dependências ou comprovam execução. Somente subsets puros MLX-LM foram observados.'),
    ('Persistência de estado', 'PARCIAL', 'Fonte salva pesos de adapter e cria otimizador novo;estado completo de otimizador/RNG/posição/crash não recuperado. Nenhum adapter criado.'),
    ('Orçamento aprovado', 'BLOQUEADO', 'Proposta de16iterações/30min e limites de memória são dados não executados,não orçamento autorizado ou medido.'),
    ('Isolamento e rollback', 'PARCIAL', 'Fontes/modelos originais preservados;ambiente futuro de treino e rollback de adapters não validados.'),
    ('Avaliação/recuperação reprodutíveis', 'PARCIAL', 'Recuperação local de fontes/evidências e consumidores selecionados funciona;avaliação neural independente e recuperação de treinamento não estão completas.'),
]
readiness = '# Prontidão de fine-tuning — NO-GO\n\n' + time_block + '\n**Zero de nove requisitos integralmente satisfeitos;gold aprovado0;optimizer steps0. Nenhum treino foi autorizado ou executado.**\n\n| Requisito | Estado | Evidência atual |\n|---|---|---|\n'
for title, state, text in gates: readiness += f'| {title} | {state} | {text} |\n'
readiness += f"""
Os adapters puros de dados não consultam aprovação/exclusão da Engineering Library. O formato nativo observado não é o schema dos305registros. Flags como `launch_allowed=False` em propostas próprias não são uma trava do código upstream. Antes de qualquer futuro piloto,validar dados aprovados,ancestralidade agrupada,prefixo real/tokenizador,domínio deslocado dos alvos,truncamento,número efetivo de módulos,chaves globais,dtype/memória e persistência real.

O plano futuro permanece não executável/não autorizado. Camadas zero/negativas e chaves omitidas podem selecionar mais módulos do que a intenção;os valores434176/81920são elementos condicionais,não memória de treino. O campo scale da rota inspecionada é multiplicador direto,sem divisão por rank. A inspeção mínima de MLX0.32.3não é ambiente resolvido. Não foram baixados pesos/tokenizer,instalados frameworks ou executados modelo,tensor,trainer,LoRA,QLoRA ou optimizer.

Nove chamadas de inferência em GGUF produziram zero entregas completas aceitas;isso não mede viabilidade de treino. Os66pares atuais de FAQ derivam de60pares de capítulos e seis standalone;77pares congelados e outros alvos/referências compartilham fontes. Nenhum split real foi criado. ExclusõesV2→V11e default-deny permanecem vigentes. O índice relativo corrente e os relatórios são artefatos de revisão,não export de treinamento.

O runtime/caller de aplicação já carregado não foi medido/reiniciado;somente arquivos-fonte,pins e Ollama/modelo foram verificados no escopo descrito. Recuperação de21534arquivos noV6e recuperação selecionada de Node/TypeScript/Go não satisfazem treino ou cold boot. Recibo final: `agent/research/continuation-20261120/closing-receipt-v1.json` quando emitido.

## Evidência anterior preservada

"""

resume = '# Continuação e recuperação segura\n\n' + time_block + f"""
Fonte atual:caller1.9.43/helper0.1.5;planner0.3.6/maintenance0.1.5inalterados. ManifestSHA `{manifest_sha}`;HEAD `{baseline['head']}`;indexSHA `{baseline['index_sha256']}`. Quatro arquivos rastreados modificados,cinco cópias redundantes de relatório removidas com preservação;testes permanentes,UI,schemas,infra e catálogo ativo não alterados. Modelo `{model['same_model']}`,digest `{model['same_digest']}`;nove chamadas completas rejeitadas,nada ativo,gold0,optimizer0,305registros intactos.

1. Ler o recibo de fechamento e seus hashes. O corteV6tem21534arquivos;seu restore foi consumido com helper0.1.5e pacote de revisão. O corte incremental final e o envelope posterior são descritos no fechamento,não inferidos a partir do nome do arquivo.
2. Verificar cada asset antes de extrair. Reconstruir baseline+overlay,depois os assets de papel `effective_parent_delta_*` na ordem registrada,e o delta atual. Preservar mas não aplicar fora de ordem os `separate_historical_delta_*`. Aplicar o envelope posterior somente depois de conferir o corte base,e verificar o mapa efetivo de hashes informado.
3. Executar `python3 agent/recovery/bootstrap.py knowledge` na raiz selecionada. Isso não instala o ambiente completo,não prova cold boot,não restaura pesos automaticamente nem autoriza iniciar serviços.
4. Consumir `current-documentation-candidate-index-v1.json` com `verify_current_candidate_index_v1.py --root <raiz explícita> --output <novo arquivo autorizado>`. O índice tem9capítulos,18arquivos de idioma,113afirmações e255trechos físicos. O ledger MLX-LMcorrente éV3com caminhos relativos;V2e o verificador antigo não devem ser usados como prova de leitura de uma raiz restaurada. O suplemento próprio corrente éV3;para citações antigas,usar `self-chapter-historical-citation-bindings-v1.json`.
5. Construir novos registries explícitos para uma nova raiz. Não editar caminhos dentro de journals antigos,não migrar/refundar budget,não reinjetar resultados legados como se fossem novos. Helper0.1.5retém versões anteriores para revisão. O parser Go local ainda é necessário para revalidar cache Go.
6. Preservar o oracle público original0/8. Os8/8Boltons expostos,23/23mapas próprios,sete HTTPX e sete referências manuais cachetools são escopos diferentes. Nenhum deles demonstra um classificador geral integrado ou publicação automática.
7. Manter frontend100/102explícito;somente o candidato isolado de links Go foi validado. Não aplicar ao catálogo durante esta continuação. Os312Python/68Linuxsubset/262Ruby1787assertions são verificações existentes,não contagem cumulativa de novos testes.
8. Continuar pela fila materializada `research-queue-current.json`,com checkpoint aproximadamente a cada30min e após operação crítica. Não reexecutar produtores exclusivos nos diretórios já existentes. Preservar todos os candidatos,fracassos,raw responses,snapshots,preimages e cadeias;nenhuma limpeza estética ou operação Git de escrita é autorizada.
9. Treino permanece **NO-GO**. Não usar os305registros ou os66pares como exemplos independentes aprovados. Nenhum download de checkpoint/tokenizer,instalação,optimizer step ou publicação decorre deste relatório. Revisar os nove requisitos e obter autorizações próprias para ações futuras.

## Notas anteriores preservadas

"""

def polish_prose(text):
    # Preserve every inline-code token and Markdown target byte-for-byte.
    text = text.replace('Wheels cp314nominais', 'Wheels `cp314` nominais')
    protected = re.compile(r'(`[^`\n]*`|\]\([^\)\n]+\))')
    parts = protected.split(text)
    before = protected.findall(text)
    for index in range(0, len(parts), 2):
        value = parts[index]
        value = re.sub(r'(?<=[0-9])(?=[A-Za-zÀ-ÖØ-öø-ÿ])', ' ', value)
        value = re.sub(r'(?<=[a-zà-öø-ÿ])(?=[0-9])', ' ', value)
        value = re.sub(r'(?<=[a-zà-öø-ÿ])(?=V[0-9])', ' ', value)
        value = re.sub(r',(?=\S)', ', ', value)
        value = re.sub(r';(?=\S)', '; ', value)
        for old, new in [('seisFAQ', 'seis FAQ'), ('GoFOUND', 'Go FOUND'), ('PythonFOUND', 'Python FOUND'), ('REFUSEDpara', 'REFUSED para'), ('DUPLICATE,a', 'DUPLICATE, a')]:
            value = value.replace(old, new)
        parts[index] = value
    result = ''.join(parts)
    assert protected.findall(result) == before
    return result

main, readiness, resume = map(polish_prose, [main, readiness, resume])

histories = {
    'AI_TRAINING_CAMPAIGN_REPORT.md': ('## Retained chronological progress', '## Histórico cronológico preservado'),
    'AI_FINE_TUNING_READINESS.md': ('## Retained readiness evidence', '## Evidência anterior preservada'),
    'AI_TRAINING_RESUME.md': ('## Retained dated continuation notes', '## Notas anteriores preservadas'),
}
history = ROOT / '.local-backups/continuation-20261120/root-report-history'
history.mkdir(exist_ok=True)
receipts = []
for name, prefix in [('AI_TRAINING_CAMPAIGN_REPORT.md', main), ('AI_FINE_TUNING_READINESS.md', readiness), ('AI_TRAINING_RESUME.md', resume)]:
    path = ROOT / name
    before = path.read_bytes(); checksum = hashlib.sha256(before).hexdigest()
    preserved = history / (checksum + '.md')
    if not preserved.exists(): preserved.write_bytes(before)
    assert preserved.read_bytes() == before
    old_marker, new_marker = histories[name]
    text = before.decode()
    marker = new_marker if new_marker in text else old_marker
    assert text.count(marker) == 1
    retained = text.split(marker, 1)[1].lstrip('\n')
    path.write_text(prefix + retained)
    receipts.append({'path': name, 'before_sha256': checksum, 'preimage': str(preserved.relative_to(ROOT)),
                     'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
record = {'at': now.isoformat(), 'local': local.isoformat(), 'phase': args.phase, 'elapsed_seconds': elapsed,
          'duration_minimum_reached': now >= minimum, 'eleven_hours_claimed': final, 'reports': receipts,
          'finalization_guard': 'Final mode refuses any measured time before baseline minimum; no sleeping or future timestamp.',
          'actual_closing_control_receipt_has_later_timestamp': True, 'source_code_changed': False,
          'model_calls': 0, 'optimizer_steps': 0, 'owner_gold': 0}
out = P / ('root-handoff-' + args.phase + '-v4.json')
with out.open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({'phase': args.phase, 'elapsed': duration, 'minimum_reached': now >= minimum, 'reports': len(receipts), 'manifest_sha256': manifest_sha}))
