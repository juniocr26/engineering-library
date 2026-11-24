"""Research-only direct written class members; no runtime binding resolution."""
import ast
import hashlib
import importlib.util
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('class_member_shared', HERE / 'module_contract_observer_v5.py')
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
VERSION = '0.0.3-research'
OWN_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
SHARED_SHA = hashlib.sha256(Path(shared.__file__).read_bytes()).hexdigest()
RETRIEVAL_SHA = hashlib.sha256(Path(shared.retrieval.__file__).read_bytes()).hexdigest()


def observe(card, selector):
    result = {'status': 'INCONCLUSIVE', 'version': VERSION, 'source_executed': False,
              'runtime_bindings_verified': False, 'training_gold': False,
              'owner_approved': False, 'publication_authorized': False,
              'scope': 'DIRECT_WRITTEN_CLASS_MEMBER_NOT_RUNTIME_ATTRIBUTE',
              'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    try:
        if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != OWN_SHA or hashlib.sha256(Path(shared.__file__).read_bytes()).hexdigest() != SHARED_SHA or hashlib.sha256(Path(shared.retrieval.__file__).read_bytes()).hexdigest() != RETRIEVAL_SHA:
            raise ValueError('loaded class observer/shared extractor implementation changed; explicit reload required')
        if type(card) is not dict or set(card) != {'path', 'revision', 'source', 'sha256'}:
            raise ValueError('closed source card required')
        card = dict(card)
        if not all(type(v) is str for v in card.values()):
            raise ValueError('string card fields required')
        shared.retrieval.relative_path(card['path'])
        if not card['path'].endswith('.py') or not card['revision'] or len(card['revision'].encode()) > 256:
            raise ValueError('bounded Python source identity required')
        if type(selector) is not str or len(selector) > 256 or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,127}\.[A-Za-z_][A-Za-z0-9_]{0,127}', selector):
            raise ValueError('explicit Class.member selector required')
        raw = card['source'].encode()
        if len(raw) > 65536 or b'\0' in raw or shared.sha(raw) != card['sha256']:
            raise ValueError('source identity or byte bound refused')
        tree = ast.parse(card['source'], type_comments=True)
        if sum(1 for _ in ast.walk(tree)) > 16384:
            raise ValueError('AST node bound refused')
        compile(tree, card['path'], 'exec', dont_inherit=True)
        owner, name = selector.split('.')
        classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == owner]
        if len(classes) != 1:
            raise ValueError('unique direct class declaration not established')
        # Require a unique lexical declaration owner. This does not resolve runtime mutation.
        owner_statements = []
        for statement in tree.body:
            names, _ = shared.module_bindings(ast.Module(body=[statement], type_ignores=[]))
            if owner in names:
                owner_statements.append(statement)
        if owner_statements != classes:
            raise ValueError('class owner also bound by another written statement')
        cls = classes[0]
        members = []
        for node in cls.body:
            names, _ = shared.module_bindings(ast.Module(body=[node], type_ignores=[]))
            if name in names:
                members.append(node)
        header_first = min([cls.lineno] + [n.lineno for n in cls.decorator_list])
        header_last = cls.body[0].lineno if cls.body else cls.lineno
        source_lines = card['source'].splitlines(keepends=True)
        header_quote = ''.join(source_lines[header_first - 1:header_last])
        if len(header_quote.encode()) > 6144:
            raise ValueError('class ownership header quote exceeds bound')
        result['class_header_evidence'] = {'first_line': header_first, 'last_line': header_last,
            'quote': header_quote, 'quote_sha256': shared.sha(header_quote.encode()),
            'quote_byte_start': len(''.join(source_lines[:header_first - 1]).encode()),
            'quote_byte_end': len(''.join(source_lines[:header_last]).encode()),
            'complete_class': False, 'purpose': 'Written class owner, decorators, bases and keywords; may include first member line.'}
        result.update(source_path=card['path'], revision=card['revision'], source_sha256=card['sha256'], selector=selector,
                      class_decorators=[ast.unparse(n) for n in cls.decorator_list],
                      class_bases=[ast.unparse(n) for n in cls.bases],
                      class_keywords=[{'name': n.arg, 'expression': ast.unparse(n.value)} for n in cls.keywords],
                      runtime_limitations=['Direct written members only; decorators, metaclasses, imports, inheritance and later mutations unresolved.',
                                           'No absence-based retirement, no runtime cache bound or thread-safety guarantee.'])
        if not members:
            result['status'] = 'NO_DIRECT_WRITTEN_MEMBER'
            return result
        if len(members) != 1:
            raise ValueError('multiple written member bindings')
        node = members[0]
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Assign, ast.AnnAssign)):
            raise ValueError('member is conditional or outside supported declaration profile')
        if isinstance(node, ast.Assign) and (len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name) or node.targets[0].id != name):
            raise ValueError('simple assignment member required')
        if isinstance(node, ast.AnnAssign) and (not isinstance(node.target, ast.Name) or node.target.id != name):
            raise ValueError('simple annotated member required')
        first = min([node.lineno] + [n.lineno for n in getattr(node, 'decorator_list', [])])
        lines = card['source'].splitlines(keepends=True)
        text = ''.join(lines[first - 1:node.end_lineno])
        if not text or len(text.encode()) > 6144:
            raise ValueError('whole member quote exceeds bound')
        result.update(status='WRITTEN_CLASS_MEMBER', evidence={'first_line': first, 'last_line': node.end_lineno,
                      'quote': text, 'quote_sha256': shared.sha(text.encode()),
                      'quote_byte_start': len(''.join(lines[:first - 1]).encode()),
                      'quote_byte_end': len(''.join(lines[:node.end_lineno]).encode()), 'complete_member': True})
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            calls = [n for n in ast.walk(node) if isinstance(n, ast.Call)]
            if len(calls) > 128:
                raise ValueError('written call count exceeds bound')
            call_records = [{'line': n.lineno, 'expression': ast.unparse(n)} for n in calls]
            if sum(len(n['expression'].encode()) for n in call_records) > 12288:
                raise ValueError('written call expression byte bound exceeded')
            result.update(member_kind='method', signature=shared.signature(node),
                          written_calls_scope='Lexical subtree includes nested/deferred bodies; no execution, ordering or call-target resolution claim.',
                          method_decorators=[ast.unparse(n) for n in node.decorator_list],
                          calls_written=call_records)
        else:
            result.update(member_kind='class-assignment', written_value=shared.literal_or_expression(node.value))
        return result
    except (ValueError, TypeError, SyntaxError, RecursionError, UnicodeError) as error:
        result.update(status='INCONCLUSIVE', reason=str(error)[:1024])
        return result
