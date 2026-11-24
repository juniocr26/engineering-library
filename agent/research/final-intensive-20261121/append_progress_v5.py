"""Append evidence-backed progress; preserve report prefixes and inventory cut."""
from pathlib import Path
import datetime
import hashlib
import json
from artifact_purpose_v1 import purpose

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
with (P/'file-inventory-cut-005.json').open('x') as stream:
    json.dump({'at':now.isoformat(),'files':inventory,
               'self_cut':'Includes current research, ignored campaign backup files and root reports before this append. Own inventory, later preimages/receipts/checkpoints and post-append report hashes are outside this cut; append receipt binds final report hashes.',
               'temporary_restores':'Exact paths are checkpoint restored_root plus each input-manifest path; outside repository and not original-source changes.',
               'status':'ACTIVE'},stream,indent=2,ensure_ascii=False)
    stream.write('\n')
table='\n| Arquivo criado nesta campanha | Finalidade |\n|---|---|\n'+''.join('| `'+r['path']+'` | '+r['purpose']+' |\n' for r in inventory)
prefix='agent/research/final-intensive-20261121/'
sections={
names[0]:f'''
## Progresso intensivo — ACTIVE em {now.isoformat()}

Tempo desde a baseline instrumentada: {elapsed:.1f}s. A meta de aproximadamente 12 horas permanece incompleta. Novas inferências, tokens e tempo neural: 0; updates e Gold: 0. Os resultados históricos não foram recontados como novas execuções.

A leitura integral e revisão G1–G9 dos pares prioritários de cache do FastAPI e validadores do Cobra foi concluída em `priority-pairs-complete-review-v2.json`. Ambos passaram no escopo original: condições de leitura/escrita e limites do cache; tipo de função versus factory/callback, caminhos distintos de Find/ValidateArgs, inicializadores e ordem de hooks/flags no Cobra. Exemplos exatos EN/PT foram analisados sintaticamente, sem importar ou executar os projetos. O exemplo Python e a consulta léxica confirmaram a única atribuição direta ao nome dependency_cache em 701; exemplos Go usaram o parser próprio já instalado. Controles próprios malformados foram recusados. Esses resultados não provam typecheck, runtime ou testes externos aprovados.

O lote principal `owner-review-batch-v3.json` prioriza os três pares originais pedidos: cache do FastAPI, Cobra e Zod corrigido. Cache é renderização determinística de regras fechadas com revisão manual; os demais têm autoria editorial manual. Nenhum tem nova contribuição do modelo local. Dois pares públicos suplementares e a nota interna do helper permanecem preservados. As três FAQs preselecionadas estão apoiadas nos capítulos aceitos, com hashes dos trechos e vínculo ao documento completo; não se afirmam documentos independentes completos sem o contexto/citações do capítulo. Aprovações do dono, publicação e Gold continuam falsas.

O novo estudo `faq-question-binding-results-v1.json` executou 14 controles congelados. A checagem literal admitiu 0/9 violações de identidade/esquema/associação e recusou 0/2 formas intactas do mesmo conjunto. Entretanto, 2/2 respostas semanticamente falsas com IDs e identificadores corretos passaram pelos vínculos literais, e 1/1 paráfrase correta foi recusada pela política de texto exato. Essas populações são distintas; os números não são precisão semântica geral nem amostras independentes. Nos dois outputs Click históricos, o diagnóstico encontrou Q002 ligado a CK03 em vez de CK02 e ausência do helper solicitado. A nova exigência de texto PT exato não foi aplicada retroativamente; os scores e bytes originais permanecem inalterados. A proposta de integração preserva arquivos-alvo, riscos e regressões, sem alteração em produção ou testes permanentes.

A auditoria `campaign-requirement-evidence-audit-v2.json` vincula as 22 perguntas finais a evidências e pendências. Ainda faltam duração, amostra independente suficientemente diversa e comparação neural nova. A nova busca histórica encontrou uso anterior de fontes Core e Godot em campanhas de 18–19 de novembro, além de documentação existente de url-shortener. Esses candidatos não foram certificados como famílias novas. Arquivos arquivados e transferências anteriores de tooling contam na avaliação de exposição; ausência nas 305 linhas não basta. Raylib continua caso prospectivo não executado, com independência externa/arquivada não certificada.

Checkpoint007 restaurou 535 arquivos com hashes/modos e sete grupos de consumidores, incluindo os novos vínculos FAQ e exemplos prioritários. A observação atual de Git confirmou 41/41 repositórios externos sem alteração de HEAD/status. Nenhuma mudança em fonte de aplicação, catálogo, peso ou Git foi feita.
''',
names[1]:f'''
## Inventário intensivo — ACTIVE em {now.isoformat()}

`{prefix}file-inventory-cut-005.json` registra {len(inventory)} arquivos: pesquisa atual, arquivos dos checkpoints ignorados pelo Git e quatro relatórios antes deste apêndice, cada um com finalidade/bytes/SHA-256. Artefatos posteriores pertencem ao próximo corte. O recibo do apêndice registra os hashes finais dos relatórios. Cópias restauradas em /private/tmp têm caminhos reconstruíveis pelo restored_root e input-manifest de cada checkpoint; não são alterações dos repositórios originais.

O classificador de finalidade foi corrigido: snapshots públicos Python em context-topic-sources são dados de fonte, e não programas verificadores próprios. Os exemplos sintéticos são identificados separadamente dos produtores. Os arquivos antigos permanecem preservados; essa correção não indica execução das fontes alvo. `repository-action-ledger-v3.json` também separa tentativas Git falhas dos arquivos efetivamente adquiridos. O src/utils.c ausente de Raylib não é listado como fonte adquirida nem prova remoção. Novas fontes incluem Click core.py/LICENSE e os seis arquivos Cobra; todos os projetos externos permanecem sem alterações, conforme `repository-state-observation-v2.json`.

Nenhum arquivo foi excluído. Stage, commit, push e alterações de histórico: nenhum. Validações novas são controles de pesquisa e consumo de restauração; os números de suítes anteriores continuam históricos.
{table}
''',
names[2]:f'''
## Prontidão intensiva — {now.isoformat()}

Os nove gates continuam NO_GO, e MODEL_READY_FOR_ASSISTED_DOCUMENTATION permanece INSUFFICIENT_EVIDENCE. O fechamento dos capítulos manuais/determinísticos e das FAQs vinculadas não mede aprendizagem neural. O protótipo de vínculos FAQ deixa passar respostas falsas com IDs corretos; seus resultados não autorizam supervisão automática, publicação ou Gold.

Core e Godot já têm evidência de exposição de fonte anterior. Url-shortener tem documentação no catálogo e investigação de exposição relacionada a HTTPX. Não declarar famílias independentes apenas pela ausência no dataset de 305 registros. Raylib permanece avaliação prospectiva não executada e excluída de treino. A diversidade Python/Go/TypeScript/JavaScript e a suficiência amostral ainda não foram estabelecidas.

Identidade estática do GGUF é consistente, mas não substitui base treinável aprovada, tokenizer/template/máscara reais, fit, inventário Q/V carregado, memória/runtime MLX ou recuperação de otimizador. Não houve instalação, download de pesos, criação de adapter ou optimizer update. O pacote anterior do primeiro piloto continua não executável e dependente de aprovação separada.
''',
names[3]:f'''
## Continuação intensiva — ACTIVE em {now.isoformat()}

Último checkpoint: `{prefix}checkpoint-007.json`, 535 arquivos e sete grupos de consumidores. Artefatos posteriores (batch v3, auditorias, inventário/relatórios deste corte e exposição arquivada) devem entrar no próximo checkpoint. Os documentos prioritários estão em `priority-pairs-complete-review-v2.json` e `zod-complete-review-v3.json`; FAQs em `priority-three-faq-bound-excerpt-review-v1.json`; lote principal em `owner-review-batch-v3.json`.

Próximo trabalho útil: resolver a seleção de famílias para benchmark com auditoria que inclua arquivos arquivados e documentação do catálogo, mantendo os casos expostos em desenvolvimento. Novas fontes públicas só podem integrar avaliação após identidade, direitos, linhagem e critérios congelados; nenhuma amostra passa a Gold automaticamente. A proposta FAQ em `faq-binding-integration-proposal-v1.json` está preservada, não aplicada. Vínculo literal não é verificação semântica.

Conferir a matriz das 22 perguntas e completar evidência onde ainda insuficiente; preservar métricas por população. Preparar próximos experimentos recuperáveis sem repetir inferências antigas ou inventar melhoria de pesos. Docker continua indisponível para inferência; continuar pesquisa útil sem contornar permissões. A campanha permanece ativa até aproximadamente 12 horas reais, salvo limite efetivo de host/recurso, que deve ser registrado com duração honesta. Nenhuma pergunta intermediária ao dono.
'''}
preimages=P/'root-preimages-cut-005'
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
with (P/'root-report-append-cut-005.json').open('x') as stream:
    json.dump({'at':now.isoformat(),'status':'ACTIVE','elapsed_seconds':elapsed,'reports':changes},stream,indent=2)
    stream.write('\n')
print(json.dumps({'status':'ACTIVE','elapsed_seconds':elapsed,'inventoried_files':len(inventory),'reports_appended':4}))
