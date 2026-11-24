from pathlib import Path
from artifact_purpose_v16 import purpose as previous_purpose

def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith(('historical-neural-failure-taxonomy','historical-diagnostic-row-binding','neural-failure-taxonomy-','curate_historical_failure_','observe_historical_diagnostic_','consume_historical_failure_')):
  return 'Curadoria de56diagnósticos históricos não privados/uma família:rawrequests/responses,14mecanismos/8estágios;24rótulos inline e32outros esquemas não formam56falhas,3/6calibração literal não é aceitação de capítulo;v1countlabel refinado v2,zero novas chamadas/Gold'
 if name.startswith(('request-section-coverage-','audit_request_section_')):
  return 'Auditoria textual das22seções originais,39itens numerados e10critérios de sucesso; resultados experimentais não alcançados e fechamento pendente explícitos,sem reescrever o pedido ou declarar12horas antes do tempo'
 if name.startswith(('owned-final-tail-controls-','final-tail-controls-','observe_final_tail_')):
  return 'Artefatos sintéticos TEST_ONLY depreflight do suplemento final dos4relatórios:1append/5recusas antes de escrever,sem alterar relatórios canônicos; não atomicidade de4arquivos/powerloss/treino'
 if name.startswith('consume_weekend_capsule_v5'):
  return 'Bootstrap isolado para9leitores de dados e nota final opcional pinada; extrai em raiz nova,verifica hash/modo/prefixo+nota+tail,sem produzir novoTAR ou alterar workspace/modelo/framework'
 if name.startswith(('all-standalone-root-inventory-','inventory_all_standalone_')):
  return 'Inventário das4raízes autônomas declaradas por recibos,23.154inputs+16relatórios pós-nota;sem busca genérica em temporários ou writes explícitos,atime não garantido'
 return previous_purpose(path)
