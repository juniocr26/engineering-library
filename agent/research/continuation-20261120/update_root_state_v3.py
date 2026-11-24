"""Preserve dated report preimages and refresh current root-only state."""
import datetime
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
now = datetime.datetime.now(datetime.timezone.utc)
baseline = json.loads((P / 'baseline.json').read_text())
elapsed = (now - datetime.datetime.fromisoformat(baseline['start_utc'])).total_seconds() / 3600
manifest = hashlib.sha256((ROOT / 'agent/recovery/manifest.json').read_bytes()).hexdigest()
history = ROOT / '.local-backups/continuation-20261120/root-report-history'
history.mkdir(exist_ok=True)
receipts = []

common = f"""Campaign ACTIVE at {now.isoformat()}, **{elapsed:.3f} measured hours**. Start08:57:10 America/Sao_Paulo; minimum end19:57:10 /22:57:10.273488Z. Eleven hours have not been achieved; no end timestamp or early-stop reason is asserted.

Current caller1.9.43, HelperRetrieval0.1.5, planner0.3.6 and maintenance0.1.5. HEAD/index remain the clean owner baseline. Four tracked files are modified; five redundant old live reports were safely migrated and removed. Current manifestSHA `{manifest}`; normal bootstrap1964entries/six small blobs passes. Nine completed inference calls produced no accepted complete requested output; inference active0, optimizer steps0, owner gold0, frozen records305 unchanged, publication0.
"""

report = """# Eleven-hour continuation — active progress report

## Current verified state

""" + common + """
- Existing verification:312Mac/Python3.14 tests pass after helper0.1.5;68existing Linux/Python3.11 helper/job tests pass after that change. Last relevant Ruby run262tests/1787assertions passes. Frontend remains100/102 with two documented preexisting catalog/input failures; historical101 is not a current green result.
- Original production public evaluation remains0/8, all inconclusive. The exposed Boltons closed-helper research profile reaches8/8 and physical binding checks pass, but these are development results; planner/routing/applier were not integrated. Independent neural lifecycle accuracy has not been established.
- New explicit written-pair role/polarity profile23/23owned controls versus14/23prior, plus seven exposed HTTPX checks. True annotations and general runtime prose stay unsupported. The actual HTTPX old-to-new helper transition remains inconclusive; matching14pairs in different source locations is not retirement or identical runtime behavior.
- Actual Go cache/receipt controls: prior2/9 versus current9/9; invalid complete-callable, receiver, kind, producer and limitation substitutions now refuse. Valid second reads are DUPLICATE, not FOUND; no second quote injection was observed. Seven Python cache controls remain7/7. Exact preimages and raw failed driver/oracle attempts are retained.
- Current FAQ census77frozen pairs plus64current candidates, of which58chapter-derived and six standalone; no code-span differences in282language rows. This does not certify semantic equivalence or independence.
- Selected pure MLX-LM argument builder and data adapters were executed in isolated namespaces. No full framework module, real tokenizer, model, tensor, trainer, optimizer or training was loaded/executed. Pure adapter14cases agree on Mac3.14/Linux3.11; four owned template-interface cases expose assumptions, not an actual tokenizer defect.
- Metadata-only partition diagnostics: hashing rows splits28bilingual tasks and15families; hashing lineages still splits four families; declared-family assignment removes measured declared overlaps only. No actual training/validation/evaluation split or export was created.
- Cachetools:23 event/owned-clock native observations in14logical groups agree on Mac3.14/Linux3.11; one additional no-store case computed twice sequentially with peak concurrency1. Its already-exposed family is not a new holdout. The ninth model response is completeJSON but labels all ten claims INSUFFICIENT, matching only1/10; rejected without retry. Seven manual lifecycle scenarios cover all five actions and have27preserved review-bundle files; they are not classifier successes. Explicit primary removal notice plus namespace/source corroboration supports only the namedMRUAPIretirement proposal.
- MLX-LM source architecture chapterV2 has14claims/sevenFAQ,19physical units,158structural checks and14agent language reviews; no independent semantic certification or owner approval.
- Latest sealed recoveryV5 verifies21114effective files and actual restored research consumption. It predates the completed backoff response and later pilot/copy/cache work; a new current cut remains required. No cold boot, remote durability or full training recovery is claimed.

Scope remains bounded: source/metadata research and preserved existing tools are authorized. No neural weights/tokenizer download, framework installation, private application collection, Git mutation, live catalog/UI/schema change or external repository mutation occurred. Fine-tuning stays NO-GO0/9.

## Retained chronological progress

"""

readiness = """# Fine-tuning readiness — training prohibited

## Current decision

**NO-GO:0/9 requirements fully satisfied.**

""" + common + """
Source-derived preparation is more precise, but compatible trainable model/tokenizer, approved targets/rights, independent evaluation, measured memory/throughput, installed locked framework and exact optimizer/RNG/data-position recovery remain unverified. The GGUF is not a trainable checkpoint. Future pilot proposals and stop thresholds are data-only and launch_allowed=False.

Pure adapters do not enforce Engineering Library approval/exclusion metadata. Their synthetic native-shaped rows are different from the frozen305 schema; no export or training admission is authorized. Four owned tokenizer-method sinks show that prefix consistency and nonempty targets need independent checks. No real tokenizer/template was run; Jinja2/MarkupSafe are absent and were not installed. Standard CPython3.14 wheel listings are nominal metadata, not installed compatibility evidence.

All new research/candidates/model responses remain excluded under the append-only V2–V9 exclusion chain and default-deny derivatives. Hypothetical family grouping removes measured overlaps only; approved gold0 and no certified independent split. Selected recovery improvements do not satisfy training persistence/hardware gates.

## Retained readiness evidence

"""

resume = """# Continuation recovery instructions

## Latest continuation state

""" + common + """
1. Continue meaningful authorized work until the measured minimum; do not infer completion from reports, passing tests or compaction. Next: refresh complete inventory and seal/consume a current delta overV5. Go controls and three legacy nonmigration readbacks are already preserved. All nine model calls are complete; no inference is active.
2. Use the original baseline/authorization, latest checkpoints, current queue and exact current manifest. Do not rerun non-reentrant old seal/writer scripts into their existing output paths.
3. Current code: caller1.9.43, helper0.1.5; helper0.1.4 and earlier journals require explicit legacy review, with no automatic migration/refund/quote injection. Older sealed cuts retain their historical source versions.
4. Preserve original0/8public oracle. Closed grammar results8/8Boltons,23/23owned map controls and seven HTTPX followups are exposed research; no production planner integration, automatic applier support or publication authority.
5. Tests312MacPython/68Linuxsubset/262Ruby1787assertions pass within their recorded scopes. Frontend100/102 remains limited. No permanent test files changed.
6. Nine model calls are complete/rejected as full requested outputs; no active inference, retry or optimizer. Future neural training remains prohibited and NO-GO0/9.
7. Current candidates64FAQpairs plus frozen77 are quarantined. Pure parser/data-adapter execution is distinct from framework/trainer execution. No actual tokenizer/MLX model run or real dataset split/export occurred.
8. Keep human campaign reports in these four root files. Technical artifacts remain under the research/preservation paths. Use record_checkpoint_v2.py approximately every30minutes; directly check source pins, HEAD/index and next safe action.

## Retained dated continuation notes

"""

extra = """
## Cache source, concrete review bundle and final inference update

Nine calls are now complete on the unchanged approved model:7source-generation/judgment tasks plus2conditions of the owned exact-copy probe,8140generated tokens and4085.059serverseconds. All complete requested outputs are rejected, with partial successes recorded separately. The latest cache source label response is valid completeJSON but all10INSUFFICIENT and only1/10matches. This is not lifecycle-action accuracy or neural improvement. No inference or optimizer is active. Current model-store/runtime revalidation is separately logged.

Cachetools was already development-exposed before this campaign. The new6.0.0helper/condition work gives23frozen native observations across14groups on Mac3.14/Linux3.11, plus one separate no-store observation:two sequential computations,peak concurrent user functions1,empty cache. That bounds exactly-once language. An initial extra diagnostic field confused condition attachment with the probe wait expectation; V2corrects the label and cross-context comparisons useV2. The pinned changelog explicitly retiresMRUCache/func.mru_cache, and full selected package exports/owned namespace checks corroborate; no current application installation is certified.

Seven manual lifecycle references (ADD1,MODIFY2,REMOVE1,NO-OP2,INCONCLUSIVE1) produced14language entries and27concrete isolated before/candidate/diff/manifest files. Source bytes/physical owned document inputs and all archive members are verified. This is an owner-review bundle, not seven classifier successes, an automatic applier, human-authored catalog certification or live publication. Earlier documents and migration provenance remain preserved.

Current FAQ auditV6:77frozen+64current pairs,58chapter-derived/six standalone;282language rows and no current code-span differences. NewMLXchapterV2has14claims/sevenFAQ with158structural checks and14agentlanguage reviews;not an independent translation certification. All new material remains excluded underV9. Frozen305rows/gold0/optimizer0/readinessNO-GO0/9remain unchanged.

## Pure data adapters, partition diagnostics and explicit map roles

The exact pinned MLX-LM five pure dataset classes plus create_dataset were executed only after source admission in an isolated namespace with owned method sinks returning integer lists. Fourteen owned cases were observed: first-row-only format selection, absent campaign approval admission, empty/mixed-input failures, cached processing, raw-dictionary item lengths, concatenation bounds/iteration and mutable row routing. Identical cases matched across MacPython3.14 and LinuxPython3.11; these are fourteen cases, not28independent cases. An own namespace annotation defect on3.11 was corrected by providing builtin bool; that failure is retained and is not an upstream compatibility bug.

Four additional ChatDataset template-interface controls show that method-returned prefix lengths are trusted without checking matching token prefixes, offsets within the full list or nonempty assistant content. Owned sinks are not a real tokenizer. Added-token metadata IDs fit configured vocabulary, bos matches and eos belongs to the modelEOS set, but BPE/template execution, shifted trainer masks and actual model compatibility remain unverified. Optional Jinja rendering was not attempted after observing Jinja2/MarkupSafe absent. No installation occurred.

The305-row metadata diagnostic found28bilingual tasks/27lineages/15families split by illustrative row hashing, four families split by lineage hashing, and no measured declared overlaps by family hashing. Labels are hypotheticalA/B diagnostics only; seven dataset file hashes and original split/approval fields remain unchanged. This is not an actual train/validation split, ancestry certificate or recommendation of final allocation.

The written-map profile requires exact bilingual literal-return role and polarity. Its23owned controls match23/23 versus14/23prior; seven HTTPX followups match seven expected outcomes. The oldHTTPX module map and current helper retain14pairs/order, while the old helper selector is absent; the real transition remains INCONCLUSIVE. This is not a REMOVE decision or general prose/runtime validator. Own V1 nonexistent exception-name failure was preserved before V2 correction.

Evidence: pilot-data-adapter-cross-context-v1.json, pilot-template-interface-results-v1.json, dataset-partition-diagnostics-v1.json, written-map-pair-results-v2.json and written-map-httpx-results-v1.json, all under agent/research/continuation-20261120/. ExclusionsV9 retains all derivatives outside training gold.
"""

for name, prefix, marker in [
    ('AI_TRAINING_CAMPAIGN_REPORT.md', report, '## Retained chronological progress'),
    ('AI_FINE_TUNING_READINESS.md', readiness, '## Retained readiness evidence'),
    ('AI_TRAINING_RESUME.md', resume, '## Retained dated continuation notes'),
]:
    path = ROOT / name
    raw = path.read_bytes()
    checksum = hashlib.sha256(raw).hexdigest()
    preserved = history / (checksum + '.md')
    if not preserved.exists():
        preserved.write_bytes(raw)
    assert preserved.read_bytes() == raw
    text = raw.decode()
    assert text.count(marker) == 1
    retained = text.split(marker, 1)[1].lstrip('\n')
    path.write_text(prefix + retained + extra)
    receipts.append({'path': name, 'preimage': str(preserved.relative_to(ROOT)), 'preimage_sha256': checksum,
                     'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})

with (P / 'root-current-state-prefix-v3.json').open('x') as stream:
    json.dump({'at': now.isoformat(), 'elapsed_hours': elapsed, 'status': 'ACTIVE', 'reports': receipts,
               'history_preserved_exactly': True, 'eleven_hours_claimed': False}, stream, indent=2)
    stream.write('\n')
print(json.dumps({'at': now.isoformat(), 'elapsed_hours': elapsed, 'reports': len(receipts)}))
