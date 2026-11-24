"""Same original eight packet fields/text; post-exposure closed-grammar research."""
import datetime,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent;OLD=P.parent/'documentation-intelligence-20261120'
spec=importlib.util.spec_from_file_location('boltons_keyword_router',P/'closed_keyword_lifecycle_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
oracle=json.loads((OLD/'public-lifecycle-oracle-v1.json').read_text());rows=[]
for case in oracle['cases']:
 original=json.loads((OLD/'public-lifecycle-results-v1'/(case['id']+'.json')).read_text())['input'];original_hash=hashlib.sha256(m.canonical(original)).hexdigest();result=m.decision(original)
 assert result.get('original_packet_sha256',original_hash)==original_hash
 rows.append({'id':case['id'],'expected':case['expected_action'],'actual':result['action'],'matches':result['action']==case['expected_action'],'original_packet_sha256':original_hash,'original_fields_and_documentation_unchanged':True,'result':result})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'correct':sum(r['matches']for r in rows),'n':len(rows),'classification':'POST_EXPOSURE_CLOSED_GRAMMAR_DEVELOPMENT_NOT_INDEPENDENT_GAIN_OR_PRODUCTION_INTEGRATION','previous_natural_closed_declaration_score':'3/8','original_frozen_production_score_unchanged':'0/8 allINCONCLUSIVE','source_executed_by_this_router':False,'typed_annotations_added_to_input':False,'new_fields_added_to_original_packets':False,'original_frozen_oracle_sha256':hashlib.sha256((OLD/'public-lifecycle-oracle-v1.json').read_bytes()).hexdigest(),'permanent_tests_or_production_planner_changed':False,'training_excluded':True,'automatic_candidate_applier_supported':False}
with(P/'boltons-keyword-router-development-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print(json.dumps({'correct':record['correct'],'n':len(rows),'actions':[(r['id'],r['actual'])for r in rows]}))
