"""Build exact physical callable evidence with the existing verified Go parser."""
import datetime,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT/'agent/tools'));import go_source_ast
fetch=json.loads((P/'humanize-source-fetch-v1.json').read_text());units={};sources={}
selected={'bytes.go':['Bytes','IBytes','ParseBytes','humanateBytes','logn'],'bigbytes.go':['BigBytes','BigIBytes','ParseBigBytes','humanateBigBytes'],'big.go':['oomm','oom'],'comma.go':['BigComma'],'si.go':['ComputeSI','ParseSI','revfmap','init']}
for entry in fetch['files']:
 path=P/entry['path'];raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256'];name=path.name;tag=entry['tag'];sources[tag+':'+name]=entry
 if name not in selected:continue
 batches=[]
 for index in range(0,len(selected[name]),4):
  result=go_source_ast.run(json.dumps({'source':raw.decode(),'path':name,'selectors':selected[name][index:index+4]}).encode())
  assert result['source_executed']is False and result['syntax_only']is True
  batches.extend((unit,result['producer'])for unit in result['units'])
 for unit,producer in batches:
  quote='\n'.join(raw.decode().splitlines()[unit['start_line']-1:unit['end_line']]);assert quote==unit['quote'];key=tag+':'+unit['selector']
  units[key]={'revision':entry['revision'],'source_path':name,'source_snapshot':entry['path'],'source_sha256':entry['sha256'],'first_line':unit['start_line'],'last_line':unit['end_line'],'quote':quote,'quote_sha256':hashlib.sha256(quote.encode()).hexdigest(),'unit':unit,'producer':producer,'physical_quote_verified':True,'complete_callable':True,'runtime_guarantee_from_syntax':False}
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':'dustin/go-humanize','units':units,'sources':sources,'runtime_results':'humanize-confined-runtime-results-v1.json','runtime_results_sha256':hashlib.sha256((P/'humanize-confined-runtime-results-v1.json').read_bytes()).hexdigest(),'training_excluded':True,'owner_approved':False,'source_parser_executes_subject':False}
with(P/'humanize-source-pack-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'units':len(units),'sources':len(sources)})
