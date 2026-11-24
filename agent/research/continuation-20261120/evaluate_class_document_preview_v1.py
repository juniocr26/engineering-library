"""Owned controlled physical binding probes, not permanent project tests."""
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

P = Path(__file__).resolve().parent


def sha(raw):return hashlib.sha256(raw).hexdigest()


def setup(module):
    def card(source, rev):return {'path': 'owned.py', 'revision': rev, 'source': source, 'sha256': sha(source.encode())}
    before = 'class Cache:\n    SIZE = 128\n    STABLE = 10\n'
    after = 'class Cache:\n    SIZE = 512\n    STABLE = 10\n'
    docs = {}
    operations = []
    for lang in ['en', 'pt-br']:
        chunks = [b'# Owned research document\n\nHuman authored prefix stays exact.\n\n']
        for claim, selector, value in [('cache-size', 'Cache.SIZE', 128), ('stable', 'Cache.STABLE', 10)]:
            chunks += [('<!-- documentation-agent:claim:' + claim + ':start -->\n').encode(), module.rendered(lang, selector, value),
                       ('<!-- documentation-agent:claim:' + claim + ':end -->\n').encode(), b'\nHuman authored interstitial stays exact.\n\n']
        chunks += [b'Human authored suffix stays exact.\n']
        raw = b''.join(chunks)
        docs[lang] = {'path': lang + '/chapter.md', 'bytes': raw, 'expected_sha256': sha(raw), 'registered_generated_claims': ['cache-size', 'stable']}
    for claim, selector, value in [('cache-size', 'Cache.SIZE', 128), ('stable', 'Cache.STABLE', 10)]:
        operations.append({'claim_id': claim, 'selector': selector, 'expected_blocks': {lang: sha(module.rendered(lang, selector, value)) for lang in docs}})
    return {'scope': 'owned-research-generated-documents', 'registered_source_path': 'owned.py',
            'previous': card(before, 'owned-before'), 'current': card(after, 'owned-after'), 'documents': docs, 'operations': operations}


def cases(module):
    base = setup(module);rows=[]
    def add(name, mutator, status, actions=None):
        spec=copy.deepcopy(base);mutator(spec);rows.append((name,spec,status,actions))
    add('simultaneous-modify-and-noop', lambda s: None, 'PREVIEW_READY', ['MODIFY','NO-OP'])
    def correct(s):
        for lang,doc in s['documents'].items():
            doc['bytes']=doc['bytes'].replace(module.rendered(lang,'Cache.SIZE',128),module.rendered(lang,'Cache.SIZE',512));doc['expected_sha256']=sha(doc['bytes']);s['operations'][0]['expected_blocks'][lang]=sha(module.rendered(lang,'Cache.SIZE',512))
    add('physically-correct-noop',correct,'PREVIEW_READY',['NO-OP','NO-OP'])
    add('stale-full-document-hash',lambda s:s['documents']['en'].update(bytes=s['documents']['en']['bytes']+b'owner edit\n'),'INCONCLUSIVE')
    add('stale-block-hash',lambda s:s['operations'][0]['expected_blocks'].update(en='0'*64),'INCONCLUSIVE')
    def disagree(s):
        doc=s['documents']['pt-br'];doc['bytes']=doc['bytes'].replace(module.rendered('pt-br','Cache.SIZE',128),module.rendered('pt-br','Cache.SIZE',129));doc['expected_sha256']=sha(doc['bytes']);s['operations'][0]['expected_blocks']['pt-br']=sha(module.rendered('pt-br','Cache.SIZE',129))
    add('bilingual-values-disagree',disagree,'INCONCLUSIVE')
    add('wrong-language-path',lambda s:s['documents']['en'].update(path='pt-br/chapter.md'),'INCONCLUSIVE')
    add('markers-without-owned-registry',lambda s:s['documents']['en'].update(registered_generated_claims=[]),'INCONCLUSIVE')
    add('duplicate-operations',lambda s:s['operations'].append(copy.deepcopy(s['operations'][0])),'INCONCLUSIVE')
    def prose(s):
        doc=s['documents']['en'];old=module.rendered('en','Cache.SIZE',128);new=b'The cache is thread-safe with capacity128.\n';doc['bytes']=doc['bytes'].replace(old,new);doc['expected_sha256']=sha(doc['bytes']);s['operations'][0]['expected_blocks']['en']=sha(new)
    add('unmapped-arbitrary-prose',prose,'INCONCLUSIVE')
    def missing(s):
        text='class Cache:\n    STABLE = 10\n';s['current'].update(source=text,sha256=sha(text.encode()))
    add('missing-member-never-remove',missing,'INCONCLUSIVE')
    add('stale-source-hash',lambda s:s['current'].update(sha256='0'*64),'INCONCLUSIVE')
    add('same-bytes-source-path-substitution',lambda s:s['current'].update(path='other.py'),'INCONCLUSIVE')
    def boolean(s):
        text=s['current']['source'].replace('512','True');s['current'].update(source=text,sha256=sha(text.encode()))
    add('bool-never-integer',boolean,'INCONCLUSIVE')
    def repair(s):s['previous']=copy.deepcopy(s['current'])
    add('unchanged-source-stale-document-repair',repair,'PREVIEW_READY',['MODIFY','NO-OP'])
    add('invalid-source-card',lambda s:s.update(current=None),'INCONCLUSIVE')
    return rows


def main(version):
    path=P/f'class_document_preview_v{version}.py';spec=importlib.util.spec_from_file_location('preview',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    controls=cases(m)
    protocol=P/'class-document-preview-control-oracle-v1.json'
    if not protocol.exists():
        protocol.write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_before_first_prediction':True,'hypothesis':'Source-bound literal statements and exact physical blocks can produce isolated multi-operation previews while refusing unowned/arbitrary/stale inputs.','producer_before_predictions_sha256':sha(path.read_bytes()),'expected':[{'id':name,'status':status,'actions':actions}for name,s,status,actions in controls],'source_scope':'Owned research docs, no publication; current real-source production applier remains unsupported.'},indent=2)+'\n')
    results=[]
    for name,s,status,actions in controls:
        try:r=m.preview(s)
        except Exception as error:r={'status':'UNCAUGHT_RESEARCH_HARNESS_BOUNDARY','error':type(error).__name__+': '+str(error)}
        checks={'status':r['status']==status}
        if actions is not None:
            checks['actions']=[x['action']for x in r.get('decisions',[])]==actions
            for lang,raw in r.get('candidates',{}).items():
                for text in [b'Human authored prefix stays exact.',b'Human authored interstitial stays exact.',b'Human authored suffix stays exact.']:
                    checks['preserved:'+lang+':'+text.decode()]=raw.count(text)==s['documents'][lang]['bytes'].count(text)
        # Persist text/hash as technical evidence, never apply to original docs.
        if 'candidates'in r:r['candidates']={k:{'text':v.decode(),'sha256':sha(v)}for k,v in r['candidates'].items()}
        results.append({'id':name,'matches':all(checks.values()),'checks':checks,'result':r})
    out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':version,'n':len(results),'correct':sum(r['matches']for r in results),'rows':results,'production_changes':False,'original_documents_written':False}
    with(P/f'class-document-preview-controls-v{version}.json').open('x')as f:json.dump(out,f,indent=2)
    print(json.dumps({'correct':out['correct'],'n':out['n'],'failures':[{'id':r['id'],'result':r['result']}for r in results if not r['matches']]}))


if __name__=='__main__':
    import sys
    main(int(sys.argv[1]))
