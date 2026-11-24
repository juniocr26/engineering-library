"""Record explicit same-agent all-prose review without training/publication approval."""
from pathlib import Path
import datetime
import hashlib
import json

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sha = lambda raw: hashlib.sha256(raw).hexdigest()
candidate = json.loads((P/'real-revision-review-v1.json').read_text())
source_base = P/'real-revision-evidence-v1'
revision = '7dbc3b696ddafb6a302ae47ea412e85b587bc308'
previous = 'b586e484a56ef7e868c7257b2ea11ad9f71b606b'
sources = {
    'helper': ('after', 'agent/tools/documentation_retrieval.py', revision),
    'old_helper': ('before', 'agent/tools/documentation_retrieval.py', previous),
    'job': ('after', 'agent/tools/documentation_job_budget.py', revision),
    'guide': ('after', 'agent/tools/documentation_retrieval.md', revision),
}
# One independently falsifiable source proposition per row. Repeated footer and
# bilingual occurrences do not create additional independent observations.
atoms = [
    ('A01', 'helper', [21,21], 'Selected helper version is 0.1.5.', ['R01']),
    ('A02', 'helper', [98,102], 'Python validation reconstructs the selected lexical callable.', ['R02','footer paragraph 1']),
    ('A03', 'helper', [100,102], 'Python validation compares canonical evidence units.', ['R02','footer paragraph 1']),
    ('A04', 'helper', [109,113], 'Go validation invokes extraction.', ['R03','footer paragraph 1']),
    ('A05', 'helper', [111,113], 'Go validation compares the resulting canonical unit.', ['R03','footer paragraph 1']),
    ('A06', 'helper', [145,148], 'Cached FOUND validation calls validate_unit.', ['R04']),
    ('A07', 'helper', [425,428], 'Fresh extraction calls validate_unit.', ['R05']),
    ('A08', 'helper', [438,439], 'Fresh inner extraction handler explicitly catches subprocess.SubprocessError.', ['R05','footer paragraph 2']),
    ('A09', 'helper', [267,269], 'Selected Go extraction subprocess has timeout=20.', ['R06']),
    ('A10', 'helper', [267,278], 'A subprocess timeout is not a returned successful extracted unit.', ['R06']),
    ('A11', 'helper', [399,438], 'Duplicate validate_cached call is outside the fresh-extraction inner try body.', ['R07']),
    ('A12', 'job', [306,310], 'The shown wrapper returns UNKNOWN_COMPLETION on an Exception from helper.request.', ['R08']),
    ('A13', 'old_helper', [21,21], 'Prior helper source version was 0.1.3.', ['footer paragraph 1']),
    ('A14', 'guide', [1,8], 'Existing guide identifies version 0.1.3.', ['footer paragraph 1']),
    ('A15', 'guide', [39,43], 'Existing guide describes checking the quote against physical source lines.', ['footer paragraph 1']),
    ('A16', 'helper', [454,460], 'Outer helper exception tuple does not explicitly name subprocess.SubprocessError.', ['footer paragraph 2']),
    ('A17', 'helper', [399,460], 'In the shown duplicate path, a subprocess exception may escape the helper handler to a caller.', ['footer paragraph 2']),
]
rows = []
for cid, key, span, proposition, occurrences in atoms:
    label, path, rev = sources[key]
    source = source_base/label/path
    raw = source.read_bytes()
    quote = '\n'.join(raw.decode().splitlines()[span[0]-1:span[1]])
    assert quote
    rows.append({'claim_id': cid, 'family': 'engineering-library', 'source_revision': rev, 'source_path': path,
                 'source_file_sha256': sha(raw), 'exact_source_evidence': quote, 'source_lines': span,
                 'expected_interpretation': proposition, 'generated_interpretation': proposition,
                 'actual_occurrences': occurrences, 'languages': ['en','pt-BR'], 'verdict': 'SUPPORTED',
                 'critical': True, 'bilingual_consistency': True,
                 'reviewer': 'Same campaign Codex agent; full EN/PT texts and contextual pinned sources read.',
                 'provenance': 'Pinned real before/after Git objects, source-diff and separate owned AST exception-scope procedure.',
                 'conditions': 'Literal selected implementation and ordinary named exception-class graph; no dynamic monkey-patching/runtime guarantee.'})
assert 'quote against physical source lines' in next(r['exact_source_evidence'] for r in rows if r['claim_id']=='A15')
process = [
    {'proposition': 'No external source/helper request/subprocess fault/application test executed for this candidate.', 'evidence': ['real-revision-acquisition-v1.json','exception-scope-results-v2.json'], 'verdict': 'SUPPORTED_PROCESS_RECORD'},
    {'proposition': 'Candidate is manually authored; no new neural improvement.', 'evidence': ['build_revision_candidate_v1.py','real-revision-review-v1.json'], 'verdict': 'SUPPORTED_PROCESS_RECORD'},
]
documents = []
for row in candidate['documents']:
    raw = (ROOT/row['path']).read_bytes()
    assert sha(raw)==row['sha256']
    documents.append(row)
review = {
    'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'contract': 'documentation-done-v3.json', 'contract_sha256': sha((P/'documentation-done-v3.json').read_bytes()),
    'scope_freeze': 'real-revision-protocol-v1.json', 'scope_freeze_sha256': sha((P/'real-revision-protocol-v1.json').read_bytes()),
    'documents': documents, 'claims': rows, 'process_claims': process,
    'nonclaim_content': 'Audience and scope labels, recommendation to retain uncertainty/reservation evidence, no automatic replay instruction, limits on publication/Gold and excluded examples/commands.',
    'all_prose_reviewed': True, 'unreviewed_critical_propositions': 0,
    'selected_unique_source_claim_precision': {'numerator': 17, 'denominator': 17, 'population': 'Manual bounded helper change-note pair,17 source propositions; correlated, not neural outputs or independent projects.', 'method': 'Same-agent contextual source review plus exact identities and separate lexical-handler AST checks.', 'baseline': None, 'confidence_limitations': 'No independent human review, generic exception model, runtime test or whole-project architecture acceptance.'},
    'architecture_edges': [
        {'caller':'HelperRetrieval._request duplicate branch','callee':'validate_cached','source':'helper:399-407'},
        {'caller':'validate_cached FOUND branch','callee':'validate_unit','source':'helper:145-148'},
        {'caller':'validate_unit Python branch','callee':'python_unit','source':'helper:98-102'},
        {'caller':'validate_unit Go branch','callee':'extract','source':'helper:109-113'},
        {'caller':'extract Go branch','callee':'subprocess.run go_source_ast.py','source':'helper:267-269'},
        {'caller':'JobBoundRetrieval.request','callee':'helper.request','source':'job:306-310'},
    ],
    'gates': {
        'G1': {'status':'PASS','evidence':'real-revision-acquisition-v1.json; exact source revisions/files/hashes/spans in claim ledger and candidate hashes.'},
        'G2': {'status':'PASS','evidence':'All17 source propositions and2 process statements source-reviewed; no critical unsupported claim observed.'},
        'G3': {'status':'PASS','evidence':'All six relevant scoped caller/callee edges and explicit cached/fresh/job error boundaries covered. Whole-project architecture excluded before generation.'},
        'G4': {'status':'PASS','evidence':'All nine mandatory requirements in frozen real-revision-protocol-v1 self_task addressed; no retrospective narrowing.'},
        'G5': {'status':'PASS','evidence':'No runtime/test/example execution claimed. Code snippets/operational commands were excluded before generation; actual checks are static Git/AST only.'},
        'G6': {'status':'PASS','evidence':'Both complete texts read; source conditions, negations, versions, IDs and limitations equivalent.17 source propositions represented in both languages.'},
        'G7': {'status':'PASS','evidence':'Real before/after helper diff plus unchanged existing guide explicitly at old version support MODIFY; no deletion action.'},
        'G8': {'status':'PASS','evidence':'Separate Git acquisition and owned lexical AST exception-scope observer distinguish8 frozen profiles including unrelated-call/string controls. Same-agent semantic review explicitly disclosed.'},
        'G9': {'status':'INCONCLUSIVE','evidence':'Candidate/source/diff/protocol/observer preserved; exact current candidate-plus-review recovery checkpoint still pending. Do not silently count stored files as operational restore.'},
    },
    'technical_status': 'INCONCLUSIVE_PENDING_RECOVERY_OF_EXACT_CURRENT_REVIEW',
    'publication_approved': False, 'owner_approved': False, 'training_gold_approved': False,
    'training_eligible': False, 'neural_contribution': False, 'model_calls': 0, 'optimizer_updates': 0,
    'original_candidate_files_unchanged': True, 'production_doc_applied': False,
}
with (P/'helper-candidate-complete-review-v1.json').open('x') as stream:
    json.dump(review, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
print(json.dumps({'source_propositions_reviewed': len(rows), 'gates_pass': 8, 'G9': 'INCONCLUSIVE', 'technical_status': review['technical_status']}))
