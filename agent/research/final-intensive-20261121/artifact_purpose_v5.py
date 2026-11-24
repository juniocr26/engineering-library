"""Separate SDK export/cache evidence from source/semantic or neural acceptance."""
from pathlib import Path
from artifact_purpose_v4 import purpose as previous_purpose

def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith('owned-go-build-cache-'):
  return 'Cache de compilação do SDK Go existente e observadores próprios; investimento preservado, sem pesos/modelos'
 if name.startswith('offline-go-type-observer-'):
  if name.endswith('/observer'):return 'Binário próprio de análise estática Go; não executa a fonte inspecionada, hash e plataforma congelados'
  if name.endswith('/main.go'):return 'Fonte própria do observador Go de tipos/imports com perfil delimitado; sem integração de produção'
  return 'Protocolo/saída/recibo de compilação do observador com SDK existente e rede desativada'
 if name.startswith(('go-stdlib-','owned-go-type-','go-type-relation-')):
  return 'Metadados de exports do SDK, controles estáticos próprios ou revisão delimitada; não é taxa neural ou revisão integral do SDK'
 if name.startswith('go-types-selection-primary-source-'):
  return 'Snapshot exato de go/types/selection.go do SDK Go existente, referência de semântica estática com licença preservada'
 if name.startswith(('existing-offpath-go-','existing-go-sdk-','owned-compiler-artifact-storage-')):
  return 'Disponibilidade/versão/licença do SDK existente ou política de preservação local de compilação, sem instalação'
 if name.startswith('go-shellwords-frozen-type-intake-'):
  return 'Aplicação sem alteração do observador congelado à entrada prospectiva incompleta; diagnóstico, sem tuning/score/aceite'
 return previous_purpose(path)
