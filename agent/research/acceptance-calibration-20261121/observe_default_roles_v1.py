"""Closed typed declaration-role observations, never a free-prose verifier."""
import ast
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
protocol_path = HERE / 'default-role-verifier-protocol-v1.json'
protocol = json.loads(protocol_path.read_text())
source = protocol['source']
raw = (ROOT / source['snapshot']).read_bytes()
if hashlib.sha256(raw).hexdigest() != source['sha256']:
    raise RuntimeError('Pinned independent source changed')
lines = raw.decode('utf-8').splitlines()
tree = ast.parse(raw.decode('utf-8'))


def physical_citation_valid(record):
    citation = record.get('citation')
    if not isinstance(citation, dict):
        return False
    line = citation.get('line')
    return (citation.get('path') == source['path']
            and citation.get('revision') == source['revision']
            and citation.get('source_sha256') == source['sha256']
            and type(line) is int and 1 <= line <= len(lines)
            and citation.get('quote') == lines[line - 1])


def typed_observation(record):
    result = {'verdict': 'INSUFFICIENT', 'record_admitted': False,
              'runtime_value_verified': False, 'free_prose_verified': False}
    if set(record) != {'role', 'owner', 'field', 'value', 'citation'}:
        return {**result, 'reason': 'Unverified extra/missing fields, including free prose'}
    if record['role'] != 'WRITTEN_LITERAL_DEFAULT':
        return {**result, 'reason': 'Runtime/constructor/factory/universal role outside admitted profile'}
    if not physical_citation_valid(record):
        return {**result, 'reason': 'Citation identity/physical bytes mismatch'}
    owners = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == record['owner']]
    if len(owners) != 1:
        return {**result, 'reason': 'Missing or ambiguous selected top-level class owner'}
    fields = [node for node in owners[0].body if isinstance(node, ast.AnnAssign)
              and isinstance(node.target, ast.Name) and node.target.id == record['field']]
    if len(fields) != 1:
        return {**result, 'reason': 'Missing or ambiguous direct annotated declaration; absence is not runtime proof'}
    field = fields[0]
    if not isinstance(field.value, ast.Constant):
        return {**result, 'reason': 'Nonliteral assignment; no call/factory execution or interpretation'}
    actual = field.value.value
    supplied = record['value']
    equivalent = type(actual) is type(supplied) and actual == supplied
    evidence = {'owner': owners[0].name, 'field': record['field'], 'actual_literal': actual,
                'actual_literal_python_type': type(actual).__name__,
                'supplied_python_type': type(supplied).__name__,
                'source_revision': source['revision'], 'source_path': source['path'],
                'source_sha256': source['sha256'], 'lines': [field.lineno, field.end_lineno],
                'exact_quote': '\n'.join(lines[field.lineno - 1:field.end_lineno]),
                'citation_names_actual_field_declaration': field.lineno <= record['citation']['line'] <= field.end_lineno}
    if not equivalent:
        return {**result, 'verdict': 'CONTRADICTED', 'evidence': evidence,
                'reason': 'Value/type differs from the exact selected declaration default; annotation token membership is not its assigned value'}
    if not evidence['citation_names_actual_field_declaration']:
        return {**result, 'evidence': evidence, 'reason': 'True data value attached to another declaration; record not admitted'}
    return {**result, 'verdict': 'SUPPORTED', 'record_admitted': True, 'evidence': evidence,
            'reason': 'Exact owner/field/written-default role and primitive value/type independently match'}


labels = ['SUPPORTED', 'CONTRADICTED', 'INSUFFICIENT']
matrix = {reference: {observed: 0 for observed in labels} for reference in labels}
records = []
rendered = []
for case in protocol['cases']:
    record = case['record']
    # This intentionally weak baseline is an isolated admission control, not the
    # real Ruby Caller or a semantic classifier. All original values survive.
    baseline_admitted = physical_citation_valid(record) and str(record.get('value')) in record['citation']['quote']
    observed = typed_observation(record)
    matrix[case['reference']][observed['verdict']] += 1
    records.append({'id': case['id'], 'original_record': record, 'reference': case['reference'],
                    'citation_token_membership_admitted': baseline_admitted,
                    'typed_source_observation': observed})
    if observed['record_admitted']:
        name = record['owner'] + '.' + record['field']
        value = repr(record['value'])
        rendered.append({'from_case': case['id'], 'authorship': 'fixed deterministic source-role template, not neural prose',
                         'en': 'The selected written `' + name + '` declaration assigns the default literal `' + value + '`.',
                         'pt-BR': 'A declaração escrita selecionada de `' + name + '` atribui o literal padrão `' + value + '`.',
                         'source_evidence': observed['evidence'], 'owner_approved': False, 'training_gold': False})


def ratio(numerator, denominator):
    return {'numerator': numerator, 'denominator': denominator,
            'ratio': numerator / denominator if denominator else None}


supported = [record for record in records if record['reference'] == 'SUPPORTED']
unsupported = [record for record in records if record['reference'] != 'SUPPORTED']
insufficient = [record for record in records if record['reference'] == 'INSUFFICIENT']
metrics = {
    'citation_token_baseline_false_admission': ratio(sum(record['citation_token_membership_admitted'] for record in unsupported), len(unsupported)),
    'typed_gate_false_admission': ratio(sum(record['typed_source_observation']['record_admitted'] for record in unsupported), len(unsupported)),
    'citation_token_baseline_valid_record_refusal': ratio(sum(not record['citation_token_membership_admitted'] for record in supported), len(supported)),
    'typed_gate_valid_record_refusal': ratio(sum(not record['typed_source_observation']['record_admitted'] for record in supported), len(supported)),
    'typed_gate_supported_verdict_precision': ratio(matrix['SUPPORTED']['SUPPORTED'], sum(matrix[label]['SUPPORTED'] for label in labels)),
    'typed_gate_justified_abstention': ratio(matrix['INSUFFICIENT']['INSUFFICIENT'], len(insufficient)),
    'closed_role_label_agreement': ratio(sum(matrix[label][label] for label in labels), len(records)),
}
result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'protocol_sha256': hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
          'observer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'source': source, 'records': records,
          'matrix_reference_rows_observed_columns': matrix, 'metrics': metrics,
          'rendered_bilingual_clauses': rendered,
          'complete_documents_generated': 0, 'new_model_calls': 0,
          'production_changes': False, 'permanent_tests_created': False,
          'owner_gold': 0, 'optimizer_updates': 0,
          'limits': ['Fourteen development-exposed owned records over one real source, not fourteen independent projects.',
                     'Typed owner/field/value and exact source-role matching supports only written primitive declaration defaults.',
                     'The observer rejects unverified free prose; it does not understand arbitrary documentation, dataclass constructors or live values.',
                     'Two deterministic bilingual clauses are not neural complete outputs, owner approval, training Gold or integrated knowledge.',
                     'Original FastAPI B response and all historical model denominators remain unchanged.']}
with (HERE / 'default-role-verifier-results-v1.json').open('x') as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
print(json.dumps(metrics, indent=2), flush=True)
