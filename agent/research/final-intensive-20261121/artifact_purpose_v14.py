"""Purpose annotations for row-level FAQ review and explicit NO_GO pilot packages."""
from pathlib import Path
from artifact_purpose_v13 import purpose as previous_purpose

def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith(('dataset-faq-','audit_dataset_faq_','consume_dataset_faq_')):
  return 'Revisão isolada de148FAQs não privadas: identidade/hash/trecho físico e limites do alvo;74pares EN/PT,2respostas incluem seção posterior,22linhas com sinais de contexto; originais imutáveis,sem aprovação semântica automática/Gold/treino'
 if name.startswith(('fine-tuning-current-nine-gates-','assess_current_fine_tuning_','first-lora-owner-authorization-','consume_scope_and_first_pilot_')):
  return 'Avaliação atual de nove condições NO_GO e pacote de decisão LoRA NÃO EXECUTÁVEL; parâmetros históricos não validados,zero alvos aprovados/otimizador/adaptadores; consumidor verifica dados preservados,sem executar treino ou planner'
 if name.startswith('source-scope-retirement-h68-h81-'):
  return 'Auditoria de fontes/inputs/saídas históricas H68–H81: REMOVE inseguro com flags de escopo verdadeiras porém sem apoio independente,trade-off conservador H75 e portabilidade Python; não execução nova nem taxa geral'
 return previous_purpose(path)
