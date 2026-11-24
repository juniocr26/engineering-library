"""Read frozen prior corpus, apply explicit conditions, retain qualified census."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
OLD=ROOT/'.local-backups/continuation-20261119/go-predeclared-binding-study'
protocol=json.loads((OLD/'protocol.json').read_text())
supplement=json.loads((OLD/'implicit-import-supplement.json').read_text())
controls=json.loads((P/'go-build-context-controls-v1.json').read_text())
if controls['correct']!=controls['n']:raise ValueError('owned context controls not accepted')
context=json.loads((P/'go-build-context-protocol-v1.json').read_text())['context']
files=[];sdk=[];imports=[];origin_paths={}

def load(path,entry):
    raw=path.read_bytes()
    if len(raw)!=entry['bytes']or hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise ValueError('frozen source drift')
    origin_paths[str(path)]=hashlib.sha256(raw).hexdigest()
    return {'path':entry['path'],'source':raw.decode(),'sha256':entry['sha256']}

for entry in protocol['files']:
    item=load(OLD/'sdk-package'/entry['path'],entry);files.append(item);sdk.append(item)
for entry in supplement['closed_import_clause_evidence']:
    group=[]
    for record in entry['files']:
        item=load(OLD/record['preserved'],record);files.append(item);group.append(item)
    imports.append({'import_path':entry['import_path'],'files':group})
packet={'context':context,'files':files};wire=json.dumps(packet,ensure_ascii=False).encode()
output=P/'go-build-context-real-v1';output.mkdir(exist_ok=False)
(output/'request.json').write_bytes(wire)
command=['docker','exec','-i','engineering-library-backend-1','/tmp/el-cont-20261120-build-context-v2/build-artifacts/build-context-linux-arm64']
r=subprocess.run(command,input=wire,capture_output=True,timeout=30)
(output/'stdout.json').write_bytes(r.stdout);(output/'stderr.txt').write_bytes(r.stderr)
if r.returncode:raise ValueError('context observer process failed;outputs preserved')
result=json.loads(r.stdout)
if result['status']!='CONSTRAINT_MATCH_OBSERVATIONS':raise ValueError('real context observation refused;preserve and do not force filter')
selected={item['path']for item in result['files']if item['constraint_match']and item['library_census_input_candidate']}
excluded=[item for item in result['files']if not item['constraint_match']]
if result['matched_import_C_paths']or result['ambiguous_library_package_directories']:
    census={'status':'REFUSED_UNRESOLVED_CGO_OR_MIXED_PACKAGE'}
else:
    filtered={'files':[{k:f[k]for k in ['path','source']}for f in sdk if f['path']in selected],
              'imports':[{'import_path':group['import_path'],'files':[{k:f[k]for k in ['path','source']}for f in group['files']if f['path']in selected]}for group in imports],
              'selected_file':protocol['selected_file'],'function':protocol['selected_function'],'names':protocol['names']}
    prior_binary=OLD/'build-artifacts/census';prior_source=OLD/'main.go'
    if hashlib.sha256(prior_binary.read_bytes()).hexdigest()!='1fa6e9e1c42c0458c6a1abe83b0307aba69a8915faa8a18367507e9c3f81536a' or hashlib.sha256(prior_source.read_bytes()).hexdigest()!='a702c120b40c3ce50afd00db6adaf3a0578496542abe0b1c2e899db14a4aa375':raise ValueError('old qualified census changed')
    request=json.dumps(filtered,ensure_ascii=False).encode();(output/'qualified-census-request.json').write_bytes(request)
    binary='/sources/engineering-library/.local-backups/continuation-20261119/go-predeclared-binding-study/build-artifacts/census'
    cr=subprocess.run(['docker','exec','-i','engineering-library-backend-1',binary],input=request,capture_output=True,timeout=30)
    (output/'qualified-census.stdout.json').write_bytes(cr.stdout);(output/'qualified-census.stderr.txt').write_bytes(cr.stderr)
    census={'process_exit':cr.returncode,'result':json.loads(cr.stdout)if cr.returncode==0 else None,'stderr':cr.stderr.decode()}
unchanged=all(hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest for path,digest in origin_paths.items())
receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'supplied_files':len(files),'original_sdk_files':len(sdk),
         'constraint_matched_files':len(result['matched_paths']),'excluded_files':excluded,
         'selected_library_census_candidates':len(selected),'qualified_census':census,
         'source_inputs_unchanged':unchanged,'request_sha256':hashlib.sha256(wire).hexdigest(),
         'old_generator_preserved':(OLD/'import-clauses/time/src/time/genzabbrs.go').is_file(),
         'source_application_executed':False,'source_packages_compiled':False,'dependency_loading':False,'model_calls':0,
         'status':'CONTEXT_QUALIFIED_SUPPLIED_SOURCE_CENSUS_NOT_FULL_BINDING_PROOF',
         'package_completeness_verified':False,'runtime_predeclared_binding_verified':False,
         'scope_limit':'Build conditions explain prior generator conflict for this declared context. Retained package/import files are supplied evidence, not a full Go-command package closure, type check or universal target proof.'}
(output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'supplied_files':len(files),'matched_files':len(result['matched_paths']),'excluded_paths':[x['path']for x in excluded],
                  'census_exit':census.get('process_exit'),'census_result_keys':list((census.get('result')or{}).keys()),'inputs_unchanged':unchanged}))
