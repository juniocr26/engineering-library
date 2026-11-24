"""Append current results, exact technical inventory and next independent queue."""
from pathlib import Path
import datetime
import hashlib
import json

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
now=datetime.datetime.now(datetime.timezone.utc)
prefix='agent/research/final-intensive-20261121/'
elapsed=(now-datetime.datetime.fromisoformat(json.loads((P/'baseline.json').read_text())['started_at'])).total_seconds()


def purpose(path):
    name=str(path.relative_to(P))
    if 'root-preimages' in name or name.endswith('.recovered.bin'):
        return 'Preimagem imutável de relatório; recuperação e preservação histórica'
    if 'exception-scope-controls' in name:
        return 'Fonte de controle sintético para escopo de exceções; não é código de produção'
    if name.startswith('real-revision-evidence'):
        return 'Objeto Git ou diff real antes/depois, somente leitura'
    if name.startswith('reacquired-public-sources'):
        return 'Fonte pública reobtida de revisão Git fixa; nunca executada'
    if name.startswith('helper-admission-observations'):
        return 'Resultado bruto de extração/validação e cobertura de citação da tarefa'
    if name.startswith('renderer-recovery-v1/'):
        return 'Entrada original, mutação ou saída preservada do consumidor de pesquisa restaurado'
    if path.suffix=='.py':
        return 'Produtor/verificador isolado de pesquisa; sem integração em produção'
    if path.suffix=='.diff':
        return 'Diff de candidato isolado para revisão humana; não aplicado'
    if path.suffix=='.md':
        return 'Candidato documental isolado EN/PT; não é catálogo publicado ou Gold'
    return 'Contrato, resultado, revisão, estado ou vínculo técnico com proveniência explícita'


files=[x for x in P.rglob('*') if x.is_file() and not x.is_symlink() and '__pycache__' not in x.parts]
inventory=[{'path':str(x.relative_to(ROOT)),'purpose':purpose(x),'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in sorted(files)]
with (P/'file-inventory-cut-002.json').open('x') as stream:
    json.dump({'at':now.isoformat(),'files':inventory,'self_cut':'This inventory and later report/preimage/checkpoint writes excluded; next inventory includes previous cut.','status':'ACTIVE'},stream,indent=2,ensure_ascii=False)
    stream.write('\n')
table='\n| Arquivo criado | Finalidade |\n|---|---|\n'+''.join('| `'+x['path']+'` | '+x['purpose']+' |\n' for x in inventory)
baseline=json.loads((P/'baseline-verification-v1.json').read_text())
repo_table='\n| Projeto exato | Trabalho deste corte | Alterações |\n|---|---|---|\n'
for repo in baseline['repositories']:
    name=repo['repository']
    if name=='engineering-library':
        work='Pesquisa isolada, revisão de fonte antes/depois, recuperação e quatro relatórios'
        changed='Somente pesquisa e relatórios autorizados'
    elif name in ['fastapi','cobra','zod']:
        work='HEAD/status, objetos Git fixados e disponibilidade de ancestral'
        changed='sem alterações'
    else:
        work='Somente HEAD/status; sem nova revisão do corpo da fonte neste corte'
        changed='sem alterações'
    repo_table+='| '+name+' | '+work+' | '+changed+' |\n'
sections={
    'AI_TRAINING_CAMPAIGN_REPORT.md':f'''
## Progresso intensivo — ACTIVE em {now.isoformat()}

Decorrido desde a primeira baseline instrumentada: {elapsed:.1f}s. Essa baseline foi persistida após a leitura inicial do pedido/instruções; não representa instrumentação exata dos primeiros minutos de descoberta. A meta de aproximadamente12horas continua em andamento. Nenhuma inferência nova foi executada; tempo/tokens de inferência desta execução:0. Testes de aplicação desta execução:nenhum. Os resultados de suítes nas seções anteriores são históricos.

A [nota manual de manutenção do helper]({prefix}helper-candidate-complete-review-v2.json) passou em G1–G9 dentro do escopo congelado de fluxo estático de cache, revisão real b586e484→7dbc3b69. Foram17 proposições de fonte revisadas, sem erro crítico observado, com os dois textos EN/PT lidos; oito grupos iniciais não foram indevidamente contados como oito afirmações atômicas. A evidência adicional de escopo léxico distinguiu8/8 perfis congelados. Este é **um par manual TECHNICALLY_ACCEPTED**, sem contribuição neural, aprovação do dono, publicação ou Gold. Não altera o histórico K nem as taxas0/9 e0/13.

Na [restauração do renderer original]({prefix}renderer-recovery-results-v1.json),30 dependências foram restauradas. Os3 replays intactos reproduziram o payload exato exceto timestamp;12 controles com ausência/obsolescência impediram montagem. Seis alterações de dependências confiadas produziram candidatos com revisão falsa ou afirmação inventada de testes:6/6 montagens inseguras sob corrupção de metadados/referências. O envelope congelado recusou6/6 alterações. Montagem não é aceitação técnica; nenhum negativo foi aprovado. O estudo delimita a confiança do renderer de pesquisa, não demonstra comprometimento dos originais ou uma nova correção aplicada em produção.

O [teste da fase de aquisição existente]({prefix}helper-admission-results-v1.json) executou `extract` e `validate_unit`, sem journal/job e sem executar fontes inspecionadas. Admitiu4/8 requisições e cobriu7/28 spans de fatos K. Dois fatos são campos de classe Python; sete dependem de `solve_dependencies`, cuja declaração completa tem6.707bytes contra limite6.144, embora o arquivo de57.721bytes caiba em65.536. Um tipo Go foi reconhecido pelo parser subjacente, mas recusado pelo helper de callables. O comentário de depreciação C09 fica antes da função, fora da citação admitida. Dez fatos TypeScript estão fora das linguagens do helper. Todos os oito statuses corresponderam ao congelado; o motivo específico de recusa da classe foi mais preciso que a string prevista, discrepância preservada. **Estas limitações não são causas demonstradas dos fracassos neurais anteriores**, que receberam cartões de fonte/bancos de fatos por outro caminho.

Checkpoint003 restaurou228 arquivos, verificou hashes/modos e reexecutou três consumidores restaurados: envelopes3/3, perfis de exceção8/8 e statuses da aquisição8/8. O parser Go próprio previamente instalado foi usado no host; nenhuma instalação, compilação ou fonte de terceiro foi executada. A [evidência]({prefix}checkpoint-003.json) não prova clone limpo, Windows, backup remoto ou estado neural. Espaço livre observado:346,76GiB; pesquisa local cerca de4,80MB e backups desta execução cerca de6,96MB no corte de medição. CPU/pico de memória não medidos; `ps` é negado pelo sandbox.

Foi congelada uma [nova revisão dos oito pares manuais restantes]({prefix}remaining-chapters-v3-review-protocol-v1.json), antes de nova leitura integral. A hipótese é sua aceitação sob G1–G9 mais explícitos, mantendo os requisitos originais pré-geração e seus antigos resultados. Não se herda PASS por hash ou pelo relatório anterior; faltas recebem INCONCLUSIVE. Essa é a próxima fila substantiva, não uma reexecução de inferências antigas.
''',
    'AI_TRAINING_FILE_INVENTORY.md':f'''
## Inventário intensivo — ACTIVE em {now.isoformat()}

`file-inventory-cut-002.json` registra{len(inventory)} arquivos técnicos presentes antes deste corte, cada um com finalidade, bytes e SHA-256. O próprio inventário e gravações posteriores são explicitamente fora do seu corte. Nenhum arquivo foi excluído ou modificado em repositório externo; os quatro relatórios foram criados por recuperação e estendidos por apêndices. Os scripts/protocolos/controles v1 que falharam foram mantidos junto das correções v2, sem redefinir expectativas antigas.

Os arquivos de aplicação apenas inspecionados incluem `agent/tools/documentation_retrieval.py`, `documentation_workspace.py`, `go_source_ast.py`, `go-source-ast/main.go`, manifesto/licença/binário Darwin do parser, `documentation_job_budget.py`, `documentation_faq.py`, `documentation_closed_faq.py`, `backend/lib/documentation/command.rb` e o guia existente `agent/tools/documentation_retrieval.md`. Permanecem inalterados. O único binário executado foi o parser próprio de sintaxe; as fontes selecionadas são dados.

Validações: scripts técnicos desta pesquisa, reaquisição Git, controles congelados, restauração e replay. `git diff` e `git diff --cached` continuaram vazios; `git status` mostra somente os quatro relatórios e o diretório novo da pesquisa. Nenhum stage/commit/push foi executado. Docker e `ps`: acesso negado, sem escalada. As validações não equivalem a testes completos de aplicação.
{repo_table}
{table}
''',
    'AI_FINE_TUNING_READINESS.md':f'''
## Prontidão no progresso intensivo {now.isoformat()}

Os nove gates continuam **NO_GO**; Gold/updates/adapters/downloads/instalações continuam0. A aceitação da nota manual não demonstra melhoria neural. Cobertura de aquisição7/28 e proteção de dependências não são critérios satisfeitos de tokenizer, máscara, base treinável, runtime Metal ou recuperação do otimizador. Os statuses existentes são limites de interface/orçamento, não uma justificativa automática para fine-tuning ou aumento de contexto.

Continua válido o pacote não executável anterior `agent/research/acceptance-calibration-20261121/pilot-supervision-approval-contract-v2.json`: identidades, direitos/alvos, avaliação por famílias, template/máscara/512fit reais, seleção Q/V/inventário, memória/tempo, estado completo e autorização separados. Seus tetos não foram alterados. Nenhum comparador base nativa versus adapter existe nesta execução; prontidão do modelo permanece INSUFFICIENT_EVIDENCE. As amostras DEV atuais não se tornam holdout ou Gold ao receber revisão adicional.
''',
    'AI_TRAINING_RESUME.md':f'''
## Próxima continuação intensiva — ACTIVE em {now.isoformat()}

Último checkpoint: `{prefix}checkpoint-003.json`,228 arquivos restaurados com três consumidores. A aceitação exata do par manual está em `helper-candidate-complete-review-v2.json`; os limites da aquisição estão em `helper-admission-results-v1.json` e `helper-admission-interpretation-v1.json`. Não somar taxas heterogêneas, não tratar montagem do renderer como aceitação e não atribuir os limites atuais do helper aos prompts históricos que receberam outra evidência.

Próximo trabalho: `remaining-chapters-v3-review-protocol-v1.json`,8pares/16textos congelados. Ler seus requisitos originais pré-geração, corpos completos EN/PT, fontes e receipts existentes; reobter objetos Git públicos separadamente quando disponíveis. Julgar cada G1–G9 com evidência e negativas; não reduzir escopo ou herdar PASS. Usar resultados para curadoria de revisão do dono e decisão defensável de avaliação independente. Docker permanece indisponível; continuar pesquisa estática/consumidores próprios sem novas instalações.

Preservar os originais e emitir novos artefatos/versões. A campanha ainda não completou12horas nem deve encerrar porque a fila inicial terminou. Não repetir inferências/suítes inalteradas, não dormir para preencher tempo, não solicitar decisões intermediárias. Os gates nativos e autorizações permanecem pendentes. Atualizar relatórios e checkpoint após avanço substantivo ou em cerca de30min.
'''
}
backup=P/'root-preimages-cut-002'
backup.mkdir()
changes=[]
for name,text in sections.items():
    path=ROOT/name
    before=path.read_bytes()
    with (backup/(name+'.bin')).open('xb') as stream:stream.write(before)
    with path.open('ab') as stream:stream.write(text.encode())
    after=path.read_bytes()
    assert after.startswith(before)
    changes.append({'path':name,'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(after).hexdigest(),'append_start_line':len(before.splitlines())+1})
with (P/'root-report-append-cut-002.json').open('x') as stream:
    json.dump({'at':now.isoformat(),'status':'ACTIVE','elapsed_seconds':elapsed,'reports':changes},stream,indent=2)
    stream.write('\n')
print(json.dumps({'status':'ACTIVE','elapsed_seconds':elapsed,'inventoried_files':len(inventory),'reports_appended':4}))
