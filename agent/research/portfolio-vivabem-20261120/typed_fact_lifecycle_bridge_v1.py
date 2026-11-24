"""Closed research bridge over reviewed source shapes and mapped bilingual claims.

No production planner replacement, arbitrary prose proof, publication or source writes.
"""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[2]
REGISTRY_SHA256 = 'da76c3983a13026606a3f2ad859eb47530a17cf60baf574cdfb85efff79abcbb'
VERSION = 'typed-fact-lifecycle-bridge/0.0.1-research'


class Unsupported(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def require(value, reason):
    if not value:
        raise Unsupported(reason)


class Bridge:
    def __init__(self):
        path = ROOT / 'typed-fact-bridge-registry-v2.json'
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == REGISTRY_SHA256, 'unregistered manual fact/text registry')
        registry = json.loads(raw)
        self.providers = {p['family']: p for p in registry['providers']}
        inventory = json.loads((ROOT / 'collection-inventory-v2.json').read_text())['repositories']
        self.repositories = {r['repository']: r['absolute_path'] for r in inventory}
        self.cache = {}

    def observe(self, family, revision):
        require(family in self.providers, 'no registered selected-fact provider')
        require(isinstance(revision, str) and re.fullmatch(r'[0-9a-f]{40}', revision), 'verified source revision unavailable')
        key = family, revision
        if key in self.cache:
            return copy.deepcopy(self.cache[key])
        provider = self.providers[family]
        command = ['git', '-c', 'core.fsmonitor=false', '-C', self.repositories[family],
                   'show', revision + ':' + provider['path']]
        run = subprocess.run(command, env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'),
                             capture_output=True, timeout=15)
        require(run.returncode == 0, 'requested Git source object unavailable; no fetch')
        require(len(run.stdout) <= 1024 * 1024, 'source exceeds bounded provider input')
        text = run.stdout.decode('utf-8')
        if family == 'starlette':
            tree = ast.parse(text)
            classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Config']
            require(len(classes) == 1, 'unique Config owner required')
            methods = [n for n in classes[0].body if isinstance(n, ast.FunctionDef) and n.name == '_perform_cast']
            require(len(methods) == 1, 'unique selected method required')
            method = methods[0]
            shape = ast.dump(method, include_attributes=False)
            quote = ast.get_source_segment(text, method)
            lines = [method.lineno, method.end_lineno]
            mechanism = 'Python AST complete selected declaration fingerprint'
        elif family == 'chi':
            tool = REPOSITORY / 'agent/tools/go_source_ast.py'
            spec = importlib.util.spec_from_file_location('bridge_go_syntax', tool)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            result = module.run(json.dumps({'source': text, 'path': provider['path'],
                                            'selectors': [provider['selector']]}).encode())
            require(len(result['units']) == 1, 'unique native Go declaration')
            unit = result['units'][0]
            shape = quote = unit['quote']
            lines = [unit['start_line'], unit['end_line']]
            mechanism = 'Verified native Go syntax declaration + registered manual semantics'
        else:
            script = (ROOT / 'observe_fastify_revision_v1.cjs').read_text()
            run = subprocess.run(['docker', 'exec', '-i', '-e', 'NODE_OPTIONS=', '-w', '/app/frontend',
                                  'engineering-library-frontend-1', 'node', '-e', script],
                                 input=json.dumps([{'revision': revision, 'path': provider['path'],
                                                    'source': text}]).encode(), capture_output=True, timeout=20)
            require(run.returncode == 0, 'existing TypeScript provider unavailable/refused source')
            result = json.loads(run.stdout)
            require(len(result['rows']) == 1 and len(result['rows'][0]['observations']) == 1,
                    'unique JS guard owner required')
            unit = result['rows'][0]['observations'][0]
            fields = {k: unit[k] for k in ['owners', 'condition', 'branch', 'else_branch']}
            shape = canonical(fields)
            quote = unit['condition'] + '\n' + unit['branch'] + '\n' + unit['else_branch']
            lines = [unit['start_line'], unit['end_line']]
            mechanism = 'Existing TypeScript lexical guard/branch AST + registered manual semantics'
        digest = hashlib.sha256(shape.encode()).hexdigest()
        registered = [s for s in provider['shapes'] if s['shape_sha256'] == digest]
        require(len(registered) == 1, 'selected source shape not in reviewed closed provider')
        expected = registered[0]
        # The accepted claim concerns only the written selected shape, not module execution.
        result = {'family': family, 'revision': revision, 'path': provider['path'],
                  'selector': provider['selector'], 'source_sha256': hashlib.sha256(text.encode()).hexdigest(),
                  'shape_sha256': digest, 'typed_fact': copy.deepcopy(expected['typed_fact']),
                  'source_lines': lines, 'quote': quote, 'mechanism': mechanism,
                  'manual_semantic_basis': provider['proof_review'],
                  'source_executed': False, 'runtime_bindings_verified': False,
                  'repository_complete_scope_proven': False}
        self.cache[key] = copy.deepcopy(result)
        return result

    def decide(self, packet):
        result = {'version': VERSION, 'action': 'INCONCLUSIVE', 'technical_recommendation': True,
                  'owner_approved': False, 'training_gold': False, 'publication_authorized': False,
                  'model_calls': 0, 'application_writes': 0, 'source_executed_by_bridge': False,
                  'candidate_application': 'OWNER_REVIEW_REQUIRED', 'evidence': {},
                  'limitations': ['Three reviewed selected source shapes/facts only, not arbitrary code/prose.',
                                 'Fingerprint integrity binds manual semantic registration; hashes are not general truth verification.',
                                 'No complete repository, runtime/global-binding or independent human proof.',
                                 'No source/absence-based REMOVE capability or automatic application.']}
        try:
            required = {'id', 'family', 'before_revision', 'after_revision', 'documentation',
                        'scope', 'human_authored'}
            require(isinstance(packet, dict) and required <= set(packet)
                    and set(packet) <= required | {'provided_current_fact'}, 'packet schema outside closed protocol')
            require(type(packet['human_authored']) is bool, 'authority flag must be Boolean')
            require(packet['scope'] == 'registered-selected-contract', 'partial/unknown selected contract scope')
            family = packet['family']
            require(family in self.providers, 'unknown provider')
            before = self.observe(family, packet['before_revision'])
            current = self.observe(family, packet['after_revision'])
            result['evidence'] = {'previous': before, 'current': current}
            if 'provided_current_fact' in packet:
                require(canonical(packet['provided_current_fact']) == canonical(current['typed_fact']),
                        'supplied fact contradicts independently reacquired source')
            document = packet['documentation']
            require(isinstance(document, dict) and set(document) == {'text', 'typed_claim'}, 'document mapping schema')
            require(isinstance(document['text'], dict) and set(document['text']) == {'en', 'pt-BR'},
                    'both registered document languages required')
            variants = self.providers[family]['registered_doc_variants']
            matched = [v for v in variants if canonical(v['text']) == canonical(document['text'])]
            require(len(matched) == 1, 'unregistered prose requires independent human/source review')
            require(canonical(document['typed_claim']) == canonical(matched[0]['typed_claim']),
                    'false typed value attached to registered prose/citation')
            if canonical(document['typed_claim']) == canonical(current['typed_fact']):
                result.update(action='NO-OP', reason='Current verified selected fact matches the registered bilingual claim.',
                              preserve_existing_document_bytes=True, proposed_documentation=None)
            else:
                require(canonical(document['typed_claim']) == canonical(before['typed_fact']),
                        'registered old claim is not supported by supplied previous source')
                replacement = [v for v in variants if canonical(v['typed_claim']) == canonical(current['typed_fact'])]
                require(len(replacement) == 1, 'no reviewed bilingual current-claim renderer')
                result.update(action='MODIFY', reason='Positive verified current selected fact contradicts the supported registered old claim.',
                              preserve_existing_document_bytes=True,
                              proposed_documentation=copy.deepcopy(replacement[0]['text']))
            result['candidate_application'] = ('HUMAN_ALIGNMENT_REQUIRED_NO_AUTOMATIC_APPLY' if packet['human_authored']
                                               else 'ISOLATED_REVIEW_CANDIDATE_ONLY')
        except (Unsupported, ValueError, KeyError, TypeError, SyntaxError, subprocess.SubprocessError) as error:
            result['reason'] = str(error)
            result['proposed_documentation'] = None
        return result
