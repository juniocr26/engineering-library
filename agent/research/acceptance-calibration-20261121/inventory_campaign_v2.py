"""Per-file purpose/hash inventory of the authorized campaign cut."""
import argparse,collections,datetime,hashlib,json,os
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--version',required=True,type=int);args=parser.parse_args()
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def purpose(path):
    parts=path.parts;name=path.name
    if 'root-report-preimages' in str(path) or name.endswith(('.prior.bin','preimage-v1.bin')):return 'Exact historical root-report bytes retained before authorized append'
    if 'checkpoint-' in str(path):return 'Point-in-time archive, member manifest or redundant verified recovery receipt'
    if any(part in parts for part in ['frozen-public-sources','chapter-context-source-v1','original-faq-source-reacquisition-v1','original-faq-expansion-sources-v1']):return 'Pinned public upstream source/license snapshot; read as text, not an executed research script'
    if any(part in parts for part in ['scope-acquisition-v1','scope-acquisition-v2']):return 'Owned lexical source-scope control or its observation; source text never executed'
    if 'cached-helper-job-seam-v1' in parts and 'source' in parts:return 'Owned Go source text for native-parser observation; program never executed'
    if name=='request.json':return 'Frozen bounded public-source inference request; not a training example'
    if name=='raw-response.json':return 'Original local model HTTP response bytes, including failures; no correction'
    if name=='model-content.txt':return 'Exact original generated model text; not a human-facing campaign report or correct target'
    if name in ['outcome.json','started.json','process.json']:return 'Worker identity, attempt status, timing/digest and terminal boundary evidence'
    if name.startswith('semantic-review'):return 'Source-grounded same-agent judgments over unchanged original output; not owner approval'
    if name.endswith('.py'):return 'Versioned isolated research observer/renderer/annotation/recovery script; not production or permanent test'
    if name.endswith(('.log','.stderr','.stdout','.jsonl')):return 'Preserved restricted runtime/test/event observation; no public upload'
    if 'snapshot' in name or 'sources' in str(path) or 'source-v1' in str(path):return 'Pinned public source bytes or owned source-only control; not upstream execution'
    if 'cached-helper-job-seam-v1' in parts:return 'Owned isolated helper/job journal, immutable delivery body, seed/preimage or case observation'
    if 'scope-acquisition' in str(path):return 'Owned finite source-scope control and lifecycle observation; no real code removal'
    if 'protocol' in name or 'freeze' in name:return 'Preregistered question/reference/decision boundary or implementation hash freeze'
    if 'inventory' in name:return 'Earlier retained file/hash/purpose inventory with explicit cut'
    if 'recovery' in name:return 'Actual archive/restore/hash receipt or recovery-cut policy evidence'
    if name.endswith('.bin'):return 'Exact preserved preimage bytes; no active model weights or adapter'
    if name.endswith('.json'):return 'Machine-readable source/claim/dataset/resource/acceptance state or versioned result'
    if name=='authorized-request.txt':return 'Exact copied owner campaign instruction attachment'
    return 'Preserved technical campaign evidence; not a production or active-catalog change'
entries=[];pending=[]
roots=[P,ROOT/'.local-backups/acceptance-calibration-20261121']
for base in roots:
    for f in sorted(base.rglob('*')):
        rel=f.relative_to(ROOT).as_posix()
        if f.is_symlink():entries.append({'path':rel,'kind':'symlink','target':os.readlink(f),'target_text_sha256':hashlib.sha256(os.readlink(f).encode()).hexdigest(),'purpose':'Owned dangling-link acquisition control; target never followed','stable_at_cut':True});continue
        if not f.is_file():continue
        terminal=True
        if (f.parent/'started.json').exists():
            try:terminal='ended_at' in json.loads((f.parent/'outcome.json').read_text())
            except (OSError,ValueError):terminal=False
        stable=terminal or f.name in ['request.json','started.json','process.json']
        row={'path':rel,'kind':'file','bytes':f.stat().st_size,'purpose':purpose(f),'stable_at_cut':stable}
        if stable:row['sha256']=sha(f)
        else:pending.append(rel);row['hash_deferred_until_terminal']=True
        entries.append(row)
reports=[]
for name in ['AI_TRAINING_CAMPAIGN_REPORT.md','AI_TRAINING_FILE_INVENTORY.md','AI_FINE_TUNING_READINESS.md','AI_TRAINING_RESUME.md']:
 f=ROOT/name;reports.append({'path':name,'bytes':f.stat().st_size,'sha256':sha(f),'purpose':'Canonical authorized human-facing root report; prior bytes preserved before each append'})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':args.version,'entries':entries,'technical_file_count':sum(e['kind']=='file' for e in entries),'technical_symlink_count':sum(e['kind']=='symlink' for e in entries),'technical_regular_bytes':sum(e.get('bytes',0) for e in entries),'canonical_root_reports':reports,'open_worker_files':pending,'self_cut':'This new inventory excludes itself and any subsequent report append/checkpoint/state file. Root hashes are exact at this cut, not future final-report hashes. Open worker raw/stderr have no stable hash until terminal. Historical inventory files remain unchanged.','classification':'RESTRICTED_INTERNAL_LOCAL_ONLY; contains local paths and proprietary own-repository proposal source quotes; no public upload/training transfer','preexisting_production_test_or_internal_doc_changes':0,'deleted_historical_files':0,'gold':0,'optimizer_updates':0}
with (P/('file-inventory-v%d.json'%args.version)).open('x') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['entries','canonical_root_reports']},indent=2))
