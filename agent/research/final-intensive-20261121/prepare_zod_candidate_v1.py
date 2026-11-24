"""Create an isolated wording clarification; preserve every original chapter byte."""
from pathlib import Path
import datetime
import difflib
import hashlib
import json
import re

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
original = ROOT/'agent/research/portfolio-vivabem-20261120/zod-safe-parse-candidate-v2'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
changes = {
    'en': ('A separate reviewer reacquires public Git objects and queries their AST.',
           'The same campaign agent used separate source-acquisition and AST-query procedures; this was not independent human review.'),
    'pt-BR': ('Um revisor separado obtém novamente objetos públicos do Git e consulta seu AST.',
              'O mesmo agente da campanha usou procedimentos separados de aquisição de fonte e consulta ao AST; isso não constituiu revisão humana independente.'),
}
freeze = {'frozen_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'source_candidate': str(original.relative_to(ROOT)),
          'scope': 'Exactly one reviewer-provenance sentence per language. No source/API/test/runtime claim or code example changes.',
          'changes': changes,
          'expected': 'Original chapter hashes unchanged; all code fences and source citations preserved; explicit same-agent wording in both languages.',
          'approval': 'Separate research candidate only. Owner/publication/training approvals remain false. No original score replacement.',
          'producer_sha256': sha(Path(__file__).read_bytes())}
with (P/'zod-clarification-protocol-v1.json').open('x') as stream:
    json.dump(freeze, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
output = P/'zod-provenance-candidate-v3'
output.mkdir()
rows = []
for language, (old, new) in changes.items():
    source = original/(language+'.md')
    raw = source.read_bytes()
    text = raw.decode()
    assert text.count(old) == 1
    candidate = text.replace(old, new)
    with (output/(language+'.md')).open('x') as stream:
        stream.write(candidate)
    patch = ''.join(difflib.unified_diff(text.splitlines(True), candidate.splitlines(True),
                                        fromfile=str(source.relative_to(ROOT)), tofile=str((output/(language+'.md')).relative_to(ROOT))))
    with (output/(language+'.diff')).open('x') as stream:
        stream.write(patch)
    fences = lambda value: re.findall(r'```[^\n]*\n.*?```', value, re.S)
    citations = lambda value: re.findall(r'packages/zod/[^`\s]+', value)
    assert fences(text) == fences(candidate)
    assert citations(text) == citations(candidate)
    assert sha(source.read_bytes()) == sha(raw)
    rows.append({'language': language, 'original': str(source.relative_to(ROOT)), 'original_sha256': sha(raw),
                 'candidate': str((output/(language+'.md')).relative_to(ROOT)), 'candidate_sha256': sha(candidate.encode()),
                 'code_fences_unchanged': True, 'source_citations_unchanged': True,
                 'review': 'Both complete language texts read; scoped source semantics unchanged, reviewer identity clarified.',
                 'original_unchanged': True})
result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'records': rows,
          'status': 'CORRECTED_ISOLATED_CANDIDATE_FOR_OWNER_REVIEW',
          'resolved_research_wording_issue': 'Ambiguous independent-reviewer attribution',
          'new_technical_acceptance': 'INCONCLUSIVE_PENDING_COMPLETE_G1_G9_REVIEW_OF_THIS_EXACT_PAIR',
          'historical_source_review': 'owner-review-package-v3.json; six source groups, 46 selected propositions are not 46 newly verified independent claims.',
          'syntax_validation': 'Unchanged code fence; previous syntax-only receipt historical, no new TypeScript parser/runtime invoked.',
          'owner_approved': False, 'publication_approved': False, 'training_gold_approved': False,
          'training_eligible': False, 'neural_authorship': False, 'model_calls': 0, 'optimizer_updates': 0}
with (P/'zod-clarification-results-v1.json').open('x') as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
print(json.dumps({'candidate_pair_created': True, 'originals_unchanged': True, 'code_and_citations_preserved': True}))
