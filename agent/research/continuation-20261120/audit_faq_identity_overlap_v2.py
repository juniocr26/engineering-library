"""Current-only FAQ lineage census, including standalone pairs without invented chapter ancestry."""
import collections,datetime,hashlib,json,re,unicodedata
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];old=ROOT/'agent/research/documentation-intelligence-20261119/datasets/v10/faq-candidates.jsonl';rows=[];inputs={str(old.relative_to(ROOT)):hashlib.sha256(old.read_bytes()).hexdigest()}
for r in map(json.loads,old.read_text().splitlines()):rows.append({'id':r['id'],'origin':'frozen_V10','family':r['source_family'].removeprefix('source-repository:'),'lineage':r['lineage_group'],'language':r['language'],'question_id':r['question_identity'],'question':r['question'],'answer':r['answer'],'owner_approved':r['owner_approved'],'training_gold':r['training_gold'],'training_use_approved':r['training_use_approved']})
selected=[('jmespath-chapter-ledger-v3.json','jmespath/jmespath.py'),('go-geom-chapter-ledger-v3.json','twpayne/go-geom'),('totalist-chapter-ledger-v2.json','lukeed/totalist'),('self-chapter-supplement-ledger-v2.json','engineering-library'),('boltons-chapter-ledger-v2.json','mahmoud/boltons'),('httpx-chapter-ledger-v3.json','encode/httpx'),('humanize-chapter-ledger-v1.json','dustin/go-humanize')]
for filename,family in selected:
 path=P/filename;inputs[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest();ledger=json.loads(path.read_text())
 for faq in ledger['faq']:
  for lang in ['en','pt-br']:
   q=faq.get(lang+'_q',faq.get('question',{}).get(lang));a=faq.get(lang+'_a',faq.get('answer',{}).get(lang));assert type(q)is str and type(a)is str
   rows.append({'id':filename+':'+faq['id']+':'+lang,'origin':'current_chapter_derived','family':family,'lineage':'current-source-chapter:'+family,'language':lang,'question_id':[family,faq['id']],'question':q,'answer':a,'owner_approved':False,'training_gold':False,'training_use_approved':False})
standalone=P/'queue-deterministic-faq-v1.json';inputs[str(standalone.relative_to(ROOT))]=hashlib.sha256(standalone.read_bytes()).hexdigest();faqdata=json.loads(standalone.read_text());items=faqdata.get('faq',faqdata.get('pairs'))
if items is None:raise ValueError('inspect standalone schema rather than invent ancestry')
for faq in items:
 for lang in ['en','pt-br']:
  values=faq[lang];q=values['question'];a=values['answer'];rows.append({'id':'queue-standalone:'+faq['id']+':'+lang,'origin':'current_standalone_source_runtime_faq','family':'sindresorhus/p-limit+yocto-queue','lineage':'related-dependency-queue-faq-v1','language':lang,'question_id':['sindresorhus/p-limit+yocto-queue',faq['id']],'question':q,'answer':a,'owner_approved':False,'training_gold':False,'training_use_approved':False})
assert len({r['id']for r in rows})==len(rows);pairs=collections.defaultdict(list)
for r in rows:pairs[json.dumps(r['question_id'],sort_keys=True)].append(r)
assert all(sorted(x['language']for x in group)==['en','pt-br']for group in pairs.values())
def norm(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFC',s).casefold()).strip()
def dup(key):
 groups=collections.defaultdict(list)
 for r in rows:groups[key(r)].append(r['id'])
 return[{'key':list(k),'rows':v}for k,v in groups.items()if len(v)>1]
code_differences=[]
for id,group in pairs.items():
 if group[0]['origin']=='frozen_V10':continue
 by={x['language']:x for x in group};en=re.findall(r'`([^`]+)`',by['en']['answer']);pt=re.findall(r'`([^`]+)`',by['pt-br']['answer'])
 if en!=pt:code_differences.append({'question_identity':json.loads(id),'en':en,'pt-br':pt})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':inputs,'language_rows_inspected':len(rows),'paired_questions':len(pairs),'frozen_V10_language_rows':154,'frozen_V10_question_pairs':77,'current_candidate_pairs':(len(rows)-154)//2,'current_chapter_derived_pairs':sum(x['origin']=='current_chapter_derived'for x in rows)//2,'current_standalone_pairs':sum(x['origin']=='current_standalone_source_runtime_faq'for x in rows)//2,'selected_current_chapter_versions':selected,'same_family_exact_question_groups':dup(lambda r:(r['family'],r['language'],norm(r['question']))),'same_family_exact_question_answer_groups':dup(lambda r:(r['family'],r['language'],norm(r['question']),norm(r['answer']))),'cross_family_exact_question_groups':dup(lambda r:(r['language'],norm(r['question']))),'current_code_span_differences':code_differences,'all_owner_and_training_flags_false':all(r[k]is False for r in rows for k in ['owner_approved','training_gold','training_use_approved']),'frozen305_changed':False,'semantic_equivalence_or_novelty_certified':False,'independent_training_targets_created':0,'interpretation':['Family prefix normalization avoids treating an existing source-repository prefix as a new family.','The current standalone queue FAQ is not invented as chapter-derived.','HTTPX/httpcore and p-limit/queue dependency ancestry must remain grouped despite distinct question IDs.','Exact identity and code-span agreement do not certify factual truth, semantic translation or independent task ancestry.','Old candidate versions and rejected model replies remain preserved but are excluded from current-only counts.'],'files_deleted':0,'source_executed':False,'model_calls':0}
with(P/'faq-identity-overlap-audit-v4.json').open('x')as f:f.write(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
print({'language_rows':len(rows),'pairs':len(pairs),'current_pairs':r['current_candidate_pairs'],'chapter_derived':r['current_chapter_derived_pairs'],'standalone':r['current_standalone_pairs'],'code_differences':len(code_differences)})
