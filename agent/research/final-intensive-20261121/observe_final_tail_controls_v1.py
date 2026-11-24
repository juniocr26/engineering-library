from pathlib import Path
import json,hashlib,datetime,importlib.util,copy
P=Path(__file__).resolve().parent;source=P/'consume_weekend_capsule_v5.py';spec=importlib.util.spec_from_file_location('owned_final_bootstrap',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);sha=lambda b:hashlib.sha256(b).hexdigest();folder=P/'owned-final-tail-controls-v1';folder.mkdir(mode=0o700,exist_ok=False);cases=[('intact',None),('wrong-source','FINAL_TAIL_SOURCE_BINDING_MISMATCH'),('wrong-before-last','FINAL_TAIL_BEFORE_OR_PAYLOAD_MISMATCH'),('wrong-payload','FINAL_TAIL_BEFORE_OR_PAYLOAD_MISMATCH'),('wrong-after-last','FINAL_TAIL_AFTERHASH_MISMATCH'),('wrong-report-path','FINAL_TAIL_REPORT_SET_MISMATCH')];protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_outcomes':True,'role':'TEST_ONLY_STRUCTURAL_FOUR_REPORT_FINAL_TAIL_PREFLIGHT_CONTROLS','source_sha256':sha(source.read_bytes()),'cases':[{'id':n,'expected_error':e} for n,e in cases],'no_production_or_canonical_report_mutation':True,'not_atomic_powerloss_or_diskfailure_proof':True}
with (P/'final-tail-controls-protocol-v1.json').open('x') as f:json.dump(protocol,f,indent=2);f.write('\n')
rows=[]
for name,expected in cases:
 base=folder/name;base.mkdir(mode=0o700);entries=[];original={}
 for report in m.REPORTS:
  raw=('OWNED_STRUCTURAL_CONTROL '+report+'\n').encode();payload=b'APPEND_CONTROL\n';(base/report).write_bytes(raw);original[report]=raw;entries.append({'path':report,'before_sha256':sha(raw),'payload_sha256':sha(payload),'after_sha256':sha(raw+payload),'append_utf8':payload.decode()})
 tail={'checkpoint':54,'source_checkpoint_receipt_sha256':'receipt-control','source_postnote_sha256':'postnote-control','reports':entries}
 if name=='wrong-source':tail['source_checkpoint_receipt_sha256']='wrong'
 elif name=='wrong-before-last':entries[-1]['before_sha256']='0'*64
 elif name=='wrong-payload':entries[0]['payload_sha256']='0'*64
 elif name=='wrong-after-last':entries[-1]['after_sha256']='0'*64
 elif name=='wrong-report-path':entries[-1]['path']='../escape.md'
 actual=None;count=None
 try:count=m.apply_final_tail(base,tail,54,'receipt-control','postnote-control')
 except ValueError as e:actual=str(e)
 assert actual==expected
 if expected:assert all((base/n).read_bytes()==raw for n,raw in original.items())
 else:assert count==4 and all((base/n).read_bytes()==raw+b'APPEND_CONTROL\n' for n,raw in original.items())
 rows.append({'id':name,'expected_error':expected,'actual_error':actual,'reports_appended':count or 0,'all_preimages_unchanged_on_refusal':bool(expected),'matched':True})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha((P/'final-tail-controls-protocol-v1.json').read_bytes()),'source_sha256':sha(source.read_bytes()),'cases':rows,'matched_controls':6,'normal_four_report_append':1,'negative_refusals_before_any_write':5,'canonical_root_reports_modified':0,'model_calls':0,'training_approval':False,'scope':'Syntheticownedpreflight/refusalcontrols; no realcampaignreportrewrite,notfourfileatomicity,powerloss/securityorcleanmachineproof.'}
with (P/'final-tail-controls-results-v1.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['cases','scope']}))
