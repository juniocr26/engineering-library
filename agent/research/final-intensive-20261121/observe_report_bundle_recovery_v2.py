"""Controlled interruption observations on owned report copies; never mutate canonical reports."""
from pathlib import Path
import datetime,hashlib,json,argparse
from report_bundle_append_v1 import REPORTS,prepare,apply,canonical,sha
parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output-root',type=Path,required=True);args=parser.parse_args();P=args.root.resolve()/'agent/research/final-intensive-20261121';folder=args.output_root.resolve();folder.mkdir(mode=0o700)
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Four owned files per case, exact canonical names but synthetic content; no actual report mutation. Controlled interruption, not process kill/host crash or arbitrary concurrent-writer proof.','cases':[{'id':'intact-and-repeat','first':'APPLIED_OR_ALREADY_APPLIED','second':'APPLIED_OR_ALREADY_APPLIED'},{'id':'between-reports','first':'OWNED_INTERRUPTION','second':'APPLIED_OR_ALREADY_APPLIED'},{'id':'partial-UTF8-bytes','first':'OWNED_INTERRUPTION','second':'APPLIED_OR_ALREADY_APPLIED'},{'id':'foreign-state-refusal','first':'REFUSED','second':None}],'prototype_sha256':sha((P/'report_bundle_append_v1.py').read_bytes()),'expected_invariants':['Preserve every original byte as prefix','Write planned payload exactly once on completed/recovered cases','Accept expected partial payload bytes without decoding/replacing historical content','Reject foreign state before modifying any report','Preserve every plan/preimage/payload/attempt receipt'],'no_new_model_calls':True}
(folder/'protocol.json').write_bytes(canonical(protocol));observations=[]
for case in protocol['cases']:
 base=folder/case['id'];base.mkdir(mode=0o700);root=base/'owned-reports';root.mkdir(mode=0o700);journal=base/'journal';before={name:('Owned original '+name+'\n').encode() for name in REPORTS};payloads={name:'\nEvidência própria — operação de pesquisa.\n'.encode() for name in REPORTS}
 for name in REPORTS:(root/name).write_bytes(before[name])
 prepare(root,journal,payloads)
 if case['id']=='foreign-state-refusal':
  with (root/REPORTS[-1]).open('ab') as f:f.write(b'FOREIGN-UNPLANNED\n')
 initial={n:(root/n).read_bytes() for n in REPORTS};kwargs={}
 if case['id']=='between-reports':kwargs={'owned_stop_after_reports':2}
 if case['id']=='partial-UTF8-bytes':kwargs={'owned_stop_after_bytes':6}
 first=apply(root,journal,**kwargs);after_first={n:(root/n).read_bytes() for n in REPORTS};second=apply(root,journal) if case['second'] else None;after={n:(root/n).read_bytes() for n in REPORTS}
 preserved=all(after[n].startswith(before[n]) for n in REPORTS);final_planned=all(after[n]==before[n]+payloads[n] for n in REPORTS) if second else None;foreign_no_changes=all(after[n]==initial[n] for n in REPORTS) if second is None else None
 matched=first['status']==case['first'] and (second is None or second['status']==case['second']) and preserved and (final_planned if second else foreign_no_changes)
 observations.append({'case':case['id'],'first':first,'second':second,'original_bytes_preserved':preserved,'final_planned_exact_once':final_planned,'foreign_state_no_modifications':foreign_no_changes,'first_report_partial_hex':after_first[REPORTS[0]][len(before[REPORTS[0]]):].hex() if case['id']=='partial-UTF8-bytes' else None,'final_sha256':{n:sha(raw) for n,raw in after.items()},'matched':matched})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha((folder/'protocol.json').read_bytes()),'observations':observations,'matched_cases':sum(r['matched'] for r in observations),'cases':len(observations),'actual_reports_mutated':False,'process_crash_tested':False,'neural_calls':0,'semantic_accuracy_metric':None}
(folder/'results.json').write_bytes(canonical(result));print(json.dumps({k:v for k,v in result.items() if k!='observations'}));assert all(r['matched'] for r in observations)
