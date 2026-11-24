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
snapshot = P / 'file-inventory-snapshot-v5.json'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
baseline = json.loads((P / 'baseline.json').read_text())
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
    if '__pycache__' in parts:
        return 'Transient ignored interpreter bytecode for ' + path.name + '; regenerated from preserved source, not a training target or permanent suite.'
    if name == str(snapshot.relative_to(ROOT)):
        return 'Machine inventory snapshot V5 including this own path; self/generated-report hashes intentionally omitted to avoid recursive identity claims.'
    if name.startswith('.local-backups/continuation-20261120/'):
        category = parts[2]
        return 'Exact local preservation artifact ' + path.name + ' in ' + category + '; content identity and member/preimage contract are recorded by associated receipts and this snapshot. No model weights were replaced or deleted.'
    if name == 'backend/lib/documentation/command.rb':
        return 'Caller 1.9.40 baseline to current 1.9.43: source-derived caught/returned-map identifier propagation and bounded bilingual quoted-reference guards; no universal semantic validation.'
    if name == 'backend/lib/documentation/python_structure.py':
        return 'Extract bounded lexical caught-exception and direct returned static Name/Attribute mapping identifiers without importing or executing Python source.'
    if name == 'agent/tools/documentation_retrieval.py':
        return 'HelperRetrieval0.1.3 to0.1.4: independently compare complete selected Python lexical units and declaration metadata, preventing five coordinated cached-result/receipt substitutions; preserve legacy journals for review.'
    if name == 'agent/recovery/manifest.json':
        return 'Refresh the two caller pins and one optional helper pin after relevant existing regressions; preserve exact old manifests and all1964 entries/model identity.'
    if flag.strip() == 'D' or name in {'AI_TRAINING_CAMPAIGN_REPORT.md','AI_TRAINING_FILE_INVENTORY.md','AI_FINE_TUNING_READINESS.md','AI_TRAINING_RESUME.md','agent/recovery/manifest.json','backend/lib/documentation/command.rb','backend/lib/documentation/python_structure.py'}:
        return old_purpose(name, flag)
    relative = path.relative_to(P.relative_to(ROOT)) if path.is_relative_to(P.relative_to(ROOT)) else None
    if relative is not None:
        first = relative.parts[0]
        if first in {'totalist-model-chapter-v1','cache-verbalization-v1','queue-model-faq-v1','humanize-model-chapter-v1','httpx-model-architecture-v1','backoff-model-chapter-v1'}:
            return 'Evaluation-only ' + first + ' artifact ' + path.name + '; exactly one model call per protocol; raw/protocol/status evidence retained. Five completed tasks are rejected and the backoff task is active/pending review at this dated inventory; no retry/gold/training.'
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
    if file.is_symlink():
        target=os.readlink(file);entry.update(file_kind='synthetic-symlink-metadata-only',link_target=target,link_target_text_sha256=sha(target.encode()),purpose=entry['purpose']+' This is a synthetic control symlink; target text is inventoried without reading its referent.')
    elif file.is_file() and file not in {snapshot, report}:
        raw = file.read_bytes()
        entry.update(bytes=len(raw), sha256=sha(raw))
    elif file in {snapshot, report}:
        entry['identity_note'] = 'Generated after collection; deliberately no self/prewrite hash presented as current. Later checkpoints/recovery cuts hash the emitted bytes.'
preservation = []
for file in sorted((ROOT / '.local-backups/continuation-20261120').rglob('*')):
    if file.is_file() and not file.is_symlink():
        raw = file.read_bytes()
        name = str(file.relative_to(ROOT))
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
record = {'at': now.isoformat(), 'local': now.astimezone(ZoneInfo('America/Sao_Paulo')).isoformat(), 'campaign_status': 'ACTIVE',
          'elapsed_hours': (now - datetime.datetime.fromisoformat(baseline['start_utc'])).total_seconds() / 3600,
          'minimum_target_utc': baseline['minimum_target_utc'], 'eleven_hours_claimed': False,
          'repository': 'engineering-library', 'root': str(ROOT), 'baseline_head': baseline['head'], 'head': head,
          'head_matches_baseline': head == baseline['head'], 'index_sha256': sha((ROOT/'.git/index').read_bytes()),
          'index_matches_baseline': sha((ROOT/'.git/index').read_bytes()) == baseline['index_sha256'],
          'created_count': len(created), 'modified_count': len(modified), 'deleted_count': len(deleted),
          'git_visible_entries': entries, 'ignored_current_preservation_files': preservation, 'transient_current_bytecode_files': bytecode,
          'pre_existing_git_changes': 'Nenhum at the measured campaign baseline; old committed work and older ignored storage are baseline, not current changes.',
          'prior_root_inventory_sha256': sha(prior_inventory) if prior_inventory else None,
          'self_identity_policy': 'This snapshot and the regenerated root inventory omit their own hashes; every path is listed, later independent checkpoint/cut supplies emitted-byte hashes.',
          'temporary_restore_and_control_roots': 'Outside the repository; exact file/member/input manifests and archive receipts cover them separately. They are not additional external writable Git repositories.',
          'source_execution_scope': 'Reviewed confined phases: two Boltons functions;selected httpcore/HTTPX exception classes/functions;four exact queue modules;complete selected go-humanize and backoff root packages with finite synthetic calls. Backoff uses owned immediate buffered timer-channel values/clocks, no real retry timers or sleeping. No application network/installed package identity; Go-geom remains compile-only.',
          'completed_new_model_calls': 5, 'all_five_completed_tasks_rejected': True, 'active_or_pending_review_model_task': 'backoff-model-chapter-v1', 'training_steps': 0, 'owner_gold': 0}


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def table(rows, description_key='purpose'):
    if not rows:
        return ['| Nenhum | |']
    return ['| `' + cell(row['path']) + '` | ' + cell(row[description_key]) + ' |' for row in rows]


lines = ['# Current campaign per-file inventory', '', 'Snapshot: ' + record['local'] + '. Campaign ACTIVE; this is a dated inventory, not final closure or eleven-hour completion.', '',
         'Repository: **engineering-library** (`' + str(ROOT) + '`). Baseline/current HEAD: `' + head + '`. Baseline tracked/untracked changes: **Nenhum**. Earlier committed work and older ignored archives are preserved baseline material.', '',
         f"Current Git-visible changes: **{len(created)} created, {len(modified)} modified, {len(deleted)} deleted live files**. Additional ignored current preservation files: **{len(preservation)}**; transient interpreter caches: **{len(bytecode)}**. Every collected path has an individual purpose below; complete sizes/hashes are in `agent/research/continuation-20261120/file-inventory-snapshot-v5.json`.", '',
         'The machine snapshot and generated inventory intentionally omit their own hashes to avoid self-referential or stale prewrite identities. Later independent checkpoints and recovery cuts hash their emitted bytes. Temporary restored/control trees are covered by separate member/input manifests, not counted as new external Git worktrees.', '',
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
lines += ['', 'Existing fresh checks:312agent Python tests pass after HelperRetrieval0.1.4 on Mac/Python3.14;68existing retrieval/job-budget tests additionally pass on Linux/Python3.11;262Ruby tests/1,787assertions passed after the last caller change;three backend Python physical-line controls passed. Twelve existing caught-identifier renderer cases passed after current1.9.43; restored V3 Linux caller1.9.43 consumed31existing caught/map cases with all20594file hashes intact, while V4 restored helper0.1.4 consumed a fresh quote and coordinated-cache refusal with all20849hashes intact. Nineteen returned-map contract controls include six deliberately accepted incorrect facts;19/19 is not semantic accuracy. Fresh frontend verification checks140source hashes against baseline and runs102existing tests:100pass and2fail on unchanged catalog/input conditions. The old101count is historical. Do not claim a green current frontend suite. An isolated EN/PT Go href-repair candidate passes the actual consumer but is not applied. Research matrices, repeated OS executions and overlapping source cases are not summed as new permanent tests or independent accuracy.', '',
          'Explicit confined source execution covers two exact Boltons functions under restricted facades;15httpcore and18HTTPX exception class definitions plus3selected functions in owned namespaces;and4exact pure p-limit/yocto-queue modules across old/current cuts,using a fixed in-memory VM graph or exact owned Git-source package fixtures. Existing compiler/Node/runtime-library/legal artifacts were copied and consumed under isolated /tmp roots without installation or global runtime changes. Their protocols, owned inputs, raw results and limits are retained. No application network request, full Boltons module, full remap traversal, sentinel factory or model-generated example/command was executed. Go-geom was compiled/type-checked without running its package code. Two complete selected Go packages,go-humanize and backoff,were separately reviewed and explicitly executed with finite synthetic observations. The former has36frozen cases,35exactownedpredictions percut;the latter30sharedcases percut plus8current-only APIcases and6compile-onlyconsumer shapes percut. All repeated versions/contexts stay grouped. Backoff used owned immediate buffered timer values and clocks,no real retrywaits. One actual owned maintenance worker killed only its own PID after first-language persistence;the parent/session remained active,partial/original bytes survived,same-root restart refused and a separate explicit fresh request succeeded. Model inference:five completed new tasks on the same approved model,all rejected;one distinct retry-adapter chapter task is active/pending review. HTTPX structured labels9/16 do not equal full-answer or lifecycle accuracy. Optimizer steps:zero;ownergold:zero.', '',
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
          '| cenkalti/backoff | Two pinned retry/context/permanent-error source/module/MIT-license cuts;80 complete parser units,30shared bounded runtime cases percut plus8current-only APIcases,6compile-only consumer shapes percut,isolated chapterV2 and pending model comparator;no real retrytimer/sleep/ticker/applicationI/O | sem alterações |',
          '| ml-explore/mlx-lm | Pinned source/config/trainer/dataset/checkpoint/mask arithmetic review only; no framework installation/import or optimizer | sem alterações |',
          '| golang/go | Previously preserved Go 1.27.4 toolchain/source used for owned static observers and offline Go compilation | sem alterações |',
          '| temporalio/sdk-go (local name sdk-go) | Previously frozen source/package census; new MatchFile study was redundant with existing GoBindingObserver and is not presented as a new capability | sem alterações |',
          '| mlx-community/Llama-3.2-3B-Instruct-4bit | Small public model/config/tokenizer-configuration metadata only; no weights acquired | sem alterações |',
          '| meta-llama/Llama-3.2-3B-Instruct | Public card/license metadata; protected config/tokenizer requests returned 401, no credential retry | sem alterações |',
          '| Official Node.js documentation / existing runtime | Utility and CommonJS interoperability docs;existing24.22.0LinuxARM64 executable/selected ELF libraries/legal notices preserved and consumed;installed runtime unchanged | sem alterações |',
          '| Existing TypeScript5.9.3 package / standard libraries | Exact compiler,57used d.ts standard-library files,package/legal notices preserved and consumed;not a full upstream Git checkout or new installation | sem alterações |']
rights = json.loads((P/'dataset-lineage-audit-v1.json').read_text())['rights_evidence']
for entry in rights:
    lines.append('| ' + cell(entry['repository']) + ' | Frozen primary license/notice provenance integrity only; no training approval or whole-repository semantic review | sem alterações |')
lines += ['', 'The V10 lineage audit covers all 305 original records, 396 immutable reference identities and the frozen primary notices. No frozen record was rewritten or promoted to approved gold. Newly curated evaluation-review records, chapters and FAQ remain excluded from training.', '',
          'Git HEAD/index remain at the measured owner baseline. No staging, commit, push, reset, clean, stash, rebase, cherry-pick or history rewrite was executed. Current root reports and technical recovery/checkpoint receipts define the next safe continuation; this inventory alone does not establish final recovery closure, cold boot, remote durability or eleven-hour completion.', '']
report.write_text('\n'.join(lines))
with snapshot.open('w') as stream:
    stream.write(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
assert all(('`' + entry['path'] + '`') in report.read_text() for entry in entries + preservation + bytecode)
print(json.dumps({'created': len(created), 'modified': len(modified), 'deleted': len(deleted), 'ignored_preservation': len(preservation), 'transient_bytecode': len(bytecode), 'head_matches_baseline': record['head_matches_baseline'], 'index_matches_baseline': record['index_matches_baseline'], 'elapsed_hours': record['elapsed_hours']}))
