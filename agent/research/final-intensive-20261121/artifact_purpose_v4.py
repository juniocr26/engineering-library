"""Keep owned controls, actual report history and browser-derived source in distinct roles."""
from pathlib import Path
from artifact_purpose_v3 import purpose as previous_purpose

def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith('report-bundle-owned-observations-'):
  return 'Controle próprio de interrupção/recovery sobre quatro arquivos sintéticos; não é versão de relatório real ou teste de crash'
 if name.startswith('root-report-bundle-progress-'):
  return 'Plano/preimagem/payload/recibo de append autorizado aos quatro relatórios reais, preservado sem truncamento'
 if name.startswith(('root-report-chain-audit-','report-history-corpus-refinement-')):
  return 'Auditoria byte a byte de prefixos/arestas com recibos no corte e classificação de proveniência; não é aceite semântico'
 if name.startswith(('helper-subprocess-','helper-job-')):
  return 'Observação dinâmica de classes Python atuais com fontes/journals próprios e falhas simuladas; sem inferência, falha real do OS ou execução do Go inspecionado'
 if name.startswith('go-shellwords-') or name.startswith(('util_posix.go.browser-','util_windows.go.browser-')):
  return 'Fonte pública apresentada/reconstruída pelo navegador, limite/falha de aquisição ou contrato Go provisório; não é blob bruto nem holdout executável certificado'
 if name.startswith(('report_bundle_append_','observe_report_bundle_')):
  return 'Utilitário/observador isolado de append recuperável dos quatro relatórios, com planos e controles próprios'
 return previous_purpose(path)
