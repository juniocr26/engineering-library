import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Progresso intensivo 051 — recuperação Ruff e reconciliação das populações

O checkpoint 035 recuperou efetivamente 4.207 arquivos regulares, 110.050.955 bytes e 36 grupos finitos de consumidores. O par original Ruff target-version passou G9 após essa recuperação, completando G1–G9 no escopo estático declarado. Os documentos originais permanecem inalterados. O recibo ruff-target-complete-review-v3.json preserva a distinção entre revisão de fonte/API e ausência de compilação, parser Rust, execução Cargo ou Ruff.

A auditoria v13 contabiliza 28 versões relacionadas de pares bilíngues: 24 tecnicamente aceitas, uma inconclusiva por lacuna de citação e três falhas históricas de atribuição. Não são 28 tarefas independentes nem uma taxa de desempenho neural. O lote de revisão v13 contém três pares prioritários e 14 suplementares públicos; o par interno do helper permanece separado. Publicação, Gold, treino e decisão do proprietário não foram concedidos. As três versões originais reprovadas continuam preservadas e fora da seleção.

A reconciliação v12 cobre os 16 nomes de métricas pedidos sem inventar denominadores gerais. Há zero novas chamadas, tokens gerados e segundos de geração do modelo local; o uso GPT/Codex da campanha é separado, não zero, com custo monetário desconhecido. O checkpoint 031 continua falho antes da extração, preservado e excluído dos sucessos de recuperação.

A consulta primária única ao Gitiles de x/net não retornou metadados acessíveis. O resultado é INCONCLUSIVE_PRIMARY_METADATA_TOOL_ACCESS, sem consultas condicionais de arquivos, repetição ou transporte alternativo. Isso não demonstra inexistência do commit nem incorreção do snapshot local. A identidade upstream e a equivalência de bytes continuam não verificadas; nenhuma independência de avaliação ou prontidão de treinamento foi promovida.

Às 05:48 UTC, decorreram cerca de sete horas desde a linha de base desta campanha, sem somar a campanha anterior de oito horas. O trabalho segue ativo rumo às aproximadamente 12 horas reais, com revisão de outros alvos e consolidação de evidências ainda pendentes.
'''
j=p/'root-report-bundle-progress-051';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v51.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
