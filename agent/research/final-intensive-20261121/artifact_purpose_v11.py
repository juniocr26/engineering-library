"""Classify new public target evidence and explicit temporary recovery inventory."""
from pathlib import Path
from artifact_purpose_v10 import purpose as previous_purpose
def purpose(path):
 name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
 if name.startswith(('temporary-replay','inventory_temporary')):return 'Inventário explícito de arquivos temporários das restaurações declaradas, diferenciando entradas arquivadas e saídas de consumidores; sem modificar raízes temporárias'
 if name.startswith(('duckdb-','review_duckdb','acquire_duckdb','consume_duckdb')):return 'Fonte pública DuckDB fixada e revisão bilíngue original da factory booleana/construtores/nulidade; resposta histórica e recuperação, sem compilar/executar banco ou aprovar Gold'
 if name.startswith(('opencv-','review_opencv','acquire_opencv','consume_opencv')):return 'Fontes públicas OpenCV fixadas, dependências/tipos/chamadores e revisão original de coerção/formas/canais, respostas históricas e recuperação; sem build/runtime'
 if name.startswith(('ruff-','review_ruff','acquire_ruff','consume_ruff')):return 'Fontes públicas Ruff fixadas e revisão estática original de versão Python/lista compilada/precedência; sem parser Rust, compilador, Cargo ou execução Ruff'
 if name.startswith('go-vendored-httpguts-upstream'):return 'Consulta primária de identidade upstream x/net inacessível; commit completo/equivalência não verificados, sem repetição ou promoção de independência'
 return previous_purpose(path)
