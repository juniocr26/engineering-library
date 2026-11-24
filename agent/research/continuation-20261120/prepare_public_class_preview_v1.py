"""Consume pinned public source and owned physical research docs, isolate preview."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.path.insert(0, str(ROOT / 'agent/tools'))
import documentation_maintenance
from documentation_workspace import directory, read, write_new

spec = importlib.util.spec_from_file_location('class_preview', P / 'class_document_preview_v2.py')
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    oldrev='e600d11e5d4e90b0d7f67882756fffc90a52eb36';newrev='6ff419a8b171d055a9bfc6904605bceb8b7a80ef'
    sources = {}
    roots = {}
    for label,rev in [('previous',oldrev),('current',newrev)]:
        root=(P/'new-public-sources-v1/jmespath--jmespath.py'/rev).resolve();roots[label]=root
        with directory(root)as fd:raw,metadata=read(fd,'jmespath/parser.py',65536)
        sources[label]={'path':'jmespath/parser.py','revision':rev,'source':raw.decode(),'sha256':sha(raw)}
    docs_root=P/'physical-class-documents-v1';docs_root.mkdir(exist_ok=False)
    documents={};operations=[]
    for lang in ['en','pt-br']:
        (docs_root/lang).mkdir()
        raw=b'# Isolated research source notes\n\nEditorial context outside generated claims must remain exact.\n\n'
        for claim,selector,value in [('cache-size','Parser._MAX_SIZE',128),('projection-stop','Parser._PROJECTION_STOP',10)]:
            raw+=('<!-- documentation-agent:claim:'+claim+':start -->\n').encode()+preview.rendered(lang,selector,value)+('<!-- documentation-agent:claim:'+claim+':end -->\n').encode()+b'\nRetained editorial separator.\n\n'
        raw+=b'End of isolated research notes.\n'
        with directory(docs_root)as fd:write_new(fd,lang+'/chapter.md',raw)
    for lang in ['en','pt-br']:
        with directory(docs_root)as fd:raw,meta=read(fd,lang+'/chapter.md',2*1024*1024)
        documents[lang]={'path':lang+'/chapter.md','bytes':raw,'expected_sha256':sha(raw),'registered_generated_claims':['cache-size','projection-stop']}
    for claim,selector,value in [('cache-size','Parser._MAX_SIZE',128),('projection-stop','Parser._PROJECTION_STOP',10)]:
        operations.append({'claim_id':claim,'selector':selector,'expected_blocks':{lang:sha(preview.rendered(lang,selector,value))for lang in documents}})
    specification={'scope':'owned-research-generated-documents','registered_source_path':'jmespath/parser.py','documents':documents,'operations':operations,**sources}
    # Freeze the physically registered intent before previewing it; bytes are represented
    # by exact text and independent hashes in the technical request record.
    serial=json.loads(json.dumps(specification,default=lambda value:{'utf8':value.decode(),'sha256':sha(value)}))
    (P/'public-class-preview-request-v1.json').write_text(json.dumps(serial,indent=2)+'\n')
    result=preview.preview(specification)
    if result['status']!='PREVIEW_READY':
        (P/'public-class-preview-refusal-v1.json').write_text(json.dumps(result,indent=2)+'\n');raise ValueError('preview refused; preserved')
    candidates=result.pop('candidates');output=P/'public-class-change-candidate-v1';output.mkdir(exist_ok=False)
    for lang,raw in candidates.items():
        (output/lang).mkdir()
        with directory(output)as fd:write_new(fd,lang+'/chapter.md',raw)
    checks={}
    for label,card in sources.items():
        with directory(roots[label])as fd:raw,_=read(fd,card['path'],65536)
        checks['source_still_pinned:'+label]=sha(raw)==card['sha256']
    for lang,doc in documents.items():
        with directory(docs_root)as fd:raw,_=read(fd,doc['path'],2*1024*1024)
        checks['original_doc_unchanged:'+lang]=raw==doc['bytes']
        with directory(output)as fd:raw,_=read(fd,doc['path'],2*1024*1024)
        checks['candidate_readback:'+lang]=raw==candidates[lang]
        old=doc['bytes'];new=candidates[lang]
        checks['exact_only_cache_line_delta:'+lang]=old.replace(preview.rendered(lang,'Parser._MAX_SIZE',128),preview.rendered(lang,'Parser._MAX_SIZE',512))==new
    unsupported={key:None for key in documentation_maintenance.TOP}
    unsupported.update(schema_version=1,scope_kind='registered-public-source-research')
    try:
        documentation_maintenance.build(unsupported,prepare=False)
        existing_applier={'status':'UNEXPECTED_ACCEPTANCE'}
    except ValueError as error:existing_applier={'status':'EXPECTED_SCOPE_REFUSAL','reason':str(error)}
    receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':result,'checks':checks,'all_checks_pass':all(checks.values()),
             'original_documents_are':'Newly authored isolated research notes, not owner catalog content; generated ownership explicitly registered.',
             'candidate_root':str(output.relative_to(ROOT)),'existing_production_applier':existing_applier,
             'publication_authorized':False,'training_gold':False,'owner_approved':False,
             'scope':'Two real-source typed written-class claims in owned isolated documents. Not arbitrary prose entailment or production integration.',
             'training_exclusion':True,'model_calls':0}
    with(P/'public-class-preview-receipt-v1.json').open('x')as stream:json.dump(receipt,stream,indent=2)
    print(json.dumps({'actions':[x['action']for x in result['decisions']],'physical_checks_pass':all(checks.values()),'existing_applier':existing_applier}))


if __name__=='__main__':main()
