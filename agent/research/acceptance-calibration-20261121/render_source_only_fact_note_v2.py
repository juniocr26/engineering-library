"""Frozen mixed-source-note renderer: original K strings only after full source gate."""
import argparse,datetime,hashlib,json
from pathlib import Path
from frozen_schema_subset_v2 import validate,unique_object
P=Path(__file__).resolve().parent
protocol=json.loads((P/'source-only-fact-render-protocol-v1.json').read_text())
refs={r['claim_id']:r for r in json.loads((P/'atomic-reference-ledger-v2.json').read_text())['claims']}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def verify_sources(task):
    rows=[]
    for cid in protocol['metadata'][task]['required_ids']:
        ref=refs[cid];source=P/'frozen-public-sources'/task/ref['source_path'];raw=source.read_bytes()
        assert sha(raw)==ref['source_file_sha256'],cid
        assert ref['exact_source_evidence'] in raw.decode(),cid
        rows.append({'id':cid,'source_path':ref['source_path'],'source_sha256':sha(raw),'source_lines':ref['source_lines']})
    return rows
parser=argparse.ArgumentParser();parser.add_argument('--task',choices=['fastapi','cobra','zod']);parser.add_argument('--preflight-sources-only',action='store_true');args=parser.parse_args()
if args.preflight_sources_only:
    print(json.dumps({t:verify_sources(t) for t in protocol['metadata']},indent=2));raise SystemExit(0)
if not args.task:raise SystemExit('--task is required for rendering')
task=args.task;folder=P/'source-only-fact-render-v1'/task/'L';metadata=protocol['metadata'][task];reasons=[];content=None;review=None;digest=None
source_checks=verify_sources(task)
try:
    raw=(folder/'model-content.txt').read_bytes();digest=sha(raw);content=json.loads(raw,object_pairs_hook=unique_object)
    schema=json.loads((folder/'request.json').read_text())['format'];errors=validate(content,schema)
    if errors:reasons.append({'structural_schema_errors':errors})
    review=json.loads((folder/'semantic-review-v2.json').read_text())
    if review.get('content_sha256')!=digest:reasons.append('Review does not bind exact original generated content')
    for key in ['all_generated_claims_reviewed','all_required_claims_covered','bilingual_semantics_correct']:
        if review.get(key) is not True:reasons.append('Gate requires '+key)
    if review.get('critical_unsupported_claims')!=0:reasons.append('Critical unsupported claim remains or count unknown')
    if review.get('source_only_semantic_admission') is not True:reasons.append('Source-only semantic admission not established')
    if sorted(review.get('required_ids_correct',[]))!=sorted(metadata['required_ids']):reasons.append('Correct required-ID set incomplete')
except (OSError,ValueError,TypeError,KeyError) as e:reasons.append(type(e).__name__+': '+str(e))
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'task':task,'method':'L','protocol':'source-only-fact-render-protocol-v1.json','original_content_sha256':digest,'source_integrity':source_checks,'status':'REFUSED_INCOMPLETE_OR_UNSUPPORTED' if reasons else 'ASSEMBLED_PENDING_COMPLETE_DIMENSION_REVIEW','refusal_reasons':reasons,'owner_approved':False,'training_gold':False,'optimizer_updates':0,'authorship':'Neural source-extracted strings copied verbatim into the assembled note; deterministic manually frozen metadata/citations/FAQ reuse. Source/exposed-task research only.'}
if not reasons:
    notes={}
    for lang in ['en','pt-BR']:
        facts=content['facts'];parts=[metadata['scope'][lang],metadata['error_boundaries'][lang]]
        for cid in metadata['required_ids']:
            ref=refs[cid];parts.append(cid+': '+facts[cid][lang]);parts.append('Source: '+ref['source_path']+':'+str(ref['source_lines'])+' @ '+ref['source_revision'])
        parts.extend([metadata['faq_question'][lang],facts[metadata['faq_fact_id']][lang],metadata['limitations'][lang]])
        notes[lang]='\n\n'.join(parts)+'\n'
    result['notes']=notes;result['neural_strings_unchanged']=True;result['faq_answer_reuses_exact_neural_fact']=metadata['faq_fact_id'];result['deterministic_uncertainty_not_neural_abstention_credit']=True
with (folder/'rendered-note-v2.json').open('x') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['notes','source_integrity']},indent=2))
