"""Atomic in-memory composition for multiple addressed owned claim bodies.

Research only: one registered EN/PT document group, no applier or publication.
"""
import copy
from contextlib import ExitStack
import hashlib
import importlib.util
import json
import os
from pathlib import Path

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('batch_single_claim', P / 'registered_claim_candidate_v2.py')
single = importlib.util.module_from_spec(spec)
spec.loader.exec_module(single)
workspace = single.workspace
candidates = single.candidates
OWN_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
SINGLE_SHA = hashlib.sha256(Path(single.__file__).read_bytes()).hexdigest()
canonical = single.canonical
sha = lambda raw: hashlib.sha256(raw).hexdigest()


class ExecutionUncertain(ValueError):
    pass


class RegisteredClaimBatch:
    def __init__(self, registration):
        if type(registration) is not dict:
            raise ValueError('explicit batch registration required')
        self.registration = copy.deepcopy(registration)
        r = self.registration
        expected = {'schema_version', 'scope', 'source_registration', 'documentation_root', 'documents', 'claims', 'managed_ownership', 'human_authored'}
        if set(r) != expected or type(r['schema_version']) is not int or r['schema_version'] != 1 or r['scope'] != 'paired-claim-batch-review':
            raise ValueError('closed research batch registration required')
        if r['managed_ownership'] is not True or r['human_authored'] is not False:
            raise ValueError('explicit owned synthetic claim group required')
        if type(r['documents']) is not dict or set(r['documents']) != {'en', 'pt-br'}:
            raise ValueError('one paired document group required')
        if any(type(v) is not dict or set(v) != {'path', 'file_sha256'} for v in r['documents'].values()):
            raise ValueError('closed paired document path/file hashes required')
        if type(r['claims']) is not dict or not 1 <= len(r['claims']) <= 8:
            raise ValueError('one to eight registered claim identities required')
        self.children = {}
        for claim, entry in r['claims'].items():
            if type(entry) is not dict or set(entry) != {'block_sha256'} or type(entry['block_sha256']) is not dict or set(entry['block_sha256']) != {'en', 'pt-br'}:
                raise ValueError('closed paired block identities required')
            child = {'schema_version': 1, 'scope': 'registered-declaration-review', 'source_registration': r['source_registration'], 'documentation_root': r['documentation_root'], 'documents': {lang: {**row, 'block_sha256': entry['block_sha256'][lang]} for lang, row in r['documents'].items()}, 'claim_id': claim, 'managed_ownership': True, 'human_authored': False}
            self.children[claim] = single.RegisteredClaimCandidate(child)
        self._registration_bytes = canonical(r)
        self._registration_sha256 = sha(self._registration_bytes)
        with workspace.directory(r['documentation_root']) as descriptor:
            stat = os.fstat(descriptor)
            self._root_identity = (stat.st_dev, stat.st_ino)

    def configuration(self):
        if canonical(self.registration) != self._registration_bytes:
            raise ValueError('batch registration drift; new instance required')
        return json.loads(self._registration_bytes)

    def prepare(self, requests):
        result = {'version': '0.0.1-research', 'status': 'REFUSED', 'writes': 0, 'model_calls': 0, 'source_executed': False,
                  'owner_approved': False, 'training_gold': False, 'publication_authorized': False,
                  'physical_documentation_certified': False, 'automatic_candidate_applier_supported': False,
                  'registration_sha256': self._registration_sha256}
        try:
            if sha(Path(__file__).read_bytes()) != OWN_SHA or sha(Path(single.__file__).read_bytes()) != SINGLE_SHA:
                raise ValueError('loaded batch/child producer changed; reload required')
            config = self.configuration()
            if type(requests) is not list or not 1 <= len(requests) <= 8:
                raise ValueError('one to eight explicit operations required')
            requests = copy.deepcopy(requests)
            ids = []
            for request in requests:
                if type(request) is not dict or set(request) != {'claim_id', 'packet', 'replacements', 'action'}:
                    raise ValueError('closed batch operation required')
                claim = request['claim_id']
                if type(claim) is not str or claim not in config['claims'] or claim in ids:
                    raise ValueError('unknown or conflicting duplicate claim operation')
                if request['action'] not in ['MODIFY', 'NO-OP'] or type(request['packet']) is not dict or request['packet'].get('logical_contract_id') != claim:
                    raise ValueError('operation action or packet identity outside supported batch profile')
                ids.append(claim)
            with ExitStack() as stack:
                fd = stack.enter_context(workspace.directory(config['documentation_root']))
                stat = os.fstat(fd)
                if (stat.st_dev, stat.st_ino) != self._root_identity:
                    raise ValueError('batch documentation root replaced since registration')
                documents = {}
                for language, entry in config['documents'].items():
                    identity = single.binding.leaf_identity(fd, entry['path'])
                    raw, metadata = workspace.read(fd, entry['path'], candidates.MAX_DOCUMENT)
                    if metadata['sha256'] != entry['file_sha256'] or identity != single.binding.leaf_identity(fd, entry['path']):
                        raise ValueError('registered original batch document changed')
                    blocks = candidates.blocks(raw)
                    documents[language] = {'raw': raw, 'identity': identity, 'blocks': blocks}
                source_fds, source_snapshots = {}, {}
                for when, entry in config['source_registration']['sources'].items():
                    source_fd = stack.enter_context(workspace.directory(entry['root']))
                    source_fds[when] = source_fd
                    stat = os.fstat(source_fd)
                    files = {}
                    for name, expected in entry['files'].items():
                        identity = single.binding.leaf_identity(source_fd, name)
                        raw, metadata = workspace.read(source_fd, name, 65536)
                        if metadata['sha256'] != expected or identity != single.binding.leaf_identity(source_fd, name):
                            raise ValueError('registered batch source changed')
                        files[name] = {'identity': identity, 'raw': raw}
                    source_snapshots[when] = {'root': (stat.st_dev, stat.st_ino), 'files': files}
                edits = {language: [] for language in documents}
                trace = []
                for request in requests:
                    claim = request['claim_id']
                    child = self.children[claim]
                    observed = copy.deepcopy(child.prepare(copy.deepcopy(request['packet']), copy.deepcopy(request['replacements']), request['action']))
                    if observed.get('source_executed') is not False:
                        raise ExecutionUncertain('child execution report is unknown or inconsistent; no candidate can be certified')
                    if observed.get('status') != 'PREPARED' or observed.get('action') != request['action']:
                        raise ValueError('a child refused the complete batch: ' + str(observed.get('reason', 'unknown')))
                    if observed.get('producer_sha256') != SINGLE_SHA or observed.get('registration_sha256') != child._registration_sha256:
                        raise ValueError('child producer or registration identity differs')
                    for flag in ['owner_approved', 'training_gold', 'publication_authorized', 'physical_documentation_certified', 'automatic_candidate_applier_supported']:
                        if observed.get(flag) is not False:
                            raise ValueError('child changed a false authority contract')
                    if observed.get('physical_claim_block_bytes_verified') is not True or observed.get('physical_source_bytes_and_registered_paths_verified') is not True:
                        raise ValueError('child did not verify physical claim/source bytes')
                    for count in ['writes', 'model_calls']:
                        if type(observed.get(count)) is not int or observed[count] != 0:
                            raise ValueError('child changed zero-operation contract')
                    current_packet = copy.deepcopy(request['packet'])
                    if request['action'] == 'MODIFY':
                        replacements = request['replacements']
                        if type(replacements) is not dict or set(replacements) != {'en', 'pt-br'}:
                            raise ValueError('paired replacements missing')
                        for text in replacements.values():
                            if type(text) is not str or len(text.encode()) > 65536 or '<!-- documentation-agent:' in text:
                                raise ValueError('invalid marker-bearing/bounded replacement')
                        current_packet['documentation'] = {lang: candidates.claim_text(text.encode()) for lang, text in replacements.items()}
                    if observed['original_source_observation'].get('request_sha256') != sha(canonical(request['packet'])) or observed['replacement_source_observation'].get('request_sha256') != sha(canonical(current_packet)):
                        raise ValueError('child source observations address different original/replacement packets')
                    paired = observed.get('candidates')
                    if type(paired) is not dict or set(paired) != {'en', 'pt-br'}:
                        raise ValueError('incomplete child language pair')
                    hashes = {}
                    for language, document in documents.items():
                        row = paired[language]
                        if type(row) is not dict or type(row.get('markdown')) is not str or row.get('path') != config['documents'][language]['path']:
                            raise ValueError('child document identity/schema differs')
                        raw = document['raw']
                        proposed = row['markdown'].encode()
                        if len(proposed) > candidates.MAX_DOCUMENT or row.get('original_sha256') != sha(raw) or row.get('candidate_sha256') != sha(proposed):
                            raise ValueError('child original/output hash differs')
                        if claim not in document['blocks']:
                            raise ValueError('addressed batch claim block missing')
                        old_start, old_end = document['blocks'][claim]
                        proposed_blocks = candidates.blocks(proposed)
                        if claim not in proposed_blocks:
                            raise ValueError('child removed addressed block')
                        new_start, new_end = proposed_blocks[claim]
                        if raw[:old_start.end()] != proposed[:new_start.end()] or raw[old_end.start():] != proposed[new_end.start():]:
                            raise ValueError('child changed bytes outside its own addressed body')
                        body = proposed[new_start.end():new_end.start()]
                        expected_body = raw[old_start.end():old_end.start()] if request['action'] == 'NO-OP' else request['replacements'][language].encode()
                        if body != expected_body:
                            raise ValueError('child output differs from the requested paired replacement')
                        edits[language].append((old_start.end(), old_end.start(), body, claim))
                        hashes[language] = row['candidate_sha256']
                    trace.append({'claim_id': claim, 'action': request['action'], 'child_producer_sha256': SINGLE_SHA, 'child_registration_sha256': child._registration_sha256, 'child_result_sha256': sha(canonical(observed)), 'individual_candidate_hashes': hashes, 'original_packet_sha256': sha(canonical(request['packet'])), 'proposed_packet_sha256': sha(canonical(current_packet))})
                prepared = {}
                for language, document in documents.items():
                    raw = document['raw']
                    parts, untouched, cursor = [], [], 0
                    for start, end, body, claim in sorted(edits[language]):
                        if start < cursor:
                            raise ValueError('overlapping batch claim edits')
                        outside = raw[cursor:start]
                        parts.extend((outside, body))
                        untouched.append(outside)
                        cursor = end
                    parts.append(raw[cursor:])
                    untouched.append(raw[cursor:])
                    proposed = b''.join(parts)
                    if len(proposed) > candidates.MAX_DOCUMENT:
                        raise ValueError('composed batch output exceeds document bound')
                    candidates.blocks(proposed)
                    prepared[language] = {'markdown': proposed.decode(), 'path': config['documents'][language]['path'], 'original_sha256': sha(raw), 'candidate_sha256': sha(proposed), 'outside_all_addressed_bodies_sha256': sha(b''.join(untouched)), 'changed': raw != proposed}
                for language, entry in config['documents'].items():
                    raw, metadata = workspace.read(fd, entry['path'], candidates.MAX_DOCUMENT)
                    if raw != documents[language]['raw'] or single.binding.leaf_identity(fd, entry['path']) != documents[language]['identity']:
                        raise ValueError('batch documents changed while children were prepared')
                with workspace.directory(config['documentation_root']) as reopened:
                    stat = os.fstat(reopened)
                    if (stat.st_dev, stat.st_ino) != self._root_identity:
                        raise ValueError('batch documentation root path changed')
                for when, source_fd in source_fds.items():
                    entry = config['source_registration']['sources'][when]
                    with workspace.directory(entry['root']) as reopened:
                        stat = os.fstat(reopened)
                        if (stat.st_dev, stat.st_ino) != source_snapshots[when]['root']:
                            raise ValueError('batch source root path changed')
                    for name, snapshot in source_snapshots[when]['files'].items():
                        raw, metadata = workspace.read(source_fd, name, 65536)
                        if raw != snapshot['raw'] or single.binding.leaf_identity(source_fd, name) != snapshot['identity']:
                            raise ValueError('batch source file path/bytes changed between children')
                self.configuration()
                result.update(status='PREPARED', candidates=prepared, operations=trace, producer_sha256=OWN_SHA,
                              atomic_language_and_operation_pair=True, physical_claim_blocks_verified=True,
                              limitations=['One registered document pair; only addressed owned body ranges are changed in memory.', 'No whole-document citation/navigation semantics, upstream Git authenticity, production integration or publication is certified.', 'Synthetic relocation evidence is not a real upstream rename or package import proof.', 'Sequential descriptor rechecks do not lock out future owner edits.'])
                if len(canonical(result)) > 2 * candidates.MAX_DOCUMENT + 65536:
                    raise ValueError('batch result byte bound exceeded')
            return result
        except ExecutionUncertain as error:
            result.update(status='REFUSED', source_executed=None, reason=str(error))
            result.pop('candidates', None)
            return result
        except (ValueError, TypeError, KeyError, UnicodeError, OSError, RecursionError) as error:
            result.update(status='REFUSED', reason=str(error)[:1024])
            result.pop('candidates', None)
            return result
