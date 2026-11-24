"""Classify recovered original-target reviews and source-graph type research."""
from pathlib import Path
from artifact_purpose_v7 import purpose as previous_purpose
def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith(('offline-go-type-observer-v3/','offline-go-type-observer-v4/','offline-go-type-observer-v5/')):
  return 'Fonte/binário/build de observador Go isolado e preservado por versão; erros de nomes/ordenação v3v4 e correção v5, sem execução da aplicação-alvo'
 if name.startswith(('go-source-graph-','run_go_source_graph','observe_go_graph','consume_go_source_graph','build_owned_go_observer','go-image-application-source-graph','observe_real_go_image_type_graph')):
  return 'Controles próprios, tipagem estática entre fontes/exports SDK e replay de recuperação; não equivale a compilação integral, instância runtime ou qualidade neural'
 if '-source-context-v' in name or '-extra-context-v' in name:
  if name.startswith('go-image-'):
   return 'Snapshot público Git fixado de fonte/configuração/licença/testes Go Image; revisão selecionada, sem executar fontes ou suítes externas'
 if name.startswith('go-image-compression-historical-witnesses-'):
  return 'Request canônica e corpo bruto de resposta histórica Go Image com hashes; não é nova inferência nem prova do digest efetivo do servidor'
 if name.startswith(('go-image-animation-attribution-candidate-','go-image-compression-attribution-candidate-')):
  return 'Par bilíngue completo ou diff de correção manual de atribuição histórica; original preservado, sem aprovação editorial/Gold'
 if name.startswith(('go-image-','review_go_image','prepare_go_image','consume_go_image','acquire_go_image','locate_go_image')):
  return 'Aquisição, vínculo/revisão de alvo original público Go Image ou correção/recuperação isolada; labels históricos preservados e falhas separadas'
 if name.startswith('kr-text-immutable-'):
  return 'Resposta de consulta pública com pin de versão conhecido e arquivo/checksum indisponível; não é fonte bruta certificada'
 return previous_purpose(path)
