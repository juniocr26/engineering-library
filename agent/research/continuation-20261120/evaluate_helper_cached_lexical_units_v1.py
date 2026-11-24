import copy,datetime,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT/'agent/tools'))
import documentation_retrieval as retrieval
phase=sys.argv[1];assert phase in ['baseline','candidate'];oracle=json.loads((P/'helper-cached-lexical-unit-oracle-v1.json').read_text())
if phase=='baseline':assert hashlib.sha256(Path(retrieval.__file__).read_bytes()).hexdigest()==oracle['existing_tool_sha256']
root=P/('helper-cached-lexical-controls-'+phase+'-v1');root.mkdir();rows=[]
for case in oracle['cases']:
    owned=root/case['id'];source_root=owned/'source';journal=owned/'journal';source_root.mkdir(parents=True);journal.mkdir();raw=case['source'].encode();assert hashlib.sha256(raw).hexdigest()==case['source_sha256'];(source_root/'owned.py').write_bytes(raw)
    registry={'owned':{'root':str(source_root),'revision':'a'*40,'files':{'owned.py':{'sha256':case['source_sha256'],'language':'python','selectors':['selected','other']}}}}
    request={'request_id':'selected-callable','source_id':'owned','revision':'a'*40,'path':'owned.py','qualified_symbol':'selected','expected_sha256':case['source_sha256']}
    helper=retrieval.HelperRetrieval(registry,str(journal));initial=helper.request(request);assert initial['status']=='FOUND'
    result_path=journal/'selected-callable.result.json';receipt_path=journal/'selected-callable.receipt.json';before=result_path.read_bytes();cached=json.loads(before);mutation=case['mutation'];unit=cached['evidence']
    if mutation=='other-callable':unit.update(retrieval.python_unit(case['source'],'other'));unit['selector']='selected'
    elif mutation in ['body-only','whole-module']:
        lines=raw.splitlines(keepends=True);first=unit['last_line']if mutation=='body-only'else 1;last=first if mutation=='body-only'else len(lines);quote=b''.join(lines[first-1:last]);unit.update(first_line=first,last_line=last,quote=quote.decode(),quote_sha256=retrieval.sha(quote),quote_byte_start=len(b''.join(lines[:first-1])),quote_byte_end=len(b''.join(lines[:last])))
    elif mutation=='decorated-flag':unit['decorated']=True
    elif mutation=='async-kind':unit['declaration_kind']='async-function'
    elif mutation!='none':raise AssertionError(mutation)
    cached['quote_bytes']=len(unit['quote'].encode());cached['cumulative_quote_bytes']=cached['quote_bytes'];encoded=retrieval.canonical(cached)
    result_path.write_bytes(encoded);receipt=retrieval.receipt_for(encoded,retrieval.canonical(request),helper.registry_sha256,case['source_sha256'],cached['extractor_identity']);receipt_path.write_bytes(retrieval.canonical(receipt))
    (owned/'result-before-controlled-rewrite.json').write_bytes(before);(owned/'exact-inputs.json').write_text(json.dumps({'registry':registry,'request':request,'mutation':mutation,'initial_result_sha256':hashlib.sha256(before).hexdigest()},indent=2)+'\n')
    observed=retrieval.HelperRetrieval(registry,str(journal)).request(request)
    rows.append({'id':case['id'],'expected':case['expected_status'],'observed':observed,'matches':observed['status']==case['expected_status'],'source_unchanged':hashlib.sha256((source_root/'owned.py').read_bytes()).hexdigest()==case['source_sha256'],'controlled_cache_result_sha256':hashlib.sha256(encoded).hexdigest(),'coordinated_receipt_rewrite':mutation!='none'})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':phase,'tool_version':retrieval.VERSION,'tool_sha256':hashlib.sha256(Path(retrieval.__file__).read_bytes()).hexdigest(),'rows':rows,'correct':sum(row['matches']for row in rows),'n':len(rows),'source_executed':False,'model_calls':0,'permanent_tests_changed':False,'new_independent_holdout':False,'scope':'Complete selected Python lexical quote/declaration metadata with coordinated owned cache/receipt inputs; not source runtime identity or proof of adversarial compromise.'}
with(P/('helper-cached-lexical-unit-results-'+phase+'-v1.json')).open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'phase':phase,'tool':retrieval.VERSION,'correct':record['correct'],'n':len(rows),'misses':[row['id']for row in rows if not row['matches']]})
