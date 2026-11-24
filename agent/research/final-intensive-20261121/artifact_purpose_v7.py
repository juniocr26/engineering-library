"""Classify new static model, lexical screen and dataset correspondence evidence."""
from pathlib import Path
from artifact_purpose_v6 import purpose as previous_purpose
def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith(('gguf-tensor-directory-','observe_gguf_tensor_directory','consume_gguf_tensor_directory','gguf-v3-tensor-layout-','qv-adapter-metadata-','review_qv_adapter_metadata')):
  return 'Diretório GGUF/metadados QV e estimativa condicional de adaptador; zero payload de tensores, inferência, módulos carregados ou estados de otimizador'
 if name.startswith(('bilingual-guard-','freeze_bilingual_guard','observe_bilingual_guard','consume_bilingual_guard')):
  return 'Protocolo/controles/replay de triagem bilíngue literal e seus limites semânticos; população de desenvolvimento correlacionada, sem certificação de equivalência'
 if name.startswith(('requested-metric-reconciliation','reconcile_requested_metrics','current-metric-population-audit-','audit_current_metric_populations')):
  return 'Reconciliação de métricas e populações com denominadores/limitações explícitos; taxas gerais desconhecidas permanecem nulas'
 if name.startswith(('proposal-integration-boundary-','audit_proposal_integration_boundaries')):
  return 'Auditoria somente leitura dos alvos e limites de propostas não aplicadas; conserva defeito de citação v1 e correção v2 separadamente'
 if name.startswith(('dataset-current-candidate-','observe_dataset_candidate_correspondence')):
  return 'Correspondência exata entre referências de alvos originais não privados e candidatos atuais; sem propagação de aprovação ou mudança dos305registros'
 if name.startswith(('prospective-go-source-identity-','kr-text-primary-browser-')):
  return 'Evidência de preflight de origem pública Go incompleta; sem tarefa certificada, instalação, checkout ou reconstrução de fonte achatada'
 return previous_purpose(path)
