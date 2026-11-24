"""Append the prospective Python case and bounded runtime failure to canonical reports."""
from pathlib import Path
import datetime,json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[2];now=datetime.datetime.now(datetime.timezone.utc).isoformat();sha=lambda b:hashlib.sha256(b).hexdigest()
pre=P/'root-preimages-progress-008';pre.mkdir(mode=0o700)
body=f'''
## Corte intensivo 008 — ACTIVE em {now}

O cliente Ollama existente foi submetido a uma tentativa limitada de readiness, sem inferência. O processo terminou com código 1: criação de /Users/juniorosa/.ollama negada pelo sandbox. A consulta HTTP local também retornou operação não permitida. O processo iniciado terminou; nenhum servidor permaneceu ativo, modelo foi carregado, framework instalado ou peso copiado. Não houve escalada, alteração de HOME ou contorno. Protocolo, stdout/stderr e recibo: host-ollama-readiness-*-v1. A ausência de runtime utilizável delimita a inferência neste ambiente; não prova defeito dos pesos.

Foi preparado OPENSHOT_PATHS_PY_EVAL_01, caso Python prospectivo de documentação completa EN/PT para oito APIs de caminhos e suas dependências. Seis snapshots entram no contexto congelado. Há 21 grupos de referência compostos e dez afirmações adversas, nunca tratados como precisão atômica ou sucesso neural. As fontes distinguem preservação de content:// nos helpers locais de expansão de mídia, prefixos startswith de validação exata, normpath de existência/contenção, normcase dependente do host e comparação de mídias vazias. Defaults de assets podem mudar; chamadas selecionadas usam create_paths=False. Os testes escritos não provam execução nativa Windows. Nenhum projeto, teste ou UI foi executado ou alterado.

A varredura direcionada examinou 7.968 arquivos históricos de texto, 213.094.118 bytes: zero ocorrências dos quatro caminhos/identificadores selecionados e 65 arquivos com metadados do repositório. Isso permite somente uma classificação prospectiva delimitada; não certifica arquivos compactados, uso externo, pré-treino ou independência humana. O caso e FAQs derivados são evaluation-only, proibidos para treino e ajuste do verificador. O request, revisão aa835d9377bdd7847ba7058874ca7e570e30eae6, fontes, referências e regras foram congelados antes de qualquer execução de modelo. O primeiro produtor falhou por faixa de citação além do fim de assets.py; falha e produtor v1 foram preservados, e v2 corrigiu as faixas antes de produzir o caso. Todos os seis arquivos passaram somente por ast.parse, sem importação/execução.

repository-action-ledger-v5.json mantém os 42 blocos e acrescenta os comandos reais de aquisição Chi/OpenShot, inclusive consulta esperada malsucedida do teste ausente no Chi antigo. Originais externos continuam sem alterações da campanha. Novas inferências, tokens Ollama e optimizer updates continuam zero; a preparação Python não preenche a lacuna Go/TypeScript do benchmark independente nem demonstra melhoria neural. MODEL_READY permanece INSUFFICIENT_EVIDENCE; nove gates de fine-tuning NO_GO, publicação/Gold não aprovados. A duração real continua inferior a aproximadamente 12 horas.
'''
rows=[]
for name in ['AI_TRAINING_CAMPAIGN_REPORT.md','AI_TRAINING_FILE_INVENTORY.md','AI_FINE_TUNING_READINESS.md','AI_TRAINING_RESUME.md']:
 f=ROOT/name;old=f.read_bytes();(pre/name).write_bytes(old);f.write_bytes(old+body.encode());rows.append({'path':name,'before_sha256':sha(old),'after_sha256':sha(f.read_bytes()),'preimage':str((pre/name).relative_to(ROOT))})
with (P/'root-report-append-receipt-v8.json').open('x') as f:json.dump({'at':now,'reports':rows,'active':True},f,indent=2);f.write('\n')
print('Four report prefixes preserved; progress008 appended')
