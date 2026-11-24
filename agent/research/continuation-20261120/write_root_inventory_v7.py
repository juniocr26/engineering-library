"""Complete per-file inventory, including ignored preservation and transient caches."""
import ast
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
report = ROOT / 'AI_TRAINING_FILE_INVENTORY.md'
snapshot = P / 'file-inventory-snapshot-v7.json'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
baseline = json.loads((P / 'baseline.json').read_text())
if datetime.datetime.now(datetime.timezone.utc) < datetime.datetime.fromisoformat(baseline['minimum_target_utc']):
    raise SystemExit('Final inventory refused before measured eleven-hour minimum')
late_control_paths = {
    'agent/research/continuation-20261120/closing-receipt-v1.json',
    '.local-backups/continuation-20261120/final-root-envelope-v1/root-reports-and-closing-metadata.tar.gz',
    '.local-backups/continuation-20261120/final-root-envelope-v1/receipt.json',
}
late_note = 'Reserved final closeout control emitted after inventory collection. Hash/size deliberately omitted here; the final envelope receipt/outer closing receipt bind actual emitted bytes. Never treat a pending placeholder identity as final.'

prior_inventory = report.read_bytes() if report.exists() else None
if prior_inventory is not None:
    history = ROOT / '.local-backups/continuation-20261120/root-report-history'
    history.mkdir(parents=True, exist_ok=True)
    preserved = history / (sha(prior_inventory) + '.md')
    if not preserved.exists():
        preserved.write_bytes(prior_inventory)
    assert preserved.read_bytes() == prior_inventory
with snapshot.open('x') as stream:
    stream.write('{}\n')
# Load only the old pure purpose function. Do not execute its report-writing top level.
old_tree = ast.parse((P / 'write_root_inventory_v1.py').read_text())
old_function = next(node for node in old_tree.body if isinstance(node, ast.FunctionDef) and node.name == 'purpose')
namespace = {'Path': Path, 'P': P, 'ROOT': ROOT}
exec(compile(ast.Module(body=[old_function], type_ignores=[]), '<owned-inventory-purpose-only>', 'exec'), namespace)
old_purpose = namespace['purpose']
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
head = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, env=env, text=True).strip()
status = subprocess.check_output(['git','status','--porcelain=v1','-z','--untracked-files=all'], cwd=ROOT, env=env).decode().split('\0')
entries = []
for item in status:
    if not item:
        continue
    flag, name = item[:2], item[3:]
    if 'R' in flag or 'C' in flag:
        raise ValueError('unexpected Git rename/copy needs separate provenance review')
    entries.append({'status': flag, 'path': name})


def purpose(name, flag):
    path = Path(name)
    parts = path.parts
    if name in late_control_paths:
        return 'Final closeout control ' + path.name + ': binds current source cut, post-cut root reports/inventory/metadata and actual overlay verification; reserved pending bytes are not final identities.'
    if '__pycache__' in parts:
        return 'Transient ignored interpreter bytecode for ' + path.name + '; regenerated from preserved source, not a training target or permanent suite.'
    if name == str(snapshot.relative_to(ROOT)):
        return 'Machine inventory snapshot V7 including this own path; self/generated-report hashes intentionally omitted to avoid recursive identity claims.'
    if name.startswith('.local-backups/continuation-20261120/'):
        category = parts[2]
        return 'Exact local preservation artifact ' + path.name + ' in ' + category + '; content identity and member/preimage contract are recorded by associated receipts and this snapshot. No model weights were replaced or deleted.'
    if name == 'backend/lib/documentation/command.rb':
        return 'Caller 1.9.40 baseline to current 1.9.43: source-derived caught/returned-map identifier propagation and bounded bilingual quoted-reference guards; no universal semantic validation.'
    if name == 'backend/lib/documentation/python_structure.py':
        return 'Extract bounded lexical caught-exception and direct returned static Name/Attribute mapping identifiers without importing or executing Python source.'
    if name == 'agent/tools/documentation_retrieval.py':
        return 'HelperRetrieval0.1.3 to0.1.5: independently reconstruct complete Python and Go selected lexical units, metadata and verified Go producer before accepting fresh/cached evidence; preserve all older journals as legacy review, with no automatic migration.'
    if name == 'agent/recovery/manifest.json':
        return 'Reconcile a preexisting missing historical-report path and two stale planner/maintenance pins; then pin two bounded caller/extractor changes and helper0.1.5. Preserve old manifests,1964entries and identical model object; no planner/maintenance source change.'
    if flag.strip() == 'D' or name in {'AI_TRAINING_CAMPAIGN_REPORT.md','AI_TRAINING_FILE_INVENTORY.md','AI_FINE_TUNING_READINESS.md','AI_TRAINING_RESUME.md','agent/recovery/manifest.json','backend/lib/documentation/command.rb','backend/lib/documentation/python_structure.py'}:
        return old_purpose(name, flag)
    relative = path.relative_to(P.relative_to(ROOT)) if path.is_relative_to(P.relative_to(ROOT)) else None
    if relative is not None:
        first = relative.parts[0]
        if first in {'totalist-model-chapter-v1','cache-verbalization-v1','queue-model-faq-v1','humanize-model-chapter-v1','httpx-model-architecture-v1','backoff-model-chapter-v1','cachetools-model-concurrency-v1','quoted-code-format-probe-v1'}:
            return 'Evaluation-only ' + first + ' artifact ' + path.name + '; nine total continuation calls across seven source-generation/judgment tasks and two copy conditions; every complete requested output rejected; raw/protocol/status evidence retained. No active inference/retry/gold/training.'
        if first.startswith(('chapter-candidates-v','go-geom-chapter-candidates-v','totalist-chapter-candidates-v','boltons-chapter-candidates-v','self-chapter-supplement-v','httpx-chapter-candidates-v','humanize-chapter-candidates-v','backoff-chapter-candidates-v')):
            return 'Isolated chapter/example candidate ' + first + '/' + path.name + '; each version is preserved, current choice and rejection/correction limits are in the adjacent ledger. No active catalog or canonical campaign report is written here.'
        if first in {'go-build-context-v1','old-sdk-go-build-context-v1'} or 'build-context' in path.name:
            return 'Retained owned MatchFile/build-context study artifact ' + path.name + '; later capability census found existing GoBindingObserver more complete, so no novel Go binding capability or integration gain is claimed.'
        if path.suffix == '.py' and (ROOT/path).is_file():
            try:
                description = ast.get_docstring(ast.parse((ROOT/path).read_text()))
                if description:
                    return 'Isolated research producer ' + path.name + ': ' + description.replace('\n',' ')[:240]
            except (ValueError, SyntaxError, UnicodeError):
                pass
        if path.suffix in {'.stdout','.stderr'}:
            return 'Exact raw process stream ' + path.name + '; associated protocol/receipt distinguishes success, expected refusal, rejected candidate and owned driver failure.'
        if path.suffix == '.json' and not (ROOT/path).is_symlink() and (ROOT / path).is_file() and (ROOT / path).stat().st_size <= 1_000_000:
            try:
                data = json.loads((ROOT / path).read_text())
                if type(data) is dict:
                    description = next((data[k] for k in ['hypothesis','classification','scope','status','reason'] if type(data.get(k)) is str), None)
                    if description:
                        return 'Machine evidence ' + path.name + ': ' + description.replace('\n',' ')[:240]
            except (ValueError, UnicodeError):
                pass
    return old_purpose(name, flag)


for entry in entries:
    entry['purpose'] = purpose(entry['path'], entry['status'])
    file = ROOT / entry['path']
    if entry['path'] in late_control_paths:
        entry['identity_note'] = late_note
    elif file.is_symlink():
        target=os.readlink(file);entry.update(file_kind='synthetic-symlink-metadata-only',link_target=target,link_target_text_sha256=sha(target.encode()),purpose=entry['purpose']+' This is a synthetic control symlink; target text is inventoried without reading its referent.')
    elif file.is_file() and file not in {snapshot, report}:
        raw = file.read_bytes()
        entry.update(bytes=len(raw), sha256=sha(raw))
    elif file in {snapshot, report}:
        entry['identity_note'] = 'Generated after collection; deliberately no self/prewrite hash presented as current. Later checkpoints/recovery cuts hash the emitted bytes.'
preservation = []
for file in sorted((ROOT / '.local-backups/continuation-20261120').rglob('*')):
    if file.is_file() and not file.is_symlink():
        name = str(file.relative_to(ROOT))
        if name in late_control_paths:
            preservation.append({'path': name, 'purpose': purpose(name, 'ignored-preservation'), 'identity_note': late_note})
            continue
        raw = file.read_bytes()
        preservation.append({'path': name, 'bytes': len(raw), 'sha256': sha(raw), 'purpose': purpose(name, 'ignored-preservation')})
bytecode = []
for file in sorted(P.rglob('*.pyc')):
    if '__pycache__' in file.parts and file.is_file():
        raw = file.read_bytes()
        name = str(file.relative_to(ROOT))
        bytecode.append({'path': name, 'bytes': len(raw), 'sha256': sha(raw), 'purpose': purpose(name, 'ignored-cache')})
now = datetime.datetime.now(datetime.timezone.utc)
created = [e for e in entries if e['status'] == '??']
modified = [e for e in entries if e['status'].strip() == 'M']
deleted = [e for e in entries if e['status'].strip() == 'D']
record = {'at': now.isoformat(), 'local': now.astimezone(ZoneInfo('America/Sao_Paulo')).isoformat(), 'campaign_status': 'MINIMUM_MEASURED_FINAL_INVENTORY_COLLECTION',
          'elapsed_hours': (now - datetime.datetime.fromisoformat(baseline['start_utc'])).total_seconds() / 3600,
          'minimum_target_utc': baseline['minimum_target_utc'], 'eleven_hours_claimed': True,
          'repository': 'engineering-library', 'root': str(ROOT), 'baseline_head': baseline['head'], 'head': head,
          'head_matches_baseline': head == baseline['head'], 'index_sha256': sha((ROOT/'.git/index').read_bytes()),
          'index_matches_baseline': sha((ROOT/'.git/index').read_bytes()) == baseline['index_sha256'],
          'created_count': len(created), 'modified_count': len(modified), 'deleted_count': len(deleted),
          'git_visible_entries': entries, 'ignored_current_preservation_files': preservation, 'transient_current_bytecode_files': bytecode,
          'pre_existing_git_changes': 'Nenhum at the measured campaign baseline; old committed work and older ignored storage are baseline, not current changes.',
          'prior_root_inventory_sha256': sha(prior_inventory) if prior_inventory else None,
          'self_identity_policy': 'This snapshot, root inventory and three reserved closing-control paths omit prewrite identities; all paths are listed. The final envelope/outer receipt supply actual emitted identities without recursive self-hash claims.', 'late_generated_control_paths': sorted(late_control_paths),
          'temporary_restore_and_control_roots': 'Outside the repository; exact file/member/input manifests and archive receipts cover them separately. They are not additional external writable Git repositories.',
          'source_execution_scope': 'Reviewed confined phases: two Boltons functions;selected httpcore/HTTPX exception classes/functions;four exact queue modules;complete selected go-humanize and backoff root packages with finite synthetic calls. Backoff uses owned immediate buffered timer-channel values/clocks, no real retry timers or sleeping. Selected pure MLX-LM argument builder and dataset classes/functions were executed in isolated namespaces with owned method sinks; no full MLX-LM module or MLX/NumPy/Transformers/model/tokenizer/trainer/optimizer import/execution. Exact reviewed cachetools source packages/func/cached helpers were executed under owned aliases with synthetic clocks and event-driven threads,23observations in14groups across two Python contexts plus one additional no-store case; unused cachedmethod/setup not executed. No application network/installed package identity; Go-geom remains compile-only.',
          'completed_new_model_calls': 9, 'all_nine_complete_requested_outputs_rejected': True, 'active_or_pending_review_model_task': None, 'training_steps': 0, 'owner_gold': 0}


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def table(rows, description_key='purpose'):
    if not rows:
        return ['| Nenhum | |']
    return ['| `' + cell(row['path']) + '` | ' + cell(row[description_key]) + ' |' for row in rows]


lines = ['# Current campaign per-file inventory', '', 'Snapshot: ' + record['local'] + '. Final inventory collection after the measured eleven-hour minimum. Reserved closing controls are emitted after this collection and bound by the envelope/outer receipt.', '',
         'Repository: **engineering-library** (`' + str(ROOT) + '`). Baseline/current HEAD: `' + head + '`. Baseline tracked/untracked changes: **Nenhum**. Earlier committed work and older ignored archives are preserved baseline material.', '',
         f"Current Git-visible changes: **{len(created)} created, {len(modified)} modified, {len(deleted)} deleted live files**. Additional ignored current preservation files: **{len(preservation)}**; transient interpreter caches: **{len(bytecode)}**. Every collected path has an individual purpose below; complete sizes/hashes are in `agent/research/continuation-20261120/file-inventory-snapshot-v7.json`.", '',
         'The machine snapshot, generated inventory and three reserved closing-control paths omit prewrite identities. Their emitted bytes are bound by the final envelope/outer receipt; pending placeholder bytes are never claimed as final. Temporary restored/control trees are covered by separate member/input manifests, not counted as new external Git worktrees.', '',
         '## Modified files', '', '| File | Individual reason |', '|---|---|']
lines += table(modified)
lines += ['', '## Deleted live report copies', '', 'Exact historical bytes, hashes and old recovery contracts were verified before removing these redundant live human-facing copies. Technical datasets/checkpoints/source evidence were retained.', '', '| File | Individual justification |', '|---|---|']
lines += table(deleted)
lines += ['', '## Created Git-visible files', '', '| File | Individual purpose |', '|---|---|']
lines += table(created)
lines += ['', '## Ignored current local preservation files', '', 'These are exact recovery/preimage/archive artifacts, not unrecorded deletion or replacement of older history. The archive-member manifests identify contained files individually; an archive itself is one newly created repository-storage file.', '', '| File | Individual preservation purpose |', '|---|---|']
lines += table(preservation)
lines += ['', '## Transient ignored interpreter caches', '', 'Listed for completeness. These are generated bytecode, not permanent tests, canonical research evidence or training examples.', '', '| File | Individual purpose |', '|---|---|']
lines += table(bytecode)
lines += ['', '## Relevant inspected-only files and observed checks', '',
          'The two caller source files, optional HelperRetrieval code and recovery manifest listed above are the only modified tracked files. No permanent test/scaffolding/fixture, active catalog, UI, schema, skill or external Git worktree was changed.', '']
inspected = ['agent/tools/documentation_lifecycle.py','agent/tools/documentation_maintenance.py','agent/tools/documentation_candidates.py','agent/tools/documentation_workspace.py','agent/tools/documentation_retrieval.py','agent/tools/documentation_revision_signals.py','agent/tools/documentation_python_dependencies.py','agent/tools/documentation_javascript.py','agent/tools/documentation_go_binding.py','agent/tools/go-build-binding/README.md','agent/tools/go-build-binding/main.go','agent/tools/go-build-binding/manifest.json','agent/tools/go_source_ast.py','agent/recovery/bootstrap.py','agent/recovery/model-bundle.json','backend/lib/documentation/project_command.rb','backend/lib/documentation/research.rb','backend/test/offline/python_structure_offline.py','agent/research/documentation-intelligence-20261120/public-lifecycle-oracle-v1.json','agent/research/documentation-intelligence-20261120/public-sources/25.0.0/boltons/fileutils.py','agent/research/documentation-intelligence-20261120/public-sources/25.0.0/boltons/iterutils.py','agent/research/documentation-intelligence-20261120/public-sources/25.0.0/boltons/typeutils.py','agent/research/documentation-intelligence-20261119/datasets/v10/manifest.json']
inspected += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'backend/test/offline').glob('*_offline.rb'))]
inspected += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'agent/test').glob('*_test.py'))]
inspected += ['agent/tools/documentation_job_budget.py','agent/test/documentation_retrieval_test.py','agent/test/documentation_job_budget_test.py','frontend/lib/documentation.ts','frontend/lib/source-links.ts','frontend/lib/source-references.ts','frontend/tests/catalog-layout.test.ts','frontend/tests/source-references.test.ts','docs/go-image-optimizer/en/operations/source-review.md','docs/go-image-optimizer/pt-br/operations/source-review.md','docs/go-image-optimizer/en/links/catalog.json']
modified_paths={entry['path']for entry in modified}
for name in inspected:
    if name not in modified_paths and (ROOT/name).is_file():
        lines.append('- `' + name + '` — existing evidence/source/check, unchanged from baseline.')
lines += ['', 'Existing fresh checks:312agent Python tests pass after HelperRetrieval0.1.5 on Mac/Python3.14;68existing retrieval/job-budget tests additionally pass on Linux/Python3.11 after helper0.1.5;262Ruby tests/1,787assertions passed after the last caller change;three backend Python physical-line controls passed. Twelve existing caught-identifier renderer cases passed after current1.9.43; restored V3 Linux caller1.9.43 consumed31existing caught/map cases with all20594file hashes intact, while V4 restored helper0.1.4 consumed a fresh quote and coordinated-cache refusal with all20849hashes intact. Nineteen returned-map contract controls include six deliberately accepted incorrect facts;19/19 is not semantic accuracy. Fresh frontend verification checks140source hashes against baseline and runs102existing tests:100pass and2fail on unchanged catalog/input conditions. The old101count is historical. Do not claim a green current frontend suite. An isolated EN/PT Go href-repair candidate passes the actual consumer but is not applied. Research matrices, repeated OS executions and overlapping source cases are not summed as new permanent tests or independent accuracy.', '',
          'Explicit confined source execution covers two exact Boltons functions under restricted facades;15httpcore and18HTTPX exception class definitions plus3selected functions in owned namespaces;and4exact pure p-limit/yocto-queue modules across old/current cuts,using a fixed in-memory VM graph or exact owned Git-source package fixtures. Existing compiler/Node/runtime-library/legal artifacts were copied and consumed under isolated /tmp roots without installation or global runtime changes. Their protocols, owned inputs, raw results and limits are retained. No application network request, full Boltons module, full remap traversal, sentinel factory or model-generated example/command was executed. Go-geom was compiled/type-checked without running its package code. Two complete selected Go packages,go-humanize and backoff,were separately reviewed and explicitly executed with finite synthetic observations. The former has36frozen cases,35exactownedpredictions percut;the latter30sharedcases percut plus8current-only APIcases and6compile-onlyconsumer shapes percut. All repeated versions/contexts stay grouped. Backoff used owned immediate buffered timer values and clocks,no real retrywaits. One actual owned maintenance worker killed only its own PID after first-language persistence;the parent/session remained active,partial/original bytes survived,same-root restart refused and a separate explicit fresh request succeeded. Model inference:nine completed calls on the same approved model,all complete requested outputs rejected;seven source-generation/judgment calls and two conditions of one exact-copy probe. Active inference0. Latest cachetools completeJSONlabels1/10,allINSUFFICIENT. No neural-improvement or independent holdout claim. HTTPX structured labels9/16 do not equal full-answer or lifecycle accuracy. Optimizer steps:zero;ownergold:zero.', '',
          '## External repository/material inventory — sem alterações', '',
          'These are pinned public/frozen source or metadata materials, not newly mutated external checkouts. Created / modified / deleted files within each external repository: **Nenhum / Nenhum / Nenhum**. The copies created inside Engineering Library are listed individually above.', '',
          '| Repository/material | Relevant inspected scope | State |', '|---|---|',
          '| jmespath/jmespath.py | Two source cuts; facade/parser/visitor, class values, exception ownership, source-reviewed chapter and rejected factual model output | sem alterações |',
          '| lukeed/totalist | Two source/package/license cuts; current complete Git tree, declarations/README, source-vs-distribution boundaries and rejected model chapter | sem alterações |',
          '| twpayne/go-geom | Two source cuts; complete current root package compiled offline, seven method sets and example object checked; no package code execution | sem alterações |',
          '| un33k/python-slugify | Two pinned source/interface/license cuts, controlled declaration claims, registered path binding and synthetic document/relocation demonstrations | sem alterações |',
          '| mahmoud/boltons | Two historical source cuts, eight original lifecycle packets, complete-statement prefix and two exact functions observed under confined owned facades | sem alterações |',
          '| encode/httpx | Two source/manifest/license cuts, mapping and adapter-boundary review, isolated chapterV3, selected pure exception definitions/functions executed in owned namespaces | sem alterações |',
          '| encode/httpcore | One pinned1.0.9 dependency cut, reexport/class review and15plain exception classes executed under confined protocol; no package import | sem alterações |',
          '| sindresorhus/p-limit | Two pinned historical source/type/manifest/license cuts;pure modules observed with fixedVM/owned package fixtures;16runtime,16type and12format observations kept distinct; no installed dependency identity claim | sem alterações |',
          '| sindresorhus/yocto-queue | Two pinned historical direct-dependency source/type/manifest/license cuts,observed in the same related task graph;not a second independent family | sem alterações |',
          '| dustin/go-humanize | Two pinned source/module/MIT-license cuts;32 complete parser units,36 finite runtime cases percut,15 typed initializer checks percut,isolated bilingual chapter and rejected model comparator;one exact example compiled not run | sem alterações |',
          '| cenkalti/backoff | Two pinned retry/context/permanent-error source/module/MIT-license cuts;80 complete parser units,30shared bounded runtime cases percut plus8current-only APIcases,6compile-only consumer shapes percut,isolated chapterV2 and rejected model comparator;no real retrytimer/sleep/ticker/applicationI/O | sem alterações |',
          '| ml-explore/mlx-lm | Pinned source/config/trainer/checkpoint/shape/mask review, exact pure parser and data-adapter source subsets observed with owned sinks;isolated chapterV2,14claims7FAQ158structural checks plus agent language review. No full framework/model/tokenizer/trainer/optimizer import or execution | sem alterações |',
          '| ml-explore/mlx | Pinned minimum-reference0.32.3 source/license definitions,static traversal/layer interface review only;no import,tensor allocation or installation | sem alterações |',
          '| tkem/cachetools | Prior exposed5.3.3/5.5.2 structural evidence reused;new6.0.0source/notice,17Git-verified source/metadata/license files;bounded native cache/thread observations,seven manual lifecycle references and concrete isolated review bundle;new label response1/10rejected | sem alterações |',
          '| PyPI release metadata:mlx0.32.3 andtransformers5.7.0 | Primary JSON artifact listings only;no wheel/sdist body acquired,resolver run or installation;nominal tags are not trainable compatibility | sem alterações |',
          '| golang/go | Previously preserved Go 1.27.4 toolchain/source used for owned static observers and offline Go compilation | sem alterações |',
          '| temporalio/sdk-go (local name sdk-go) | Previously frozen source/package census; new MatchFile study was redundant with existing GoBindingObserver and is not presented as a new capability | sem alterações |',
          '| mlx-community/Llama-3.2-3B-Instruct-4bit | Small public model/config/tokenizer-configuration metadata only; no weights acquired | sem alterações |',
          '| meta-llama/Llama-3.2-3B-Instruct | Public card/license metadata; protected config/tokenizer requests returned 401, no credential retry | sem alterações |',
          '| Official Node.js documentation / existing runtime | Utility and CommonJS interoperability docs;existing24.22.0LinuxARM64 executable/selected ELF libraries/legal notices preserved and consumed;installed runtime unchanged | sem alterações |',
          '| Existing TypeScript5.9.3 package / standard libraries | Exact compiler,57used d.ts standard-library files,package/legal notices preserved and consumed;not a full upstream Git checkout or new installation | sem alterações |']
rights = json.loads((P/'dataset-lineage-audit-v1.json').read_text())['rights_evidence']
remote_metadata = json.loads((ROOT/'agent/research/documentation-intelligence-20261119/chapter-source-reverification.json').read_text())
remote_names = {row['name']:row['remote'].removeprefix('https://github.com/').removesuffix('.git') for row in remote_metadata['repositories']}
for entry in rights:
    exact_name = remote_names.get(entry['repository'],entry['repository'])
    if any(line.startswith('| '+exact_name+' |') or line.startswith('| '+exact_name+' (') for line in lines):
        continue
    lines.append('| ' + cell(exact_name) + ' (frozen local alias '+cell(entry['repository'])+') | Frozen primary license/notice provenance integrity only; no training approval or whole-repository semantic review. Live external worktree status not refreshed. | sem alterações |')
lines += ['', 'Final control-plane note: the outer closing receipt and envelope/archive receipt are intentionally emitted after this inventory. Their paths are already listed, with no placeholder hashes or sizes represented as final. Source-cutV7andthepost-cut envelope have separate explicit contracts.', '', 'Current source phase clarification: exact reviewed cachetools source package/func/cached helpers executed with owned clocks and finite event-driven threads. MLX-LM execution remained selected pure parser/data adapters only; no full framework,real tokenizer,model,tensor,trainer or optimizer. Current FAQ66candidate pairs (60chapter-derived/six standalone) plus77frozen pairs remain quarantined. Nine model calls completed,none active;8140generated tokens and4085.059serverseconds are not training steps or an accuracy denominator. The seven cachetools lifecycle scenarios are manual references,not classifier successes. Their27file owner-review bundle preserves previous documents and explicit named-API retirement evidence without live edits.', 'The V10 lineage audit covers all 305 original records, 396 immutable reference identities and the frozen primary notices. No frozen record was rewritten or promoted to approved gold. Newly curated evaluation-review records, chapters and FAQ remain excluded from training.', '',
          'Git HEAD/index remain at the measured owner baseline. No staging, commit, push, reset, clean, stash, rebase, cherry-pick or history rewrite was executed. Current root reports and technical recovery/checkpoint receipts define the next safe continuation; the collection is measured after the eleven-hour minimum; the outer closing receipt supplies final source/envelope/overlay verification. Cold boot, remote durability and training recovery remain unverified.', '']
report.write_text('\n'.join(lines))
with snapshot.open('w') as stream:
    stream.write(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
assert all(('`' + entry['path'] + '`') in report.read_text() for entry in entries + preservation + bytecode)
print(json.dumps({'created': len(created), 'modified': len(modified), 'deleted': len(deleted), 'ignored_preservation': len(preservation), 'transient_bytecode': len(bytecode), 'head_matches_baseline': record['head_matches_baseline'], 'index_matches_baseline': record['index_matches_baseline'], 'elapsed_hours': record['elapsed_hours']}))
