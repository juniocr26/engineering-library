"""Observe the real production consumer without replacing its planner."""
import copy,datetime,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sys.path.insert(0,str(ROOT/'agent/tools'))
import documentation_candidates as candidates
import documentation_lifecycle as lifecycle
protocol=json.loads((P/'registered-slugify-real-protocol-v1.json').read_text())
row=protocol['cases'][0];packet=copy.deepcopy(row['packet']);logical=packet['logical_contract_id']
body=(packet['documentation']['en']+'\n').encode()
document=b'# Owned synthetic review document\n\n'+('<!-- documentation-agent:claim:'+logical+':start -->\n').encode()+body+('<!-- documentation-agent:claim:'+logical+':end -->\n').encode()+b'\nHuman context remains here.\n'
replacement={'en':'smart_truncate has a word_boundary parameter.\n','pt-br':'smart_truncate possui parâmetro word_boundary.\n'}
operation={'action':'MODIFY','claim_id':logical,'source_packet':packet,'source_packet_sha256':candidates.packet_sha(packet),'expected_file_sha256':candidates.sha(document),'expected_block_sha256':candidates.sha(body),'replacements':replacement}
try:
 output,trace=candidates.rewrite_owned(document,'en',[operation]);result={'status':'CANDIDATE_RETURNED','trace':trace,'bytes':len(output)}
except candidates.CandidateRefused as error:result={'status':'REFUSED','reason':str(error)}
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Unmodified production rewrite_owned and its imported production decision; no mocking or planner substitution.','source_case':row['id'],'research_registered_recommendation':'MODIFY','production_recommendation':lifecycle.decision(packet),'consumer':result,'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'production_consumer_sha256':hashlib.sha256(Path(candidates.__file__).read_bytes()).hexdigest(),'original_files_written':0,'published':False,'owner_approved':False,'training_gold':False,'claim':'Research declaration results have no current production candidate handoff; refusing an unsupported claim is the correct current boundary.'}
(P/'candidate-consumer-boundary-v1.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,ensure_ascii=False))
