"""Metadata provenance graph and public-development-only lexical overlap audit."""
import json,hashlib,datetime,re,collections,itertools
from pathlib import Path
P=Path(__file__).resolve().parent
baseline=json.loads((P/'dataset-quality-audit-v1.json').read_text())
parent={};edges=[];meta={};texts=[];file_rows={}
def root(x):
    parent.setdefault(x,x)
    if parent[x]!=x:parent[x]=root(parent[x])
    return parent[x]
def join(a,b,kind):
    ra,rb=root(a),root(b)
    if ra!=rb:parent[rb]=ra
    edges.append({'from':a,'to':b,'kind':kind})
def refs(node,path=''):
    out=[]
    if isinstance(node,dict):
        if isinstance(node.get('sha256'),str) and len(node['sha256'])==64:
            out.append((node['sha256'],node.get('path'),path))
        for key,value in node.items():out+=refs(value,path+'/'+key)
    elif isinstance(node,list):
        for i,value in enumerate(node):out+=refs(value,path+'/'+str(i))
    return out
for m in baseline['records_metadata']:
    path=m['file']
    if path not in file_rows:file_rows[path]=Path(path).read_text().splitlines()
    row=json.loads(file_rows[path][m['line']-1]);rid=m['id'];node='row:'+rid;family=m['family'];lineage=m['lineage'];meta[rid]=m
    join(node,'family:'+family,'declared_family')
    if lineage:join(node,'lineage:'+family+':'+lineage,'declared_lineage')
    revision=row.get('source_revision')
    if revision:join(node,'revision:'+family+':'+str(revision),'declared_revision')
    # Only reference fields: do not traverse inline source evidence, prompt, observed output or answer bodies.
    for key,value in row.items():
        if key.endswith('_ref'):
            for digest,target,location in refs(value,key):join(node,'blob:'+digest,'immutable_reference:'+location)
    if m['private_excluded'] or m['split']!='DEVELOPMENT_QUARANTINE' or m['record_role']=='rejected_model_diagnostic_not_target' or 'model-diagnostics' in Path(path).name:continue
    body=(row.get('question','')+' '+row.get('answer','')) if 'answer' in row else row.get('candidate_documentation','')
    if not body.strip():continue
    tokens=re.findall(r'[\w]+',body.lower(),flags=re.UNICODE);grams={tuple(tokens[i:i+5]) for i in range(max(0,len(tokens)-4))}
    texts.append({'id':rid,'family':family,'language':m['language'],'token_count':len(tokens),'text_sha256':hashlib.sha256(body.encode()).hexdigest(),'grams':grams})
components=collections.defaultdict(list)
for rid in meta:components[root('row:'+rid)].append(rid)
comp_records=[];byrow={}
for index,ids in enumerate(sorted(components.values(),key=lambda v:sorted(v)),1):
    cid='component-'+str(index);ids=sorted(ids)
    for rid in ids:byrow[rid]=cid
    comp_records.append({'id':cid,'rows':ids,'record_count':len(ids),'families':sorted({meta[r]['family'] for r in ids}),'lineages':sorted({meta[r]['lineage'] for r in ids}),'splits':dict(collections.Counter(meta[r]['split'] for r in ids)),'private_metadata_rows':sum(meta[r]['private_excluded'] for r in ids)})
overlap=[];comparison_count=0
for a,b in itertools.combinations(texts,2):
    if a['language'].lower()!=b['language'].lower():continue
    comparison_count+=1;union=a['grams']|b['grams'];intersection=a['grams']&b['grams'];score=len(intersection)/len(union) if union else 0
    if score>=0.25:overlap.append({'left':a['id'],'right':b['id'],'jaccard_token5gram':score,'same_declared_family':a['family']==b['family'],'same_provenance_component':byrow[a['id']]==byrow[b['id']],'note':'Possible overlap only; not semantic identity or permission to change splits.'})
overlap.sort(key=lambda r:(-r['jaccard_token5gram'],r['left'],r['right']))
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'dataset-provenance-graph-protocol-v1.json','rows':len(meta),'edge_count':len(edges),'components':comp_records,'component_count':len(comp_records),'cross_split_components':[r['id'] for r in comp_records if len(r['splits'])>1],'cross_family_components':[r['id'] for r in comp_records if len(r['families'])>1],'lexical_scan':{'public_development_prose_records':len(texts),'same_language_pair_comparisons':comparison_count,'pairs_at_or_above_threshold':len(overlap),'threshold':0.25,'overlap_candidates':overlap,'record_metadata':[{k:v for k,v in x.items() if k!='grams'} for x in texts],'private_and_test_only_text_not_scanned':True,'rejected_diagnostics_not_targets_or_similarity_candidates':True},'edges':edges,'interpretation':'Declared family grouping already binds EN/PT, FAQ/chapter derivatives and revisions; exact reference links can only strengthen that conservative grouping. Low lexical similarity cannot certify independence. Graph components are metadata dependence constraints, not source/training-rights certification.','future_dependency_policy':'Current305 contains Starlette but no FastAPI family. This campaigns FastAPI development material must be co-grouped/audited with Starlette before any future training/evaluation design. No new split is assigned.','training_gold':0,'optimizer_updates':0,'original_dataset_unchanged':True,'no_model_calls':True}
with (P/'dataset-provenance-graph-results-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['edges','components','lexical_scan']},indent=2));print(json.dumps({k:v for k,v in result['lexical_scan'].items() if k not in ['overlap_candidates','record_metadata']},indent=2));print('Top5metadata-only',overlap[:5])
