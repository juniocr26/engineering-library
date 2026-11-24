"""Read-only FAQ identity/overlap audit; no semantic deduplication or deletions."""
import collections,datetime,hashlib,json,re,unicodedata
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=ROOT/'agent/research/documentation-intelligence-20261119/datasets/v10/faq-candidates.jsonl'
rows=[];inputs={str(old.relative_to(ROOT)):sha(old)}
for r in map(json.loads,old.read_text().splitlines()):
 rows.append({'id':r['id'],'origin':'frozen_V10','family':r['source_family'],'lineage':r['lineage_group'],'language':r['language'],'question_id':r['question_identity'],'question':r['question'],'answer':r['answer'],'claim_alignment':r.get('claim_alignment_record_id'),'owner_approved':r['owner_approved'],'training_gold':r['training_gold'],'training_use_approved':r['training_use_approved']})
selected=[('jmespath-chapter-ledger-v3.json','jmespath/jmespath.py'),('go-geom-chapter-ledger-v3.json','twpayne/go-geom'),('totalist-chapter-ledger-v2.json','lukeed/totalist'),('self-chapter-supplement-ledger-v1.json','engineering-library')]
for filename,family in selected:
 path=P/filename;inputs[str(path.relative_to(ROOT))]=sha(path);ledger=json.loads(path.read_text())
 for faq in ledger['faq']:
  for language in ['en','pt-br']:
   q=faq.get(language+'_q',faq.get('question',{}).get(language));a=faq.get(language+'_a',faq.get('answer',{}).get(language))
   assert type(q)is str and type(a)is str
   rows.append({'id':filename+':'+faq['id']+':'+language,'origin':'current_continuation_candidate','family':'source-repository:'+family,'lineage':'current-source-chapter:'+family,'language':language,'question_id':[family,faq['id']],'question':q,'answer':a,'claim_alignment':faq.get('claim',faq.get('claim_id',faq.get('answer_claim',faq.get('claims')))),'supersedes_candidate_question_id':faq.get('supersedes_candidate_question_id'),'owner_approved':False,'training_gold':False,'training_use_approved':False})
assert len({r['id']for r in rows})==len(rows)
def normalize(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFC',s).casefold()).strip()
def duplicates(key):
 groups=collections.defaultdict(list)
 for r in rows:groups[key(r)].append(r['id'])
 return[{'key':list(k)if type(k)is tuple else k,'rows':v}for k,v in groups.items()if len(v)>1]
pairs=collections.defaultdict(list)
for r in rows:pairs[json.dumps(r['question_id'],sort_keys=True)].append(r)
assert all(sorted(r['language']for r in v)==['en','pt-br']for v in pairs.values())
oldkeys=collections.Counter(tuple(r['question_identity'])for r in map(json.loads,old.read_text().splitlines()))
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':inputs,'language_rows_inspected':len(rows),'paired_questions':len(pairs),'frozen_V10_language_rows':154,'frozen_V10_question_pairs':len(oldkeys),'current_candidate_pairs':(len(rows)-154)//2,'current_candidate_versions_only':selected,'same_family_same_language_exact_question_duplicates':duplicates(lambda r:(r['family'],r['language'],normalize(r['question']))),'same_family_same_language_exact_question_answer_duplicates':duplicates(lambda r:(r['family'],r['language'],normalize(r['question']),normalize(r['answer']))),'cross_family_exact_question_reuse':duplicates(lambda r:(r['language'],normalize(r['question']))),'current_questions_superseding_rejected_questions':[{'id':r['id'],'supersedes':r.get('supersedes_candidate_question_id')}for r in rows if r.get('supersedes_candidate_question_id')],'all_current_rows_are_chapter_derived_not_independent_targets':True,'owner_gold':sum(r['training_gold']for r in rows),'all_owner_and_training_flags_false':all(r[k]is False for r in rows for k in ['owner_approved','training_gold','training_use_approved']),'interpretation':['An exact generic question across distinct source families is a template overlap signal, not automatic duplicate content or deletion authority.','Question and answer byte identity does not prove source-revision freshness, semantic equivalence or factual correctness.','All new FAQ answers reuse current chapter claims; do not add them to existing305 as independently approved training examples.','Superseded candidate ledger versions are deliberately excluded from current pair counts, but exact historical files remain preserved.','JMESPath V2 question relevance failure shows physical/code identity checks cannot replace a question-specific source review.'],'files_deleted':0,'datasets_changed':False,'source_executed':False,'model_calls':0}
with(P/'faq-identity-overlap-audit-v1.json').open('x')as f:f.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items()if k in ['language_rows_inspected','paired_questions','frozen_V10_question_pairs','current_candidate_pairs','owner_gold','all_owner_and_training_flags_false']}));print({'same_family_exact_question_groups':len(record['same_family_same_language_exact_question_duplicates']),'cross_family_exact_question_groups':len(record['cross_family_exact_question_reuse'])})
