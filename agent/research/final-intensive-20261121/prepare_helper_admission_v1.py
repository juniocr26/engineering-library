"""Freeze acquisition feasibility of the existing K source propositions."""
from pathlib import Path
import datetime
import hashlib
import json

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
tasks = [
    {'id':'python-class-field', 'task':'fastapi', 'path':'fastapi/dependencies/models.py', 'language':'python', 'selector':'Dependant', 'claim_ids':['F01','F02'], 'expected':'REFUSED', 'expected_reason':'missing or ambiguous callable'},
    {'id':'python-whole-solver', 'task':'fastapi', 'path':'fastapi/dependencies/utils.py', 'language':'python', 'selector':'solve_dependencies', 'claim_ids':['F03','F04','F05','F06','F07','F08','F09'], 'expected':'REFUSED', 'expected_reason':'complete decorated callable exceeds quote budget'},
    {'id':'go-function-type', 'task':'cobra', 'path':'args.go', 'language':'go', 'selector':'PositionalArgs', 'claim_ids':['C01'], 'expected':'REFUSED', 'expected_reason':'invalid Go callable declaration kind'},
    {'id':'go-membership', 'task':'cobra', 'path':'args.go', 'language':'go', 'selector':'OnlyValidArgs', 'claim_ids':['C02','C03'], 'expected':'ADMITTED_LEXICAL_UNIT'},
    {'id':'go-exact-args', 'task':'cobra', 'path':'args.go', 'language':'go', 'selector':'ExactArgs', 'claim_ids':['C04','C05'], 'expected':'ADMITTED_LEXICAL_UNIT'},
    {'id':'go-composition', 'task':'cobra', 'path':'args.go', 'language':'go', 'selector':'MatchAll', 'claim_ids':['C06','C07'], 'expected':'ADMITTED_LEXICAL_UNIT'},
    {'id':'go-deprecation-comment', 'task':'cobra', 'path':'args.go', 'language':'go', 'selector':'ExactValidArgs', 'claim_ids':['C08','C09'], 'expected':'ADMITTED_LEXICAL_UNIT', 'expected_uncovered_claims':['C09']},
    {'id':'typescript-source', 'task':'zod', 'path':'packages/zod/src/v4/core/parse.ts', 'language':'typescript', 'selector':'_safeParse', 'claim_ids':['Z01','Z02','Z03','Z04','Z05','Z06','Z07','Z08','Z09','Z10'], 'expected':'REFUSED', 'expected_reason':'unsupported registered language'},
]
for task in tasks:
    source = P/'reacquired-public-sources'/task['task']/task['path']
    task['source_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    task['source_bytes'] = source.stat().st_size
dependencies = ['agent/tools/documentation_retrieval.py','agent/tools/documentation_workspace.py','agent/tools/go_source_ast.py','agent/tools/go-source-ast/main.go','agent/tools/go-source-ast/manifest.json','agent/tools/go-source-ast/GO-LICENSE','agent/tools/go-source-ast/bin/go-source-ast-darwin-arm64']
protocol = {'frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'hypothesis':'Source-reviewed K notes do not imply that all their source facts are obtainable through the current optional callable-only helper API. Whole-callable quote budgets, declaration kinds, comments and language support may limit acquisition before model inference.',
            'tasks':tasks, 'dependencies':[{'path':name,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()} for name in dependencies],
            'scope':'Direct existing pure extraction/validation functions on pinned source text; no HelperRetrieval journal, source repository execution or model inference. Existing native owned Go parser may execute, never selected Go source.',
            'predicted_lexical_fact_span_coverage':{'numerator':7,'denominator':28},
            'metric_boundary':'Coverage of exact required evidence spans in admitted helper quotes, not factual precision or general repository retrieval success. Related previously exposed source tasks.',
            'host_exception':'Docker inaccessible. Use existing host Python and already installed owned darwin-arm64 parser, no installs or compilation.',
            'not_production_integration':True, 'model_calls':0, 'optimizer_updates':0,'gold':0}
with (P/'helper-admission-protocol-v1.json').open('x') as stream:
    json.dump(protocol,stream,indent=2)
    stream.write('\n')
print(json.dumps({'frozen_tasks':len(tasks),'required_claims':sum(len(t['claim_ids']) for t in tasks)}))
