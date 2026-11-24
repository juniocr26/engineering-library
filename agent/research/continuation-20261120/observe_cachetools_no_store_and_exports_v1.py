"""One additional no-store condition case and bounded public-export observations."""
import datetime
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import threading

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
ROOT = P.parents[2]
protocol_path = P / 'cachetools-no-store-condition-protocol-v1.json'
protocol = json.loads(protocol_path.read_text())
provenance = json.loads((P / 'cachetools-source-provenance-v1.json').read_text())
for row in provenance['files']:
    assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
modules = {}
exports = []
for tag, revision, alias in [('v5.3.3', '1fcadea96ce67d499965b085f0b0b2253b78bb80', 'owned_cache_export_old'),
                             ('v6.0.0', 'e497575fcb4d29dfb773824956539215db964059', 'owned_cache_export_new')]:
    directory = P / 'new-public-sources-v1/tkem--cachetools' / revision / 'src/cachetools'
    spec = importlib.util.spec_from_file_location(alias, directory / '__init__.py', submodule_search_locations=[str(directory)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    facade = importlib.import_module(alias + '.func')
    exports.append({'tag': tag, 'MRUCache_attribute_present': hasattr(module, 'MRUCache'),
                    'MRUCache_in_declared_exports': 'MRUCache' in module.__all__,
                    'mru_cache_attribute_present': hasattr(facade, 'mru_cache'),
                    'mru_cache_in_declared_exports': 'mru_cache' in facade.__all__})
    modules[tag] = module
assert all(exports[0][key] is True and exports[1][key] is False for key in exports[0] if key != 'tag')

class Condition(threading.Condition):
    def __init__(self):
        super().__init__()
        self.wait_seen = threading.Event()
    def wait(self, timeout=None):
        self.wait_seen.set()
        return super().wait(timeout)

condition = Condition()
started, release = threading.Event(), threading.Event()
guard = threading.Lock()
state = {'calls': 0, 'active': 0, 'peak': 0}
results = {}

def function(key):
    with guard:
        state['calls'] += 1
        ordinal = state['calls']
        state['active'] += 1
        state['peak'] = max(state['peak'], state['active'])
    try:
        if ordinal == 1:
            started.set()
            assert release.wait(5), 'owned first computation release timeout'
        return 'xx'
    finally:
        with guard:
            state['active'] -= 1

module = modules['v6.0.0']
cache = module.Cache(1, getsizeof=len)
wrapper = module.cached(cache, condition=condition, info=True)(function)

def call(name):
    try: results[name] = wrapper('a')
    except Exception as error: results[name + '_error'] = type(error).__name__

threads = [threading.Thread(target=call, args=(name,), daemon=True) for name in ['first', 'second']]
try:
    threads[0].start()
    assert started.wait(5), 'owned first start timeout'
    threads[1].start()
    assert condition.wait_seen.wait(5), 'owned second wait timeout'
    release.set()
    for thread in threads: thread.join(5)
finally:
    release.set()
    for thread in threads:
        if thread.ident is not None: thread.join(5)
observed = {'computations': state['calls'], 'peak_concurrent_user_functions': state['peak'], 'results': results,
            'cache_size': len(cache), 'wait_observed': condition.wait_seen.is_set(),
            'no_live_workers': all(not thread.is_alive() for thread in threads)}
checks = {key: observed[key] == value for key, value in protocol['case']['expected'].items()}
assert all(checks.values()), observed
uncached_condition = threading.Condition()
uncached = module.cached(None, condition=uncached_condition, info=True)(lambda value: value)
attribute = {'attached_condition_identity_matches_argument': uncached.cache_condition is uncached_condition,
             'cache_is_none': uncached.cache is None,
             'interpretation': 'Attached metadata alone does not establish coordination; prior actual two-worker uncached case computed twice. V1 extra condition_present probe label was incorrect; V2 separately records actual attachment and wait expectation.'}
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'NO_STORE_CONDITION_AND_EXPORT_BOUNDARIES_OBSERVED',
          'protocol_sha256': hashlib.sha256(protocol_path.read_bytes()).hexdigest(), 'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'no_store_case': {'observed': observed, 'checks': checks, 'pass': all(checks.values())},
          'public_exports': exports, 'uncached_condition_attribute': attribute,
          'source_executed': True, 'package_installed': False, 'independent_neural_holdout': False,
          'owner_approved': False, 'training_gold': False, 'publication': False, 'model_calls': 0,
          'limits': 'One additional owned no-store case, not exactly-once or distributed proof. Export absence is corroborating namespace evidence; primary explicit retirement notice is recorded separately. No automatic documentation removal.'}
with (P / 'cachetools-no-store-and-export-results-v1.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({'no_store_case': observed, 'public_exports': exports, 'uncached_condition_attribute': attribute}))
