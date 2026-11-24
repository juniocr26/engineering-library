"""Append the final human-facing research cut to exactly four canonical root reports."""
from pathlib import Path
import datetime,hashlib,json,sys,re
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
names=['AI_TRAINING_CAMPAIGN_REPORT.md','AI_TRAINING_FILE_INVENTORY.md','AI_FINE_TUNING_READINESS.md','AI_TRAINING_RESUME.md']
assert sorted(x.name for x in ROOT.glob('AI_*.md'))==sorted(names)
integrity=json.loads((P/'campaign-closing-integrity-v2.json').read_text())
assert all(integrity[k]for k in ['all_heads_unchanged_since_current_campaign_start','all_41_external_statuses_unchanged','all_commands_successful','git_index_matches_start','all_input_hashes_match','all_versions_match'])
assert integrity['own_tracked_diff']['stdout']==integrity['own_staged_diff']['stdout']==''
checkpoint=json.loads((P/'recovery-checkpoint-015.json').read_text())
assert checkpoint['owned_parser_restored_replay']['exact_original_observer_output_reproduced']
assert checkpoint['owned_identity_parser_restored_replay']['exact_original_observer_output_reproduced']
metrics=json.loads((P/'acceptance-metric-catalog-v5.json').read_text())
lifecycle=json.loads((P/'lifecycle-matrix-and-rate-audit-v8.json').read_text())
assert lifecycle['new_owned_unique_cases']==84 and lifecycle['matrix_rate_invariants_verified']==85
assert set(json.loads((P/'fine-tuning-nine-gate-review-v7.json').read_text())['all_nine_gates'].values())=={'NO_GO'}
ledger=json.loads((P/'current-campaign-inference-ledger-v2.json').read_text())
assert ledger['current_campaign_attempts']==98 and not ledger['active_started_without_terminal']
at=datetime.datetime.now(datetime.timezone.utc)
start=datetime.datetime.fromisoformat('2026-11-21T13:27:15.678298+00:00')
elapsed=(at-start).total_seconds();whole=int(elapsed)
duration=f'{whole//3600}h{whole%3600//60:02d}m{whole%60:02d}s'
local=at.astimezone(datetime.timezone(datetime.timedelta(hours=-3)))
prefix='agent/research/acceptance-calibration-20261121/'
def link(name,label=None):return f'[{label or name}]({prefix}{name})'
def matrix_table(condition):
 c=next(c for c in lifecycle['new_owned_cohorts']if c['cohort']=='new-retirement-reachability-challenge-8')
 m=c['conditions'][condition]['matrix_reference_rows_predicted_columns'];labels=['ADD','MODIFY','REMOVE','NO-OP','INCONCLUSIVE']
 text='| Referência / previsão | ADD | MODIFY | REMOVE | NO-OP | INCONCLUSIVE |\n|---|---:|---:|---:|---:|---:|\n'
 return text+'\n'.join('| '+r+' | '+' | '.join(str(m[r][c])for c in labels)+' |'for r in labels)+'\n'

campaign=f'''Este é o corte final de resultados da pesquisa atual; os registros anteriores permanecem como histórico. Início efetivo: **2026-11-21 13:27:15.678298 UTC / 10:27:15 São Paulo**. Fechamento desta análise: **{at.isoformat()} / {local.strftime('%H:%M:%S')} São Paulo**. Decorrido até este corte: **{duration}**. Houve duas pausas e retomadas explícitas do proprietário. Não existe instrumentação exata de tempo produtivo/pausado; tempo do servidor de inferência não equivale a trabalho decorrido. As cerca de12horas da campanha anterior não entram neste tempo. O horário posterior de encerramento da preservação, hashes e estado final estão no {link('campaign-completion-receipt-v1.json','recibo de conclusão')}, produzido após restaurar o corte final. Nenhum tempo de espera artificial ou repetição de suíte inalterada foi usado para preencher a campanha.

O resultado principal é uma fronteira de aceitação mais confiável, **sem demonstração de mudança nos pesos ou geração autônoma de capítulos completos**. Os denominadores históricos continuam **0/9** e **0/13**, separados. K aprovou3/3 notas limitadas mistas porque copiou literalmente28 pares de fatos EN/PT fornecidos e combinou metadados determinísticos; isso comprova cópia/serialização sob estas condições, não descoberta factual. T aprovou2/2 notas de template manual, com contribuição neural zero. Os casos de extração da fonte continuaram a falhar na aceitação integral. Não há OWNER_APPROVED, Gold, publicação, novo adaptador ou atualização de otimizador.

| Estratégia | Unidade efetivamente solicitada | Aceitação completa dessa unidade |
|---|---|---:|
| A | Nota bilíngue limitada, geração direta | 0/3 |
| B | Notas montadas a partir de10 chamadas de seções | 0/3 |
| C | Nota a partir de fatos verificados fornecidos | 0/3 |
| D | Conjunto estruturado completo de afirmações | 0/3 |
| E | FAQ bilíngue | 0/3 |
| F | Montagem após verificação separada dos mesmos D | 0/3; nenhuma chamada nova |
| G | Nota com instrução explícita de abstenção | 0/3 |
| H / J | Formato por schema, comparado respectivamente a A / C | 0/3 em cada condição |
| K | Nota mista com cópia do banco de fatos correto | 3/3; respostas fornecidas na entrada |
| L | Mesmo formato limitado, extraindo fatos da fonte | 0/3 |
| M | Correção de uma pergunta de L/Cobra | 0/1 |
| P | Relações AST tipadas convertidas em prosa neural | 0/1 |
| Q | Escolha entre relações oferecidas, seguida de montagem | 0/3 |
| T | Template manual a partir de relações tipadas | 2/2; zero contribuição neural |

W e X são controles de cópia, sem denominador de documento: W reproduziu0/9 linhas exatamente a partir de cartões com endereços; X reproduziu9/9 strings de linhas corretas fornecidas, incluindo espaços e tabulações. X muda representação da entrada e remove localização conjuntamente. A inversão das alternativas do usuário em Q/FastAPI mudou seis escolhas: três melhoraram, uma regrediu e duas permaneceram erradas;3/9→5/9, ainda sem nota aceita. Inverter apenas a ordem do schema não mudou escolhas. M corrigiu C01/C04, mas regrediu C05. Nenhuma destas comparações identifica uma causa interna geral ou constitui amostras independentes.

As98 tentativas atuais estão terminais:95 respostas,87 paradas normais,8 por limite de saída e3 falhas de transporte. Foram31.911 tokens gerados e15.320,597 segundos de servidor; estes são totais operacionais heterogêneos. Todos os pedidos permanecem vinculados aos protocolos e hashes congelados:39FastAPI,31Cobra,28Zod, todos DEV expostos e excluídos de treino. Não houve novas chamadas neurais nos controles finais de identidade, publicação e inicialização. A configuração usual congelada foi temperatura0, seed11621,4threads e contexto8192; a condição de recurso do crítico usou4096 e foi mantida separada. Limites de saída e keep_alive variam apenas conforme seus protocolos, não como uma configuração única agregada.

O {link('acceptance-metric-catalog-v5.json','catálogo de métricas')} conserva unidades e fontes. A precisão selecionada de proposições de L/FastAPI é5/10 suportadas,2/10 contraditas,3/10 insuficientes; L/Cobra7/10 suportadas e3/10 contraditas. Em Zod, os10 fatos EN têm5S/4C/1I, enquanto os pares EN/PT têm2S/4C/4I. Não são métricas de toda a prosa nem grupos independentes. O suplemento pós-saída separa12 propriedades em6 pares, com os14 campos de proveniência; não altera referências ou resultados originais. A precisão atômica exaustiva das95 respostas não foi universalmente medida e não é inventada.

Os críticos de rótulo corrigidos V/R acertaram4/9 referências cada. Entre6 negativos, V deu falso suporte em4 e R em1; R também se absteve em2/3 positivos. Ambos identificaram0/3 contradições como CONTRADICTED. Falsa rejeição estrita S→C é0/3 para ambos, mas isso não elimina as abstenções indevidas. Razão/evidência não foram solicitadas nessa condição: sua validade é null. O estudo separado de18 críticas de saídas reais tem15 respostas válidas e3 truncadas, com seus próprios limites. Mesmo modelo gerador/crítico e mesmo agente não fornecem certificação independente.

O índice de documentos registra11 dimensões para34 fluxos de notas,3 pares existentes selecionados,23 pares públicos do dataset original e1 par do adaptador próprio:61 registros de escopos sobrepostos, não61 ensaios independentes. Dez suplementos preencheram pontuações explícitas sem mudar veredictos. Documento ausente recebe0 por ausência da unidade, não como afirmação factual contradita. C/Cobra era JSON válido, mas um fragmento parecido com PT estava dentro de uma string; não havia objeto PT correspondente. C/Zod cobriu10/10 fatos e falhou por FAQ falsa.

Na manutenção documental há84 casos próprios em11 coortes e8 coortes históricas separadas. A nova coorte de inicialização tem4 referências REMOVE e4 INCONCLUSIVE. **V7:**

{matrix_table('v7_action')}
**V8, perfil conservador de módulo literal:**

{matrix_table('v8_action')}
V7 ainda faz4/4 falsas remoções nesta coorte. V8 bloqueia as4, mas mantém apenas1/4 remoções legítimas e perde outras4 legítimas em coortes anteriores. As antigas coortes de autoridade continuam registradas: V6 tinha6/6 e4/4 falsas remoções; o sucesso limitado de V7 nelas não se generalizou. ADD/NO-OP não têm suporte de referência nas novas coortes, e taxas sem denominador são null. As85 matrizes/indicadores foram recalculadas a partir das observações sem reexecutar planejadores: {link('lifecycle-matrix-and-rate-audit-v8.json','matrizes completas')}. Nenhum documento real foi removido.

O diagnóstico confirmado inclui associação à função errada, inversão de guardas, confusão entre tipo/default/comportamento, identificadores alterados, EN/PT incompleto, FAQs incorretas, negativas globais sem escopo, abstenção inadequada e truncamento. A pergunta original de C01 e o contexto incompleto do cabeçalho em críticos antigos são confundidores preservados, não falhas atribuídas integralmente ao modelo. O primeiro HTTP500 de A não teve corpo preservado; isso é uma limitação permanente, sem reconstrução ou repetição. Nem todos os HTTP500 têm causa comprovada. Histórico de OOM no contêiner não valida nem inviabiliza por si só o futuro runtime nativo.

Os57 controles tipados Go/TS e27 Python só validam interfaces finitas. Quatro variantes conservaram vetores AST, três alteraram qualificadores semânticos. A identidade completa das funções detectou mudanças de corpo, mas duas novas mudanças de dependência conservaram essa identidade e alteraram o significado. Todos os mutantes diferem do hash original; nenhum foi admitido como nova revisão. Hash, citação, schema, identificador ou sintaxe isolados não certificam verdade.

Nos documentos existentes selecionados, FastAPI/Cobra passaram apenas em revisão de fonte pelo mesmo agente; Zod precisa esclarecer a redação que sugere revisor independente. Os3 pares de FAQ selecionados estão corretos no escopo limitado. O pacote preserva6 textos de capítulos,116 proposições selecionadas e76 intervalos de citações conferidos; não é precisão universal nem aprovação do dono. Dos23 pares públicos originais,20 passaram em revisão de fonte e3 precisam de ajustes procedurais (compressão, animação e Redis). Os69 pares públicos de FAQ foram revisados separadamente; nenhuma redação original foi alterada. Consulte {link('owner-review-package-v3.json','pacote para revisão')} e {link('public-chapter-body-proposed-clarifications-v1.json','ajustes propostos')}.

A população histórica de documentação manual continua em11 tópicos de10 famílias,22 arquivos EN/PT e11/20 versões editoriais prontas para revisão do dono; contagens/statuses não foram promovidos por esta campanha. Somente os três pares selecionados receberam a revisão semântica atual detalhada; os demais mantêm verificação de integridade, sem alegação de nova certificação. Caller1.9.43, planner0.3.6, HelperRetrieval0.1.5 e Maintenance0.1.5 permanecem iguais ao início.

Os305 registros originais permanecem em7 arquivos:293DEV e12TEST_ONLY,42 linhagens,398 referências imutáveis conferidas. Os229 registros não privados de candidatos/referências DEV receberam revisão apropriada ao papel, não aprovação semântica/treinável universal;56 diagnósticos rejeitados permanecem observações,8 privados e12 de avaliação ficam excluídos. Os17 componentes fortes não provam independência semântica completa; FastAPI/Starlette têm relação de dependência. Derivações EN/PT/FAQ/capítulo/revisão não viram holdout por mudar de nome. Direitos e aprovação para treino permanecem pendentes.

| Verificação já autorizada, executada uma vez | Resultado observado |
|---|---|
| Python, unittest discover existente | 312 passaram |
| Ruby, subconjunto documentation offline existente | 242 execuções;1.699 asserções;0 falhas/erros/skips |
| Frontend, npm test existente | 100/102 passaram;2 falhas preservadas |

As duas falhas de frontend são os casos de coleções bilíngues legíveis/imagens e de referências aprovadas dos projetos em ambos os idiomas. Nenhum teste foi reescrito para passar. Os comandos e logs reais estão nos recibos de teste, sem nova execução de suítes externas.

As lacunas de produção continuam: admissão estrutural não é aprovação semântica; exceções de revalidação Go em cache escapam para UNKNOWN; declaração de completude não prova REMOVE; publicação de arquivo único não resolve transações de jobs. Há20 observações da costura de helper/job,8 interrupções e2 bifurcações de journal, além dos17 processos de publicação. Propostas exatas, arquivos, riscos e resultados de regressão esperados estão em {link('proposed-fixes-for-owner-review-v6.json','propostas não aplicadas')}. O livro de defeitos é {link('remaining-defects-and-boundaries-v3.json')}; o recibo final encerra apenas o item de tempo, não estas lacunas técnicas.

Todos os9 gates de fine-tuning continuam NO-GO. Os limites16 atualizações/batch1/acumulação1/512/rank4/QV/600s/1.800s são tetos propostos, não configurações validadas. A proposta de primeira pergunta de aprendizagem é suporte de uma afirmação com escopo qualificado, com positivos/contradições/insuficiência e custo de abstenção, antes de capítulos. Ainda não foi escolhida/aprovada: {link('future-first-learning-task-proposal-v1.json')}. Próximo passo recomendado: revisão semântica independente e aprovação de direitos/alvos, congelamento da avaliação por famílias relacionadas e decisão separada sobre as correções de produção. Só depois cabem preflight nativo e eventual autorização de lançamento.

O último corte já restaurado antes deste apêndice é015:2.792 arquivos regulares comuns,3 symlinks sem seguir e23 membros restritos de apoio; arquivos e modos conferem, os dois parsers próprios restaurados reproduzem suas saídas. A cápsula de420 entradas fundamentais foi restaurada e verificada no corte013. Um suplemento restrito de13 arquivos próprios de código/testes também foi restaurado, e seis módulos próprios foram importados sem helpers ou suítes; ele acrescenta11 entradas distintas. A verificação colocada de431 entradas no corte016 é registrada no recibo final, sem alegação de fechamento transitivo completo. O corte final016 inclui este apêndice; sua confirmação está no recibo final, fora do próprio arquivo, com cópia redundante. Isto não é prova de clone limpo, restauração remota, queda de energia, Windows ou estado neural completo. Os arquivos de publicação têm observações de hardlinks preservadas, mas o tar customizado não reconstrói suas relações de inode.

A conferência final dos42 repositórios confirma HEADs/estados externos, índice Git e versões; os7 datasets,398 referências,2.341 arquivos anteriores e22 documentos manuais mantêm os hashes. HEAD próprio164ae1f679300c2aaaaabb433643699f65e23a6a; índice d9d755da4e9445f1f9911e218b3ae34f2de6cba3a48e4d18a95e949ff1f1fbca. Os41 externos: **sem alterações**. Apenas os quatro relatórios restaurados e a pesquisa/preservação isolada deste projeto foram criados/estendidos. Código rastreado, testes permanentes, UI, schema, documentação interna adicional e Git não foram modificados. O {link('requirement-coverage-audit-v2.json','fechamento por requisito')} e o recibo final registram as verificações finais e seus limites.
'''

repositories=json.loads((P/'repository-inspected-files-v2.json').read_text())['repositories']
repo_table='| Repositório | Coleção | Arquivos públicos selecionados | Criados / modificados rastreados / excluídos pela campanha | Estado |\n|---|---|---:|---|---|\n'
for repo in repositories:
 own=repo['repository']=='engineering-library'
 repo_table+=f"| {repo['repository']} | {repo['collection']} | {len(repo['inspected_only_public_pinned_files'])} | {'4relatórios + pesquisa técnica / 0 / 0'if own else'0 / 0 / 0'} | {'Somente escopo autorizado'if own else'sem alterações'} |\n"
inventory=f'''Corte final dos quatro relatórios: **{at.isoformat()}**. As versões anteriores são preimagens preservadas, não arquivos removidos. O inventário final por arquivo é {link('file-inventory-v15.json')}, com finalidade, tamanho, SHA256 e comando efetivo de verificação. Ele exclui a si mesmo e gravações posteriores; o {link('campaign-completion-receipt-v1.json','recibo final')} relaciona os arquivos tardios de fechamento, hashes dos relatórios e da recuperação. Não há promessa de hash autorreferente.

{repo_table}
Os42 incluem32Portfolio e10VivaBem. Há69 identidades públicas de arquivos selecionados em14clones Portfolio, todas conferidas contra blobs da revisão Git exata, mais uma fonte Rails já instalada fora dos42 clones. Isto não é contagem de todos os arquivos lidos ou revisados semanticamente. Os demais9VivaBem receberam somente HEAD/status; não houve leitura semântica de código privado. Cocos2d-x já tinha duas modificações .project no início e continua com esse mesmo estado, sem atribuição à campanha.

{link('repository-inspected-files-v2.json')} relaciona cada fonte pública, finalidade e comando; {link('selected-source-git-binding-audit-v1.json')} registra as69 comparações reais git show/revisão/caminho/hash. {link('own-selected-inspected-files-v1.json')} discrimina13 caminhos próprios preexistentes de código/testes, todos iguais ao HEAD, com o grau de inspeção indicado. Hash/existência ou seleção por suíte não são apresentados como revisão semântica exaustiva de cada corpo.

| Família de arquivos criados neste projeto | Finalidade e verificação efetiva |
|---|---|
| Quatro AI_*.md na raiz | Restauração byte a byte anterior e apêndices; preimagens/hash antes/depois e cadeia de prefixos |
| request/raw-response/model-content/outcome | Pedidos congelados e saídas originais;98 terminais,95 respostas, sem corrigir texto rejeitado |
| Protocolos/referências/revisões JSON | Critérios, átomos/pares,11dimensões, matrizes e proveniência; fontes/veredictos versionados |
| Snapshots públicos/licenças/metadados | Fonte fixada, hashes/Gitblobs/identidade; sem executar projetos ou aprovar direitos de treino |
| Controles próprios e observadores Python/Go/TS | Experimentos finitos de papel, escopo, identidade, interrupção e publicação; programas-fonte inertes não executados |
| Parsers Go próprios compilados | Parsing AST, não aplicações upstream; bytes/modos e saídas reexecutadas após restauração |
| Inventários/recibos/arquivos de recuperação | Corte de bytes/modos/symlinks e restauração real; sem prova de estado neural/clone limpo |
| Logs e cápsula restrita de420 entradas | Preservação local; privados/avaliação opacos, não enviados a modelos nem promovidos a treino |

As finalidades por arquivo e os comandos/outcomes específicos estão no inventário e nos recibos vinculados; esta tabela é um índice. Os arquivos produzidos/alterados durante a construção de protótipos são pesquisa nova, não alterações em código de produção preexistente. Não foram criados testes permanentes, fixtures, componentes visuais, migrações ou relatórios humanos adicionais. Arquivos históricos excluídos:0; externos criados/modificados/excluídos:0.

Checkpoint015: arquivo comumSHA256 **{checkpoint['archive_sha256']}**, manifestoSHA256 **{checkpoint['manifest_sha256']}**. Foram2.792 regulares comuns+3symlinks+23membros de apoio restaurados, ambos os parsers reproduziram saídas, diretório0700 e archives0600 conferidos. A perda de permissão executável do corte012 permanece registrada; não foi apagada, e produtores novos preservam modos. P/B atuais são0700, e bytes dos archives antigos não mudaram. A cápsula7datasets+398refs+15dependências foi restaurada opacamente no013; não é fechamento transitivo completo. O suplemento own-source-recovery-supplement-v2.json preserva13 fontes/testes próprios inalterados, com restauração/hash/modos e importação de6 módulos; há2 sobreposições, total431 entradas distintas selecionadas. A primeira observação de importação falhou por sintaxe antes de importar módulos; produtor/archive/logs originais foram mantidos, o observador corrigido usou nova raiz de restauração. Hardlinks e ACL/xattrs/metadados de diretório não são reconstruídos pelo contrato de bytes/modos, nem há alegação de restauração nativa neural.

Este apêndice tem preimagensv17 e recibo de corte final com linhas/hashes. O corte016 vem depois; recibos/manifestos ficam fora de seus próprios archives, com cópias redundantes. Consulte o recibo final para resultado, contagens e horário efetivo de preservação. Não houve staging, commit, push ou outra escrita Git.
'''

readiness=f'''**NO-GO nos nove gates**, no corte de pesquisa **{at.isoformat()}**. Esta campanha executou inferência do modelo existente e pesquisa; não fez fine-tuning. Novos frameworks instalados0, pesos baixados0, adaptadores0, atualizações de otimizador0, OWNER_APPROVED0, Gold0. A autorização atual proíbe lançamento.

| Gate | Evidência atual e falta necessária |
|---|---|
|1.Base treinável/tokenizer | GGUF existente não é a base nativa pareada; candidato MLX público somente em metadados, não selecionado/carregado |
|2.Alvos e direitos |305 originais preservados;229 candidatos/referências DEV auditados por papel, não Gold; aprovações de direitos/alvos ausentes |
|3.Avaliação independente | Nenhum conjunto semântico aprovado por famílias relacionadas; DEV/derivados não viram holdout;12cachetools só papel estrutural |
|4.Supervisão | Tarefa aprovada e pares finais ausentes; cópia fornecida e descoberta/suporte de fonte são tarefas diferentes |
|5.Tokenização/máscaras | Prefixo real, template/data/EOS/pad/shift/alvos assistente e512fit não conferidos no tokenizer aprovado; canário mostra padding contado como alvo |
|6.Framework Apple Silicon | Metadados de releases/wheels não validam runtime; mlx/mlx_lm/torch/transformers/peft/tokenizers não descobertos no Python observado |
|7.Hardware/tempo | M1Pro16GiB não demonstra pico/throughput nativos; limite30min não medido; histórico Docker distinto |
|8.Alvos e recuperação | Seletores/chaves/contagens efetivos e restore de adaptador+otimizador+scheduler+step+RNG ausentes; arquivos de pesquisa não substituem isso |
|9.Autorização | Aprovação explícita de lançamento ausente; nenhuma pergunta de autorização durante a campanha |

Modelo de inferência observado: llama3.2:3b, GGUFQ4_K_M, digest a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72. Não mudou nos pedidos congelados/verificação de tags. Isso não é verificação byte a byte de um futuro modelo treinável. O candidato informativo mlx-community/Llama-3.2-3B-Instruct-4bit@7f0dc925e0d0afb0322d96f9255cfddf2ba5636e tem config/índice/template/metadados fixados; nenhum peso/tokenizer efetivo foi validado. Fonte Git MLX-LM e release0.32.2 têm diferenças de loader que não podem ser misturadas.

Os canários são aritmética/metadados, sem tensores/adaptadores: máscara com ntoks positivo pode conter apenas padding; num_layers0/-1 pode selecionar todas as camadas no helper estudado; nomes completos podem escapar da seleção relativa, chaves não casadas podem selecionar nada; a colisão do novo remapeamento Git não foi atribuída ao release que não o possui. Defaults e metadados não substituem inventário real de parâmetros. O loop de validação antes da última atualização não substitui avaliação após ela.

Tetos preservados: **16 updates; batch1; acumulação1; sequência512; LoRA rank4; Q/V explícitos;600s de otimizador;1.800s de piloto inteiro, incluindo baseline, avaliação, pontuação e preservação**. Nenhum destes valores é configuração nativa validada. Os prompts de K tiveram2.094–2.653 tokens no runtime Ollama observado, acima de512; isso não mede o tokenizer nativo, mas impede tratar a cópia completa atual como exemplo já validado para esse teto. Nomes/camadas/base/tokenizer/lock/targets/aprovações continuam não escolhidos. Não se deve truncar contexto crítico para alegar512fit, ocultar baseline fora do relógio ou reiniciar orçamento após falha.

A proposta de primeira aprendizagem é julgar suporte de uma única afirmação com escopo definido e evidência, antes de capítulos. Deve medir falso suporte em C/I, falsa rejeição e abstenção indevida sobre positivos, cobertura e equivalência linguística quando exigida. Continua uma recomendação não selecionada: {link('future-first-learning-task-proposal-v1.json')}. Comparar sempre com a mesma base nativa não adaptada, tarefas/configuração congeladas, e avaliar depois da última atualização. Loss menor, JSON/citações válidos ou reprodução de respostas fornecidas não demonstram ganho semântico.

Antes de qualquer lançamento futuro, o {link('pilot-supervision-approval-contract-v2.json','contrato de aprovação')} exige identidades imutáveis, direitos e revisão semântica independente, avaliação segregada, prefixo/máscara/tokenização reais, inventário Q/V, pico/tempo, recuperação de estado completo e autorização explícita. Falha, OOM ou ambiguidade: STOP_PRESERVE_NO_AUTORETRY_OR_BUDGET_RESET, sem destruir evidência. Propostas de produção e texto continuam não aplicadas. A decisão atual é NO-GO, não uma solicitação de permissão.
'''

resume=f'''O trabalho de pesquisa deste corte foi encerrado em **{at.isoformat()}**, após início em **2026-11-21T13:27:15.678298Z**; decorrido **{duration}**. Dois eventos de pausa/retomada foram respeitados; duração produtiva exata não foi instrumentada. A conclusão verificada da preservação e seu horário posterior estão em {link('campaign-completion-receipt-v1.json')}. Os parágrafos antigos ACTIVE são histórico; não são instrução para reiniciar a campanha após o recibo final COMPLETE_VERIFIED.

Não há worker de inferência ativo. As98 tentativas têm estado terminal;95 respostas,87 normais,8 por limite e3 falhas de transporte. Nunca repetir pedidos iniciados para preencher corpos/contagens faltantes. Os61NOT_STARTED,18superseded e3cópias históricas de pedidos no censo têm papéis explícitos, não são inferências executadas. Não relançar suítes inalteradas, instalar framework, baixar pesos, gerar adaptadores, fazer updates ou publicar catálogo.

Leitura atual: {link('acceptance-metric-catalog-v5.json')}; {link('lifecycle-matrix-and-rate-audit-v8.json')}; {link('fine-tuning-nine-gate-review-v7.json')}; {link('remaining-defects-and-boundaries-v3.json')}; {link('proposed-fixes-for-owner-review-v6.json')}; {link('requirement-coverage-audit-v2.json')}. Os relatórios preservam0/9 e0/13 históricos separados. K3/3 é cópia de fatos fornecidos; T2/2 é manual; L/M/P/Q não produziram nota integral aceita. Todos os gates nativos NO-GO e Gold/updates0.

Antes do último apêndice, checkpoint015 já está restaurado e os dois parsers reproduziram saídas. A preservação final usa inventáriov15 e checkpoint016/produtorv4, com archives0600, diretório0700, bytes/modos/symlinks e replay dos parsers. O recibo final confirma o que efetivamente ocorreu e declara os arquivos tardios fora do próprio archive. A cápsula420 de entradas foi restaurada no013; não há prova de clone limpo, estado neural completo, Windows ou queda de energia. Não repetir checkpoint016 se seu recibo já existir; observar primeiro qualquer estado interrompido.

Em eventual nova sessão, ler o recibo final e a auditoria por requisito, conferir o estado atual sem escrita Git e só continuar o escopo que o proprietário autorizar. Permanecem decisões separadas sobre semântica/Gold/direitos/avaliação independente, redações propostas, três correções de produção e preflight nativo. A recomendação é revisão independente do pequeno conjunto factual e congelamento da avaliação antes de qualquer piloto; a proposta de tarefa de suporte de afirmação não é autorização. Os41 externos permanecem sem alterações e não devem receber mutações.

Sugestões de commit somente para revisão posterior, não executadas nesta campanha:

Projeto: engineering-library
English: docs(research): record documentation acceptance calibration and recovery evidence

Projeto: engineering-library
Português: docs(research): registrar calibração de aceitação documental e evidências de recuperação
'''

texts=dict(zip(names,[campaign,inventory,readiness,resume]))
if '--validate-only' in sys.argv:
 future={'campaign-completion-receipt-v1.json','requirement-coverage-audit-v2.json','file-inventory-v15.json','remaining-defects-and-boundaries-v3.json'}
 links=[]
 for name,text in texts.items():
  for target in re.findall(r'\]\(([^)]+)\)',text):
   path=ROOT/target
   allowed=path.is_file()or(path.parent==P and path.name in future)
   assert allowed,(name,target)
   links.append({'report':name,'target':target,'exists_now':path.is_file(),'permitted_final_closure_reference':not path.is_file()})
 result={'at':at.isoformat(),'status':'FINAL_WRITER_PLAN_VALIDATED_NOT_EXECUTED','report_names':names,
         'section_utf8_bytes':{name:len(text.encode())for name,text in texts.items()},'links':links,
         'all_link_targets_exist_or_are_declared_final_closure_files':True,'root_reports_written':False,
         'protected_integrity_receipt':'campaign-closing-integrity-v2.json','gold':0,'optimizer_updates':0}
 with(P/'final-canonical-plan-validation-v1.json').open('x')as stream:json.dump(result,stream,indent=2,ensure_ascii=False);stream.write('\n')
 print(json.dumps({k:v for k,v in result.items()if k!='links'},indent=2));raise SystemExit(0)
before={name:(ROOT/name).read_bytes()for name in names}
pre=P/'root-report-preimages-v17';pre.mkdir(exist_ok=False)
for name in names:(pre/name).write_bytes(before[name])
rows=[]
for name in names:
 header=f'\n\n## Fechamento da pesquisa — {at.isoformat()}\n\n'
 addition=(header+texts[name]).encode()
 with(ROOT/name).open('ab')as stream:stream.write(addition)
 after=(ROOT/name).read_bytes();assert after==before[name]+addition
 rows.append({'path':name,'pre_sha256':hashlib.sha256(before[name]).hexdigest(),
              'post_sha256':hashlib.sha256(after).hexdigest(),'final_section_start_line':before[name].count(b'\n')+3,
              'final_section_bytes':len(addition)})
append={'at':at.isoformat(),'append_only':True,'preimages':rows}
with(P/'root-report-append-v17.json').open('x')as stream:json.dump(append,stream,indent=2);stream.write('\n')
cut={'at':at.isoformat(),'research_start_utc':start.isoformat(),'research_end_utc':at.isoformat(),
     'research_elapsed_wall_seconds':elapsed,'research_elapsed_formatted':duration,'owner_pause_resume_events':2,
     'productive_time_limit':'Exactpaused/productiveintervalsnotinstrumented; serversecondsnotwalltime;priorcampaignnotcounted.',
     'reports':rows,'next_preservation_checkpoint':16,'next_inventory_version':15,
     'completion_receipt':'campaign-completion-receipt-v1.json','no_further_canonical_append_planned':True,
     'optimizer_updates':0,'gold':0}
with(P/'root-report-final-cut-v1.json').open('x')as stream:json.dump(cut,stream,indent=2);stream.write('\n')
state={'at':at.isoformat(),'status':'RESEARCH_CLOSED_FINAL_PRESERVATION_PENDING','research_end_utc':at.isoformat(),
       'active_inference_workers':0,'terminal_inference_attempts':98,'metric_catalog':'acceptance-metric-catalog-v5.json',
       'lifecycle_catalog':'lifecycle-matrix-and-rate-audit-v8.json','latest_verified_checkpoint':15,
       'next_checkpoint':16,'checkpoint_producer':4,'gold':0,'optimizer_updates':0}
with(P/'campaign-state-v18.json').open('x')as stream:json.dump(state,stream,indent=2);stream.write('\n')
print(json.dumps(cut,indent=2))
