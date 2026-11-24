import copy,datetime,hashlib,importlib.util,json,os,shutil
from pathlib import Path
P=Path(__file__).resolve().parent
protocol=json.loads((P/'helper-budget-audit-controls-v1.json').read_text())
source=P/'helper_recovery_budget_audit_v1.py'
assert hashlib.sha256(source.read_bytes()).hexdigest()==protocol['candidate_sha256']
spec=importlib.util.spec_from_file_location('owned_helper_budget_audit',source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
old=P/'helper-journal-public-v1';registry=json.loads((P/'helper-public-registry-v1.json').read_text());ids=sorted(p.name.removesuffix('.request.json')for p in old.glob('*.request.json'))
root=P/'helper-budget-control-journals-v1';root.mkdir()
rows=[]
for case in protocol['rows']:
    journal=root/case['id'];journal.mkdir()
    for path in old.iterdir():
        if path.is_file():(journal/path.name).write_bytes(path.read_bytes())
    reg=copy.deepcopy(registry);keys=ids[:];mutation=case['mutation'];key=keys[0]
    if mutation=='extra':(journal/'unexpected.json').write_text('{}')
    elif mutation in ['missing-result','missing-receipt']:(journal/(key+('.result.json'if mutation=='missing-result'else'.receipt.json'))).unlink()
    elif mutation=='tamper-result':
        path=journal/(key+'.result.json');d=json.loads(path.read_text());d['quote_bytes']+=1;path.write_text(json.dumps(d))
    elif mutation=='tamper-receipt':
        path=journal/(key+'.receipt.json');d=json.loads(path.read_text());d['result_sha256']='0'*64;path.write_text(json.dumps(d))
    elif mutation=='omit-id':keys=keys[1:]
    elif mutation=='duplicate-id':keys.append(keys[0])
    elif mutation=='registry-revision':reg['jmespath']['revision']='0'*40
    elif mutation=='symlink-result':
        path=journal/(key+'.result.json');path.unlink();path.symlink_to(old/path.name)
    elif mutation=='orphan-request':(journal/'orphan.request.json').write_text('{}')
    elif mutation!='none':raise AssertionError(mutation)
    before={path.name:('symlink:'+os.readlink(path)if path.is_symlink()else hashlib.sha256(path.read_bytes()).hexdigest())for path in journal.iterdir()}
    result=module.audit(reg,str(journal),keys,total_steps=case['total_steps'],total_quote_bytes=case['total_quote_bytes'])
    after={path.name:('symlink:'+os.readlink(path)if path.is_symlink()else hashlib.sha256(path.read_bytes()).hexdigest())for path in journal.iterdir()}
    matched=result['status']==case['expected_status']and before==after
    if result['status']in ['AVAILABLE','EXHAUSTED']:matched=matched and result['used_steps']==4 and result['used_quote_bytes']==1603
    rows.append({'id':case['id'],'expected_status':case['expected_status'],'result':result,'journal_unchanged':before==after,'matches':matched,'input_hashes_or_symlink_targets':before})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'correct':sum(row['matches']for row in rows),'n':len(rows),'source_executed':False,'model_calls':0,'permanent_tests_changed':False,'ruby_routing_changed':False,'owner_approved':False,'cross_process_reservation_provided':False}
with(P/'helper-budget-audit-results-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({'correct':record['correct'],'n':record['n'],'failed':[r['id']for r in rows if not r['matches']]})
