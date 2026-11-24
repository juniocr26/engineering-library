import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common="""

### Progresso intensivo 071 — testemunho positivo de fonte derivado de árvore Git

Foi adquirido um testemunho positivo para backend/internal/infrastructure/imaging/limits.go no commit48476de6e4450294b7769ab7af90805100bb21b5do go-image-optimizer, fonte pública já exposta e revisada nesta campanha. Doze comandos Git somente leitura preservaram commit, cinco árvores no caminho e blob; os sete objetos tiveram IDs Git recomputados e o blob coincide com SHA-256b1b23e6c4721e843b93864a1109900d27217c58792a8e9def4fe9bb181044cb8já conhecido. HEAD/status antes/depois permaneceram iguais. Não houve fetch, checkout ou execução da aplicação. O ledger24acrescenta as operações sem criar nova família independente.

O verificador de recuperação lê somente os objetos preservados, sem Git ou modelo. Um testemunho real íntegro e seis perturbações próprias corresponderam aos rótulos congelados: corrupção de blob, árvore raiz ausente, blob ausente, caminho inexistente, SHA de fonte errado e traversal foram recusados. Esses sete casos não medem semântica, precisão de ciclo de vida ou segurança geral.

O resultado prova presença exata da fonte selecionada na árvore pinada, sem depender de complete_scope fornecido pelo autor. Não prova enumeração de declarações de todo o repositório, continuidade semântica por nome, inexistência de código gerado/aliases, aposentadoria ou autorização de REMOVE/MODIFY. O estado de ciclo de vida permanece INCONCLUSIVE com testemunho positivo de pertencimento. O planner de produção continua intacto e o limite H68não foi declarado corrigido.

O checkpoint050anterior restaurou5.811arquivos de358.756.226bytes, com50grupos finitos e pós-registro de quatro relatórios exatos. Seu consumidor de recibos versão4foi executado de dentro do arquivo e mostrou os três caminhos sob a própria raiz restaurada, resolvendo nesse corte a limitação do novo grupo049. O testemunho Git e os sete controles são posteriores ao050e ainda precisam ser preservados em novo corte.
"""
j=p/'root-report-bundle-progress-071';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v71.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
