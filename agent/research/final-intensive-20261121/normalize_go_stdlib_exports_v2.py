"""Normalize actual offline SDK export closure, retaining the intrinsic unsafe node."""
from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).resolve().parent;ROOT=P.parents[2];folder=P/'go-stdlib-export-closure-v1';raw=(folder/'stdout.json-stream').read_text();dec=json.JSONDecoder();at=0;records=[];intrinsics=[]
while at<len(raw):
 while at<len(raw) and raw[at].isspace():at+=1
 if at==len(raw):break
 item,at=dec.raw_decode(raw,at);assert item.get('Standard') is True,item.get('ImportPath')
 if not item.get('Export'):
  assert item['ImportPath']=='unsafe';intrinsics.append({'import_path':'unsafe','kind':'COMPILER_INTRINSIC_NO_EXPORT_FILE','standard':True});continue
 export=Path(item['Export']);assert export.is_file();relative=str(export.relative_to(ROOT));records.append({'import_path':item['ImportPath'],'export_path':relative,'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'export_bytes':export.stat().st_size,'standard':True,'module':item.get('Module'),'directory':item['Dir'],'go_files':item.get('GoFiles',[]),'imports':item.get('Imports',[])})
manifest={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'toolchain':'Go1.27.1darwinarm64','original_root':str(ROOT),'records':records,'compiler_intrinsics':intrinsics,'package_count':len(records)+len(intrinsics),'export_file_count':len(records),'all_standard':True,'scope':'SDK standard library compiled export closure, not manual semantic review or project dependency installation.'}
with (folder/'manifest-v2.json').open('x') as f:json.dump(manifest,f,indent=2);f.write('\n')
print(json.dumps({'packages':manifest['package_count'],'exports':len(records),'intrinsics':intrinsics,'export_bytes':sum(r['export_bytes'] for r in records)}))
