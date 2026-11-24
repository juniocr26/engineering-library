"""Finite cachetools source observations with owned clocks and event-driven workers."""
import datetime
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import threading
import warnings

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
ROOT = P.parents[2]
protocol_path = P / 'cachetools-confined-runtime-protocol-v1.json'
protocol = json.loads(protocol_path.read_text())
for item in protocol['source_files']:
    raw = (ROOT / item['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item['sha256']
    assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == item['git_blob']
expected_cases = {row['id']: row for row in protocol['cases']}
rows = []

def require(event, label):
    if not event.wait(5):
        raise RuntimeError('Owned coordination timeout: ' + label)

def finish(thread):
    thread.join(5)
    if thread.is_alive():
        raise RuntimeError('Owned worker did not finish: ' + thread.name)

def record(tag, identity, observed):
    case = expected_cases[identity]
    expected = case.get('expected_both', case.get('expected_current' if tag == 'v6.0.0' else 'expected_old', case.get('expected')))
    # JSON normalization records tuples as arrays without changing values.
    observed = json.loads(json.dumps(observed))
    checks = {key: observed.get(key) == value for key, value in expected.items()}
    row = {'tag': tag, 'id': identity, 'expected': expected, 'observed': observed,
           'checks': checks, 'pass': all(checks.values())}
    rows.append(row)

class Clock:
    def __init__(self): self.now = 0
    def __call__(self): return self.now

class ObservedCondition(threading.Condition):
    def __init__(self):
        super().__init__()
        self.wait_seen = threading.Event()
    def wait(self, timeout=None):
        self.wait_seen.set()
        return super().wait(timeout)

def worker_call(wrapper, results, name):
    try:
        results[name] = wrapper('a')
    except Exception as error:
        results[name + '_error'] = type(error).__name__

def pair_work(module, facade=False, no_cache=False):
    first_started, release_first, wait_seen = threading.Event(), threading.Event(), threading.Event()
    count_lock = threading.Lock()
    calls, results = [], {}
    def function(key):
        with count_lock:
            calls.append(key)
            ordinal = len(calls)
        if ordinal == 1:
            first_started.set()
            require(release_first, 'release first duplicate computation')
            return 11
        return 22
    if facade:
        func = importlib.import_module(module.__name__ + '.func')
        wrapper = func.lru_cache(maxsize=2)(function)
        condition = getattr(wrapper, 'cache_condition', None)
        if condition is not None:
            original_wait = condition.wait
            def observed_wait(timeout=None):
                wait_seen.set()
                return original_wait(timeout)
            condition.wait = observed_wait
    elif no_cache:
        wrapper = module.cached(None, condition=ObservedCondition())(function)
        condition = None  # Explicitly uncached source branch, not synchronized.
    else:
        wrapper = module.cached({}, lock=threading.RLock(), info=True)(function)
        condition = None
    first = threading.Thread(target=worker_call, args=(wrapper, results, 'first'), daemon=True, name='owned-first')
    second = threading.Thread(target=worker_call, args=(wrapper, results, 'second'), daemon=True, name='owned-second')
    try:
        first.start()
        require(first_started, 'first computation started')
        second.start()
        if condition is not None:
            require(wait_seen, 'same key condition wait')
            release_first.set()
            finish(first)
            finish(second)
        else:
            finish(second)  # Its completion proves work was not serialized behind first.
            release_first.set()
            finish(first)
    finally:
        release_first.set()
        for thread in [first, second]:
            if thread.ident is not None:
                thread.join(5)
    return {'computations': len(calls), 'results': results,
            'cache_values': list(wrapper.cache.values()) if wrapper.cache is not None else None,
            'condition_present': getattr(wrapper, 'cache_condition', None) is not None,
            'probe_wait_expected': condition is not None,
            'no_live_workers': not first.is_alive() and not second.is_alive()}

def condition_work(module, mode):
    first_started, release_first = threading.Event(), threading.Event()
    condition = ObservedCondition()
    results, calls = {}, []
    calls_lock = threading.Lock()
    def function(key):
        with calls_lock:
            calls.append(key)
            ordinal = calls.count('a')
        if key == 'b':
            return 99
        if ordinal == 1:
            first_started.set()
            require(release_first, 'release first condition computation')
            if mode == 'error':
                raise ValueError('owned failure, not cached')
            return 11
        return 22
    wrapper = module.cached({}, condition=condition, info=True)(function)
    first = threading.Thread(target=worker_call, args=(wrapper, results, 'first'), daemon=True, name='owned-condition-first')
    second = threading.Thread(target=worker_call, args=(wrapper, results, 'second'), daemon=True, name='owned-condition-second')
    different = None
    try:
        first.start()
        require(first_started, 'condition first started')
        second.start()
        require(condition.wait_seen, 'condition second waiting')
        if mode == 'different-key':
            different = wrapper('b')
        elif mode == 'clear':
            wrapper.cache_clear()
        release_first.set()
        finish(first)
        finish(second)
    finally:
        release_first.set()
        for thread in [first, second]:
            if thread.ident is not None:
                thread.join(5)
    return {'a_computations': calls.count('a'), 'b_result': different, 'results': results,
            'cache_values': list(wrapper.cache.values()), 'cache_info': wrapper.cache_info()._asdict(),
            'condition_wait_observed': condition.wait_seen.is_set(),
            'no_live_workers': not first.is_alive() and not second.is_alive()}

for tag, revision, alias in [
    ('v5.3.3', '1fcadea96ce67d499965b085f0b0b2253b78bb80', 'owned_cachetools_533'),
    ('v6.0.0', 'e497575fcb4d29dfb773824956539215db964059', 'owned_cachetools_600'),
]:
    package = P / 'new-public-sources-v1/tkem--cachetools' / revision / 'src/cachetools'
    spec = importlib.util.spec_from_file_location(alias, package / '__init__.py', submodule_search_locations=[str(package)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    assert module.__version__ == tag[1:]
    for identity in ['ttl-before-deadline', 'ttl-at-deadline', 'ttl-expire-order', 'ttl-missing-lazy-storage', 'ttl-len-expiration', 'tlru-expiration-order']:
        clock = Clock()
        if identity == 'tlru-expiration-order':
            cache = module.TLRUCache(4, lambda key, value, now: now + (10 if key == 'a' else 1), timer=clock)
            cache['a'] = 10
            clock.now = 1
            cache['b'] = 20
            clock.now = 2
            result = cache.expire()
            observed = {'returned': result, 'raw_items': [[key, value] for key, value in cache._Cache__data.items()]}
            record(tag, identity, observed)
            continue
        cache = module.TTLCache(4, 3, timer=clock)
        cache['a'] = 10
        if identity == 'ttl-before-deadline':
            clock.now = 2
            observed = {'returned': cache.expire(), 'raw_count': module.Cache.__len__(cache)}
        elif identity == 'ttl-at-deadline':
            clock.now = 3
            observed = {'returned': cache.expire(), 'raw_count': module.Cache.__len__(cache)}
        elif identity == 'ttl-expire-order':
            clock.now = 1
            cache['b'] = 20
            clock.now = 4
            observed = {'returned': cache.expire(), 'raw_count': module.Cache.__len__(cache)}
        elif identity == 'ttl-missing-lazy-storage':
            clock.now = 3
            before = module.Cache.__len__(cache)
            contains = 'a' in cache
            error = None
            try: cache['a']
            except KeyError: error = 'KeyError'
            observed = {'contains': contains, 'get_error': error, 'raw_count_before': before, 'raw_count_after': module.Cache.__len__(cache)}
        else:
            clock.now = 3
            before = module.Cache.__len__(cache)
            logical = len(cache)
            observed = {'raw_count_before': before, 'logical_length': logical, 'raw_count_after': module.Cache.__len__(cache)}
        record(tag, identity, observed)
    record(tag, 'lock-only-duplicate-work', pair_work(module))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        wrapper = module.cached({}, module.keys.hashkey, None, True)(lambda value: value)
        wrapper(1)
        record(tag, 'legacy-positional-info', {'info_present': wrapper.cache_info is not None,
               'condition_attached': getattr(wrapper, 'cache_condition', None) is not None,
               'warning_types': [type(w.message).__name__ for w in caught]})
    record(tag, 'facade-same-key', pair_work(module, facade=True))
    if tag == 'v6.0.0':
        for identity, mode in [('condition-different-key-progress', 'different-key'), ('condition-error-cleanup', 'error'), ('condition-clear-does-not-cancel', 'clear')]:
            record(tag, identity, condition_work(module, mode))
        record(tag, 'none-cache-condition-ignored', pair_work(module, no_cache=True))
    else:
        error = None
        try: module.cached({}, condition=ObservedCondition())
        except TypeError: error = 'TypeError'
        record(tag, 'old-condition-keyword-absent', {'error': error})

for item in protocol['source_files']:
    assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
record_value = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'BOUNDED_NATIVE_SOURCE_RESULTS_RECORDED',
                'protocol_sha256': hashlib.sha256(protocol_path.read_bytes()).hexdigest(), 'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'python': sys.version, 'rows': rows, 'passes': sum(row['pass'] for row in rows), 'observations': len(rows),
                'logical_case_groups': len(expected_cases), 'source_executed': True,
                'execution_scope': 'Exact reviewed cachetools package/func/cached helper source under owned import aliases; bounded synthetic inputs/events only; setup and unused cachedmethod helper not executed.',
                'source_hashes_unchanged': True, 'model_calls': 0, 'permanent_tests_changed': False,
                'training_or_optimizer_steps': 0, 'owner_approved': False, 'training_gold': False,
                'independent_family_or_neural_holdout': False, 'sleep_calls': 0,
                'limits': 'Native source observations, not installed distribution identity, general thread safety, distributed coordination or all callback behavior.'}
output = Path(sys.argv[1]) if len(sys.argv) == 2 else P / 'cachetools-confined-runtime-results-v2.json'
with output.open('x') as stream:
    json.dump(record_value, stream, indent=2)
    stream.write('\n')
print(json.dumps({'passes': record_value['passes'], 'observations': len(rows), 'misses': [{key: row[key] for key in ['tag', 'id', 'expected', 'observed']} for row in rows if not row['pass']]}))
