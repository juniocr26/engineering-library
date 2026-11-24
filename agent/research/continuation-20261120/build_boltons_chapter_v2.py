"""Complete bounded bilingual chapter from physical source and confined receipts."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import re

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
OLD = P.parent / 'documentation-intelligence-20261120'
REVS = {'24.0.0': '992a58c1036fcf4d52cbf3313b6217b7c07b11d9', '25.0.0': 'c23dbdadb6fecdf505eb4231559561913b84c13f'}
sha = lambda data: hashlib.sha256(data).hexdigest()
oracle = json.loads((OLD / 'public-lifecycle-oracle-v1.json').read_text())
router = json.loads((P / 'boltons-keyword-router-development-v1.json').read_text())
units = {}
for case in oracle['cases']:
    if case['id'] == 'public-remap-trace':
        continue
    for version, span in case['source_spans'].items():
        if span['quote'] is None:
            continue
        path = ROOT / span['path']
        raw = path.read_bytes()
        quote = ''.join(raw.decode().splitlines(keepends=True)[span['first_line'] - 1:span['last_line']])
        assert sha(raw) == span['sha256'] and quote == span['quote']
        assert len(quote.encode()) <= 6144
        key = version + ':' + span['selector']
        units[key] = {'path': span['path'], 'revision': REVS[version], 'source_sha256': sha(raw), 'first_line': span['first_line'], 'last_line': span['last_line'], 'quote': quote, 'quote_sha256': sha(quote.encode()), 'complete_callable': True}
remap = next(row for row in router['rows'] if row['id'] == 'public-remap-trace')['result']['keyword_evidence']
for version, when in [('24.0.0', 'previous'), ('25.0.0', 'current')]:
    path = OLD / 'public-sources' / version / 'boltons/iterutils.py'
    raw = path.read_bytes()
    assert sha(raw) == remap[when]['source_card']['sha256']
    for kind, evidence in remap[when]['evidence'].items():
        quote = ''.join(raw.decode().splitlines(keepends=True)[evidence['first_line'] - 1:evidence['last_line']])
        assert quote == evidence['quote'] and sha(quote.encode()) == evidence['sha256']
        units[version + ':remap:' + kind] = {'path': str(path.relative_to(ROOT)), 'revision': REVS[version], 'source_sha256': sha(raw), 'first_line': evidence['first_line'], 'last_line': evidence['last_line'], 'quote': quote, 'quote_sha256': sha(quote.encode()), 'complete_callable': False, 'complete_statement_prefix': kind == 'complete_statement_prefix', 'owner_callable_ast_sha256': remap[when]['callable_full_ast_sha256']}
license_path = OLD / 'public-sources/25.0.0/LICENSE'
receipts = {}
for filename in ['rotate-confined-macos-v1.json', 'rotate-confined-linux-v1.json', 'find-depth-confined-macos-v1.json', 'find-depth-confined-linux-v1.json']:
    path = P / filename
    data = json.loads(path.read_text())
    assert data['correct'] == data['n']
    receipts[filename] = {'sha256': sha(path.read_bytes()), 'cases': data['n'], 'source_sha256': data['source_sha256'], 'selected_public_function_executed': True, 'whole_public_module_imported': False}
claims = []


def add(identifier, section, en, pt, refs, observations=None):
    assert refs and all(r in units for r in refs)
    assert re.findall(r'`([^`]+)`', en) == re.findall(r'`([^`]+)`', pt), identifier
    claims.append({'id': identifier, 'section': section, 'en': en, 'pt-br': pt, 'source_units': refs, 'runtime_observations': observations or [], 'review_status': 'CODEX_SOURCE_REVIEWED_NOT_OWNER_APPROVED'})


add('scope', 'purpose',
    'This chapter compares selected `fileutils`, `iterutils` and `typeutils` contracts at `24.0.0` and `25.0.0`. It covers the preserved revisions, not the latest Boltons release or the entire package.',
    'Este capítulo compara contratos selecionados de `fileutils`, `iterutils` e `typeutils` em `24.0.0` e `25.0.0`. Ele cobre as revisões preservadas, em vez da versão mais recente do Boltons ou do pacote inteiro.',
    ['25.0.0:rotate_file', '25.0.0:research', '25.0.0:make_sentinel'])
add('interfaces', 'configuration',
    'The current declarations include `rotate_file(filename, *, keep: int = 5)`, `max_depth=None` on `iter_find_files`, and `enter=default_enter` on `research`. Default expressions and annotations are written source; their import-time evaluation is not tested by this chapter.',
    'As declarações atuais incluem `rotate_file(filename, *, keep: int = 5)`, `max_depth=None` em `iter_find_files` e `enter=default_enter` em `research`. Expressões padrão e anotações são código escrito; sua avaliação durante importação não é testada por este capítulo.',
    ['25.0.0:rotate_file', '25.0.0:iter_find_files', '25.0.0:research'])
add('rotation-source', 'responsibilities',
    '`rotate_file` checks `keep < 1`, returns if the source path is absent, and rejects a non-file source. It splits the filename, builds numbered names, renames the chain in reverse order and then removes the final numbered destination when it exists. The selected body contains no rollback branch.',
    '`rotate_file` verifica `keep < 1`, retorna se o caminho de origem estiver ausente e rejeita uma origem que não seja arquivo. Ele separa o nome do arquivo, monta nomes numerados, renomeia a cadeia em ordem inversa e depois remove o último destino numerado se ele existir. O corpo selecionado não contém ramo de rollback.',
    ['25.0.0:rotate_file'])
add('rotation-traces', 'observations',
    'On the frozen owned macOS/Linux fixtures, `keep=1` moved the original to its first numbered destination and then removed it; no rotated copy remained. Prepared existing chains with `keep=2` and `keep=5` retained one and four numbered files, respectively. This does not establish crash atomicity, race safety, Windows overwrite behavior or maintainer intent.',
    'Nas estruturas sintéticas congeladas de macOS/Linux, `keep=1` moveu o original para o primeiro destino numerado e depois o removeu; nenhuma cópia rotacionada permaneceu. Cadeias existentes preparadas com `keep=2` e `keep=5` conservaram um e quatro arquivos numerados, respectivamente. Isso não estabelece atomicidade contra falhas, segurança contra disputas, comportamento de sobrescrita no Windows nem intenção do mantenedor.',
    ['25.0.0:rotate_file'], ['rotate-confined-macos-v1.json', 'rotate-confined-linux-v1.json'])
add('depth-filter', 'observations',
    'The `max_depth` branch skips processing a yielded root when its computed depth is too large; it does not edit the walker directory list. In the fully consumed three-directory fixtures, `max_depth=0` yielded only the root text file while native walking still visited all three directories. This is yield filtering, not an observed traversal-pruning guarantee.',
    'O ramo de `max_depth` pula o processamento de uma raiz fornecida quando sua profundidade calculada é grande demais; ele não altera a lista de diretórios do percurso. Nas estruturas de três diretórios com o gerador totalmente consumido, `max_depth=0` forneceu apenas o arquivo de texto da raiz, enquanto o percurso nativo ainda visitou os três diretórios. Isso é filtragem dos resultados, sem garantia observada de poda do percurso.',
    ['25.0.0:iter_find_files'], ['find-depth-confined-macos-v1.json', 'find-depth-confined-linux-v1.json'])
add('directory-filter', 'observations',
    'With `include_dirs=True` and `max_depth=0`, the fixture also yielded `tree/deep`, a child directory encountered at the root. With `ignored=\'deep\'`, that directory name was not yielded, but its descendants were still visited and eligible files were yielded. Neither setting pruned the observed native directory list.',
    'Com `include_dirs=True` e `max_depth=0`, a estrutura também forneceu `tree/deep`, um diretório filho encontrado na raiz. Com `ignored=\'deep\'`, esse nome de diretório não foi fornecido, mas seus descendentes ainda foram visitados e arquivos elegíveis foram fornecidos. Nenhuma dessas opções podou a lista nativa de diretórios observada.',
    ['25.0.0:iter_find_files'], ['find-depth-confined-macos-v1.json', 'find-depth-confined-linux-v1.json'])
add('research-wire', 'architecture',
    '`research` declares caller-supplied `enter=default_enter`, defines `_enter`, passes it as `remap(root, enter=_enter)`, and writes `return enter(path, key, value)` inside that wrapper. Describing this as always calling a fixed helper loses the caller-supplied parameter. Runtime callback binding and full traversal behavior were not executed here.',
    '`research` declara `enter=default_enter` fornecido pelo chamador, define `_enter`, passa esse wrapper como `remap(root, enter=_enter)` e escreve `return enter(path, key, value)` dentro dele. Descrever isso como uma chamada sempre feita a um auxiliar fixo perde o parâmetro fornecido pelo chamador. A vinculação do callback em execução e o percurso completo não foram executados aqui.',
    ['24.0.0:research', '25.0.0:research'])
add('query-boundary', 'errors',
    'The nested `_enter` wrapper catches `Exception` around the `query` call and result append; when `reraise` is true, it re-raises. Its final `return enter(path, key, value)` lies after that local handler. This source boundary does not establish how every downstream traversal error is handled.',
    'O wrapper interno `_enter` captura `Exception` em torno da chamada a `query` e da adição do resultado; quando `reraise` é verdadeiro, ele relança a exceção. Seu `return enter(path, key, value)` final fica depois desse handler local. Esse limite no código não estabelece como todo erro posterior do percurso é tratado.',
    ['25.0.0:research'])
add('keyword-prefix', 'configuration',
    'The earlier `remap` prefix pops `reraise_visit` before its remaining-keyword guard. The current prefix also pops `trace` with default `()`, normalizes `True` and strings, checks for `tuple`, `list` or `set`, and derives event flags before the remaining-keyword guard. It therefore writes explicit handling for `trace`; recognition does not guarantee that every value is valid or that later traversal succeeds.',
    'O prefixo anterior de `remap` extrai `reraise_visit` antes da verificação de opções restantes. O prefixo atual também extrai `trace` com padrão `()`, normaliza `True` e strings, verifica `tuple`, `list` ou `set` e deriva indicadores de eventos antes da verificação de opções restantes. Portanto, ele escreve tratamento explícito para `trace`; reconhecer a opção não garante que todo valor seja válido nem que o percurso posterior tenha sucesso.',
    ['24.0.0:remap:complete_statement_prefix', '25.0.0:remap:complete_statement_prefix', '25.0.0:remap:header'])
add('trace-false', 'errors',
    'In the selected current prefix, `trace is True` is normalized, but literal `False` has no corresponding normalization branch and does not belong to `tuple`, `list` or `set`. The written type-check branch raises `TypeError` for that value if reached. This is a source-path observation, not an executed full `remap` call.',
    'No prefixo atual selecionado, `trace is True` é normalizado, mas o literal `False` não tem ramo correspondente de normalização nem pertence a `tuple`, `list` ou `set`. O ramo escrito de verificação de tipo lança `TypeError` para esse valor se for alcançado. Esta é uma observação do caminho no código, em vez de uma chamada completa de `remap` executada.',
    ['25.0.0:remap:complete_statement_prefix'])
add('sentinel-methods', 'architecture',
    'The selected `make_sentinel` body writes `return Sentinel()`. Its current local class directly defines `__copy__` and `__deepcopy__`, both with `return self`; the earlier selected local class lacks those two direct definitions. This describes the written local class and constructor expression, not a universal runtime allocation or inheritance guarantee.',
    'O corpo selecionado de `make_sentinel` escreve `return Sentinel()`. Sua classe local atual define diretamente `__copy__` e `__deepcopy__`, ambos com `return self`; a classe local selecionada anterior não possui essas duas definições diretas. Isso descreve a classe local escrita e a expressão de construção, sem garantir universalmente alocação ou herança em execução.',
    ['24.0.0:make_sentinel', '25.0.0:make_sentinel'])
add('written-returns', 'inputs_outputs',
    '`strip_iter` writes `rstrip_iter(lstrip_iter(iterable, strip_value), strip_value)` as its return expression. `rstrip` writes `list(rstrip_iter(iterable, strip_value))`. `default_visit` writes `return key, value`. These selected expressions remain the same across the compared cuts; no general helper equivalence or runtime binding is inferred.',
    '`strip_iter` escreve `rstrip_iter(lstrip_iter(iterable, strip_value), strip_value)` como expressão de retorno. `rstrip` escreve `list(rstrip_iter(iterable, strip_value))`. `default_visit` escreve `return key, value`. Essas expressões selecionadas permanecem iguais entre os recortes comparados; nenhuma equivalência geral de auxiliares nem vinculação em execução é inferida.',
    ['24.0.0:strip_iter', '25.0.0:strip_iter', '24.0.0:rstrip', '25.0.0:rstrip', '24.0.0:default_visit', '25.0.0:default_visit'])
faq = [
    ('one-copy', 'Does keep=1 guarantee one preserved rotated copy in this cut?', 'keep=1 garante uma cópia rotacionada preservada neste recorte?', 'rotation-traces'),
    ('pruning', 'Does max_depth=0 stop the walker from visiting child directories here?', 'max_depth=0 impede o percurso de visitar diretórios filhos aqui?', 'depth-filter'),
    ('ignore-subtree', 'Does an ignored directory name automatically exclude its subtree?', 'Um nome de diretório ignorado exclui automaticamente sua subárvore?', 'directory-filter'),
    ('custom-enter', 'Does research always delegate to a fixed default_enter helper?', 'research sempre delega a um auxiliar default_enter fixo?', 'research-wire'),
    ('trace-values', 'Does keyword recognition make trace=False a validated value?', 'Reconhecer a opção torna trace=False um valor validado?', 'trace-false'),
    ('copy-hooks', 'Which copy hooks are directly written on the current local sentinel class?', 'Quais métodos de cópia estão escritos diretamente na classe sentinela local atual?', 'sentinel-methods'),
    ('query-error-scope', 'Does the query handler directly enclose the final enter call?', 'O handler de query abrange diretamente a chamada final a enter?', 'query-boundary'),
]
lookup = {c['id']: c for c in claims}
example = "from boltons.iterutils import default_visit\nfrom boltons.fileutils import iter_find_files\n\nkey_value = default_visit((), 'item', 7)\npaths = iter_find_files('owned-example', '*.txt', max_depth=0)\n"
compile(example, '<boltons-illustrative-example>', 'exec', dont_inherit=True)
out = P / 'boltons-chapter-candidates-v2'
out.mkdir(exist_ok=False)
headers = [('purpose', 'Purpose and scope', 'Propósito e escopo'), ('architecture', 'Architecture and helper direction', 'Arquitetura e direção dos auxiliares'), ('responsibilities', 'Filesystem responsibilities', 'Responsabilidades no sistema de arquivos'), ('configuration', 'Configuration and declared inputs', 'Configuração e entradas declaradas'), ('inputs_outputs', 'Written return expressions', 'Expressões de retorno escritas'), ('errors', 'Error boundaries', 'Limites de erros'), ('observations', 'Confined native observations', 'Observações nativas confinadas')]
for language in ['en', 'pt-br']:
    en = language == 'en'
    parts = ['# ' + ('Boltons selected utilities: source changes and confined observations' if en else 'Utilitários selecionados do Boltons: mudanças no código e observações confinadas'),
             ('Isolated research chapter; not published, owner-approved or training gold. Source revisions: ' if en else 'Capítulo isolado de pesquisa; sem publicação, aprovação do proprietário ou gold de treinamento. Revisões de código: ') + '`' + REVS['24.0.0'] + '` → `' + REVS['25.0.0'] + '`.']
    for section, english, portuguese in headers:
        parts.append('## ' + (english if en else portuguese))
        for claim in claims:
            if claim['section'] == section:
                parts.append(claim[language] + ' ' + ' '.join('[source:' + key + ']' for key in claim['source_units']) + ' ' + ' '.join('[observation:' + key + ']' for key in claim['runtime_observations']))
    parts += ['## ' + ('Dependency map' if en else 'Mapa de dependências'),
              '| ' + ('Selected owner | Written dependency | Scope |' if en else 'Responsável selecionado | Dependência escrita | Escopo |') + '\n|---|---|---|\n| `rotate_file` | `os.path`, `os.rename`, `os.remove` | [source:25.0.0:rotate_file] |\n| `iter_find_files` | `os.walk`, `fnmatch.translate`, `re.compile` | [source:25.0.0:iter_find_files] |\n| `research` | `query`, caller `enter`, `remap` | [source:25.0.0:research] |\n| `make_sentinel` | local `Sentinel` | [source:25.0.0:make_sentinel] |',
              '## ' + ('Written call relationships' if en else 'Relações de chamadas escritas'),
              '```mermaid\nflowchart LR\n  A["research"] --> B["remap(root, enter=_enter)"]\n  B --> C["_enter"]\n  C --> D["query(path, key, value)"]\n  C --> E["enter(path, key, value)"]\n  F["iter_find_files"] --> G["os.walk"]\n  F --> H["yield filtering by max_depth"]\n```',
              ('The diagram summarizes selected written relationships, not a complete runtime call graph.' if en else 'O diagrama resume relações escritas selecionadas, sem constituir um grafo completo de chamadas em execução.'),
              '## ' + ('Illustrative example and syntax command' if en else 'Exemplo ilustrativo e comando de sintaxe'),
              ('The example is syntax checked only. Imports, the displayed calls and the command below were not executed; no output list is asserted.' if en else 'O exemplo tem apenas a sintaxe verificada. As importações, as chamadas exibidas e o comando abaixo não foram executados; nenhuma lista de saída é afirmada.'),
              '```python\n' + example + '```\n\n```sh\npython -m py_compile boltons-example.py\n```',
              '## ' + ('FAQs' if en else 'Perguntas frequentes')]
    for identifier, english, portuguese, claim_id in faq:
        claim = lookup[claim_id]
        parts.append('### ' + (english if en else portuguese) + '\n\n' + claim[language] + ' ' + ' '.join('[source:' + key + ']' for key in claim['source_units']) + ' ' + ' '.join('[observation:' + key + ']' for key in claim['runtime_observations']))
    parts += ['## ' + ('License and verification limits' if en else 'Licença e limites da verificação'),
              ('The original BSD-style three-clause notice is preserved and linked below; this is not approval for training. Only rotate_file and iter_find_files were executed, each as an exact reviewed function under a restricted facade on owned temporary data. All other claims are source inspection. No whole Boltons module, full remap/research traversal, sentinel factory, copied helper, model-generated command or illustrative example was executed. The macOS/Linux cases are correlated repetitions; Windows, concurrency, crash durability and complete package semantics remain unverified.' if en else 'O aviso original de estilo BSD com três cláusulas está preservado e vinculado abaixo; isso não aprova treinamento. Apenas rotate_file e iter_find_files foram executados, cada um como função exata revisada sob uma fachada restrita em dados temporários sintéticos. Todas as outras afirmações são inspeção de código. Nenhum módulo Boltons inteiro, percurso completo de remap/research, fábrica de sentinelas, auxiliar de cópia, comando gerado por modelo ou exemplo ilustrativo foi executado. Os casos de macOS/Linux são repetições correlacionadas; Windows, concorrência, durabilidade contra falhas e semântica completa do pacote continuam não verificados.'),
              '## ' + ('Physical source and observation references' if en else 'Referências físicas de código e observação')]
    for key, unit in units.items():
        target = ROOT / unit['path']
        relative = os.path.relpath(target, out)
        parts.append('[source:' + key + ']: ' + relative + '#L' + str(unit['first_line']) + ' "' + unit['source_sha256'] + '"')
    for filename, receipt in receipts.items():
        parts.append('[observation:' + filename + ']: ../' + filename + ' "' + receipt['sha256'] + '"')
    parts.append('[source-license]')
    parts.append('[source-license]: ' + os.path.relpath(license_path, out) + ' "' + sha(license_path.read_bytes()) + '"')
    (out / (language + '.md')).write_text('\n\n'.join(parts) + '\n')
(out / 'boltons-example.py').write_text(example)
ledger = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'source_revisions': REVS, 'units': units, 'runtime_receipts': receipts, 'claims': claims,
          'faq': [{'id': identifier, 'en_q': en, 'pt-br_q': pt, 'claim_id': claim, 'en_a': lookup[claim]['en'], 'pt-br_a': lookup[claim]['pt-br'], 'source_units': lookup[claim]['source_units'], 'runtime_observations': lookup[claim]['runtime_observations']} for identifier, en, pt, claim in faq],
          'files': {str(f.relative_to(P)): {'sha256': sha(f.read_bytes()), 'bytes': f.stat().st_size} for f in out.iterdir()},
          'license': {'path': str(license_path.relative_to(ROOT)), 'sha256': sha(license_path.read_bytes()), 'training_use_approved': False},
          'source_family': 'mahmoud/boltons', 'development_exposed': True, 'certified_neural_holdout': False, 'source_review_author': 'Codex',
          'selected_public_functions_executed': ['rotate_file', 'iter_find_files'], 'full_public_module_imported': False,
          'model_calls': 0, 'owner_approved': False, 'training_gold': False, 'training_exclusion': True, 'published': False,
          'limits': ['One historical public family, selected physical source contracts and bounded owned native traces only.', 'FAQ answers overlap chapter claims; no independent new training examples.', 'No automated full-prose entailment or independent human semantic certification.']}
with (P / 'boltons-chapter-ledger-v2.json').open('x') as stream:
    stream.write(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'claims': len(claims), 'faq_pairs': len(faq), 'physical_units': len(units), 'confined_observation_receipts': len(receipts)}))
