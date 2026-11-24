"""Extend inventory roles for native compiler evidence and exposure audits."""
from pathlib import Path
from artifact_purpose_v1 import purpose as previous_purpose


def purpose(path):
    name=str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
    if name.startswith('cpp-ast-dispatch-observations-'):
        return 'AST ou diagnóstico bruto de análise estática Clang dos controles C++ próprios; sem executar programas'
    if name.startswith('cpp-qualified-dispatch-owned-'):
        if name.endswith('source.cpp'):
            return 'Controle C++ próprio sem main para comparar chamada qualificada e não qualificada; não executado'
        if name.endswith('.ll'):
            return 'IR LLVM textual para o controle C++ próprio; nenhum objeto ou executável emitido'
        return 'AST ou diagnóstico bruto do controle C++ próprio, preservado com identidade exata'
    if name.startswith('cpp-same-TU-normalized-callee-difference'):
        return 'Diff de projeções AST normalizadas que refuta a hipótese de igualdade completa; não é alteração de código'
    if name.startswith('user-request-'):
        return 'Pedido original do usuário e recibo de preservação exata das condições de autorização'
    if name.startswith('repository-exposure-matrix'):
        return 'Classificação conservadora de exposição e confidencialidade; não certifica independência ou treino'
    if name.startswith('archived-family-exposure'):
        return 'Auditoria de exposição histórica/integridade de fontes públicas; hashes não são revisão semântica'
    if name.startswith('model-exposure-execution-witness'):
        return 'Vínculos de requests históricos a respostas e recibos; não são novas inferências'
    if name.startswith('current-metric-population-audit'):
        return 'Populações e denominadores reconciliados sem agregar versões/traduções como ensaios independentes'
    if name.startswith('typed-evidence-interpretation-supplement'):
        return 'Clarificação técnica futura das camadas de evidência, sem reavaliar critérios ou resultados anteriores'
    return previous_purpose(path)
