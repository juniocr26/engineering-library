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
with (P/'file-inventory-cut-003.json').open('x') as stream:
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
 'AI_TRAINING_CAMPAIGN_REPORT.md':f"""
## Progresso intensivo — ACTIVE em {now.isoformat()}

Decorrido instrumentado: {elapsed:.1f}s; aproximadamente12horas ainda NÃO cumpridas. Baseline persistida após descoberta inicial. Inferências novas0, tokens/tempo neural0, updates0, testes de aplicação novos0. Nenhuma melhoria de pesos demonstrada.

A revisão integral dos oito tópicos restantes está em `{prefix}remaining-chapters-complete-recovery-review-v1.json`: FastAPI request, Chi writer, DuckDB C API, Fastify route, OpenCV Algorithm, Ruff fix e Prometheus query receberam aceitação técnica manual no escopo original congelado após leitura EN/PT, aquisição separada de fontes e recuperação. SQLX original continua INCONCLUSIVE por citação de depreciação ausente; a nova versão isolada v3 inclui named.go408–412 em ambos os idiomas e recebeu aceitação técnica. São oito tópicos, nove registros de versão, não nove tarefas independentes nem taxa de sucesso do modelo. A nota manual anterior do helper permanece separada. Aprovação do dono/publicação/Gold:0.

As revisões preservam limites específicos: wrappers Chi não garantem capacidades universais; DuckDB não inicializa universalmente resultado no catch; Fastify diferencia opção pública e sinal interno de HEAD; OpenCV diferencia despacho virtual, overload e execução real da biblioteca; SQLX distingue bind, callbacks/reflection e execução de SQL; Ruff resolve política de fix sem provar segurança semântica; Prometheus diferencia construção, execução, finalização HTTP, devolução de buffers e fechamento do storage. Exemplos não executados e testes apenas escritos estão explicitamente identificados. Recibos históricos de compilação/parser não são execuções novas.

Checkpoint004:415 arquivos restaurados com hash/modo, incluindo capítulos/especificações originais, fontes fixadas e evidência histórica declarada. Replays de consumidores restaurados: envelopes3/3, perfisAST8/8, aquisiçãohelper8/8. Isso não prova backup remoto, clone limpo, Windows ou semântica por hash. A agregação inicialmente falhou por chave version ausente em dois schemas; falha preservada e corrigida sem alterar reviews ou scores anteriores.
""",
 'AI_TRAINING_FILE_INVENTORY.md':f"""
## Inventário intensivo — ACTIVE em {now.isoformat()}

Inventário individual com propósito/bytes/SHA256: `{prefix}file-inventory-cut-003.json`, {len(inventory)} arquivos antes deste corte. Fontes recém-inspecionadas em FastAPI, Chi, DuckDB, Fastify, OpenCV, SQLX, Ruff e Prometheus foram obtidas por git show de revisões fixadas; todos permanecem sem alterações. As afirmações de inspeção apenasHEAD/status dos cortes anteriores valiam para aqueles cortes; este apêndice registra o escopo ampliado. Quatro relatórios somente por apêndice; originais/candidatos anteriores preservados. Nenhum arquivo excluído, stage, commit ou push.
{table}
""",
 'AI_FINE_TUNING_READINESS.md':f"""
## Prontidão intensiva em {now.isoformat()}

Nove gates continuam NO_GO. Oito tópicos manuais revistos, com uma correção de citação isolada, não constituem melhoria neural, holdout independente, Gold ou autorização de publicação. Papel DEV preservado. Os pares traduzidos, versões e cláusulas do mesmo tópico não aumentam o número de tarefas independentes. Nenhum runtime treinável, máscara real, inventário Q/V, recuperação do otimizador ou treinamento foi validado nesta execução. Docker segue sem acesso; artefatos de treino não foram instalados ou modificados.
""",
 'AI_TRAINING_RESUME.md':f"""
## Continuação intensiva — ACTIVE em {now.isoformat()}

Checkpoint004 restaurou415arquivos, com três consumidores; recibo `{prefix}checkpoint-004.json`. Resultado das oito revisões em `remaining-chapters-complete-recovery-review-v1.json`; SQLX original mantém lacuna, somente cópia isolada v3 corrigida. Esse recibo posterior está fora do próprio checkpoint004 e deve entrar no próximo checkpoint. Não reinterpretar G9 como prova de runtime ou durabilidade remota.

Próximas hipóteses independentes: concluir G1–G9 do Zod v3 com fontes/testes/notices; curadoria de lote pequeno para revisão do dono sem Gold automático; verificar identidade estática de manifesto/blobs já existentes do modelo sem instalar/copiar pesos; delimitar avaliação futura por famílias independentes. Continuar até aproximadamente12horas reais com pesquisa útil, sem sleeps artificiais, novas instalações, fontes de produção alteradas ou perguntas intermediárias. Duração ainda insuficiente; não encerrar por término da fila inicial.
"""
}
backup=P/'root-preimages-cut-003'
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
with (P/'root-report-append-cut-003.json').open('x') as stream:
    json.dump({'at':now.isoformat(),'status':'ACTIVE','elapsed_seconds':elapsed,'reports':changes},stream,indent=2)
    stream.write('\n')
print(json.dumps({'status':'ACTIVE','elapsed_seconds':elapsed,'inventoried_files':len(inventory),'reports_appended':4}))
