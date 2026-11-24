"""Describe research inventory roles without treating target snapshots as tools."""
from pathlib import Path


def purpose(path):
    name = str(Path(path).resolve().relative_to(Path(__file__).resolve().parent))
    if 'root-preimages' in name or name.endswith('.recovered.bin'):
        return 'Preimagem imutável de relatório, preservada para recuperação histórica'
    if name.startswith(('reacquired-public-sources/', 'context-topic-sources-',
                        'priority-pair-source-', 'faq-question-binding-source-',
                        'raylib-evaluation-source-', 'zod-complete-source-')):
        return 'Fonte fixada adquirida em leitura; dado para revisão/sintaxe, sem executar a aplicação'
    if name.startswith('real-revision-evidence'):
        return 'Objeto Git ou diff real antes/depois, adquirido sem alterações no projeto'
    if 'exception-scope-controls' in name:
        return 'Fonte sintética própria para investigar escopo de exceções; sem integração em produção'
    if name.startswith('raylib-evaluation-owned-examples-'):
        return 'Fragmento C próprio de controle sintático; sem link ou execução de Raylib'
    if name.startswith('context-topic-verification-') and 'owned-example' in name:
        return 'Fragmento próprio de exemplo, preservado para análise sintática'
    if name.startswith('renderer-recovery-v1/'):
        return 'Entrada, mutação ou saída preservada do consumidor de pesquisa restaurado'
    if name.startswith('helper-admission-observations'):
        return 'Saída bruta da extração/validação e cobertura de citações do helper existente'
    if name.endswith(('.py', '.cjs')):
        return 'Programa isolado de pesquisa: protótipo, produtor ou verificador, sem integração em produção'
    if name.endswith('.diff'):
        return 'Diff de candidato isolado para revisão; não aplicado'
    if name.endswith('.md'):
        return 'Candidato documental isolado; sem publicação ou aprovação Gold'
    if 'owner-review-batch' in name:
        return 'Lote de revisão com identidades e restrições de uso; elegibilidade de treino negada'
    if 'model-static-identity' in name:
        return 'Identidade estática local do modelo e limites de inferência/treino não verificados'
    if 'inventory' in name or 'ledger' in name:
        return 'Inventário ou registro de vínculos, populações e proveniência com escopo explícito'
    if 'protocol' in name or 'freeze' in name or 'contract' in name:
        return 'Critérios ou entradas congeladas antes da avaliação correspondente'
    if 'review' in name or 'adjudication' in name:
        return 'Revisão delimitada de evidência; não é aprovação do dono, publicação ou Gold'
    if 'failure' in name or 'unavailable' in name:
        return 'Falha ou limitação preservada, sem apagar tentativas anteriores'
    if 'checkpoint' in name:
        return 'Recibo de arquivo/restauração e consumo operacional delimitado'
    if 'result' in name or 'observation' in name:
        return 'Resultado ou observação efetiva, com população e limitações declaradas'
    return 'Artefato técnico de pesquisa com identidade e proveniência preservadas'
