"""Read-only research budget reconstruction; not a reservation or Ruby router."""
import copy,hashlib,json,os,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'agent/tools'))
from documentation_retrieval import HelperRetrieval,canonical,strict_json
from documentation_workspace import census,directory,read,same_root
VERSION='research-recovery-budget-audit-0.1.0'
KEY=re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z')

def audit(registry,journal_root,request_ids,*,total_steps,total_quote_bytes):
    base={'version':VERSION,'status':'REFUSED','source_executed':False,'runtime_bindings_verified':False,'owner_approved':False,'publication_allowed':False,'reservation_created':False,'automatic_retry_allowed':False}
    try:
        registry=copy.deepcopy(registry);ids=copy.deepcopy(request_ids)
        if type(total_steps)is not int or not 1<=total_steps<=16 or type(total_quote_bytes)is not int or not 1<=total_quote_bytes<=98304:raise ValueError('invalid frozen total budget')
        if not isinstance(ids,list)or not 1<=len(ids)<=16 or any(not isinstance(key,str)or not KEY.fullmatch(key)for key in ids)or len(set(ids))!=len(ids):raise ValueError('invalid explicit request identity list')
        helper=HelperRetrieval(registry,str(journal_root),max_steps=1,max_quote_bytes=1)
        expected={key+suffix for key in ids for suffix in ['.request.json','.result.json','.receipt.json']}
        snapshot={};used_bytes=0
        with directory(journal_root)as fd:
            if set(census(fd,maximum=48))!=expected:raise ValueError('journal census differs from complete explicit receipt triples')
            identity=(os.fstat(fd).st_dev,os.fstat(fd).st_ino)
            for name in sorted(expected):snapshot[name]=read(fd,name,16384)[0]
            for key in ids:
                req=strict_json(snapshot[key+'.request.json'])
                if not isinstance(req,dict)or req.get('request_id')!=key:raise ValueError('request identity differs from registered journal key')
                response=helper.request(req)
                if response.get('status')!='DUPLICATE'or response.get('original_status')!='FOUND':raise ValueError('cached operation is not a verified completed FOUND result: '+str(response.get('status')))
                cached=strict_json(snapshot[key+'.result.json'])
                if hashlib.sha256(snapshot[key+'.result.json']).hexdigest()!=response['result_sha256']:raise ValueError('validated result differs from initial snapshot')
                # Per-instance cumulative counters may reset; charge each exact delivered quote once.
                used_bytes+=cached['quote_bytes']
            if set(census(fd,maximum=48))!=expected or any(read(fd,name,16384)[0]!=raw for name,raw in snapshot.items())or not same_root(journal_root,fd):raise ValueError('journal changed during budget reconstruction')
            helper.configuration()
        used_steps=len(ids)
        if used_steps>total_steps or used_bytes>total_quote_bytes:raise ValueError('completed history already exceeds frozen total budget')
        remaining_steps=total_steps-used_steps;remaining_bytes=total_quote_bytes-used_bytes
        base.update(status='EXHAUSTED'if remaining_steps==0 or remaining_bytes==0 else'AVAILABLE',used_steps=used_steps,used_quote_bytes=used_bytes,remaining_steps=remaining_steps,remaining_quote_bytes=remaining_bytes,journal_identity=list(identity),registry_sha256=helper.registry_sha256,history_sha256=hashlib.sha256(canonical({name:hashlib.sha256(raw).hexdigest()for name,raw in snapshot.items()})).hexdigest(),snapshot_hashes={name:hashlib.sha256(raw).hexdigest()for name,raw in snapshot.items()},limitations=['Advisory reconstruction under operator-exclusive journal access; no interprocess lock or atomic future reservation.','No automatic retry of interrupted, missing-receipt, inconclusive, legacy or unknown operations.','Caller must revalidate the snapshot and pass only remaining budgets to any newly constructed helper.','This audit does not inject cached quotes and does not authenticate operator registry revisions against Git.'])
    except (ValueError,OSError,KeyError,TypeError,RecursionError)as error:base['reason']=str(error)
    return base
