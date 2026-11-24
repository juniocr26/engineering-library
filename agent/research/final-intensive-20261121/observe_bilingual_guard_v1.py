"""Execute frozen screening policy; SCREEN_CLEAR never means technical acceptance."""
import json,re,hashlib,datetime,collections
from pathlib import Path
p=Path(__file__).resolve().parent;protocol=p/'bilingual-guard-study-protocol-v1.json';raw=protocol.read_bytes();d=json.loads(raw);policy=d['frozen_policy'];records=[]
for case in d['cases']:
 en,pt=case['en'],case['pt-BR'];missing={lang:[lit for lit in policy['identifiers'][case['claim_id']] if lit not in text] for lang,text in [('en',en),('pt-BR',pt)]}
 neg_en=bool(re.search(policy['en_negation_pattern'],en,re.I));neg_pt=bool(re.search(policy['pt_negation_pattern'],pt,re.I));flags=[]
 if any(missing.values()):flags.append('PROTECTED_LITERAL_MISSING')
 if neg_en!=neg_pt:flags.append('NEGATION_PRESENCE_DIFFERS')
 records.append({'id':case['id'],'category':case['category'],'verdict':'FLAG' if flags else 'SCREEN_CLEAR','flags':flags,'missing':missing,'manual_reference_pair_equivalence':case['manual_reference_pair_equivalence'],'technical_acceptance':False})
summary={}
for category in sorted({r['category'] for r in records}):
 rows=[r for r in records if r['category']==category];summary[category]={'screen_flagged':sum(r['verdict']=='FLAG' for r in rows),'denominator':len(rows)}
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':hashlib.sha256(raw).hexdigest(),'records':records,'category_counts':summary,'source_fact_count_increase':0,'independent_bilingual_accuracy':None,'semantic_false_admission_rate':None,'semantic_false_refusal_rate':None,'observed_limits':['Both intact identifiers and matching negation permit wrong action and wrong subject.','Valid paraphrase deixa de testar is flagged because the frozen lexicon does not encode it.','Exact operator/identifier constraints flag only known protected forms; no general semantic equivalence guarantee.'],'model_calls':0,'production_changes':False}
with (p/'bilingual-guard-study-results-v1.json').open('x') as f:json.dump(out,f,indent=2,ensure_ascii=False);f.write('\n')
print(json.dumps(summary))
