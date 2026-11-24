"""Distinguish newly preserved source bytes, browser transcriptions and inference metadata."""
from pathlib import Path
from artifact_purpose_v2 import purpose as previous_purpose

def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith('golang-sync-browser-line-reconstruction'):
  return 'Transcrição derivada de linhas da fonte pública exibida pelo navegador; não é blob Git bruto validado nem holdout certificado'
 if name.startswith('golang-sync-'):
  return 'Evidência pública de aquisição/linhagem e recusas preservadas; candidato Go não certificado para avaliação independente'
 if name.startswith('gguf-tokenizer-metadata-prefix'):
  return 'Somente prefixo de metadados GGUF, sem diretório/dados de tensores; preserva vocabulário/template sem copiar pesos'
 if name.startswith(('gguf-candidate-','gguf-tokenizer-','tokenizer-stop-padding-')):
  return 'Correspondência estática de tokenizer/template/stops/padding; não executa tokenizer/modelo nem promove piloto'
 if name.startswith(('existing-native-inference-','host-ollama-readiness-')):
  return 'Disponibilidade do cliente e falha limitada de readiness do servidor; sem inferência e sem contorno de permissões'
 if name.startswith(('openshot-prospective-source-snapshots-','openshot-path-context-snapshots-','javascript-prospective-source-snapshots-','esp-hal-js-context-snapshots-')):
  return 'Snapshot de blob público adquirido por Git somente leitura ou saída de busca declarada no recibo; aquisição não implica revisão integral'
 if name.startswith(('openshot-','esp-hal-parser-','esp-hal-js-','cocos-tsx-','prospective-javascript-','javascript-prospective-')):
  return 'Preparação/verificação delimitada de caso prospectivo evaluation-only, formato da fonte ou exposição; sem treino/execução de modelo'
 if name.startswith('chi-revision-context-') or name.startswith('chi-writer-current-head-'):
  return 'Revisão real Chi, candidato completo EN/PT ou evidência de contexto/recuperação; uma comparação com contratos correlacionados'
 return previous_purpose(path)
