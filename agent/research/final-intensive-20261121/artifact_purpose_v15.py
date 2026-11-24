"""Refine weekend capsule failure preservation and positive Git membership artifacts."""
from pathlib import Path
from artifact_purpose_v14 import purpose as previous_purpose

def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith(('pinned-tree-','pinned_tree_','acquire_pinned_tree_','consume_pinned_tree_','observe_pinned_tree_')):
  return 'Testemunho positivo de pertencimento de fonte pública já exposta a commit/árvores/blob Git fixados; sete objetos, um positivo e seis perturbações; sem prova de escopo global/continuidade semântica/REMOVE, sem execução do alvo ou ganho neural'
 if name.startswith(('weekend-','consume_weekend_','inventory_weekend_','observe_weekend_')):
  return 'Consumo autônomo do capsule048e recibos, scripts/receitas versionados, controles e falhas preservadas; v1perde streams em timeout, v2do runner preserva bytes; consumidor de recibos v2lia três caminhos absolutos, v3falhou por âncora portátil e v4corrige via plano pinado; sem execução de modelo/treino ou certificação geral'
 if name.startswith(('campaign-activity-evidence-timeline-','build_campaign_activity_timeline_')):
  return 'Linha temporal de timestamps/hash de recibos desta campanha desde baseline; exclui durações históricas, não mede atividade produtiva contínua/CPU/inferência e não transforma lacunas em prova de trabalho'
 if name.startswith('goal-accounting-observation-'):
  return 'Corte datado da contabilidade do objetivo GPT/Codex, separado de duração de parede e inferência local zero; não custo monetário final nem certificação de atividade contínua'
 if name.startswith('checkpoint-049-weekend-consumer-corrected-'):
  return 'Suplemento pós049com consumidor corrigido v4sobre dados restaurados; código novo não está no arquivo049original; CP050inclui a correção e registra três caminhos sob raiz restaurada'
 return previous_purpose(path)
