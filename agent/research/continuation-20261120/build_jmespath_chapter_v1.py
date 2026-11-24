"""Deterministic bilingual technical candidate from an explicitly reviewed ledger."""
import datetime
import hashlib
import json
import re
from pathlib import Path

P = Path(__file__).resolve().parent
pack_path = P / 'jmespath-source-evidence-pack-v1.json'
pack = json.loads(pack_path.read_text())
claims = []


def add(identifier, section, en, pt, refs, scope='written-source'):
    if not refs or any(ref not in pack['units'] for ref in refs):
        raise ValueError('unregistered evidence')
    if re.findall(r'`([^`]+)`', en) != re.findall(r'`([^`]+)`', pt):
        raise ValueError('bilingual identifiers or their order diverged: ' + identifier)
    claims.append({'id': identifier, 'section': section, 'en': en, 'pt-br': pt,
                   'evidence_ids': refs, 'scope': scope,
                   'review_status': 'AGENT_SOURCE_REVIEWED_CANDIDATE_NOT_OWNER_GOLD',
                   'automated_entailment_proven': False})


add('purpose', 'purpose',
    'This chapter follows the written path from `compile` and `search` into `Parser.parse`; it documents the pinned source revision rather than a measured execution.',
    'Este capítulo acompanha o caminho escrito de `compile` e `search` até `Parser.parse`; documenta a revisão fixada do código, sem representar uma execução medida.',
    ['compile', 'search', 'Parser.parse'])
add('facade', 'architecture',
    '`compile(expression)` returns the expression `parser.Parser().parse(expression)`. `search(expression, data, options=None)` appends `.search(data, options=options)` to that chain.',
    '`compile(expression)` retorna a expressão `parser.Parser().parse(expression)`. `search(expression, data, options=None)` acrescenta `.search(data, options=options)` a essa cadeia.',
    ['compile', 'search'])
add('import-wire', 'dependencies',
    'The facade writes `from jmespath import parser`. The parser writes `from jmespath import visitor`. These imports identify source relationships; the runtime import loader was not checked.',
    'A fachada declara `from jmespath import parser`. O parser declara `from jmespath import visitor`. Essas importações identificam relações no código; o carregador de importações em execução não foi verificado.',
    ['jmespath/__init__.py:import:1', 'jmespath/parser.py:import:32'])
add('cache-owner', 'responsibilities',
    '`Parser.parse` first attempts `self._CACHE[expression]`. After a `KeyError`, it calls `self._do_parse(expression)` and contains the capacity check before its final cache assignment.',
    '`Parser.parse` primeiro tenta `self._CACHE[expression]`. Após um `KeyError`, chama `self._do_parse(expression)` e contém a verificação de capacidade antes da atribuição final ao cache.',
    ['Parser.parse'])
add('configuration', 'configuration',
    '`Parser._MAX_SIZE` is written as the integer 512. This is a class-level source value, not proof of a live cache occupancy limit under every execution.',
    '`Parser._MAX_SIZE` está escrito como o inteiro 512. Esse é um valor no código da classe, sem constituir prova de um limite de ocupação do cache em toda execução.',
    ['Parser._MAX_SIZE', 'Parser.parse'])
add('input-wire', 'inputs_outputs',
    '`search` forwards `data` and `options` to the written chained call. `ParsedResult.search` constructs `visitor.TreeInterpreter(options)`, calls `interpreter.visit(self.parsed, value)` and returns the local `result`. The returned runtime type is not established by these statements alone.',
    '`search` encaminha `data` e `options` para a chamada encadeada escrita. `ParsedResult.search` constrói `visitor.TreeInterpreter(options)`, chama `interpreter.visit(self.parsed, value)` e retorna a variável local `result`. Essas instruções, isoladamente, não estabelecem o tipo retornado em execução.',
    ['search', 'ParsedResult.search'])
add('parse-errors', 'error_handling',
    '`Parser._do_parse` catches `exceptions.LexerError` and `exceptions.ParseError`, assigns `e.expression = expression` and re-raises. For `exceptions.IncompleteExpressionError`, it calls `e.set_expression(expression)` and re-raises. The exception class implementations are outside this evidence pack.',
    '`Parser._do_parse` captura `exceptions.LexerError` e `exceptions.ParseError`, atribui `e.expression = expression` e relança a exceção. Para `exceptions.IncompleteExpressionError`, chama `e.set_expression(expression)` e relança a exceção. As implementações dessas classes de exceção estão fora deste conjunto de evidências.',
    ['Parser._do_parse', 'jmespath/parser.py:import:31'])
add('eviction-errors', 'error_handling',
    'The eviction block in `Parser.parse` catches `KeyError`, `StopIteration` and `RuntimeError`, then returns `parsed_result` before the final `self._CACHE[expression] = parsed_result` statement. This is written control flow, not a concurrency guarantee.',
    'O bloco de remoção em `Parser.parse` captura `KeyError`, `StopIteration` e `RuntimeError`, e então retorna `parsed_result` antes da instrução final `self._CACHE[expression] = parsed_result`. Isso descreve o fluxo escrito, sem garantir comportamento concorrente.',
    ['Parser.parse'])
add('limits', 'limitations',
    'The source pack does not establish LRU behavior, thread safety, timeout units, retries, authentication or external API responses. Runtime helper resolution, package installation and example execution were not verified.',
    'O conjunto de código não estabelece comportamento LRU, segurança entre threads, unidades de timeout, retentativas, autenticação ou respostas de APIs externas. A resolução de auxiliares em execução, a instalação do pacote e a execução do exemplo não foram verificadas.',
    ['Parser.parse', 'search', 'ParsedResult.search'], 'explicit-evidence-limit')
faq = [
    {'id': 'facade-vs-cache', 'en_q': 'Do unchanged facade signatures mean the cache chapter stays unchanged?',
     'pt-br_q': 'Assinaturas iguais na fachada significam que o capítulo do cache permanece igual?',
     'claim': 'configuration'},
    {'id': 'result-type', 'en_q': 'Does this source path prove one fixed return type?',
     'pt-br_q': 'Esse caminho no código prova um único tipo de retorno?', 'claim': 'input-wire'},
    {'id': 'translated-keys', 'en_q': 'Should source identifiers change in the Portuguese chapter?',
     'pt-br_q': 'Os identificadores do código devem mudar no capítulo em português?', 'claim': 'facade'},
    {'id': 'exception-owner', 'en_q': 'Which local method enriches parser errors here?',
     'pt-br_q': 'Qual método local acrescenta contexto aos erros do parser neste trecho?', 'claim': 'parse-errors'},
    {'id': 'concurrency', 'en_q': 'Does catching eviction errors prove thread safety?',
     'pt-br_q': 'Capturar erros na remoção prova segurança entre threads?', 'claim': 'eviction-errors'},
    {'id': 'unverified', 'en_q': 'Which operational guarantees remain unknown?',
     'pt-br_q': 'Quais garantias operacionais permanecem desconhecidas?', 'claim': 'limits'},
]
# FAQ answers reuse reviewed claim text; no independent-example inflation.
lookup = {c['id']: c for c in claims}
for item in faq:
    item['en_a'] = lookup[item['claim']]['en']
    item['pt-br_a'] = lookup[item['claim']]['pt-br']
    item['evidence_ids'] = lookup[item['claim']]['evidence_ids']
headers = {
    'purpose': ('Purpose', 'Propósito'), 'architecture': ('Architecture', 'Arquitetura'),
    'responsibilities': ('Responsibilities', 'Responsabilidades'), 'dependencies': ('Dependencies', 'Dependências'),
    'configuration': ('Configuration', 'Configuração'), 'inputs_outputs': ('Inputs and outputs', 'Entradas e saídas'),
    'error_handling': ('Error handling', 'Tratamento de erros'), 'examples': ('Example', 'Exemplo'),
    'commands': ('Command', 'Comando'), 'source_table': ('Source map', 'Mapa do código'),
    'diagram': ('Written call relationships', 'Relações de chamadas escritas'),
    'faq': ('FAQ', 'Perguntas frequentes'), 'limitations': ('Limitations', 'Limitações'),
    'citations': ('Physical source citations', 'Citações físicas do código')}
example = 'jmespath.search("name", {"name": "Ada"})'
command = '''python -c 'import jmespath; print(jmespath.search("name", {"name": "Ada"}))' '''.rstrip()
diagram = '''flowchart LR
    A["compile(expression)"] --> B["Parser.parse(expression)"]
    C["search(expression, data, options=None)"] --> B
    C --> D[".search(data, options=options)"]
    E["ParsedResult.search(value, options=None)"] --> F["visitor.TreeInterpreter(options)"]
    E --> G["interpreter.visit(self.parsed, value)"]'''
output = P / 'chapter-candidates-v1'
output.mkdir(exist_ok=False)
files = {}
for lang, index in [('en', 0), ('pt-br', 1)]:
    title = 'Pinned parser and cache source walkthrough' if lang == 'en' else 'Leitura do código fixado do parser e do cache'
    paragraphs = ['# ' + title, '',
        ('Research candidate. Not published, owner-approved or training gold.' if lang == 'en' else 'Candidato de pesquisa. Não publicado, aprovado pelo proprietário ou classificado como gold de treinamento.'), '',
        'Revision: `' + pack['revision'] + '`.', '']
    for section, pair in headers.items():
        paragraphs += ['## ' + pair[index], '']
        for claim in claims:
            if claim['section'] == section:
                paragraphs += [claim[lang] + ' ' + ' '.join('[source:' + ref + ']' for ref in claim['evidence_ids']), '']
        if section in ('examples', 'commands'):
            paragraphs += [('Illustrative and unexecuted. No output or successful installation is claimed.' if lang == 'en' else 'Ilustrativo e não executado. Nenhuma saída ou instalação bem-sucedida é afirmada.'), '',
                '```' + ('python' if section == 'examples' else 'sh'), example if section == 'examples' else command, '```', '', '[source:search]', '']
        if section == 'source_table':
            paragraphs += ['| Unit | File |', '|---|---|']
            paragraphs += ['| `' + ref + '` | `' + pack['units'][ref]['source_path'] + '` |' for ref in ['compile', 'search', 'Parser.parse', 'Parser._MAX_SIZE', 'Parser._do_parse', 'ParsedResult.search']]
            paragraphs += ['']
        if section == 'diagram':
            paragraphs += [('Edges show written call expressions; they do not certify runtime target identity or a complete execution trace.' if lang == 'en' else 'As setas mostram expressões de chamada escritas; não certificam a identidade dos destinos em execução nem um rastreamento completo.'), '', '```mermaid', diagram, '```', '', '[source:compile] [source:search] [source:ParsedResult.search]', '']
        if section == 'faq':
            for item in faq:
                paragraphs += ['### ' + item[lang + '_q'], '', item[lang + '_a'] + ' ' + ' '.join('[source:' + ref + ']' for ref in item['evidence_ids']), '']
        if section == 'citations':
            for key, unit in pack['units'].items():
                e = unit['evidence']
                paragraphs += ['- [source:' + key + '] [' + unit['source_path'] + ':' + str(e['first_line']) + '–' + str(e['last_line']) + '](' + unit['url'] + '); SHA-256 `' + unit['source_sha256'] + '`.', '']
    text = '\n'.join(paragraphs).rstrip() + '\n'
    dest = output / (lang + '.md')
    dest.write_text(text)
    files[str(dest.relative_to(P))] = {'sha256': hashlib.sha256(text.encode()).hexdigest(), 'bytes': len(text.encode())}
ledger = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'claims': claims, 'faq': faq,
          'source_pack_sha256': hashlib.sha256(pack_path.read_bytes()).hexdigest(), 'files': files,
          'scope': 'DETERMINISTIC_SOURCE_REVIEWED_TECHNICAL_CANDIDATE_NOT_NEURAL_IMPROVEMENT',
          'owner_approved': False, 'training_gold': False, 'training_exclusion': True,
          'published_catalog_written': False, 'new_model_calls': 0,
          'faq_overlap': 'All six FAQ answers reuse chapter claims; not six independent training examples.'}
with (P / 'jmespath-chapter-ledger-v1.json').open('x') as stream:
    json.dump(ledger, stream, indent=2, ensure_ascii=False)
print(json.dumps({'claims': len(claims), 'faq_pairs': len(faq), 'files': files}))
