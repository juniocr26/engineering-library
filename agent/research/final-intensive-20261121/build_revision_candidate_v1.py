"""Produce a bilingual, source-bound maintenance candidate, never apply it."""
from pathlib import Path
import ast
import datetime
import difflib
import hashlib
import json

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
E = P/'real-revision-evidence-v1'
old = (E/'before/agent/tools/documentation_retrieval.py').read_text()
new = (E/'after/agent/tools/documentation_retrieval.py').read_text()
doc = (E/'after/agent/tools/documentation_retrieval.md').read_text()
job = (E/'after/agent/tools/documentation_job_budget.py').read_text()
sha = lambda raw: hashlib.sha256(raw).hexdigest()
assert 'VERSION = "0.1.3"' in old and 'VERSION = "0.1.5"' in new
assert (E/'before/agent/tools/documentation_retrieval.md').read_bytes() == (E/'after/agent/tools/documentation_retrieval.md').read_bytes()
assert 'Version 0.1.3 is' in doc
assert 'expected = python_unit' not in old and 'expected = python_unit' in new
assert 'expected = extract(raw.decode' not in old and 'expected = extract(raw.decode' in new
sources = {'helper': new, 'job': job, 'existing_doc': doc, 'previous_helper': old}
claims = [
    ('R01', 'helper', [21, 21], 'VERSION = "0.1.5"', 'The selected helper version is 0.1.5.', 'A versão selecionada do helper é 0.1.5.'),
    ('R02', 'helper', [98, 102], 'expected = python_unit', 'Python unit validation reconstructs the selected lexical callable and compares canonical evidence units.', 'A validação de unidades Python reconstrói o callable léxico selecionado e compara as unidades de evidência canônicas.'),
    ('R03', 'helper', [109, 113], 'expected = extract', 'Go unit validation invokes extraction and compares the resulting canonical unit.', 'A validação de unidades Go chama a extração e compara a unidade canônica resultante.'),
    ('R04', 'helper', [145, 148], 'validate_unit(cached["evidence"]', 'A cached FOUND result calls validate_unit during cached-result validation.', 'Um resultado FOUND em cache chama validate_unit durante a validação do resultado em cache.'),
    ('R05', 'helper', [425, 439], 'validate_unit(unit, raw', 'The fresh-extraction path also calls validate_unit and catches subprocess.SubprocessError in its inner extraction handler.', 'O caminho de extração nova também chama validate_unit e captura subprocess.SubprocessError em seu tratador interno de extração.'),
    ('R06', 'helper', [267, 269], 'timeout=20', 'The selected Go extraction subprocess uses timeout=20; a timeout is not successful source retrieval.', 'O subprocesso selecionado de extração Go usa timeout=20; um timeout não é obtenção bem-sucedida da fonte.'),
    ('R07', 'helper', [399, 413], 'validate_cached(cached', 'The duplicate path calls validate_cached outside the fresh-extraction inner handler.', 'O caminho de duplicata chama validate_cached fora do tratador interno da extração nova.'),
    ('R08', 'job', [306, 310], 'except Exception as error', 'The shown JobBoundRetrieval wrapper returns UNKNOWN_COMPLETION when helper.request raises an Exception.', 'O wrapper JobBoundRetrieval mostrado retorna UNKNOWN_COMPLETION quando helper.request lança uma Exception.'),
]
# Compound R05 is explicitly two properties; this ledger is eight review groups,
# not eight independent atomic propositions or a new model precision estimate.
rows = []
for cid, source, span, marker, en, pt in claims:
    lines = sources[source].splitlines()
    quote = '\n'.join(lines[span[0]-1:span[1]])
    assert marker in quote, (cid, quote)
    rows.append({'id': cid, 'source': source, 'source_lines': span, 'exact_source_evidence': quote,
                 'source_sha256': sha(sources[source].encode()), 'en': en, 'pt-BR': pt,
                 'verdict': 'SUPPORTED_STATIC_REVIEW', 'reviewer': 'same Codex campaign agent, separate pinned Git reads',
                 'atomic_metric_eligible': False})
out = P/'helper-cache-maintenance-candidate-v1'
out.mkdir()
header = {
    'en': '# Bounded helper cache validation: maintenance candidate\n\nResearch-only change note for engineering-library from b586e484a56ef7e868c7257b2ea11ad9f71b606b to 7dbc3b696ddafb6a302ae47ea412e85b587bc308. Audience: operators of the optional source-retrieval API. This is selected static control flow, not exhaustive helper architecture or observed runtime behavior.\n',
    'pt-BR': '# Validação de cache do helper delimitado: candidato de manutenção\n\nNota de alteração somente para pesquisa em engineering-library, de b586e484a56ef7e868c7257b2ea11ad9f71b606b para 7dbc3b696ddafb6a302ae47ea412e85b587bc308. Público: operadores da API opcional de obtenção de fonte. Descreve o fluxo de controle estático selecionado, sem cobrir toda a arquitetura do helper ou comportamento observado em runtime.\n',
}
footer = {
    'en': 'The prior helper source version was 0.1.3; the existing guide still identifies that version and describes physical-quote checks. The source revision adds whole lexical-unit reconstruction and comparison. The existing guide therefore needs MODIFY within this declared scope.\n\nThe outer helper exception tuple does not include subprocess.SubprocessError, while the fresh-extraction inner tuple does. In the shown duplicate path, a Go subprocess exception may escape to the job wrapper. Do not promise that every cached revalidation returns a normal status or that a failed subprocess retrieved valid evidence. The caller must retain uncertainty and the reserved-job evidence. No automatic replay is justified here.\n\nNo external source, helper request, subprocess fault or application test was executed for this candidate. Historical defect receipts remain separate. Lexical evidence is not runtime binding, source semantics, publication permission or training Gold. Examples and operational commands are outside this bounded change-note scope. This candidate was manually authored; no neural improvement is claimed.\n',
    'pt-BR': 'A versão anterior da fonte do helper era 0.1.3; o guia existente ainda identifica essa versão e descreve verificações de citações físicas. A revisão da fonte acrescenta reconstrução e comparação de toda a unidade léxica. O guia existente portanto precisa de MODIFY dentro deste escopo declarado.\n\nA tupla externa de exceções do helper não inclui subprocess.SubprocessError, enquanto a tupla interna da extração nova inclui. No caminho de duplicata mostrado, uma exceção do subprocesso Go pode escapar para o wrapper do job. Não prometa que toda revalidação em cache retorna um status normal ou que um subprocesso que falhou obteve evidência válida. O chamador deve preservar a incerteza e a evidência do job reservado. Nenhum replay automático se justifica aqui.\n\nNenhuma fonte externa, requisição ao helper, falha de subprocesso ou teste de aplicação foi executado para este candidato. Os recibos históricos do defeito ficam separados. Evidência léxica não é vínculo em runtime, semântica da fonte, permissão de publicação ou Gold de treinamento. Exemplos e comandos operacionais estão fora do escopo desta nota delimitada. Este candidato foi escrito manualmente; não se alega melhoria neural.\n',
}
paths = {'helper': 'agent/tools/documentation_retrieval.py', 'job': 'agent/tools/documentation_job_budget.py'}
documents = []
for language in ['en', 'pt-BR']:
    text = header[language]+'\n'
    for row in rows:
        text += row['id']+': '+row[language]+'\n\nSource: '+paths[row['source']]+':'+str(row['source_lines'])+' @ 7dbc3b696ddafb6a302ae47ea412e85b587bc308\n\n'
    text += footer[language]
    with (out/(language+'.md')).open('x') as stream:
        stream.write(text)
    documents.append({'language': language, 'path': str((out/(language+'.md')).relative_to(ROOT)), 'sha256': sha(text.encode())})
with (out/'new-candidate.diff').open('x') as stream:
    for item in documents:
        text = (ROOT/item['path']).read_text()
        stream.write(''.join(difflib.unified_diff([], text.splitlines(True), fromfile='/dev/null', tofile=item['path'])))
observations = json.loads((P/'real-revision-acquisition-v1.json').read_text())
result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'repository': 'engineering-library',
          'lifecycle_decision': 'MODIFY', 'reason': 'Pinned source behavior/version changed while existing helper guide stayed byte-identical and identifies old version.',
          'existing_document': 'agent/tools/documentation_retrieval.md', 'existing_document_modified': False,
          'review_groups': rows, 'review_groups_are_not_atomic_claim_count': True, 'documents': documents,
          'new_complete_document_technical_status': 'PENDING_ALL_PROSE_G1_G9_REVIEW',
          'external_tasks': observations['external'], 'unsafe_REMOVE_recommendations': 0,
          'lifecycle_accuracy': None, 'accuracy_limit': 'Same-agent source adjudication, no independent frozen reference set for new real revision tasks; no percentage manufactured.',
          'source_snapshot_revision_matches_current_file': (ROOT/'agent/tools/documentation_retrieval.py').read_bytes() == new.encode(),
          'source_program_executed': False, 'tests_executed': False, 'owner_approved': False, 'publication_approved': False,
          'training_gold_approved': False, 'model_calls': 0, 'optimizer_updates': 0}
with (P/'real-revision-review-v1.json').open('x') as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
print(json.dumps({'self_lifecycle': 'MODIFY', 'external_inconclusive': sum(x['lifecycle_status']=='INCONCLUSIVE' for x in observations['external']), 'candidate_pair': len(documents)}))
