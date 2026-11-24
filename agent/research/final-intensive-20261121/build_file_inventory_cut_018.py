import datetime,json,hashlib
from pathlib import Path
from artifact_purpose_v14 import purpose
p=Path(__file__).resolve().parent;root=p.parents[2];rows=[]
files=sorted(x for x in p.rglob('*') if x.is_file() and not x.is_symlink() and '__pycache__' not in x.parts)
files+=sorted(x for x in (root/'.local-backups/final-intensive-20261121').rglob('*') if x.is_file() and not x.is_symlink())
files+=[root/n for n in ('AI_TRAINING_CAMPAIGN_REPORT.md','AI_TRAINING_FILE_INVENTORY.md','AI_FINE_TUNING_READINESS.md','AI_TRAINING_RESUME.md')]
purpose_overrides={x['path']:x for x in json.loads((p/'file-purpose-supplement-checkpoint040-v1.json').read_text())['records']}
for f in files:
 why=purpose(f) if f.is_relative_to(p) else (('Checkpoint031 FALHO antes da extração: arquivo/manifesto/diagnóstico preservado; zero consumidores, não recuperação bem-sucedida' if 'checkpoint-031' in f.parts else 'Checkpoint local imutável com manifesto/recibo de restauração; limitações por versão') if '.local-backups' in f.parts else 'Relatório humano canônico raiz; histórico preservado por acréscimo')
 if str(f.relative_to(root)) in purpose_overrides:
  override=purpose_overrides[str(f.relative_to(root))];assert hashlib.sha256(f.read_bytes()).hexdigest()==override['sha256'];why=override['supplemental_precise_purpose']
 rows.append({'path':str(f.relative_to(root)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'purpose':why})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':rows,'file_count':len(rows),'self_cut':'Exact files existing before writing this inventory; this file and subsequent receipts/postnotes are excluded. Ignored research SDK caches and native binaries are included.','classifier':'artifact_purpose_v14.py','private_external_source_bodies_included':False,'files_modified_by_inventory':False}
with (p/'file-inventory-cut-018.json').open('x') as f:json.dump(out,f,indent=2,ensure_ascii=False);f.write('\n')
print(json.dumps({'files':len(rows),'research_files':sum(x.is_relative_to(p) for x in files)}))
