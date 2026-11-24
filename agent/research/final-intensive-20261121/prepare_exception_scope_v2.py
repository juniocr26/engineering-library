"""Freeze literal exception-scope controls for the new maintenance candidate."""
from pathlib import Path
import datetime
import hashlib
import json

P = Path(__file__).resolve().parent
E = P/'real-revision-evidence-v1/after/agent/tools'
helper = (E/'documentation_retrieval.py').read_text()
job = (E/'documentation_job_budget.py').read_text()
outer = 'except (RetrievalRefused, WorkspaceRefused, ValueError, OSError, UnicodeError, KeyError, TypeError, RecursionError) as error:'
inner = 'except (RetrievalRefused, ValueError, OSError, UnicodeError, subprocess.SubprocessError, RecursionError) as error:'
assert helper.count(outer) == 1 and helper.count(inner) == 1
cases = [
    ('original', helper, job, {'cached_outer_explicit_subprocess_catch': False, 'fresh_explicit_subprocess_catch': True, 'job_explicit_exception_catch': True, 'cached_call_count': 1}),
    ('benign-comment', helper+'\n# Owned benign comment control.\n', job, {'cached_outer_explicit_subprocess_catch': False, 'fresh_explicit_subprocess_catch': True, 'job_explicit_exception_catch': True, 'cached_call_count': 1}),
    ('outer-adds-subprocess', helper.replace(outer, outer.replace('RecursionError)', 'RecursionError, subprocess.SubprocessError)')), job, {'cached_outer_explicit_subprocess_catch': True, 'fresh_explicit_subprocess_catch': True, 'job_explicit_exception_catch': True, 'cached_call_count': 1}),
    ('fresh-removes-subprocess', helper.replace(inner, inner.replace('subprocess.SubprocessError, ', '')), job, {'cached_outer_explicit_subprocess_catch': False, 'fresh_explicit_subprocess_catch': False, 'job_explicit_exception_catch': True, 'cached_call_count': 1}),
    ('job-only-runtimeerror', helper, job.replace('except Exception as error:', 'except RuntimeError as error:'), {'cached_outer_explicit_subprocess_catch': False, 'fresh_explicit_subprocess_catch': True, 'job_explicit_exception_catch': False, 'cached_call_count': 1}),
    ('remove-cached-validation', helper.replace('                    validate_cached(cached, request, request_bytes, registry_sha256, raw, identity)', '                    pass  # Owned removal control'), job, {'cached_outer_explicit_subprocess_catch': None, 'fresh_explicit_subprocess_catch': True, 'job_explicit_exception_catch': True, 'cached_call_count': 0}),
    ('unrelated-nested-function', helper+'\ndef unrelated():\n    try:\n        validate_cached(None, None, None, None, None, None)\n    except subprocess.SubprocessError:\n        pass\n', job, {'cached_outer_explicit_subprocess_catch': False, 'fresh_explicit_subprocess_catch': True, 'job_explicit_exception_catch': True, 'cached_call_count': 1}),
    ('unrelated-string-decoy', helper+'\n# except subprocess.SubprocessError: is not a handler.\nDECOY = "validate_cached(cached)"\n', job, {'cached_outer_explicit_subprocess_catch': False, 'fresh_explicit_subprocess_catch': True, 'job_explicit_exception_catch': True, 'cached_call_count': 1}),
]
out = P/'exception-scope-controls-v2'
out.mkdir()
rows = []
for name, h, j, expected in cases:
    folder = out/name
    folder.mkdir()
    for fname, source in [('helper.py', h), ('job.py', j)]:
        with (folder/fname).open('x') as stream:
            stream.write(source)
    rows.append({'id': name, 'helper': str((folder/'helper.py').relative_to(P)), 'helper_sha256': hashlib.sha256(h.encode()).hexdigest(),
                 'job': str((folder/'job.py').relative_to(P)), 'job_sha256': hashlib.sha256(j.encode()).hexdigest(), 'expected': expected})
protocol = {'frozen_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'cases': rows,
            'hypothesis': 'An owned AST procedure scoped to the exact lexical helper/job owners distinguishes explicit cached, fresh and job exception handlers, ignoring unrelated calls, comments and strings.',
            'unit': 'Eight synthetic static control-flow profiles, not application execution or generic exception inference.',
            'criterion': 'Observe only explicitly named handler types and literal lexical try containment; no dynamic class hierarchy, monkey patching or full call-graph guarantee.',
            'independence': 'Separate AST procedure after same-agent source reading. Not independent human/holdout.',
            'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_program_execution': False, 'training_eligible': False}
with (P/'exception-scope-protocol-v2.json').open('x') as stream:
    json.dump(protocol, stream, indent=2)
    stream.write('\n')
print(json.dumps({'frozen_cases': len(rows)}))
