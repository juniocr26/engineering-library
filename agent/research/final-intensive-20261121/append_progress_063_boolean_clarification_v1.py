import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
note="""

Esclarecimento literal do progresso 063: no pedido misleading-complete, os valores de complete_scope, aliases_checked e relocations_checked são todos true. As afirmações de completude e ausência de relocação são falsas diante do mapa independente; não são flags com valor false. A expressão anterior “deliberadamente falsos” se refere às declarações sobre o escopo, não aos valores booleanos serializados. O pedido bruto, o mapa e o resultado REMOVE permanecem preservados e vinculados por hash.
"""
j=p/'root-report-bundle-progress-063-boolean-note';prepare(root,j,{n:note.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v63-boolean-note.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
