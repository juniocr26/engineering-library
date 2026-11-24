from pathlib import Path
import json,hashlib,datetime,re
p=Path(__file__).resolve().parent;root=p.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest();pre=json.loads((p/'opencv-original-targets-preflight-v1.json').read_text());source=p/'opencv-targets-source-context-v1';binding=json.loads((p/'opencv-targets-source-binding-observations-v1.json').read_text());deps={}
def dep(f):
 deps[str(f.relative_to(root))]=sha(f.read_bytes())
for name in ['opencv-original-targets-preflight-v1.json','opencv-targets-source-protocol-v1.json','opencv-targets-source-scope-extension-v1.json','opencv-targets-source-binding-observations-v1.json','opencv-depth-historical-origin-v1.json','opencv-scalar-declaration-location-v1.json']:
 dep(p/name)
for v in [1,2,3]:
 f=p/f'opencv-targets-source-acquisition-v{v}.json';dep(f)
 for e in json.loads(f.read_text())['records']:
  if e['exit_code']==0:
   f=root/e['saved_path'];assert sha(f.read_bytes())==e['sha256'];dep(f)
for e in json.loads((p/'opencv-depth-historical-origin-v1.json').read_text())['artifacts']:dep(root/e['path'])
history=root/'agent/research/acceptance-calibration-20261121/original-public-chapter-provenance-captures-v1/opencv-shape-contract'
for n in ['origin.json','model-content.txt','raw-response.json','recorded-request.json']:dep(history/n)
groups={
'opencv-depth-coercion':[
('D01','Equal inputs return depth1 before flag and macro path','Flag overrides equal depths: false'),
('D02','Unequal integer-boundary branch contains negated flag and both smaller-depth comparisons','CV8S branch outside CV32S or !muldiv omitted: false'),
('D03','Bitwise comparisons, strict macro-size >4, integer code return without image buffers','Short-circuit operators, >=4 or element conversion: false'),
('D04','Actual historical onefact bothlanguages misnests branch and omits flag','No unsupported attribution; equal maximum wording imprecise but same numeric result'),
('D05','Caller arithm_op_ocl has no-OpenCL false path and many earlier guards; reached coercion paths each call twice','Every public operation necessarily invokes helper: false'),
('D06','Caller equal triple bypasses helper; later integer-output/scaled-kernel adjustment and type packing','Helper result always final working type: false'),
('D07','Macro/depth context now acquired but original selected evidence deliberately omits definitions','Original claims missing definitions within original evidence remain accurate; no arbitrary-input safety inferred'),
('D08','Full ENPT and three FAQ meanings match with same code/IDs','Manual correction not local model learning or approved training')],
'opencv-shape-contract':[
('S01','sizend outputs counts/entries; supplied channels appended and counts incremented','Spatial-only or channel equality-only rule: false'),
('S02','Both indices must remain nonnegative, decrement together','Same complete lengths or every leading dimension visited: false'),
('S03','Mismatch AND neither one rejects, otherwise continue until termination','Any one immediately returns true: false'),
('S04','Conceptual [2,3]+4 vs [3]+4 compares channels and trailing 3 only','Illustration not actual executed OpenCV test'),
('S05','Historical model right-to-left/unit facts present; channels/counts/stopping missing; PT transmissão present','No claim old model omitted everything or executed test'),
('S06','Caller !s1&&!s2 outer gate and scalar-like hit short-circuit helper, failure sets s1 like1/s2 like2&&!like1','false necessarily rejects arithmetic immediately: false'),
('S07','Actual precomp scalar probes have kind/shape/continuity/value guards; sizend may assert or call other getters','Boolean helper is no general invalid InputArray safety/no-throw proof'),
('S08','MatShape MAX_DIMS10; stack arrays11; supplied count assumptions not newly certified','No heap/output allocation, constant-time benchmark or full backend contract inferred'),
('S09','All ENPT meanings/three FAQs/code/IDs matched','Same-agent review not independent human, publication/Gold or neural improvement')]}
for item in pre['topics']:
 topic=item['topic'];docs=[]
 for i,e in enumerate(item['files']):
  f=root/e['path'];assert sha(f.read_bytes())==e['sha256'];assert (root/e['original_path']).read_bytes()==f.read_bytes();dep(f);dep(root/e['original_path'])
  if i<2:docs.append({'language':['en','pt-br'][i],'path':e['path'],'sha256':e['sha256'],'readable_original_path':e['original_path']})
 texts=[(root/d['path']).read_text() for d in docs];spans=lambda t:re.findall(r'(?<!`)`([^`\n]+)`(?!`)',t);ids=lambda t:re.findall(r'<!-- reading-section: faq:([^ ]+) -->',t);assert spans(texts[0])==spans(texts[1]);assert ids(texts[0])==ids(texts[1]) and len(ids(texts[0]))==3
 gates={g:{'status':'PASS','basis':basis} for g,basis in zip(['G1','G2','G3','G4','G5','G6','G7','G8'],['Pinned Git bytes and original exact ranges/documents','Entire bilingual prose/FAQs/historical attribution source reviewed within declared bounds','Helper/caller/config/types/macros/scalar dependency relevant closure reviewed; no full backend certification','Original requirements retained without narrowing','No executable chapter commands; shape conceptual trace statically validated, no OpenCV compilation/parser/runtime claims','Full ENPT predicates/negations/code/FAQ meanings reviewed','NOOP original fixed-pin chapter, not universal revision decision','Separate acquisition/binding plus explicit adverse adjudications; same agent not independent human'])};gates['G9']={'status':'INCONCLUSIVE','basis':'Fresh checkpoint actual restore with new consumer still required'}
 result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'topic':topic,'version':'original_dataset_target','documents':docs,'gates':gates,'source_claim_groups':[{'id':i,'meaning':m,'adverse_challenge':c,'verdict':'SUPPORTED_SCOPED_STATIC','reviewer':'Same campaign agent'} for i,m,c in groups[topic]],'exact_source_range_bindings':[e for e in binding['bindings'] if e['topic']==topic],'FAQ_ids':ids(texts[0]),'technical_status':'INCONCLUSIVE_RECOVERY_PENDING','authorship':'Manual Codex source-reviewed original chapter; not current neural output','external_dependency_edges':[{'path':k,'sha256':v} for k,v in sorted(deps.items())],'OpenCV_parser_compiler_build_or_runtime_executed':False,'new_model_calls':0,'publication_approved':False,'owner_gold':False,'training_approved':False}
 with (p/(topic+'-complete-review-v1.json')).open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({'topic':topic,'groups':len(groups[topic]),'G1_G8':'PASS','G9':'PENDING'}))
