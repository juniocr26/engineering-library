"""Frozen typed-request comparison over recorded Go/TS AST observations; no source/model rerun."""
from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).resolve().parent
protocol=json.loads((P/'cross-language-typed-relations-protocol-v1.json').read_text());claims=json.loads((P/'cross-language-typed-relations-claims-v1.json').read_text())['claims'];refs={r['task']:r for r in protocol['source_snapshots']};tables={};proofs=[]
for task in ['cobra','zod']:
 path=P/(task+'-typed-relations-stdout-v1.json');raw=path.read_bytes();obs=json.loads(raw);ref=refs[task];src=Path(ref['path']).read_bytes();assert hashlib.sha256(src).hexdigest()==ref['sha256']==obs['source_sha256'];tables[task]={r['id']:r for r in obs['relations']};assert len(tables[task])==len(obs['relations']);lines=src.decode().splitlines()
 for row in obs['relations']:
  span='\n'.join(lines[row['first_line']-1:row['last_line']]);assert row['exact_ast_source'] in span
 proofs.append({'task':task,'source_sha256':obs['source_sha256'],'raw_observer_output_sha256':hashlib.sha256(raw).hexdigest(),'extracted_relations':len(obs['relations']),'all_AST_fragments_located_in_recorded_physical_spans':True})
rows=[];labels=['SUPPORTED','CONTRADICTED','INSUFFICIENT'];matrix={r:{c:0 for c in labels} for r in labels}
for claim in claims:
 actual=tables[claim['task']].get(claim['relation_id'])
 if actual is None or actual['owner']!=claim['owner']:verdict='INSUFFICIENT';reason='MISSING_OR_DIFFERENT_REQUESTED_LEXICAL_OWNER'
 elif actual['normalized_relation']==claim['requested_normalized_relation']:verdict='SUPPORTED';reason='EXACT_SELECTED_AST_ROLE_RELATION'
 else:verdict='CONTRADICTED';reason='SELECTED_AST_ROLE_RELATION_DIFFERS'
 matrix[claim['expected']][verdict]+=1;rows.append({'request':claim,'observed_verdict':verdict,'reason':reason,'actual_relation':actual})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol':'cross-language-typed-relations-protocol-v1.json','claims_sha256':hashlib.sha256((P/'cross-language-typed-relations-claims-v1.json').read_bytes()).hexdigest(),'source_proofs':proofs,'records':rows,'matrix_reference_rows_observed_columns':matrix,'matches':sum(x['request']['expected']==x['observed_verdict'] for x in rows),'cases':len(rows),'scope':'57 controlled typed requests over19already-exposed selected source relations. Exact finite AST role/owner interface; not natural-language semantic accuracy, generic source resolver, native source execution or neural gain. Manual normalization includes role labels for callbacks/order/deprecation.','typed_supported_precision':{'numerator':matrix['SUPPORTED']['SUPPORTED'],'denominator':sum(matrix[r]['SUPPORTED'] for r in labels)},'false_support_on_negative_controls':{'numerator':matrix['CONTRADICTED']['SUPPORTED']+matrix['INSUFFICIENT']['SUPPORTED'],'denominator':sum(matrix['CONTRADICTED'].values())+sum(matrix['INSUFFICIENT'].values())},'full_document_approval_from_this_checker':False,'owner_approved':False,'training_gold':False,'optimizer_updates':0}
with (P/'cross-language-typed-relations-results-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:result[k] for k in ['cases','matches','matrix_reference_rows_observed_columns','false_support_on_negative_controls']},indent=2))
