"""Seven bilingual manual lifecycle references, with explicit bounded retirement evidence."""
import ast
import collections
import datetime
import hashlib
import json
from pathlib import Path
import re

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
oracle = json.loads((P / 'cachetools-concurrency-model-oracle-v1.json').read_text())
provenance = json.loads((P / 'cachetools-source-provenance-v1.json').read_text())
notice = json.loads((P / 'cachetools-retirement-notice-source-v1.json').read_text())
units = dict(oracle['source_units'])
for tag, path, selector, key in [
    ('v5.3.3', 'src/cachetools/__init__.py', 'MRUCache', 'old:MRUCache'),
    ('v5.3.3', 'src/cachetools/func.py', 'mru_cache', 'old:mru_cache'),
    ('v6.0.0', 'src/cachetools/__init__.py', '__all__', 'new:exports'),
    ('v6.0.0', 'src/cachetools/func.py', '__all__', 'new:func_exports'),
]:
    item = next(row for row in provenance['files'] if row['tag'] == tag and row['upstream_path'] == path)
    source = (ROOT / item['path']).read_text()
    tree = ast.parse(source)
    if selector == '__all__':
        node = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == selector for t in n.targets))
    else:
        node = next(n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == selector)
    first, last = node.lineno, node.end_lineno
    quote = ''.join(source.splitlines(keepends=True)[first - 1:last])
    units[key] = {'path': path, 'local_evidence_path': item['path'], 'revision': item['revision'],
                  'source_sha256': item['sha256'], 'first_line': first, 'last_line': last,
                  'quote': quote, 'quote_sha256': hashlib.sha256(quote.encode()).hexdigest()}
source = (ROOT / notice['path']).read_text()
lines = source.splitlines(keepends=True)
first = next(i for i, line in enumerate(lines, 1) if '- Remove ``MRUCache``' in line)
last = first + 1
quote = ''.join(lines[first - 1:last])
units['notice:explicit-removal'] = {'path': 'CHANGELOG.rst', 'local_evidence_path': notice['path'],
    'revision': notice['revision'], 'source_sha256': notice['sha256'], 'first_line': first, 'last_line': last,
    'quote': quote, 'quote_sha256': hashlib.sha256(quote.encode()).hexdigest()}

targets = []
def add(identity, action, en_q, pt_q, before_en, before_pt, after_en, after_pt, evidence, observation, basis):
    for en, pt in [(en_q, pt_q), (before_en, before_pt), (after_en or '', after_pt or '')]:
        assert re.findall(r'`([^`]+)`', en) == re.findall(r'`([^`]+)`', pt), identity
    assert all(key in units for key in evidence)
    targets.append({'id': identity, 'manual_reference_action': action,
                    'question': {'en': en_q, 'pt-br': pt_q},
                    'documentation_before': {'en': before_en, 'pt-br': before_pt},
                    'candidate_after': {'en': after_en, 'pt-br': after_pt},
                    'evidence_ids': evidence, 'observation_artifact': observation, 'basis': basis,
                    'physical_documentation_certified': False, 'automatic_candidate_applier_supported': False,
                    'owner_approved': False, 'training_gold': False, 'training_use_approved': False})

add('condition-faq-add', 'ADD',
    'What does the newly available `condition` argument coordinate?', 'O que o novo argumento `condition` disponível coordena?',
    '', '',
    'With a standard condition and a cache that stores the result, the selected wrapper tracks pending keys and lets a same-key waiter reuse the stored result. The owned different-key computation progressed separately. This is bounded in-process coordination, not a distributed exactly-once guarantee.',
    'Com uma condição padrão e um cache que armazena o resultado, o wrapper selecionado acompanha chaves pendentes e permite que uma chamada aguardando a mesma chave reutilize o resultado armazenado. A computação própria de outra chave avançou separadamente. Isso é coordenação limitada dentro de um processo, não uma garantia distribuída de execução exatamente uma vez.',
    ['new:cached', 'new:condition', 'new:router'], 'cachetools-confined-runtime-results-v2.json',
    'Hypothetical owned catalog has no corresponding EN/PT entry; new source API and bounded behavior are known. Actual published catalog absence has not been certified.')

add('facade-default-modify', 'MODIFY',
    'Does the selected facade use the same synchronization strategy in both cuts?', 'A fachada selecionada usa a mesma estratégia de sincronização nos dois recortes?',
    'The selected `func._cache` supplies `RLock()` and the owned same-key calls computed twice.',
    'O `func._cache` selecionado fornece `RLock()` e as chamadas próprias com a mesma chave computaram duas vezes.',
    'The newer `func._cache` supplies `Condition()`. With the owned storable result, a same-key waiter reused the first result and one computation occurred; the earlier facade computed twice. This does not establish global exactly-once execution or performance.',
    'O `func._cache` mais recente fornece `Condition()`. Com o resultado próprio que pôde ser armazenado, uma chamada aguardando a mesma chave reutilizou o primeiro resultado e ocorreu uma computação; a fachada anterior computou duas vezes. Isso não estabelece execução global exatamente uma vez nem desempenho.',
    ['old:facade', 'new:facade', 'new:condition'], 'cachetools-cross-context-v1.json',
    'Real cross-file source/default change with event-controlled native observations; not a generic thread-safety or throughput certificate.')

add('named-mru-api-retirement', 'REMOVE',
    'What supports retiring the obsolete named MRU API entry?', 'O que sustenta retirar a entrada obsoleta da API MRU nomeada?',
    'The current API provides `MRUCache` and `func.mru_cache`.',
    'A API atual fornece `MRUCache` e `func.mru_cache`.',
    None, None,
    ['old:MRUCache', 'old:mru_cache', 'new:exports', 'new:func_exports', 'notice:explicit-removal'],
    'cachetools-no-store-and-export-results-v1.json',
    'Primary pinned6.0.0changelog explicitly removes both names; full selected source package exports and owned native namespace checks corroborate. Retire only this version-specific current API entry, preserve historical text and migration notice. No whole-chapter deletion or actual catalog mutation authorized.')

add('lock-scope-stable', 'NO-OP',
    'Does moving the helper require changing every lock-scope statement?', 'Mover o auxiliar exige mudar toda afirmação sobre escopo do lock?',
    'On a miss, the selected lock-only memoization wrapper calls the user function outside its cache lock. The owned two-thread case computed twice and returned the cache-winning value to both callers.',
    'Em uma falta no cache, o wrapper selecionado de memoização apenas com lock chama a função do usuário fora do lock do cache. O caso próprio de duas threads computou duas vezes e retornou aos dois chamadores o valor que venceu no cache.',
    'On a miss, the selected lock-only memoization wrapper calls the user function outside its cache lock. The owned two-thread case computed twice and returned the cache-winning value to both callers.',
    'Em uma falta no cache, o wrapper selecionado de memoização apenas com lock chama a função do usuário fora do lock do cache. O caso próprio de duas threads computou duas vezes e retornou aos dois chamadores o valor que venceu no cache.',
    ['new:locked'], 'cachetools-cross-context-v1.json',
    'The narrow documented property and selected trace remain true although implementation location changes. Source hash difference alone is not a mandatory documentation edit. Old complete closure is preserved in the prior source snapshot.')

add('legacy-info-warning-modify', 'MODIFY',
    'Is the legacy fourth positional boolean still warning-free?', 'O quarto booleano posicional legado continua sem aviso?',
    'A fourth positional `True` enables statistics without a deprecation warning.',
    'Um quarto argumento posicional `True` habilita estatísticas sem aviso de descontinuação.',
    'The current `cached` recognizes the boolean in the new fourth slot as legacy statistics configuration, clears its condition value and emits `DeprecationWarning`. The owned explicit-warning-filter observation retained statistics; the boolean did not become condition-based synchronization.',
    'O `cached` atual reconhece o booleano na nova quarta posição como configuração legada de estatísticas, limpa seu valor de condição e emite `DeprecationWarning`. A observação própria com filtro explícito de avisos manteve as estatísticas; o booleano não se tornou sincronização por condição.',
    ['new:cached', 'new:router'], 'cachetools-cross-context-v1.json',
    'Observed compatibility bridge plus a new emitted warning; default application warning visibility is not claimed.')

add('already-current-condition-answer', 'NO-OP',
    'Should an already-current answer change merely because the old source differed?', 'Uma resposta já atual deve mudar apenas porque o código antigo era diferente?',
    'The selected current facade supplies `Condition()`; in the owned storable-result case one same-key computation served both callers.',
    'A fachada atual selecionada fornece `Condition()`; no caso próprio com resultado armazenável, uma computação da mesma chave atendeu os dois chamadores.',
    'The selected current facade supplies `Condition()`; in the owned storable-result case one same-key computation served both callers.',
    'A fachada atual selecionada fornece `Condition()`; no caso próprio com resultado armazenável, uma computação da mesma chave atendeu os dois chamadores.',
    ['new:facade', 'new:condition'], 'cachetools-cross-context-v1.json',
    'Current documentation truth controls this hypothetical target; previous-source difference alone does not justify a patch.')

add('distributed-guarantee-insufficient', 'INCONCLUSIVE',
    'Does this source certify a distributed application guarantee?', 'Este código certifica uma garantia de aplicação distribuída?',
    'The application performs every cache-key computation exactly once across all hosts.',
    'A aplicação realiza cada computação de chave de cache exatamente uma vez em todos os hosts.',
    None, None,
    ['new:condition', 'new:router'], 'cachetools-no-store-and-export-results-v1.json',
    'Source and owned observations concern one process; actual application/distributed architecture and physical documentation ownership are absent. Keep original documentation for review, do not remove based on unsupported global claims. One no-store case already disproves a blanket local exactly-once interpretation.')

pack = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'repository': 'tkem/cachetools',
        'units': units, 'positive_retirement': {'primary_notice': 'notice:explicit-removal',
            'native_namespace_observation': 'cachetools-no-store-and-export-results-v1.json',
            'scope': 'Named current6.0.0 API entry only; historical content/migration note retained, no whole-chapter retirement.'},
        'source_executed_by_this_builder': False, 'owner_approved': False, 'training_gold': False}
with (P / 'cachetools-lifecycle-evidence-pack-v1.json').open('x') as stream:
    json.dump(pack, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
with (P / 'cachetools-lifecycle-review-targets-v1.jsonl').open('x') as stream:
    for target in targets:
        for language in ['en', 'pt-br']:
            row = {'id': target['id'] + ':' + language, 'task': 'MANUAL_DOCUMENTATION_LIFECYCLE_REVIEW_REFERENCE',
                   'logical_scenario': target['id'], 'language': language, 'source_family_group': 'development-exposed:tkem/cachetools',
                   'source_revisions': {'previous': '1fcadea96ce67d499965b085f0b0b2253b78bb80', 'current': 'e497575fcb4d29dfb773824956539215db964059'},
                   'manual_reference_action': target['manual_reference_action'], 'question': target['question'][language],
                   'documentation_before': target['documentation_before'][language], 'candidate_after': target['candidate_after'][language],
                   'evidence_ids': target['evidence_ids'], 'observation_artifact': target['observation_artifact'], 'basis': target['basis'],
                   'physical_documentation_certified': False, 'automatic_candidate_applier_supported': False,
                   'owner_approved': False, 'training_gold': False, 'training_use_approved': False,
                   'license_status': 'PRIMARY_MIT_NOTICES_PRESERVED_NOT_TRAINING_AUTHORIZATION', 'private_application_data': False,
                   'training_excluded': True, 'keep_original_pending_review': True,
                   'not_original_planner_packet_or_schema_extension': True}
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')
summary = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'logical_scenarios': len(targets),
           'language_rows': 2 * len(targets), 'manual_reference_action_counts': dict(collections.Counter(t['manual_reference_action'] for t in targets)),
           'classifier_predictions': 0, 'accuracy_claimed': False, 'neural_evaluation_independence': False,
           'owner_approved': False, 'training_gold': False, 'frozen305_changed': False,
           'publication': False, 'active_catalog_changed': False,
           'interpretation': 'Manual development-exposed scenario targets, not seven classifier successes, physical-catalog actions or independent FAQ pairs. REMOVE requires explicit pinned notice plus bounded corroboration and remains owner-review-only.'}
with (P / 'cachetools-lifecycle-review-summary-v1.json').open('x') as stream:
    json.dump(summary, stream, indent=2)
    stream.write('\n')
print(json.dumps(summary))
