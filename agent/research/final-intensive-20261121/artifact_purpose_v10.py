"""Classify current original-target, checkpoint-failure and tokenizer-readiness evidence."""
from pathlib import Path
from artifact_purpose_v9 import purpose as previous_purpose
def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith(('redis-','review_redis','prepare_redis','acquire_redis','consume_redis','observe_redis')):
  return 'Fontes Redis públicas fixadas, revisão bilíngue original/correção de atribuição, lexer bruto e recuperação; sem executar servidor, compilar a aplicação ou conceder direitos/Gold'
 if name.startswith(('rails-request','review_rails','consume_rails','acquire_rails','observe_rails')):
  return 'Dependência pública actionpack instalada, fonte/licença/gemspec, AST Ripper e revisão bilíngue de getters; propriedade lexical não é binding runtime nem compatibilidade do framework'
 if name.startswith(('candidate-tokenizer-json','acquire_candidate_tokenizer')):
  return 'Protocolo e tentativa única de leitura de JSON de tokenizer público fixado; falha DNS sem conteúdo, pesos, framework, tokenização, inferência ou treinamento'
 if name.startswith(('checkpoint-path','checkpoint_paths','consume_checkpoint_paths','checkpoint-031-failure')):
  return 'Falha real de checkpoint preservada e resolução confinada de aliases de dependências; controles finitos não certificam segurança geral ou durabilidade'
 if name.startswith(('source-preparation-metadata','prepare_metadata_leakage')):
  return 'Diagnóstico histórico de metadados do parser tratados como contrato e dois envelopes para comparação não executada; sem causalidade, vencedor ou mudança de prompt de produção'
 return previous_purpose(path)
