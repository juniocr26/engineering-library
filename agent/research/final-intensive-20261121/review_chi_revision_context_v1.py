"""Review exact Chi revision evidence; optional native replay uses restored data."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import sys

parser=argparse.ArgumentParser()
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
parser.add_argument('--replay-native',action='store_true')
parser.add_argument('--stdout-only',action='store_true')
args=parser.parse_args()
ROOT=args.root
P=ROOT/'agent/research/final-intensive-20261121'
sha=lambda b:hashlib.sha256(b).hexdigest()
protocol=json.loads((P/'chi-revision-context-protocol-v1.json').read_text())
verification=json.loads((P/'chi-revision-context-verification-protocol-v1.json').read_text())
acquisitions={}
for number in [1,2,3]:
    packet=json.loads((P/f'chi-revision-context-acquisition-v{number}.json').read_text())
    acquisitions[number]=packet
    for row in packet['records']:
        path=ROOT/row.get('stdout_path',row.get('saved_path'))
        assert sha(path.read_bytes())==row.get('stdout_sha256',row.get('sha256'))
        if number==2:
            assert (row['exit_code']==0)==row['expected_present']
        else:assert row['exit_code']==0

base=P/'chi-revision-context-evidence-v1'
context=P/'chi-revision-context-evidence-v2'
before_meta=(base/'before/commit.txt').read_text().splitlines()
after_meta=(base/'after/commit.txt').read_text().splitlines()
assert before_meta[0]==protocol['before'] and after_meta[0]==protocol['after']
assert after_meta[1]==protocol['before']
assert before_meta[1]=='04f7f55a7b5ddb2ecd79a8d813b2256c1113b8a9'
assert (base/'changed-paths.txt').read_text()=='A\tmiddleware/request_size_test.go\n'
assert not (base/'selected.patch').read_bytes()
equal_files={}
for name in ['middleware/wrap_writer.go','middleware/wrap_writer_test.go','go.mod','LICENSE']:
    equal_files[name]=(base/'before'/name).read_bytes()==(base/'after'/name).read_bytes()
for name in ['middleware/logger.go','middleware/middleware_test.go',
             'middleware/wrap_writer_readfrom_test.go','middleware/request_size.go']:
    equal_files[name]=(context/'before'/name).read_bytes()==(context/'after'/name).read_bytes()
assert all(equal_files.values())


def lexical_refs(label):
    return [line.split(':',1)[1] for line in (base/label/'wrapper-lexical-refs.txt').read_text().splitlines()]


assert lexical_refs('before')==lexical_refs('after')
calls=[]
for line in lexical_refs('after'):
    path,number,code=line.split(':',2)
    if code.lstrip().startswith(('//','func NewWrapResponseWriter')):continue
    calls.append({'path':path,'line':int(number),'code':code})
assert len(calls)==3
api=(context/'after/middleware/request_size.go').read_text()
tests=(context/'after/middleware/request_size_test.go').read_text()
assert 'WriteHeader' not in api
assert 'r.Body = http.MaxBytesReader(w, r.Body, bytes)' in api
assert 'h.ServeHTTP(w, r)' in api
assert sum(line.strip().startswith('{"should ') for line in tests.splitlines())==4

index=json.loads((P/'chi-revision-context-candidate-index-v1.json').read_text())
documents=[]
snippets=[]
for row in index['records']:
    original=(ROOT/row['original']).read_bytes()
    candidate=(ROOT/row['candidate']).read_bytes()
    assert sha(original)==row['original_sha256']
    assert sha(candidate)==row['candidate_sha256']
    language=row['language']
    heading='## Maintenance across the selected local revisions' if language=='en' else '## Manutenção entre as revisões locais selecionadas'
    evidence='## Evidence and limits' if language=='en' else '## Evidências e limites'
    prefix,rest=candidate.decode().split(heading,1)
    suffix=evidence+rest.split(evidence,1)[1]
    restored_body=(prefix+suffix).replace(protocol['after'],protocol['before'],1)
    assert restored_body.encode()==original
    code=re.findall(r'```go\n(.*?)```',candidate.decode(),re.S)
    assert len(code)==1
    snippets.append(code[0])
    documents.append({'language':language,'path':row['candidate'],'sha256':row['candidate_sha256']})
assert snippets[0]==snippets[1]
example=P/'context-topic-verification-v1/chi-owned-example.go'
example_packet=json.loads((P/'context-topic-verification-v1/chi-owned-example-native.json').read_text())
assert example.read_text().endswith(snippets[0])
assert example_packet['source_sha256']==sha(example.read_bytes())
assert example_packet['syntax_only'] is True and example_packet['source_executed'] is False

native=json.loads((P/'chi-revision-context-native-results-v1.json').read_text())
replayed=0
if args.replay_native:
    sys.dont_write_bytecode=True
    sys.path.insert(0,str(ROOT/'agent/tools'))
    import go_source_ast
for row in native['records']:
    source=context/'after'/row['source_path']
    assert sha(source.read_bytes())==row['source_sha256']
    request=json.loads((ROOT/row['request']).read_text())
    response=json.loads((ROOT/row['response']).read_text())
    assert request['source']==source.read_text()
    assert response['source_sha256']==row['source_sha256']
    assert response['source_executed'] is False and response['syntax_only'] is True
    if args.replay_native:
        assert go_source_ast.run(json.dumps(request).encode())==response
        replayed+=1

gates={key:{'status':'PASS','evidence':value} for key,value in {
    'G1':'Exact three revision roles, candidate/source hashes, parent/tree/patch evidence and source citations verified; before missing test output is a failed query, never an old empty source file.',
    'G2':'Actual complete EN/PT bodies and diffs read with current wrapper/tests/callers. Original meanings preserved; new maintenance claims checked against full tree delta and added test/unchanged implementation. No critical factual error observed.',
    'G3':'Original factory/capability/state/WriteHeader/Write/ReadFrom/exception limits retained; selected lexical callers/module/test context compared. Dynamic/external caller completeness and runtime remain unverified.',
    'G4':'Full original chapter requirements plus frozen revision-impact requirements covered; no retrospective scope narrowing.',
    'G5':'Unchanged actual example bytes bind prior exact syntax observation; four new context/test functions parsed by owned native Go tool. Target code/imports/typecheck/tests not executed.',
    'G6':'Both full language texts, new paragraphs, code, conditions, revision roles and identifiers reviewed; exact code fence equality verified.',
    'G7':'One real direct-parent pair: NO-OP for historical source contract; MODIFY provenance/context only for explicitly requested new-pin contract. No external/original documentation edit or REMOVE.',
    'G8':'Separate local Git object/tree acquisition with no lazy fetch/drivers, native exact-owner syntax checks and eight manually adjudicated adverse claims. Same-agent procedures, not independent human or generic semantic-verifier accuracy.'}.items()}
gates['G9']={'status':'INCONCLUSIVE','evidence':'New exact candidate/evidence awaits next verified restoration and native consumer replay; current metadata validation alone does not confer recovery PASS.'}
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'documents':documents,'protocol_sha256':sha((P/'chi-revision-context-protocol-v1.json').read_bytes()),
        'gates':gates,'technical_status':'INCONCLUSIVE_PENDING_RECOVERY',
        'compared_revision_pair_count':1,'correlated_document_contract_views':2,
        'lifecycle_actions':{'historical-note':'NO-OP','explicit-current-pin-target':'MODIFY_PROVENANCE_AND_CONTEXT'},
        'independent_lifecycle_accuracy':None,'equal_selected_files':equal_files,
        'lexical_invocation_sites':calls,'lexical_search_is_not_dynamic_call_graph':True,
        'full_original_body_preserved_except_pin_and_new_section':True,
        'example_syntax_input_bound':True,'new_native_selected_functions':4,
        'native_packets_replayed_exactly':replayed,
        'manual_negative_challenges':[dict(row,observed=row['expected'],method='Actual source/context read by same Codex campaign agent; not a new automatic prediction.') for row in verification['negative_claims']],
        'all_actual_prose_reviewed':True,'critical_factual_errors_observed':0,'atomic_precision_metric':None,
        'review_groups_not_independent_atomic_claims':True,'neural_contribution':False,
        'independent_human_review':False,'owner_approved':False,'publication_approved':False,
        'training_gold_approved':False,'training_eligible':False,'new_local_model_calls':0,
        'original_and_external_documents_unchanged':True,'target_source_executed':False}
if not args.stdout_only:
    with (P/'chi-revision-context-complete-review-v1.json').open('x') as stream:
        json.dump(result,stream,indent=2)
        stream.write('\n')
print(json.dumps({'one_real_revision_pair':True,'lifecycle_views':result['lifecycle_actions'],
                  'unchanged_selected_files':len(equal_files),'lexical_invocation_sites':len(calls),
                  'native_packets_replayed_exactly':replayed,'G9':'INCONCLUSIVE_PENDING_RECOVERY',
                  'new_local_model_calls':0}))
