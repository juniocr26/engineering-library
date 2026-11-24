from pathlib import Path
from artifact_purpose_v17 import purpose as previous_purpose

def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith(('append_final_canonical_tail_','finalize_campaign_acceptance_','preserve_final_evidence_supplement_','final-tail-source-','checkpoint054-postnote-')):
  return 'Código/achado técnico de fechamento finito: guard temporal, quatro relatórios, pins e suplemento posterior; versões preparatórias preservadas não são execuções nem aprovação de modelo'
 if name.startswith(('weekend-nine-readers-','observe_weekend_nine_')):
  return 'Observação Python open dos nove leitores CP054: perfil real isolado, limites de instrumentação e runtime explícitos; não certificação OS/Windows/segurança'
 if name.startswith(('accepted-versions-owner-selection-','audit_accepted_versions_')):
  return 'Reconciliação exata: 35 versões aceitas,28 pares públicos selecionados e7 versões aceitas fora da seleção; sem nova revisão semântica/Gold'
 if name.startswith(('next-neural-adjudication-','prepare_next_neural_adjudication_')):
  return 'Plano prospectivo de adjudicação e limites causais do par DEV: zero chamadas, sem criar independência ou autorização'
 if name.startswith(('campaign-unobserved-','final-metric-arithmetic-','audit_final_metric_')):
  return 'Contabilidade honesta de lacuna temporal ou aritmética de16métricas; sem medir produtividade contínua ou verdade semântica'
 return previous_purpose(path)
