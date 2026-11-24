"""Read-only binding of inline declaration claims to frozen local source files.

Operator registration is trusted configuration, not a signature or independent
Git authentication. Sequential checks do not freeze future owner filesystem edits.
"""
import copy
from contextlib import ExitStack
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import sys

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
sys.path.insert(0,str(ROOT/'agent/tools'))
import documentation_workspace as workspace
spec=importlib.util.spec_from_file_location('registered_decl_adapter',P/'closed_declaration_lifecycle_v2.py')
adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
OWN_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
ADAPTER_SHA=hashlib.sha256(Path(adapter.__file__).read_bytes()).hexdigest()
WORKSPACE_SHA=hashlib.sha256(Path(workspace.__file__).read_bytes()).hexdigest()
SHA=re.compile(r'[0-9a-f]{64}')


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()


def leaf_identity(root_fd,name):
    with workspace.parent(root_fd,name)as(parent_fd,leaf):
        entry=os.stat(leaf,dir_fd=parent_fd,follow_symlinks=False)
        parent=os.fstat(parent_fd)
        if not stat.S_ISREG(entry.st_mode):raise ValueError('registered source is not a regular file')
        return (parent.st_dev,parent.st_ino,entry.st_dev,entry.st_ino,entry.st_size,entry.st_mtime_ns,entry.st_ctime_ns,stat.S_IMODE(entry.st_mode))


class RegisteredDeclaration:
    def __init__(self,registration):
        if type(registration)is not dict:raise ValueError('explicit operator registration required')
        self.registration=copy.deepcopy(registration)
        r=self.registration
        if set(r)!={'schema_version','scope','sources','contracts'}or type(r['schema_version'])is not int or r['schema_version']!=1 or r['scope']!='registered-module-research':
            raise ValueError('closed registered module research scope required')
        if type(r['sources'])is not dict or set(r['sources'])!={'previous','current'}:raise ValueError('paired registered source roots required')
        root_identities={}
        for when,source in r['sources'].items():
            if type(source)is not dict or set(source)!={'root','revision','files'}:raise ValueError('closed source registration required')
            if type(source['root'])is not str or type(source['revision'])is not str or not re.fullmatch(r'[0-9a-f]{40}',source['revision']):raise ValueError('explicit root and operator-pinned revision required')
            root=Path(source['root'])
            if not root.is_absolute()or'..'in root.parts:raise ValueError('absolute canonical source root required')
            with workspace.directory(root)as fd:
                entry=os.fstat(fd);root_identities[when]=(entry.st_dev,entry.st_ino)
            files=source['files']
            if type(files)is not dict or not 1<=len(files)<=16:raise ValueError('bounded explicit module file registry required')
            for name,digest in files.items():
                workspace.relative_path(name)
                if not name.endswith('.py')or type(digest)is not str or not SHA.fullmatch(digest):raise ValueError('registered Python path/hash required')
        contracts=r['contracts']
        if type(contracts)is not dict or not 1<=len(contracts)<=16:raise ValueError('bounded logical-contract allowlist required')
        for logical,entry in contracts.items():
            if type(logical)is not str or len(logical)>256 or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*',logical):raise ValueError('invalid registered logical identity')
            if type(entry)is not dict or set(entry)!={'selector','previous_path','current_path'}or not adapter.engine.valid_name(entry['selector'])or entry['selector']!=logical.rsplit('.',1)[-1]:raise ValueError('explicit matching selector required')
            for when in ['previous','current']:
                if entry[when+'_path']not in r['sources'][when]['files']:raise ValueError('contract path outside source allowlist')
        self._registration_bytes=canonical(r)
        self._registration_sha256=hashlib.sha256(self._registration_bytes).hexdigest()
        self._root_identities=root_identities

    def configuration(self):
        if canonical(self.registration)!=self._registration_bytes:raise ValueError('operator registration drift;explicit new instance required')
        return json.loads(self._registration_bytes)

    def decide(self,packet):
        result={'version':'0.0.2-research','action':'INCONCLUSIVE','writes':0,'model_calls':0,'source_executed':False,
                'physical_source_bytes_and_registered_paths_verified':False,'physical_documentation_certified':False,
                'upstream_git_revision_authenticated':False,'owner_approved':False,'training_gold':False,
                'publication_authorized':False,'automatic_candidate_applier_supported':False,
                'registration_sha256':self._registration_sha256}
        try:
            if hashlib.sha256(Path(__file__).read_bytes()).hexdigest()!=OWN_SHA or hashlib.sha256(Path(adapter.__file__).read_bytes()).hexdigest()!=ADAPTER_SHA or hashlib.sha256(Path(workspace.__file__).read_bytes()).hexdigest()!=WORKSPACE_SHA:
                raise ValueError('loaded binding/adapter/filesystem implementation changed;reload required')
            config=self.configuration()
            if type(packet)is not dict:raise ValueError('explicit closed packet required')
            packet=copy.deepcopy(packet)
            if set(packet)!=adapter.TOP:raise ValueError('original packet schema required')
            logical=packet['logical_contract_id']
            if type(logical)is not str or logical not in config['contracts']:raise ValueError('logical contract outside frozen operator allowlist')
            contract=config['contracts'][logical]
            request_sha256=hashlib.sha256(canonical(packet)).hexdigest()
            snapshots={};fds={}
            with ExitStack()as stack:
                for when,key in [('previous','previous_source'),('current','current_source')]:
                    source=config['sources'][when];fd=stack.enter_context(workspace.directory(source['root']));fds[when]=fd
                    root_stat=os.fstat(fd)
                    if (root_stat.st_dev,root_stat.st_ino)!=self._root_identities[when]:raise ValueError('registered root replaced since configuration')
                    name=contract[when+'_path'];identity=leaf_identity(fd,name);raw,metadata=workspace.read(fd,name,65536)
                    if identity!=leaf_identity(fd,name):raise ValueError('physical source path changed while reading')
                    if metadata['sha256']!=source['files'][name]or type(packet[key])is not str or packet[key].encode()!=raw:
                        raise ValueError('inline source differs from registered physical bytes')
                    snapshots[when]={'path':name,'sha256':metadata['sha256'],'size':len(raw),'identity':identity,
                                     'operator_reported_revision':source['revision'],'raw':raw}
                observed=copy.deepcopy(adapter.decision(copy.deepcopy(packet)))
                if type(observed)is not dict or observed.get('action')not in ['ADD','MODIFY','NO-OP','INCONCLUSIVE']:
                    raise ValueError('delegate result outside closed no-retirement contract')
                for flag in ['source_executed','runtime_bindings_verified','physical_source_paths_authenticated','physical_documentation_certified','owner_approved','training_gold','publication_authorized','automatic_candidate_applier_supported']:
                    if observed.get(flag)is not False:
                        result['upstream_contract_rejection']={flag:observed.get(flag)}
                        if flag=='source_executed':
                            result['source_executed']=None
                            result['source_execution_status']='No source executed by binding layer;delegate execution report violates expected contract and is not relabeled false.'
                        raise ValueError('delegate changed required false authority/execution flag: '+flag)
                for count in ['model_calls','writes']:
                    if type(observed.get(count))is not int or observed[count]!=0:
                        raise ValueError('delegate changed zero-operation contract: '+count)
                if observed.get('producer_sha256')!=ADAPTER_SHA or observed.get('engine_sha256')!=adapter.ENGINE_SHA:
                    raise ValueError('delegate producer identity does not match loaded frozen adapter')
                if observed['action']!='INCONCLUSIVE'and observed.get('original_packet_sha256')!=request_sha256:
                    raise ValueError('delegate observation belongs to different source/documentation packet')
                if (observed['action']!='INCONCLUSIVE'or observed.get('selector')is not None)and observed.get('selector')!=contract['selector']:
                    raise ValueError('inner selector differs from registered logical contract')
                for when in ['previous','current']:
                    source=config['sources'][when];snapshot=snapshots[when];fd=fds[when]
                    with workspace.directory(source['root'])as reopened:
                        a,b=os.fstat(fd),os.fstat(reopened)
                        if (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino):raise ValueError('source root changed during declaration observation')
                    raw,metadata=workspace.read(fd,snapshot['path'],65536)
                    if raw!=snapshot['raw']or metadata['sha256']!=snapshot['sha256']or leaf_identity(fd,snapshot['path'])!=snapshot['identity']:
                        raise ValueError('physical source bytes/path identity changed during declaration observation')
                self.configuration()
                result.update(action=observed['action'],reason=observed['reason'],observation=observed,request_sha256=request_sha256,
                              physical_source_bytes_and_registered_paths_verified=True,
                              physical_source_binding={when:{key:value for key,value in item.items()if key not in['raw','identity']}for when,item in snapshots.items()},
                              binding_scope='Descriptor-checked local registered paths/bytes at completion;operator revision assertions are not independent Git authentication and future edits are not frozen.')
            return result
        except (ValueError,TypeError,KeyError,UnicodeError,OSError,RecursionError)as error:
            result.update(action='INCONCLUSIVE',reason=str(error)[:1024]);return result
