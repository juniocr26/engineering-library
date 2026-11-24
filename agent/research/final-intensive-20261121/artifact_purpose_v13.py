"""Purpose annotations for unexecuted paired model packets and explicit temporary inventories."""
from pathlib import Path
from artifact_purpose_v12 import purpose as previous_purpose

def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith(('next-neural-matched-','prepare_next_neural_matched_')):
  return 'Protocolo/pedidos pareados de documentação completa para experimento DEV futuro sobre três campos de metadados; preparação e falha de preflight preservadas, NÃO EXECUTADO, zero chamadas/resultados, sem mudança do prompt de produção ou aprovação de treino'
 if name.startswith(('temporary-report-reconstruction','inventory_report_reconstruction')):
  return 'Inventário somente de raízes temporárias declaradas por recibos de reconstrução de relatórios; confere hashes after do corte histórico sem inferir igualdade ao relatório atual, sem escrever conteúdo/metadados'
 if name.startswith('file-purpose-supplement-'):
  return 'Suplemento por caminho/hash que refina propósitos de arquivos de backup já inventariados, distinguindo arquivo original e suplementos obrigatórios; inventários anteriores preservados'
 if name.startswith(('repository-exposure-matrix-v5','refine_current_exposure_matrix_v5')):
  return 'Matriz de42repositórios com uso seletivo atual de fonte separado do campo legado de consulta ao catálogo; nove privados externos só metadados e nenhuma independência certificada'
 return previous_purpose(path)
