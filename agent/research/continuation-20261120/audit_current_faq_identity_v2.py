"""Audit current versions only; lexical duplication is not semantic independence."""
from collections import defaultdict
import datetime,hashlib,json,re,unicodedata
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
inputs={};rows=[]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def normalized(value):return ' '.join(unicodedata.normalize('NFKC',value).casefold().split())
frozen=ROOT/'agent/research/documentation-intelligence-20261119/datasets/v10/faq-candidates.jsonl'
inputs[str(frozen.relative_to(ROOT))]=digest(frozen)
for row in map(json.loads,frozen.read_text().splitlines()):
 assert row['owner_approved']is False and row['training_gold']is False and row['training_use_approved']is False
 rows.append({'origin':'frozen-v10','id':row['id'],'pair':str(row['question_identity']),'family':row['source_family'],'language':row['language'],'question':row['question'],'answer':row['answer'],'chapter_derived':True,'owner_approved':False,'training_gold':False})
specs=[('jmespath-chapter-ledger-v3.json','jmespath/jmespath.py'),('go-geom-chapter-ledger-v3.json','twpayne/go-geom'),('totalist-chapter-ledger-v2.json','lukeed/totalist'),('boltons-chapter-ledger-v2.json','mahmoud/boltons'),('httpx-chapter-ledger-v3.json','encode/httpx'),('self-chapter-supplement-ledger-v2.json','engineering-library')]
current_counts={};supersedes=[]
for filename,family in specs:
 path=P/filename;ledger=json.loads(path.read_text());inputs[str(path.relative_to(ROOT))]=digest(path)
 assert ledger['owner_approved']is False and ledger['training_gold']is False
 current_counts[family]=len(ledger['faq'])
 for faq in ledger['faq']:
  for language in ['en','pt-br']:
   question=faq.get(language+'_q')or faq.get('question',{}).get(language)
   answer=faq.get(language+'_a')or faq.get('answer',{}).get(language)
   assert isinstance(question,str)and isinstance(answer,str)and question and answer
   row={'origin':'current-candidate','ledger':filename,'id':filename+':'+faq['id']+':'+language,'pair':filename+':'+faq['id'],'family':family,'language':language,'question':question,'answer':answer,'chapter_derived':True,'owner_approved':False,'training_gold':False,'evidence_ids':faq.get('evidence_ids',faq.get('evidence',[]))}
   rows.append(row)
   if faq.get('supersedes_candidate_question_id'):supersedes.append({'id':row['id'],'supersedes':faq['supersedes_candidate_question_id']})
pairs=defaultdict(list)
for row in rows:pairs[(row['origin'],row['family'],row['pair'])].append(row)
assert all(sorted(r['language']for r in pair)==['en','pt-br']for pair in pairs.values())
def collisions(key,distinct_family=False):
 groups=defaultdict(list)
 for row in rows:groups[key(row)].append(row)
 return [[r['id']for r in group]for group in groups.values()if len(group)>1 and(not distinct_family or len({r['family']for r in group})>1)]
code_mismatches=[]
for key,pair in pairs.items():
 codes=[re.findall(r'`([^`\n]+)`',row['question']+'\n'+row['answer'])for row in sorted(pair,key=lambda r:r['language'])]
 if codes[0]!=codes[1]:code_mismatches.append({'pair':key,'en_code_spans':codes[0],'pt_code_spans':codes[1],'interpretation':'Lexical difference requiring contextual review; not automatic mistranslation.'})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':inputs,'language_rows':len(rows),'question_pairs':len(pairs),'frozen_question_pairs':77,'current_candidate_pairs':sum(current_counts.values()),'current_counts':current_counts,'current_versions_only':specs,'same_family_same_language_normalized_question_duplicates':collisions(lambda r:(r['family'],r['language'],normalized(r['question']))),'same_family_same_language_normalized_question_answer_duplicates':collisions(lambda r:(r['family'],r['language'],normalized(r['question']),normalized(r['answer']))),'cross_family_normalized_question_reuse':collisions(lambda r:(r['language'],normalized(r['question'])),True),'paired_code_span_differences':code_mismatches,'superseding_question_ids':supersedes,'all_rows_chapter_derived':True,'owner_approved_gold':0,'all_owner_and_training_flags_false':True,'certified_semantic_equivalence':False,'certified_independent_examples':False,'interpretation':'Current chapter FAQs and their chapter claims share source families and often prose. Zero lexical collisions cannot certify semantic novelty or independent evaluation. Historical candidate versions are not additive examples.','frozen_datasets_changed':False,'source_executed':False,'model_calls':0}
with(P/'faq-identity-overlap-audit-v2.json').open('x')as f:f.write(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
with(P/'faq-current-version-review-rows-v2.jsonl').open('x')as f:
 for row in rows:
  if row['origin']=='current-candidate':f.write(json.dumps(row,ensure_ascii=False)+'\n')
print({'language_rows':len(rows),'pairs':len(pairs),'current_pairs':sum(current_counts.values()),'paired_code_span_differences':len(code_mismatches),'same_family_question_duplicates':len(record['same_family_same_language_normalized_question_duplicates'])})
