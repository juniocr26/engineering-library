"""Purpose annotations for current full-chapter and recovery evidence, preserving prior classifiers."""
from pathlib import Path
from artifact_purpose_v11 import purpose as previous_purpose

def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith('agent-contracts-dated-optional-source-cut-'):
  return 'Bytes exatos de ferramentas opcionais próprias no corte histórico, recuperados do arquivo operacional v7; fonte inspecionada como dado, sem substituir código ativo ou executar aplicação'
 if name.startswith('agent-contracts-current-chapter-snapshot-'):
  return 'Snapshot integral do capítulo interno EN/PT e metadados originais; preserva cortes mistos históricos e estado anterior à explicitação temporal/população'
 if name.startswith('agent-contracts-dated-reviewed-candidate-v1/'):
  return 'Primeiro candidato integral interno EN/PT com nota temporal e links realocados; preservado após ambiguidade cinco tarefas/dois caminhos, sem promoção automática'
 if name.startswith('agent-contracts-dated-reviewed-candidate-v2/'):
  return 'Segundo candidato integral interno EN/PT e diff: explicita época e cinco tarefas/dois caminhos de fonte; aceitação técnica vinculada ao recibo/recovery044, sem publicação/Gold/treino'
 if name.startswith(('agent-contracts-','consume_agent_contracts')):
  return 'Preflight, revisão integral, comparação de fontes/respostas/recibos/logs ou consumidor finito do capítulo interno; escopos datados e populações separados, falhas/versões preservadas, não aprovação humana nem inferência local'
 if name.startswith(('prometheus-','review_prometheus','acquire_prometheus','consume_prometheus')):
  return 'Fontes Prometheus fixadas/variantes de labels e revisão integral Builder/Keep; atribuição histórica original/correção completa, sintaxe limitada e recuperação, sem execução Prometheus'
 if name.startswith(('fastify-','review_fastify','acquire_fastify','consume_fastify')):
  return 'Fontes Fastify fixadas, chamadores/helpers/receivers e fonte primária JavaScript; revisão EN/PT/sintaxe/proveniência/recuperação, sem servidor ou testes upstream'
 if name.startswith(('sqlx-','review_sqlx','acquire_sqlx','consume_sqlx')):
  return 'Fontes SQLX fixadas e contratos In/map/named, reflexão/Valuer/chamadores e respostas históricas; revisão integral estática e recuperação, sem banco ou suíte SQLX'
 if name.startswith(('sdk-retry-','review_sdk_retry','acquire_sdk_retry','consume_sdk_retry')):
  return 'Fonte SDK retry fixada/censo Go e proveniência; original com falha de atribuição, correção EN/PT e recuperação, sem executar retries, SDK ou testes de aplicação'
 if name.startswith(('chi-target','chi-middleware','chi-throttle','review_chi_targets','acquire_chi_targets','consume_chi_targets','observe_chi_syntax')):
  return 'Fonte Chi fixada e contratos Timeout/Recoverer/throttle, respostas históricas, derivações Retry-After/sintaxe e revisão EN/PT recuperável; sem servidor ou testes Chi'
 if name.startswith(('own-repository-baseline-semantics','refresh_repository_ledger')):
  return 'Reconciliação explícita do estado próprio inicial limpo22:42 e observação posterior22:45 com relatórios/pesquisa autorizados; preserva comandos e rótulos antigos, sem mutação Git'
 return previous_purpose(path)
