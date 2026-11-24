"""Read-only git-show public development sources; no source program execution."""
import datetime,hashlib,json,re,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
protocol=json.loads((P/'original-faq-remaining-public-protocol-v1.json').read_text());repos={r['repository']:r for r in json.loads((P/'baseline-verification-v1.json').read_text())['repositories']};seen_evidence=set();files={};receipts=[]
def file_refs(node):
 out=[]
 if isinstance(node,dict):
  source=node.get('path',node.get('source_path'));digest=node.get('full_file_sha256',node.get('source_sha256',node.get('sha256')))
  if isinstance(source,str) and isinstance(digest,str) and re.fullmatch('[0-9a-f]{64}',digest):out.append((source,digest))
  for value in node.values():
   if isinstance(value,(dict,list)):out.extend(file_refs(value))
 elif isinstance(node,list):
  for value in node:out.extend(file_refs(value))
 return out
for pair in protocol['pairs']:
 ref=pair['rows'][0]['source_evidence_ref']
 if ref['sha256'] in seen_evidence:continue
 seen_evidence.add(ref['sha256']);raw=(ROOT/ref['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==ref['sha256'];evidence=json.loads(raw);repository=evidence['repository'];revision=evidence['revision'];assert repository in ['fastify','opencv','prometheus','sdk-go','sqlx','starlette'] and re.fullmatch('[0-9a-f]{40}',revision);refs=file_refs(evidence);assert refs
 acquired=[]
 for source,expected in sorted(set(refs)):
  rel=Path(source);assert not rel.is_absolute() and '..' not in rel.parts
  key=(repository,revision,source)
  if key in files:
   row=files[key];assert row['sha256']==expected
  else:
   command=['/opt/homebrew/bin/git','--no-optional-locks','-C',repos[repository]['absolute_path'],'show',revision+':'+source];r=subprocess.run(command,capture_output=True,check=True);assert len(r.stdout)<=2*1024*1024
   target=P/'original-faq-remaining-public-sources-v1'/repository/revision/source;target.parent.mkdir(parents=True,exist_ok=True)
   with target.open('xb') as out:out.write(r.stdout)
   digest=hashlib.sha256(r.stdout).hexdigest();row={'repository':repository,'revision':revision,'source_path':source,'snapshot':str(target.relative_to(ROOT)),'sha256':digest,'expected_sha256':expected,'bytes':len(r.stdout),'source_matches_prior':digest==expected,'command':command,'exit_code':r.returncode};files[key]=row
  acquired.append(row)
 receipts.append({'family':pair['family'],'source_evidence_ref':ref,'source_identity':{'repository':repository,'revision':revision},'files':acquired,'all_source_matches_prior':all(r['source_matches_prior'] for r in acquired)})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'original-faq-remaining-public-protocol-v1.json','source_lineages':len(receipts),'unique_physical_files':len(files),'lineage_file_occurrences':sum(len(r['files']) for r in receipts),'receipts':receipts,'all_source_matches_prior':all(r['source_matches_prior'] for r in files.values()),'no_external_project_execution_or_modification':True,'no_reserve_or_private_source_read':True,'model_calls':0,'optimizer_updates':0,'gold':0}
with (P/'original-faq-remaining-public-source-acquisition-v1.json').open('x') as out:json.dump(result,out,indent=2);out.write('\n')
print(json.dumps({k:v for k,v in result.items() if k!='receipts'},indent=2))
if not result['all_source_matches_prior']:raise SystemExit('Source drift: stop semantic review and preserve evidence')
