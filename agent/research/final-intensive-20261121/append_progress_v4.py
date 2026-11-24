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
with (P/'file-inventory-cut-004.json').open('x') as stream:
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

Tempo instrumentado: {elapsed:.1f}s. Aproximadamente12horas NÃO concluídas. Inferências/tokens/tempo neural novos:0; updates0; Gold0. Campanha anterior e seus98attempts não são execuções atuais.

O Zod v3 corrigido recebeu TECHNICALLY_ACCEPTED em `zod-complete-review-v3.json`, após preservar estados intermediários inconclusivos. Tentativa inicial com Node falhou porque o executável não existe no host; o parser TypeScript5.9.3 já instalado foi então executado pelo JavaScriptCore existente do macOS, sem instalar nada. Os dois exemplos exatos EN/PT produziram zero diagnostics; controle malformado produziu1109. Isso é sintaxe apenas, sem resolução/tipos/runtime Zod. Checkpoint006 incluiu parser/licença, restaurou478arquivos e reexecutou esse consumidor a partir do parser restaurado. Também repetiu envelopes3/3, perfisAST8/8, helper8/8 e três fragmentos próprios C contra header fixado: válido aceita, callback incompatível e API inventada recusam. Os fragmentos C não ligam/executam Raylib. Framework/compilador nativos são dependências do host, não uma imagem portátil arquivada.

Lote `owner-review-batch-v2.json`:3pares públicos manuais EN/PT (FastAPI request, SQLX v3 e Zod v3), com hashes exatos, fontes, notices e exclusão por família; mais1par do helper para revisão exclusivamente interna. LICENSE local é aviso proprietário em rascunho, não autorização para inferência externa/publicação/treino. Todos permanecem training_eligible=false, aprovação do dono/publicação/Gold=false. Esse lote não contém amostras novas de avaliação independente.

A auditoria de exposição leu8.298artefatos textuais históricos,217.363.693bytes;386arquivos tiveram matches candidatos. Click e Axum têm requests antigos efetivos e não são famílias novas, apesar da ausência nas305linhas. Raylib teve apenas metadados na auditoria delimitada, sem certificação de pretraining/fora do corpus. Foi preparado1caso prospectivo C/Raylib, com requisitos, fontes,15unidades referenciais e8desafios negativos antes de qualquer chamada. Quinze unidades compostas NÃO são15afirmações atômicas independentes. O caso e request estão NOT_EXECUTED: acesso ao servidor, identidade em execução e fit token/template continuam sem prova. Um caso C não cobre diversidade Python/Go/TS nem sustenta MODEL_READY. A observação de que SaveFileText marca true por fclose==0 sem condicionar esse ramo ao fprintf>=0 é estática, não um teste de I/O executado ou correção de produção.

Identidade estática local do modelo: manifesto a52a4a87… e sete blobs declarados conferem tamanho/SHA256; GGUF2.019.377.376bytes com header versão3/255tensores/30metadados. Config declara Q4_K_M/3.2B. Isso não prova identidade do servidor, tokenizer/máscara, base treinável ou treinamento pronto. Pesos somente lidos para hash/header, sem copiar/alterar ou carregar modelo.
""",
 'AI_TRAINING_FILE_INVENTORY.md':f"""
## Inventário intensivo — ACTIVE em {now.isoformat()}

Inventário `{prefix}file-inventory-cut-004.json`: {len(inventory)} arquivos técnicos antes deste corte, com finalidade/hash/bytes; próprio inventário/preimagens/apêndices posteriores fora do corte. Atribuição por42repositórios em `repository-action-ledger-v2.json`, com comandos reais de baseline/aquisição e paths; v2 expande explicitamente os arquivos criados em engineering-library, em vez de deixar a lista genérica vazia como v1. Repositórios externos:sem alterações. Raylib agora teve leitura de src/rcore.c,src/raylib.h,src/config.h,LICENSE e examples/core/core_text_file_loading.c; src/utils.c faltante foi registrado e não tratado como remoção. Click/Axum tiveram leitura de evidência histórica, não nova execução de seus projetos. TypeScript e framework JSC existentes foram tooling; código Zod/Raylib continua dado não executado.

`resource-observation-v2.json` registra espaço/bytes reais; CPU/RSS continuam não medidos. Nenhuma instalação, alteração de peso, stage, commit ou push. Os pesos não foram copiados para checkpoints; identidade estática preservada por manifesto/receipts, recuperação de inferência/otimizador não demonstrada.
{table}
""",
 'AI_FINE_TUNING_READINESS.md':f"""
## Prontidão intensiva — {now.isoformat()}

Nove gates continuam NO_GO; MODEL_READY_FOR_ASSISTED_DOCUMENTATION permanece INSUFFICIENT_EVIDENCE. Hash consistente de GGUF Q4_K_M não é checkpoint treinável nem tokenizer/chat-template/loss-mask verificados. O template Go local foi lido e sua identidade preservada; não equivale a comprovar igualdade do chat template de uma futura base MLX. Nenhum download/framework/optimizer/adapter foi autorizado ou executado.

O lote3pares públicos manuais permanece default-deny para treinamento. Nota interna tem aviso proprietário e está excluída de inferência externa/treino. Click/Axum usados historicamente não podem ser rebatizados como fresh holdout; o primeiro caso Raylib não executado ainda deixa Python/Go/TS independentes e revisão humana sem prova. Todo artefato de avaliação Raylib deve permanecer excluído de treino, incluindo traduções/revisões/FAQs/derivados. Contrato do piloto anterior permanece não executável e requer aprovação separada.
""",
 'AI_TRAINING_RESUME.md':f"""
## Continuação intensiva — ACTIVE em {now.isoformat()}

Checkpoint006:478arquivos/restauração de cinco consumidores (envelopes,escopoAST,helper,parserJSC,fragmentosC). `zod-complete-review-v3.json` registra aceitação exata posterior; `owner-review-batch-v2.json` contém3pares públicos mais1interno. Artefatos criados após checkpoint006 devem entrar no próximo checkpoint; não alegar auto-hash infinito. Host sem Node foi superado apenas para parsing por JSC existente, sem mudar ambiente. Docker segue inacessível para inferência.

Próximo trabalho útil: auditar requisitos da campanha contra evidência atual; aprofundar preservados fracassos de associação FAQ e negação com hipóteses novas; completar casos prospectivos independentes somente após auditoria de exposição/dependências, nunca chamar Raylib1caso de benchmark suficiente. Preservar `raylib-evaluation-request-NOT-EXECUTED-v1.json` sem chamar modelo antes de preflight/identidade/fit. Não inserir respostas do ledger no prompt. Continuar pesquisa útil até aproximadamente12horas reais, sem sleeps artificiais ou repetições sem hipótese. Não concluir a meta por terminar este corte.
"""
}
backup=P/'root-preimages-cut-004'
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
with (P/'root-report-append-cut-004.json').open('x') as stream:
    json.dump({'at':now.isoformat(),'status':'ACTIVE','elapsed_seconds':elapsed,'reports':changes},stream,indent=2)
    stream.write('\n')
print(json.dumps({'status':'ACTIVE','elapsed_seconds':elapsed,'inventoried_files':len(inventory),'reports_appended':4}))
