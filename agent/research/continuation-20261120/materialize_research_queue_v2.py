"""Rebuild current queue from immutable task catalogs and all event key forms."""
import collections,datetime,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
base=json.loads((P/'research-queue-v1.json').read_text());tasks={r['id']:r for r in base['tasks']};catalogs=['research-queue-v1.json']
for path in sorted(P.glob('research-queue-extension-v*.json')):
 catalogs.append(path.name)
 for row in json.loads(path.read_text())['tasks']:
  if row['id']in tasks:raise ValueError('duplicate task identity')
  tasks[row['id']]=row
lines=(P/'queue-events.jsonl').read_text().splitlines();non_task=[]
for index,line in enumerate(lines,1):
 event=json.loads(line)
 if 'id'in event and'task'in event and event['id']!=event['task']:raise ValueError('conflicting event identity fields')
 identity=event.get('id',event.get('task'))
 if identity not in tasks:non_task.append({'event_line':index,'event':event});continue
 row=tasks[identity];raw=event['state']
 if raw.startswith('COMPLETED')or raw in ['BOUNDED_MODULE_FACT_AND_TYPED_MAPPING_PROTOTYPES_IMPLEMENTED','FIVE_REDUNDANT_LIVE_REPORTS_MIGRATED_WITH_EXACT_HISTORY_AND440FILE_OLD_RECOVERY_PROOF']:state='COMPLETED'
 elif raw in ['PENDING','PARTIAL','ACTIVE','BLOCKED']:state=raw
 else:state='PARTIAL'
 row.update(state=state,latest_event=event,latest_event_line=index)
path=P/'research-queue-current.json';previous=path.read_bytes()if path.exists()else None
if previous:
 backup=ROOT/'.local-backups/continuation-20261120/queue-history';backup.mkdir(parents=True,exist_ok=True);dest=backup/(hashlib.sha256(previous).hexdigest()+'.json')
 if not dest.exists():dest.write_bytes(previous)
record={k:v for k,v in base.items()if k!='tasks'};record.update(as_of=datetime.datetime.now(datetime.timezone.utc).isoformat(),tasks=list(tasks.values()),baseline_queue_preserved=True,catalogs=catalogs,event_lines_consumed=len(lines),event_identity_keys_supported=['id','task'],non_task_events=non_task,state_counts=dict(collections.Counter(r['state']for r in tasks.values())),materializer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),event_log_sha256=hashlib.sha256((P/'queue-events.jsonl').read_bytes()).hexdigest(),previous_materialization_sha256=hashlib.sha256(previous).hexdigest()if previous else None)
path.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'tasks':len(tasks),'event_lines_consumed':len(lines),'state_counts':record['state_counts'],'unexplained_active_tasks':[r['id']for r in tasks.values()if r['state']=='ACTIVE']}))
