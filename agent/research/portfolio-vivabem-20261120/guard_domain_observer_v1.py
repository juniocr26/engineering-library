from pathlib import Path
import json,re,hashlib

def inconclusive(reason):
 return {'status':'INCONCLUSIVE','reason':reason,'runtime_verified':False,'document_lifecycle_action':None}

def compare_thresholds(old,new,intervals,complete):
 if type(old) is not int or type(new) is not int or not (0<=old<=1024 and 0<=new<=1024):
  return inconclusive('unsupported threshold')
 if complete is not True or not isinstance(intervals,list) or not intervals:
  return inconclusive('missing or incomplete domain')
 for interval in intervals:
  if not isinstance(interval,list) or len(interval)!=2:return inconclusive('invalid interval shape')
  lower,upper=interval
  if type(lower) is not int or lower<0:return inconclusive('invalid lower bound')
  if upper is not None and (type(upper) is not int or upper<lower):return inconclusive('invalid upper bound')
 lo,hi=min(old,new),max(old,new)-1
 witness=None
 if lo<=hi:
  for lower,upper in intervals:
   start=max(lo,lower);end=hi if upper is None else min(hi,upper)
   if start<=end:witness=start;break
 return {'status':'DIFFERENT_ON_DECLARED_DOMAIN' if witness is not None else 'EQUIVALENT_ON_DECLARED_DOMAIN','difference_interval':[lo,hi] if lo<=hi else None,'witness_length':witness,'scope':'Guardbooleanbranchdecisiononly,conditionalondeclareddomain;notfullhelper/SQL/runtime/lifecycleequivalence.','runtime_verified':False,'document_lifecycle_action':None}

PATTERN=re.compile(r'(?m)^(\tif len\(loc\) < )([0-9]+)( \{\n\t\treturn bound\n\t\})$')

def observe_source_pair(before,after,fact_bytes,config):
 sha=lambda b:hashlib.sha256(b).hexdigest()
 if sha(fact_bytes)!=config['reviewed_domain_fact_sha256']:return inconclusive('reviewed fact hash mismatch')
 try:fact=json.loads(fact_bytes)
 except (ValueError,UnicodeError):return inconclusive('invalid reviewed fact')
 if fact.get('id')!=config['fact_id'] or fact.get('producer')!='regexp.(*Regexp).FindStringIndex':return inconclusive('unsupported producer fact')
 limits=[]
 for text in [before,after]:
  found=list(PATTERN.finditer(text))
  if len(found)!=1:return inconclusive('selected canonical guard missing/ambiguous')
  literal=found[0].group(2)
  if str(int(literal))!=literal:return inconclusive('noncanonical decimal')
  normalized=PATTERN.sub(lambda m:m.group(1)+'__LIMIT__'+m.group(3),text)
  if sha(normalized.encode())!=config['normalized_context_sha256']:return inconclusive('other source context changed')
  limits.append(int(literal))
 result=compare_thresholds(limits[0],limits[1],fact.get('length_intervals'),fact.get('complete_under_declared_contract'))
 result.update(source_profile='closed-sqlx-fixBound-context-v1',conditional_on_reviewed_contract=True,contract_truth_automatically_verified=False)
 return result
