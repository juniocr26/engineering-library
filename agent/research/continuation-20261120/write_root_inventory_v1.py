"""Materialize complete current per-file inventory in the designated root report."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
baseline=json.loads((P/'baseline.json').read_text())
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,env=env,text=True).strip()
raw=subprocess.check_output(['git','status','--porcelain=v1','-z','--untracked-files=all'],cwd=ROOT,env=env)
items=raw.decode().split('\0');entries=[];index=0
while index<len(items):
    item=items[index];index+=1
    if not item:continue
    status=item[:2];name=item[3:]
    if 'R'in status or 'C'in status:
        original=items[index];index+=1
        raise ValueError('unexpected rename/copy;review owner provenance before inventory')
    entries.append({'status':status,'path':name})


def purpose(name,status):
    path=Path(name);relative=path.relative_to(P.relative_to(ROOT))if path.is_relative_to(P.relative_to(ROOT))else None
    if status.strip()=='D':return 'Redundant previous partial-campaign human report; exact bytes archived and all440historical recovery files restored before live-copy removal. Sealed references remain dated and reproducible.'
    known={
      'AI_TRAINING_CAMPAIGN_REPORT.md':'Canonical root active campaign findings, timing, outcomes, failures and limitations; no early completion claim.',
      'AI_TRAINING_FILE_INVENTORY.md':'Canonical root complete individual-file inventory, provenance, repository scope and checks.',
      'AI_FINE_TUNING_READINESS.md':'Canonical root nine-gate readiness report; explicit NO-GO, zero training and owner gold.',
      'AI_TRAINING_RESUME.md':'Canonical root recoverable continuation instructions and dated checkpoints.',
      'agent/recovery/manifest.json':'Reconcile missing historical report/two pre-existing stale tool hashes, then pin the validated two-source bilingual guard; exact prior locks preserved; model unchanged.',
      'backend/lib/documentation/command.rb':'Caller1.9.42:carry AST catch-reference metadata and refuse observed bilingual quoted-exception spelling/owner drift, including ambiguous shared terminals.',
      'backend/lib/documentation/python_structure.py':'Extract bounded written catch-reference identifiers from AST function spans without executing source; no runtime exception binding claim.'}
    if name in known:return known[name]
    if relative:
        parts=relative.parts
        if parts[0]=='new-public-sources-v1'and len(parts)>=4:return 'Pinned read-only '+parts[1].replace('--','/')+'@'+parts[2]+' snapshot: '+ '/'.join(parts[3:])+'; exact source/license/package evidence, never executed.'
        if parts[0]=='training-primary-sources-v1':return 'Pinned framework/model primary-source metadata or source: '+path.name+'; no weights or package installation.'
        if parts[0].startswith('chapter-candidates-v'):
            return 'Isolated full technical chapter '+parts[0]+' '+path.stem+';source/citation review evidence, not a canonical campaign report or published catalog. First version retains FAQ relevance defect.'
        if parts[0]in['physical-class-documents-v1','public-class-change-candidate-v1']:
            return 'Isolated '+('original physically registered'if parts[0].startswith('physical')else'proposed source-bound')+' generated-claim document '+ '/'.join(parts[1:])+';exact outside-byte preservation research, not owner catalog content.'
        if parts[0]=='exception-guard-owned-sources-v1':return 'Owned non-executed Python source observation for '+parts[1]+';qualified-name/bare/comment/dynamic exception guard boundary, not permanent test fixture.'
        if parts[0]=='helper-journal-public-v1':return 'Durable HelperRetrieval '+path.suffix.lstrip('.')+' journal artifact '+path.name+'; binds exact public request/result/receipt and preserves bounded recovery.'
        if path.name=='build-context-linux-arm64':return 'Preserved owned compiled Go build-condition observer for existing Linux ARM64 runtime;not an external application or inference artifact.'
        if path.name=='GO-LICENSE':return 'Exact preserved Go BSD license accompanying the owned standard-library-linked observer build.'
    suffix=path.suffix
    if suffix in['.py','.rb','.cjs','.go']:
        text=(ROOT/path).read_text(errors='replace')[:2000]
        first=next((line.strip(' #"\'')for line in text.splitlines()if line.strip()),'Research producer')
        return 'Research producer '+path.name+': '+first[:200]
    if suffix in['.stdout','.stderr','.txt']:
        if path.name=='authorized-request.txt':return 'Exact user authorization and eleven-hour operating/report-location requirements retained for reproducible scope.'
        return 'Raw '+('stderr/failure evidence'if suffix=='.stderr'else'stdout/source/command evidence')+' for '+path.stem+';retained rather than replaced by summary.'
    if suffix=='.jsonl':return 'Append-only machine records '+path.name+' for queue/checkpoints/metadata proposals;no automatic training promotion.'
    if suffix=='.json':
        label=path.stem
        if 'protocol'in label or 'oracle'in label or 'freeze'in label:return 'Frozen machine protocol/reference/producer identity '+path.name+';expected scope and observations defined before applicable prediction.'
        if 'checkpoint'in label:return 'Recoverable timestamped checkpoint/hash metadata '+path.name+';actual elapsed time and pending work.'
        if 'manifest'in label:return 'Machine manifest/candidate or preservation receipt '+path.name+';dated identity,not publication/owner approval.'
        return 'Machine result/receipt '+path.name+';individual retained evidence for '+label.replace('-',' ')+'.'
    return 'Retained technical evidence '+path.name+';see adjacent frozen protocol/receipt for experiment scope.'


for entry in entries:
    entry['purpose']=purpose(entry['path'],entry['status'])
    path=ROOT/entry['path']
    if path.is_file():entry.update(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
report=ROOT/'AI_TRAINING_FILE_INVENTORY.md'
if report.exists():
    old=report.read_bytes();history=ROOT/'.local-backups/continuation-20261120/root-report-history';history.mkdir(parents=True,exist_ok=True);archive=history/(hashlib.sha256(old).hexdigest()+'.md')
    if not archive.exists():
        with archive.open('xb')as stream:stream.write(old)
    if archive.read_bytes()!=old:raise ValueError('old root inventory preservation failed')
created=[e for e in entries if e['status']=='??'];modified=[e for e in entries if e['status'].strip()=='M'];deleted=[e for e in entries if e['status'].strip()=='D']
lines=['# Active campaign repository and individual-file inventory','',
       'Snapshot: '+now+'. Campaign ACTIVE; this is an incremental inventory, not a final recovery closure.','',
       'Engineering Library: `'+str(ROOT)+'`. Baseline/current HEAD `'+head+'`;baseline was clean, so pre-existing tracked/untracked changes: Nenhum. Owner baseline changes from the earlier partial campaign are preserved as baseline, not attributed to this continuation. No staging/commit/history operation was performed.','',
       'Current counts: '+str(len(created))+'created files, '+str(len(modified))+'modified files, '+str(len(deleted))+'deleted live copies. Ignored local recovery archives/preimages are separately recorded below. Each retained source version, rejected response and failed producer remains technical evidence.','',
       '## Modified files','', '| File | Individual reason |','|---|---|']
for entry in modified:lines.append('| `'+entry['path']+'` | '+entry['purpose']+' |')
if not modified:lines.append('| Nenhum | |')
lines+=['','## Deleted live copies','', '| File | Individual justification |','|---|---|']
for entry in deleted:lines.append('| `'+entry['path']+'` | '+entry['purpose']+' Exact file-specific hash/archive mapping is in `agent/research/continuation-20261120/report-migration-v1.json`. |')
if not deleted:lines.append('| Nenhum | |')
lines+=['','## Created files — complete individual purposes','', '| File | Individual purpose |','|---|---|']
for entry in created:lines.append('| `'+entry['path']+'` | '+entry['purpose'].replace('|','\\|')+' |')
lines+=['','## Relevant inspected-only files and checks','',
       'The source changes above are the only production source changes. No permanent test file, schema, UI, skill or published catalog was changed. Relevant inspected-only files include:','']
inspected=[
'agent/tools/documentation_lifecycle.py','agent/tools/documentation_maintenance.py','agent/tools/documentation_candidates.py','agent/tools/documentation_workspace.py','agent/tools/documentation_retrieval.py','agent/tools/documentation_retrieval.md','agent/tools/go_source_ast.py','agent/tools/go-source-ast/main.go','agent/tools/go-source-ast/manifest.json','agent/tools/go-source-ast/README.md','agent/recovery/bootstrap.py','agent/recovery/model-bundle.json','backend/lib/documentation/project_command.rb','backend/lib/documentation/research.rb','agent/research/documentation-intelligence-20261120/closing-receipt-v1.json','agent/research/documentation-intelligence-20261120/recovery-manifest-candidate-v1.json','agent/research/documentation-intelligence-20261120/helper-consumption-and-control-review-v1.json','agent/research/documentation-intelligence-20261119/datasets/v10/manifest.json','agent/research/continuation-20261119/go-predeclared-binding-study.json','agent/research/continuation-20261119/go-module-boundaries.json','agent/research/continuation-20261119/go-module-resolution-study.json']
inspected += [str(path.relative_to(ROOT))for path in sorted((ROOT/'backend/test/offline').glob('*_offline.rb'))]
inspected += [str(path.relative_to(ROOT))for path in sorted((ROOT/'agent/test').glob('*_test.py'))]
inspected += ['backend/test/offline/python_structure_offline.py']
for name in inspected:
    if (ROOT/name).is_file():lines.append('- `'+name+'` — inspected/executed existing evidence; unchanged from baseline.')
lines+=['','Existing executions:312agentPython tests passed after report migration;262Ruby tests/1787assertions passed after the actual caller correction;3backendPythonphysical-line tests passed. Repeated research matrices are not counted as new distinct permanent tests.101JavaScript baseline tests are inherited dated evidence until a justified fresh run. Individual research controls/results are in their technical receipts;they are not new permanent suites.','',
'## External repository material — read-only snapshots, sem alterações','',
'No external Git worktree was written. The following names identify repositories represented by read-only public or previously frozen material, rather than new writable clones. Created/modified/deleted files in each external repository: Nenhum.','',
'| Repository/material | Inspected scope | State |','|---|---|',
'| jmespath/jmespath.py | Two exact source revisions,license bytes,facade/parser/visitor metadata and source claims | sem alterações |',
'| twpayne/go-geom | Two pinned source/license/module snapshots;syntax-only producer observations | sem alterações |',
'| lukeed/totalist | Two pinned JS source/package/license snapshots;exports/signatures | sem alterações |',
'| ml-explore/mlx-lm | Exact framework source revision,LoRA entry point/trainer/configuration metadata | sem alterações |',
'| golang/go | Preserved Go1.27.4toolchain source,MatchFile implementation and supplied import-clause snapshots | sem alterações |',
'| sdk-go | Previously frozen82-file package snapshot,qualified lexical census only | sem alterações |',
'| Boltons | Original8frozen lifecycle inputs and exact source snapshots;development-exposed | sem alterações |',
'| mlx-community/Llama-3.2-3B-Instruct-4bit | Small model/config/tokenizer-configuration metadata only;no weights | sem alterações |',
'| meta-llama/Llama-3.2-3B-Instruct | Public model/card/license metadata;two protected requests401,no credentials/retry | sem alterações |']
rights=json.loads((P/'dataset-lineage-audit-v1.json').read_text())['rights_evidence']
for entry in rights:lines.append('| '+entry['repository']+' | Frozen primary license/notice records checked for integrity only;training rights not approved | sem alterações |')
lines+=['','Dataset-family metadata and396registered immutable references were read for hash/lineage integrity;this does not mean every represented external source was semantically reviewed or every original checkout was reopened.','',
'## Ignored local preservation and migration dependencies','',
'- `.local-backups/continuation-20261120/report-history-v1/` retains exact5removed report preimages. Previous sealed base+delta archives independently reconstruct all440historical files and original paths.','- `.local-backups/continuation-20261120/recovery-manifests/` retains each exact operational lock before atomic replacement.','- `.local-backups/continuation-20261120/exception-identifier-guard-preimages/` retains baseline and rejected intermediate source versions.','- `.local-backups/continuation-20261120/go-build-context-v1/build-artifacts.tar.gz` retains the exact owned offline observer build,source,license andflags;preservation receipt pins every member.','- `.local-backups/continuation-20261120/root-report-history/` retains superseded root inventory bytes.','- `agent/research/continuation-20261119/agentic-architecture.md` remains intact:1495incomingreferences include operational/dataset/recovery dependencies. No blanket nested-Markdown removal occurred.','',
'No remote durability,cold-boot recovery,owner approval,neural fine-tuning or eleven-hour completion is implied by this inventory.','']
report.write_text('\n'.join(lines))
payload={'at':now,'baseline_head':baseline.get('head'),'current_head':head,'entries':entries,'root_report':str(report.relative_to(ROOT)),'scope':'Incremental individual-file inventory;own mutable report hash is a dated pre-write snapshot,not final closure.','pre_existing_changes':'Nenhum','external_worktree_changes':'Nenhum'}
with(P/'file-inventory-snapshot-v1.json').open('x')as stream:json.dump(payload,stream,indent=2)
print(json.dumps({'created':len(created),'modified':len(modified),'deleted':len(deleted),'head_unchanged':head==baseline.get('head')}))
