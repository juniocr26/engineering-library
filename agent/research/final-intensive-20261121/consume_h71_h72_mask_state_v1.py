import argparse,json,hashlib,tarfile
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);ROOT=ap.parse_args().root.resolve();P=ROOT/'agent/research/final-intensive-20261121';sha=lambda b:hashlib.sha256(b).hexdigest();a=json.loads((P/'h71-h72-mask-state-current-audit-v1.json').read_bytes())
for e in a['dependencies']:assert sha((ROOT/e['path']).read_bytes())==e['sha256']
old=ROOT/'agent/research/portfolio-vivabem-20261120';cards=json.loads((old/'public-framework-mask-state-source-cards-v1.json').read_bytes());assert len(cards['units'])==14
for u in cards['units']:
 raw=(old/'public-framework-source-v1'/u['path']).read_bytes();assert sha(raw)==u['file_sha256'];quote=''.join(raw.decode().splitlines(keepends=True)[u['start']-1:u['end']]);assert quote==u['quote'] and sha(quote.encode())==u['quote_sha256']
freeze=json.loads((old/'owned-loss-mask-index-input-freeze-v1.json').read_bytes());archive=ROOT/freeze['archive'];assert sha(archive.read_bytes())==freeze['archive_sha256'];mf=json.loads((ROOT/freeze['manifest']).read_bytes())
with tarfile.open(archive,'r:gz') as tar:
 for e in mf['files']:assert tar.extractfile(e['path']).read()==(ROOT/e['path']).read_bytes() and sha((ROOT/e['path']).read_bytes())==e['sha256']
rows={x['id']:x for x in a['historical_owned_vectors']};assert len(rows)==6 and rows['masked-short']['source_selected_count']==5 and rows['masked-short']['real_target_count']==4 and rows['masked-short']['padding_positions']==[8]
assert rows['exact-cap-control']['padding_positions']==[] and rows['padding-only-count-positive']['real_target_count']==0 and rows['padding-only-count-positive']['source_selected_count']==1
assert rows['entire-target-truncated']['source_selected_count']==0 and rows['partial-target-truncated']['lost_target_positions']==8
assert a['framework_imports']==a['historical_producer_executions']==a['tokenizer_model_loads']==a['optimizer_updates']==0 and a['actual_framework_loss_measured'] is False
gates=json.loads((P/'fine-tuning-current-nine-gates-assessment-v3.json').read_bytes());assert len(gates['gates'])==9 and all(g['launch_decision']=='NO_GO' for g in gates['gates'])
for g in gates['gates']:
 for e in g['current_references']:assert sha((ROOT/e['path']).read_bytes())==e['sha256']
for e in json.loads((P/'remaining-chapters-recovery-dependencies-v40.json').read_bytes())['dependencies']:assert sha((ROOT/e['path']).read_bytes())==e['sha256']
assert json.loads((P/'dataset-faq-selected-source-support-review-v1.json').read_bytes())['pair_count']==3
assert len(json.loads((P/'campaign-requirement-evidence-audit-v11.json').read_bytes())['final_question_audit'])==22
print(json.dumps({'status':'PASS_H71_H72_PINNED_SOURCE_AND_RECORD_RECOVERY','source_units':14,'frozen_archive_inputs':4,'historical_owned_vectors':6,'launch_NO_GO_gates':9,'framework_or_model_imports':0,'optimizer_updates':0,'framework_loss_or_training_success_inferred':False}))
