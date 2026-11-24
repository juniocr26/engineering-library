"""Metadata-only controls; no inspected source execution occurs."""
import argparse,copy,datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('version',choices=['1','2']);args=parser.parse_args()
 spec=importlib.util.spec_from_file_location('execution_candidate',P/('registered_claim_candidate_v'+args.version+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 pre=json.loads(Path('/private/tmp/el-claim-candidate-controls-20261120-v1/valid-paired-modify/exact-control-preimage.json').read_text());rows=[]
 for id,value in [('delegate-reports-source-executed',True),('delegate-source-execution-unknown',None),('delegate-source-execution-flag-string','false')]:
  c=m.RegisteredClaimCandidate(pre['registration']);original=c.source_binding.decide
  def delegate(packet):
   result=original(packet);result['source_executed']=value;return result
  c.source_binding.decide=delegate;result=c.prepare(copy.deepcopy(pre['packet']),copy.deepcopy(pre['replacements']),pre['requested_action']);matches=result['status']=='REFUSED'and result['source_executed']is None
  rows.append({'id':id,'matches':matches,'result':result,'metadata_only_simulation':True,'actual_inspected_source_executed':False})
 record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':args.version,'rows':rows,'correct':sum(r['matches']for r in rows),'n':len(rows),'new_model_calls':0,'source_executed':False,'production_changes':False}
 with(P/('claim-execution-uncertainty-v'+args.version+'.json')).open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
 print(json.dumps({'correct':record['correct'],'n':len(rows),'observed_flags':[r['result']['source_executed']for r in rows]}))
