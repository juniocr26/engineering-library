"""Refine owner batch diversity and bounded Python-open recovery observations."""
from pathlib import Path
from artifact_purpose_v15 import purpose as previous_purpose

def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith(('owner-review-batch-identity-','audit_owner_review_batch_identity_','owner-review-family-dependency-')):
  return 'Auditoria de identidade/diversidade do pacote28públicos+2internos:60hashes únicos,15rótulos públicos/0independência certificada,grafo parcial FastAPI-Starlette; falhas v1/v2de identificação de idioma preservadas,v3concluída; avisos não são direitos de treino/Gold'
 if name.startswith(('weekend-seven-readers-open-audit','weekend-reader-open-audit','weekend_reader_open_audit','observe_weekend_seven_readers_')):
  return 'Observação Python open de sete leitores restaurados:4654eventos/0aberturas do workspace/0writes;29paths externos do runtime e controle fraco v2detectado com3leituras; não traceOS/nativo/startup,segurança geral,modelo ou precisão semântica'
 if name.startswith('consume_current_portable_recovery_evidence_'):
  return 'Consumidor de pacote LoRA não executável atualizado e provas de recuperação:5871inputs históricos+4prefixos de relatório,7readers/openaudit; mapeia refs ao ROOT selecionado e não reextrai arquivo051nem lê raízes temporárias antigas'
 if name.startswith('first-lora-owner-authorization-package-v2'):
  return 'Pacote LoRA NÃO EXECUTÁVEL atualizado para noveNO_GOv4,identidade/famílias e recuperação atuais; parâmetros/budgets/zeroGold preservados,sem configuraçãotrainável,modelo,otimizador ou aprovação'
 return previous_purpose(path)
