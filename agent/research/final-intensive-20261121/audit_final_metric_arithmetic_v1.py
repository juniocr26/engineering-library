"""Observe arithmetic consistency of the current registry; not a semantic score."""
from pathlib import Path
import json,hashlib,datetime,math
P=Path(__file__).resolve().parent; source=P/'requested-metric-reconciliation-v23.json';data=json.loads(source.read_bytes());findings=[];populations=[]
for r in data['records']:
 n,d,q=r.get('current_general_numerator'),r.get('current_general_denominator'),r.get('current_general_ratio')
 if d==0 and q is not None:findings.append({'metric':r['request_metric_number'],'kind':'ZERO_GENERAL_DENOMINATOR_WITH_RATE'})
 if isinstance(n,(int,float)) and isinstance(d,(int,float)) and d>0 and isinstance(q,(int,float)) and not math.isclose(q,n/d,rel_tol=1e-9):findings.append({'metric':r['request_metric_number'],'kind':'GENERAL_ARITHMETIC_MISMATCH'})
 for row in r.get('bounded_measured_subpopulations',[]):
  n,d,q=row.get('numerator'),row.get('denominator'),row.get('ratio');status='UNMEASURED_OR_NONRATIO'
  if isinstance(n,(int,float)) and isinstance(d,(int,float)):
   if d<0 or n<0:findings.append({'metric':r['request_metric_number'],'id':row.get('id'),'kind':'NEGATIVE_COUNT'})
   if d==0:
    status='ZERO_DENOMINATOR_NO_RATE'
    if q is not None:findings.append({'metric':r['request_metric_number'],'id':row.get('id'),'kind':'ZERO_DENOMINATOR_WITH_RATE'})
   elif isinstance(q,(int,float)):
    status='ARITHMETIC_MATCH' if math.isclose(q,n/d,rel_tol=1e-9,abs_tol=1e-12) else 'ARITHMETIC_MISMATCH'
    if status.endswith('MISMATCH'):findings.append({'metric':r['request_metric_number'],'id':row.get('id'),'kind':status,'expected':n/d,'observed':q})
  populations.append({'metric':r['request_metric_number'],'id':row.get('id'),'numerator':n,'denominator':d,'ratio':q,'arithmetic_status':status,'assessment_kind':row.get('assessment_kind'),'pool_with_other_populations':row.get('pool_with_other_populations'),'population':row.get('population')})
assert sorted(r['request_metric_number'] for r in data['records'])==list(range(1,17))
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'metric_count':len(data['records']),'population_count':len(populations),'observations':populations,'findings':findings,'scope':'Numerical consistency only; no assertion that numerator, population, semantics, independence or human approval are correct. Count-only/unknown ratios remain unknown. No pooling or recomputation of source observations.','model_calls':0,'optimizer_updates':0}
with (P/'final-metric-arithmetic-observation-v1.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'metrics':len(data['records']),'populations':len(populations),'findings':findings}))
