from pathlib import Path
import json,hashlib,datetime,importlib.util,tempfile,shutil
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();cpfile=p/'checkpoint-040.json';raw=cpfile.read_bytes();cp=json.loads(raw);folder=(root/cp['archive']).parent;assert (folder/'receipt.json').read_bytes()==raw;rest=Path(cp['restored_root']);manifest=json.loads((root/cp['input_manifest']).read_text());expected={e['path']:e for e in manifest};script=rest/'agent/research/final-intensive-20261121/append_checkpoint_report_note_v22.py';assert sha(script.read_bytes())==expected[str(script.relative_to(rest))]['sha256'];spec=importlib.util.spec_from_file_location('archived_note040',script);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
late=p/'root-report-bundle-progress-055';plan=json.loads((late/'plan.json').read_text());assert plan['original_root']==str(root);edges={e['path']:e for e in plan['reports']};note=mod.make_note(cp)+b'\nReconstrucao especifica do checkpoint040: entre o corte e esta nota, progresso055 foi acrescentado. O bundle055 completo foi preservado como sidecar adicional; os relatÃ³rios finais foram reconstruÃ­dos como prefixo arquivado + payload055 + esta nota, com hashes e bytes conferidos. A recusa inicial por diferenca de prefixo foi preservada.\n'
sidecar=folder/'late-root-report-bundle-progress-055';sidecar.mkdir();copied=[]
for f in sorted(late.iterdir()):
 assert f.is_file() and not f.is_symlink();blob=f.read_bytes();dest=sidecar/f.name
 with dest.open('xb') as stream:stream.write(blob)
 copied.append({'path':str(dest.relative_to(root)),'sha256':sha(blob)})
reconstructed=Path(tempfile.mkdtemp(prefix='el-report-reconstruction-040-late-',dir='/private/tmp'));candidates=[]
for name in REPORTS:
 archived=(rest/name).read_bytes();before=(late/(name+'.before.bin')).read_bytes();payload=(late/(name+'.append.bin')).read_bytes();e=edges[name];assert sha(archived)==expected[name]['sha256'] and archived==before;assert sha(before)==e['before_sha256'] and sha(payload)==e['payload_sha256'];current=(root/name).read_bytes();assert archived+payload==current and sha(current)==e['after_sha256'];rebuilt=archived+payload+note
 with (reconstructed/name).open('xb') as stream:stream.write(rebuilt)
 candidates.append({'path':name,'before_sha256':sha(current),'after_sha256':sha(rebuilt),'append_only':True})
j=p/'root-report-bundle-checkpoint-040-late-note';prepare(root,j,{n:note for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
for n in REPORTS:assert (root/n).read_bytes()==(reconstructed/n).read_bytes()
d={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checkpoint':40,'source_receipt_sha256':sha(raw),'archived_script_sha256':sha(script.read_bytes()),'note_sha256':sha(note),'note_utf8':note.decode(),'reconstructed_root':str(reconstructed),'reports':candidates,'exact_final_reports_reconstructed':4,'late_append_sidecar':copied,'late_plan_sha256':sha((late/'plan.json').read_bytes()),'bundle_application':out,'reconstruction_inputs':'Archived report prefixes + extra preserved bundle055 sidecar payloads/plan/preimages/attempt receipts + archivedv22make_note + checkpointreceipt; late supplementalproducerhash below. Not archive+receiptalone.','supplemental_producer_sha256':sha(Path(__file__).read_bytes()),'initial_failure':'v22guard refused currentroot!=archivedcut beforewriting; failedemptytemp reconstruction retained; nofalsepostnotereceipt','campaign_active':True,'neural_calls':0,'gold':0}
for f in [p/'root-report-checkpoint-040-postnote-v1.json',folder/'final-report-reconstruction-receipt-v1.json']:
 with f.open('x') as stream:json.dump(d,stream,indent=2);stream.write('\n')
print(json.dumps({'checkpoint':40,'reports_reconstructed':4,'late_bundle055_preserved':len(copied),'initial_guard_failure_preserved':True}))
