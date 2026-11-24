"""Classify installed runtime snapshots and denied IPC separately from inference results."""
from pathlib import Path
from artifact_purpose_v5 import purpose as previous_purpose

def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith('installed-llama-native-artifacts-'):
  return 'Cópia preservada de biblioteca x86_64 já instalada, alias regular ou licença; sem pesos, carga de modelo ou ABI compatível comprovada'
 if name.startswith(('installed-llama-native-artifact-manifest-','existing-ollama-native-','existing-native-llama-','existing-llama-','existing-native-cpu-','native-cpu-symbols-','native-inference-','native-llama-','owned-unix-ipc-')):
  return 'Metadados/ajuda/símbolos/formatos e precondições de runtime ou recusa de IPC; não constitui inferência ou ambiente treinável'
 if name.startswith(('go-shellwords-version-source-comparison-','go-shellwords-version-scope-','go-shellwords-selector-')):
  return 'Comparação de versões públicas representadas, referência de escopo ou falha do adaptador preservada; sem score neural, runtime ou blob bruto validado'
 return previous_purpose(path)
