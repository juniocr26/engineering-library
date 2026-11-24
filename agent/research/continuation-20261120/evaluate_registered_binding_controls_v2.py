"""Owned physical/source/callee drift observations, outside permanent test trees."""
import copy
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

P=Path(__file__).resolve().parent
version=int(sys.argv[1])
if version not in [1,2]:raise ValueError('fixed producer version required')
producer=P/f'registered_declaration_binding_v{version}.py'
spec=importlib.util.spec_from_file_location('binding',producer);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=Path('/private/tmp')/f'el-registered-decl-controls-20261120-v{version}';base.mkdir(exist_ok=False)
before='def api():\n    return 1\n';after='def api(limit=None):\n    return 1\n'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
recipes=[('valid-physical-binding','MODIFY'),('inline-current-substitution','INCONCLUSIVE'),('inline-previous-substitution','INCONCLUSIVE'),
('current-file-stale-before-call','INCONCLUSIVE'),('public-config-path-swap','INCONCLUSIVE'),('unknown-logical-identity','INCONCLUSIVE'),
('leaf-symlink','INCONCLUSIVE'),('parent-symlink','INCONCLUSIVE'),('fifo-source','INCONCLUSIVE'),('root-replaced-after-configuration','INCONCLUSIVE'),
('source-mutated-during-prediction','INCONCLUSIVE'),('identical-bytes-new-inode-during-prediction','INCONCLUSIVE'),('configuration-mutated-during-prediction','INCONCLUSIVE'),
('callee-mutates-passed-source-packet','INCONCLUSIVE'),('callee-grants-owner-approval','INCONCLUSIVE'),('callee-reports-execution','INCONCLUSIVE'),
('caller-original-mutation-does-not-change-snapshot','MODIFY'),('explicit-new-registration-can-select-other-file','MODIFY'),('unsupported-prose-with-bound-source','INCONCLUSIVE'),('wrong-registered-hash','INCONCLUSIVE')]
cases=[]
for name,expected in recipes:
    root=base/name;old=root/'previous';new=root/'current'
    for parent,text in [(old,before),(new,after)]:
        (parent/'pkg').mkdir(parents=True);(parent/'pkg/api.py').write_text(text);(parent/'pkg/shadow.py').write_text(text)
    registration={'schema_version':1,'scope':'registered-module-research','sources':{
        label:{'root':str(parent),'revision':hashlib.sha1(text.encode()).hexdigest(),'files':{'pkg/api.py':sha(text.encode()),'pkg/shadow.py':sha(text.encode())}}
        for label,parent,text in [('previous',old,before),('current',new,after)]},
        'contracts':{'owned.api':{'selector':'api','previous_path':'pkg/api.py','current_path':'pkg/api.py'}}}
    packet={'id':name,'family':'owned-physical-binding-controls','language':'python','previous_source':before,'current_source':after,
            'documentation':{'en':'api has no limit parameter.','pt-br':'api não possui parâmetro limit.'},'complete_scope':True,'source_available':True,
            'positive_retirement_evidence':None,'logical_contract_id':'owned.api','metadata':{}}
    cases.append({'id':name,'expected':expected,'root':str(root),'registration':registration,'packet':packet})
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'producer_sha256':sha(producer.read_bytes()),'cases':cases,'frozen_before_predictions':True,
          'source_execution_allowed':False,'synthetic_revision_tokens':'SHA1ofownsourcecontent,NOTGitcommits;registrationdoesnotauthenticateupstreamhistory.',
          'scope':'Ownedtemporaryfilesonly;calleeoutputdriftisatrusted-processintegritycontrol,notamultiusersandboxclaim.'}
oracle=P/'registered-binding-control-oracle-v1.json'
if version==1:
    with oracle.open('x')as stream:json.dump(protocol,stream,indent=2,ensure_ascii=False)
else:
    old_oracle=json.loads(oracle.read_text())
    if [(x['id'],x['expected'])for x in old_oracle['cases']]!=recipes:raise ValueError('expected controls drifted')
    with(P/'registered-binding-execution-plan-v2.json').open('x')as stream:json.dump(protocol,stream,indent=2,ensure_ascii=False)
rows=[]
for case in cases:
    name=case['id'];root=Path(case['root']);old=root/'previous';new=root/'current';target=new/'pkg/api.py';registration=copy.deepcopy(case['registration']);packet=copy.deepcopy(case['packet'])
    if name=='explicit-new-registration-can-select-other-file':registration['contracts']['owned.api']['current_path']='pkg/shadow.py'
    if name=='wrong-registered-hash':registration['sources']['current']['files']['pkg/api.py']='0'*64
    tool=m.RegisteredDeclaration(registration)
    if name=='inline-current-substitution':packet['current_source']=before
    if name=='inline-previous-substitution':packet['previous_source']=after
    if name=='current-file-stale-before-call':target.write_text(before)
    if name=='public-config-path-swap':tool.registration['contracts']['owned.api']['current_path']='pkg/shadow.py'
    if name=='unknown-logical-identity':packet['logical_contract_id']='foreign.api'
    if name=='leaf-symlink':target.rename(new/'pkg/api.original.py');target.symlink_to(new/'pkg/shadow.py')
    if name=='parent-symlink':(new/'pkg').rename(new/'pkg.original');(new/'pkg').symlink_to(new/'pkg.original',target_is_directory=True)
    if name=='fifo-source':target.rename(new/'pkg/api.original.py');os.mkfifo(target,0o600)
    if name=='root-replaced-after-configuration':
        new.rename(root/'current.original');(new/'pkg').mkdir(parents=True);target.write_text(after)
    if name=='unsupported-prose-with-bound-source':packet['documentation']={'en':'api always accepts every keyword.','pt-br':'api sempre aceita toda opção.'}
    original=m.adapter.decision
    def callee(received):
        if name=='source-mutated-during-prediction':target.write_text(before)
        if name=='identical-bytes-new-inode-during-prediction':
            info=target.stat();target.rename(new/'pkg/api.original.py');target.write_text(after);os.utime(target,ns=(info.st_atime_ns,info.st_mtime_ns))
        if name=='configuration-mutated-during-prediction':tool.registration['sources']['current']['files']['pkg/api.py']='0'*64
        if name=='callee-mutates-passed-source-packet':received['current_source']=before
        if name=='caller-original-mutation-does-not-change-snapshot':packet['documentation']['en']='api has a limit parameter.'
        result=original(received)
        if name=='callee-grants-owner-approval':result['owner_approved']=True
        if name=='callee-reports-execution':result['source_executed']=True
        return result
    with patch.object(m.adapter,'decision',side_effect=callee):result=tool.decide(packet)
    rows.append({'id':name,'expected':case['expected'],'observed':result['action'],'matches':result['action']==case['expected'],
                 'result':result,'physical_current_after':target.read_text()if target.is_file()and not target.is_symlink()else'NONREGULAR_OR_SYMLINK_PRESERVED',
                 'source_preservation':'Initialexactsourceandregistrationretainedinoracle;allownedtemporarymutationsremainisolated,noexternalorpublicsnapshotmodified.'})
report={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'producer_version':version,'correct':sum(x['matches']for x in rows),'n':len(rows),'rows':rows,
        'source_executed':False,'permanent_tests_modified':False,'new_control_count':len(rows)if version==1 else 0,'temporary_owned_root':str(base)}
with(P/f'registered-binding-controls-v{version}.json').open('x')as stream:json.dump(report,stream,indent=2)
print(json.dumps({'correct':report['correct'],'n':report['n'],'failures':[{'id':x['id'],'observed':x['observed'],'physical_bound':x['result']['physical_source_bytes_and_registered_paths_verified']}for x in rows if not x['matches']]}))
