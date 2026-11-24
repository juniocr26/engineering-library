"""Append evidence-backed progress; preserve report prefixes and inventory cut."""
from pathlib import Path
import datetime
import hashlib
import json
from artifact_purpose_v2 import purpose

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
now = datetime.datetime.now(datetime.timezone.utc)
baseline = json.loads((P/'baseline.json').read_text())
elapsed = (now-datetime.datetime.fromisoformat(baseline['started_at'])).total_seconds()
sha = lambda b: hashlib.sha256(b).hexdigest()
names = ['AI_TRAINING_CAMPAIGN_REPORT.md','AI_TRAINING_FILE_INVENTORY.md',
         'AI_FINE_TUNING_READINESS.md','AI_TRAINING_RESUME.md']
research = [f for f in P.rglob('*') if f.is_file() and not f.is_symlink() and '__pycache__' not in f.parts]
backups = [f for f in (ROOT/'.local-backups/final-intensive-20261121').rglob('*') if f.is_file() and not f.is_symlink()]
inventory = []
for f in sorted([*research, *backups, *(ROOT/n for n in names)]):
    role = purpose(f) if f in research else ('Arquivo/manifesto/recibo de checkpoint local preservado' if f in backups else 'Relatório canônico criado por recuperação e estendido por apêndices')
    inventory.append({'path':str(f.relative_to(ROOT)), 'purpose':role,
                      'bytes':f.stat().st_size, 'sha256':sha(f.read_bytes())})
with (P/'file-inventory-cut-006.json').open('x') as stream:
    json.dump({'at':now.isoformat(),'files':inventory,
               'self_cut':'Includes current research, ignored campaign backup files and root reports before this append. Own inventory, later preimages/receipts/checkpoints and post-append report hashes are outside this cut; append receipt binds final report hashes.',
               'temporary_restores':'Exact paths are checkpoint restored_root plus each input-manifest path; outside repository and not original-source changes.',
               'status':'ACTIVE'},stream,indent=2,ensure_ascii=False)
    stream.write('\n')
table='\n| Arquivo criado nesta campanha | Finalidade |\n|---|---|\n'+''.join('| `'+r['path']+'` | '+r['purpose']+' |\n' for r in inventory)
prefix='agent/research/final-intensive-20261121/'
sections={
names[0]:f"""
## Progresso intensivo — ACTIVE em {now.isoformat()}

Tempo desde a baseline instrumentada: {elapsed:.1f}s. A campanha ainda não completou aproximadamente 12 horas. Novas chamadas, tokens e tempo de inferência do **Ollama local**: 0. Isso não significa ausência de trabalho GPT/Codex: o contador interno do objetivo registrou 740.969 tokens e 6.758 segundos no snapshot `goal-accounting-observation-v1.json`; esse contador não é faturamento nem tokens do Ollama. Custo monetário não medido. Treinamento, updates e Gold: 0.

O estudo C++ fez uma pergunta nova sobre representação, sem repetir a execução histórica dos programas. Seis fontes próprias preservadas foram submetidas ao Clang: cinco traduções válidas e uma recusa esperada por overload oculto. AST parcial dessa tradução recusada não recebeu admissão. Nenhuma aplicação OpenCV ou outro projeto foi executado, e nenhum executável/objeto foi emitido. Um novo controle próprio sem main gerou apenas AST e IR LLVM textual com O0 no alvo registrado pelo compilador.

A hipótese de que os subtrees AST completos seriam iguais após normalização **não se confirmou**: a chamada qualificada tem uma camada de cast diferente. As chamadas selecionam a mesma declaração Base::value e os campos próprios de MemberExpr coincidem, mas o IR textual tem chamada indireta em unqualified e chamada direta a Base::value em qualified. Further::value apresenta OverrideAttr e não apresenta o campo JSON virtual. Ausência de campo não é prova de método não virtual. O resultado está em `cpp-ast-dispatch-review-v2.json` e no consumidor v3; a hipótese inicial e o diff que a refuta permanecem preservados. Isso é evidência estática delimitada, não um verificador C++ geral nem observação de valores em runtime.

A auditoria de exposição verificou tamanho/SHA-256 de 145 snapshots públicos arquivados, 2.350.625 bytes, em 15 famílias. Todos correspondem aos inventários antigos; não são 145 afirmações semânticas novas. A primeira tentativa assumiu incorretamente o prefixo sources/ para todos os caminhos; seis entradas usavam outros dois layouts arquivados conhecidos. A falha e a correção foram preservadas, mantendo contenção do arquivo, caminhos relativos e hashes congelados. Nenhum original foi corrigido ou apagado.

A matriz atual de 42 repositórios registra 19 públicos com exposição anterior confirmada de fonte/modelo, nove públicos ainda não certificados, três projetos com catálogo e exposição não resolvida, Raylib apenas prospectivo, nove VivaBem externos com metadados somente e a Engineering Library como desenvolvimento interno. Isso não é taxa de desempenho ou prova de que 19 famílias foram fornecidas ao modelo. Seis requests históricos selecionados tiveram resposta bruta, recibo, conteúdo e tokens conferidos: todos correspondem; continuam históricos. Request preparado sozinho não prova execução, e nome de modelo não fornece digest criptográfico. Url-shortener foi corrigido no pré-check: seus metadados são Python/FastAPI, não Go; nenhuma tarefa Go foi executada com esse rótulo errado.

`current-metric-population-audit-results-v1.json` reconcilia contadores com os registros brutos. Há 12 pares de versões de capítulos revistos: 11 tecnicamente aceitos e o SQLX original inconclusivo por citação, com versão corrigida separada. A nota de manutenção do helper fica em população separada. Esses números descrevem versões manuais/determinísticas relacionadas, não ensaios neurais independentes. Transições de gate e traduções não multiplicam amostras. Taxa de aceite neural atual é nula por denominador zero; precisão atômica global, acordo bilíngue independente e preservação de identificadores em população independente continuam sem denominador válido.

A clarificação `typed-evidence-interpretation-supplement-v1.json` preserva observação bruta, relação de fonte e proposição documental como camadas distintas. Não altera o DoD v3, escopos ou scores anteriores. O pedido original do usuário também foi preservado byte a byte para recuperação. Os nove gates de fine-tuning continuam NO_GO; novas tentativas de sysctl foram negadas, sem escalada. Espaço livre observado: 372.326.400.000 bytes; pesquisa cerca de 26,23 MB e backups cerca de 44,88 MB naquele corte, sem copiar pesos.
""",
names[1]:f"""
## Inventário intensivo — ACTIVE em {now.isoformat()}

`{prefix}file-inventory-cut-006.json` registra {len(inventory)} arquivos presentes antes deste apêndice, incluindo pesquisa, checkpoints ignorados pelo Git e quatro relatórios. Scripts, AST/IR, protocolos, falhas, manifests e diffs têm finalidade individual no inventário. O classificador v2 identifica corretamente AST/diagnósticos, IR textual, controle C++ próprio e o diff de análise; esse diff não é proposta de alteração de aplicação.

`repository-action-ledger-v4.json` acrescenta os 145 caminhos arquivados apenas verificados por hash aos respectivos projetos. Isso não é nova revisão semântica integral ou alteração dos checkouts externos. Os arquivos de source-code originais dos controles C++ continuam inalterados. Novos controles/consumidores foram criados apenas na pesquisa autorizada. O pedido colado e suas restrições foram copiados como entrada técnica, sem criar um quinto relatório humano.

Os recibos de aquisição C++ preservam comandos completos, versões, stdout AST/IR e stderr. A recusa de overload oculto e as falhas de hipótese/caminho/identidade nullable não foram apagadas. Consultas de capacidade sysctl e ps permanecem negadas; nenhum contorno de sandbox foi tentado. Nenhum teste permanente, catálogo, fonte de aplicação, peso, stage, commit, push ou histórico Git foi modificado.
{table}
""",
names[2]:f"""
## Prontidão intensiva — {now.isoformat()}

NO_GO nos nove gates; MODEL_READY_FOR_ASSISTED_DOCUMENTATION continua INSUFFICIENT_EVIDENCE. A matriz conservadora impede chamar Core, Godot, Axum ou Click de famílias novas apenas porque não constam das 305 linhas originais. Raylib continua prospectivo e excluído de treino. Não há amostra suficientemente diversa de tarefas independentes Python/Go/TypeScript/JavaScript, nem nova inferência local pareada. O pré-check corrigiu o rótulo Go incorreto de url-shortener antes de gerar/executar uma tarefa.

A identidade estática do GGUF não comprova base treinável ou servidor em execução; ausência do campo virtual no AST também não comprova propriedade semântica negativa. Essas são limitações de inferência de evidência, não justificativas automáticas para alterar pesos. Não houve instalação de framework, aquisição de pesos, adapter ou optimizer update. Nenhuma revisão técnica virou publicação ou Gold.

O contador interno GPT/Codex é separado dos tokens locais Ollama e de cobrança financeira. Capacidade RAM/CPU e pico de uso desta campanha não foram medidos; sysctl e ps negados não foram contornados. O cenário de armazenamento em `resource-observation-v3.json` usa o tamanho real do último arquivo para estimar crescimento, sem prometer custo ou durabilidade futura e sem apagar material.
""",
names[3]:f"""
## Continuação intensiva — ACTIVE em {now.isoformat()}

O último checkpoint completo no início deste corte é 008. O corte atual deve ser arquivado pelo produtor v9 em checkpoint009, com consumo adicional dos AST/IR C++ e das 145 fontes arquivadas/seis witnesses históricos. O recibo de checkpoint e a nota posterior de recuperação, quando presentes, são a autoridade de conclusão; não assumir que um plano já foi executado.

A fonte atual de contagens é `current-metric-population-audit-results-v1.json`; os papéis de corpus estão em `repository-exposure-matrix-v3.json`. O lote principal para revisão permanece `owner-review-batch-v3.json`. A hipótese C++ refutada e suas limitações estão em `cpp-ast-dispatch-review-v2.json`; use o consumidor v3 para distinguir campo ausente de null. Request Raylib preparado continua sem execução. Nunca usar ausência de campo ou request existente como prova semântica/de execução.

Próximos trabalhos substantivos: investigar revisões locais disponíveis além do pai imediato, sem fetch, para avaliar consequências documentais por escopo/callers; resolver a seleção real de famílias e linguagens do benchmark sem reaproveitar casos expostos como independentes. Se fontes novas forem necessárias, manter leitura pública limitada, identidade/linhagem e critérios congelados antes de qualquer modelo; não adquirir pesos/frameworks. Continuar trabalho útil até aproximadamente 12 horas reais, sem sleeps artificiais, repetição de inferências antigas ou perguntas intermediárias.

O script `append_checkpoint_report_note_v1.py` foi preparado para reconstruir os quatro relatórios finais do corte a partir dos prefixos arquivados, do próprio script arquivado e do receipt lateral. A demonstração deve ocorrer após a restauração; não confundir esse mecanismo com clone limpo, recuperação de modelo ou durabilidade remota.
"""}
preimages=P/'root-preimages-cut-006'
preimages.mkdir()
changes=[]
for name,section in sections.items():
    target=ROOT/name
    before=target.read_bytes()
    with (preimages/(name+'.bin')).open('xb') as stream:stream.write(before)
    with target.open('ab') as stream:stream.write(section.encode())
    after=target.read_bytes()
    assert after.startswith(before)
    changes.append({'path':name,'before_sha256':sha(before),'after_sha256':sha(after),
                    'append_start_line':len(before.splitlines())+1})
with (P/'root-report-append-cut-006.json').open('x') as stream:
    json.dump({'at':now.isoformat(),'status':'ACTIVE','elapsed_seconds':elapsed,'reports':changes},stream,indent=2)
    stream.write('\n')
print(json.dumps({'status':'ACTIVE','elapsed_seconds':elapsed,'inventoried_files':len(inventory),'reports_appended':4}))
