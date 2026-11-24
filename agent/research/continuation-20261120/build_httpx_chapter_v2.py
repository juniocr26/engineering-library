"""Source-reviewed bilingual adapter chapter, no HTTPX import or network execution."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import tomllib

P=Path(__file__).resolve().parent
mapping=json.loads((P/'httpx-mapping-results-v2.json').read_text())
boundaries=json.loads((P/'httpx-source-boundary-pack-v1.json').read_text())
freeze=json.loads((P/'httpx-source-family-freeze-v1.json').read_text())
current=next(row for row in mapping['rows']if row['tag']=='0.28.1')
previous=next(row for row in mapping['rows']if row['tag']=='0.25.2')
current_boundaries=next(row for row in boundaries['rows']if row['tag']=='0.28.1')
assert mapping['all_checks_match']and boundaries['all_checks_pass']
units={};identities={};aliases={}


def unit(key,value):
    identity=tuple(value[k]for k in ['path','revision','source_sha256','first_line','last_line','quote_sha256'])
    if identity in identities:
        aliases[key]=identities[identity]
        return identities[identity]
    identities[identity]=key;units[key]=value
    return key


for key,value in current['result']['evidence'].items():unit('current:'+key,value)
for key,value in current_boundaries['evidence'].items():unit('current:'+key,value)
for key in ['context','mapping_provider']:unit('previous:'+key,previous['result']['evidence'][key])
base=P/'new-public-sources-v1/encode--httpx'/current['revision']
source_path='httpx/_transports/default.py';source=(base/source_path).read_text();tree=ast.parse(source)
card={'path':source_path,'source':source,'sha256':hashlib.sha256(source.encode()).hexdigest(),'revision':current['revision']}
# Exact source-unit arithmetic shared with the already verified mapping evidence builder.
import importlib.util
spec=importlib.util.spec_from_file_location('chapter_physical_units',P/'transport_mapping_observer_v2.py');source_units=importlib.util.module_from_spec(spec);spec.loader.exec_module(source_units)
import_node=next(node for node in tree.body if isinstance(node,ast.ImportFrom)and node.module=='_exceptions'and node.level==2)
unit('current:exception-import-wire',source_units.source_unit(card,import_node,'complete-relative-exception-import-statement'))
constructor_facts={}
for owner in ['HTTPTransport','AsyncHTTPTransport']:
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name==owner)
    constructor=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='__init__')
    unit('current:'+owner+'.__init__',source_units.source_unit(card,constructor,'complete-selected-constructor'))
    calls=[n for n in ast.walk(constructor)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and ast.unparse(n.func).startswith('httpcore.')]
    constructor_facts[owner]={'signature':source_units.shared.signature(constructor),'constructor_keyword_sets':{ast.unparse(call.func):[keyword.arg for keyword in call.keywords]for call in calls if ast.unparse(call.func)!='httpcore.URL'}}
    selector='__exit__'if owner=='HTTPTransport'else'__aexit__'
    method=next(n for n in cls.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))and n.name==selector)
    unit('current:'+owner+'.'+selector,source_units.source_unit(card,method,'complete-selected-context-exit-method'))
    assert len(method.body)==1 and isinstance(method.body[0],ast.With)and ast.unparse(method.body[0].items[0].context_expr)=='map_httpcore_exceptions()'
metadata={}
for cut in freeze['revisions']:
    path=P/'new-public-sources-v1/encode--httpx'/cut['revision']/'pyproject.toml';raw=path.read_bytes();parsed=tomllib.loads(raw.decode());metadata[cut['tag']]={'requires_python':parsed['project']['requires-python'],'dependencies':parsed['project']['dependencies']}
    assert metadata[cut['tag']]['requires_python']=='>=3.8'and'httpcore==1.*'in metadata[cut['tag']]['dependencies']
    unit(cut['tag']+':pyproject',{'path':'pyproject.toml','revision':cut['revision'],'source_sha256':hashlib.sha256(raw).hexdigest(),'first_line':1,'last_line':len(raw.decode().splitlines()),'quote':raw.decode(),'quote_sha256':hashlib.sha256(raw).hexdigest(),'kind':'complete-project-metadata','source_executed':False})
license_path=base/'LICENSE.md';license_raw=license_path.read_bytes()
unit('current:license',{'path':'LICENSE.md','revision':current['revision'],'source_sha256':hashlib.sha256(license_raw).hexdigest(),'first_line':1,'last_line':len(license_raw.decode().splitlines()),'quote':license_raw.decode(),'quote_sha256':hashlib.sha256(license_raw).hexdigest(),'kind':'complete-primary-license-notice','source_executed':False})
claims=[]


def add(identity,section,en,pt,refs):
    refs=[aliases.get(ref,ref)for ref in refs]
    assert refs and all(ref in units for ref in refs),identity
    assert re.findall(r'`([^`]+)`',en)==re.findall(r'`([^`]+)`',pt),identity
    claims.append({'id':identity,'section':section,'en':en,'pt-br':pt,'evidence':list(dict.fromkeys(refs)),'review':'CODEX_SOURCE_REVIEWED_NOT_OWNER_APPROVED'})


add('purpose','purpose',
    'The selected `HTTPTransport` and `AsyncHTTPTransport` bodies adapt a request into `httpcore.Request`, call their pool, then write a `Response` construction. `ResponseStream` and `AsyncResponseStream` wrap the returned stream expressions. This chapter covers the pinned private implementation cuts, not the complete HTTPX API or a tested endpoint.',
    'Os corpos selecionados de `HTTPTransport` e `AsyncHTTPTransport` adaptam uma requisição para `httpcore.Request`, chamam seu pool e depois escrevem a construção de `Response`. `ResponseStream` e `AsyncResponseStream` envolvem as expressões dos streams retornados. Este capítulo cobre os recortes privados de implementação fixados, em vez da API HTTPX completa ou de um endpoint testado.',
    ['current:HTTPTransport.handle_request','current:AsyncHTTPTransport.handle_async_request','current:ResponseStream.__iter__','current:AsyncResponseStream.__aiter__'])
add('initialization','architecture',
    'At the earlier cut, `HTTPCORE_EXC_MAP` is a module-level literal dictionary. At the later cut it starts as `{}`; `map_httpcore_exceptions` declares it global and calls `_load_httpcore_exceptions()` when its length is zero, before the selected `try`/`yield`. The loader imports `httpcore` locally and returns the literal mapping. This is source structure, not a startup-time, dependency-availability or thread-safety measurement.',
    'No recorte anterior, `HTTPCORE_EXC_MAP` é um dicionário literal no nível do módulo. No recorte posterior ele começa como `{}`; `map_httpcore_exceptions` declara esse nome global e chama `_load_httpcore_exceptions()` quando seu tamanho é zero, antes do `try`/`yield` selecionado. O carregador importa `httpcore` localmente e retorna o mapa literal. Isso é estrutura de código, sem medir tempo de inicialização, disponibilidade da dependência ou segurança entre threads.',
    ['previous:mapping_provider','previous:context','current:mapping_provider','current:context'])
add('stable-pairs','architecture',
    'The fourteen ordered source/target reference pairs are unchanged across the two cuts. Each current target resolves through a written relative import to a class declaration in `_exceptions.py`, and its selected declared ancestry includes `RequestError`. The external classes were not imported; their runtime identities and matching behavior remain unverified. An unchanged mapping table does not certify old physical citations after its provider moves.',
    'Os quatorze pares ordenados de referências de origem/destino permanecem iguais entre os dois recortes. Cada destino atual se vincula, por uma importação relativa escrita, a uma declaração de classe em `_exceptions.py`, e sua ancestralidade declarada selecionada inclui `RequestError`. As classes externas não foram importadas; suas identidades e seu comportamento de correspondência em execução continuam não verificados. Um mapa inalterado não certifica citações físicas antigas depois que seu provedor muda de lugar.',
    ['previous:mapping_provider','current:mapping_provider','current:exception-import-wire','current:exception:TransportError','current:exception:RequestError','current:exception:HTTPError'])
add('handler','errors',
    'The selected mapper catches `Exception`, tests `isinstance(exc, from_exc)`, and updates its accumulator when empty or when `issubclass(to_exc, mapped_exc)` holds. If no target was selected it uses a bare `raise`; otherwise it writes `message = str(exc)` followed by `raise mapped_exc(message) from exc`. This does not prove that every exception type is mapped, that every target relation is comparable or that every error is swallowed.',
    'O mapeador selecionado captura `Exception`, testa `isinstance(exc, from_exc)` e atualiza seu acumulador quando ele está vazio ou quando `issubclass(to_exc, mapped_exc)` é verdadeiro. Se nenhum destino foi selecionado, usa `raise` sem argumento; caso contrário, escreve `message = str(exc)` seguido de `raise mapped_exc(message) from exc`. Isso não prova que todo tipo de exceção é mapeado, que toda relação entre destinos é comparável nem que todo erro é suprimido.',
    ['current:context'])
add('request-boundary','responsibilities',
    'In both selected request methods, `httpcore.Request(...)` is constructed before `with map_httpcore_exceptions()`. The protected statement is the pool call, synchronous or awaited. The response-stream assertion and `Response(...)` return construction come after that local block. Claiming that this one block encloses every request/response setup failure would exceed its written scope.',
    'Nos dois métodos de requisição selecionados, `httpcore.Request(...)` é construído antes de `with map_httpcore_exceptions()`. A instrução protegida é a chamada ao pool, síncrona ou aguardada. A asserção do stream de resposta e a construção de retorno `Response(...)` ficam depois desse bloco local. Afirmar que esse único bloco abrange toda falha de preparação de requisição/resposta excederia seu escopo escrito.',
    ['current:HTTPTransport.handle_request','current:AsyncHTTPTransport.handle_async_request'])
add('data-forwarding','inputs_outputs',
    'The request construction forwards written expressions for `method`, `url`, `headers`, `content` and `extensions`. The response construction forwards `resp.status`, `resp.headers` and `resp.extensions`, and supplies the selected stream wrapper. The source body contains assertions about stream interfaces; it does not by itself certify all runtime bindings, body buffering, copying behavior or higher-level status handling.',
    'A construção da requisição encaminha expressões escritas para `method`, `url`, `headers`, `content` e `extensions`. A construção da resposta encaminha `resp.status`, `resp.headers` e `resp.extensions`, além de fornecer o wrapper de stream selecionado. O corpo do código contém asserções sobre interfaces de stream; ele não certifica por si só todas as vinculações em execução, armazenamento do corpo em memória, comportamento de cópia nem tratamento de status em camadas superiores.',
    ['current:HTTPTransport.handle_request','current:AsyncHTTPTransport.handle_async_request'])
add('iteration-and-close','responsibilities',
    'The selected `ResponseStream.__iter__` and `AsyncResponseStream.__aiter__` loop inside an explicit mapper context. Their `close`/`aclose` bodies and the transport `close`/`aclose` bodies contain no explicit mapper context. Separately, `HTTPTransport.__exit__` and `AsyncHTTPTransport.__aexit__` do wrap their pool-exit call in that context. These local differences do not prove that a downstream close implementation can never translate errors.',
    'Os métodos selecionados `ResponseStream.__iter__` e `AsyncResponseStream.__aiter__` executam seus laços dentro de um contexto explícito do mapeador. Seus corpos `close`/`aclose` e os corpos `close`/`aclose` dos transportes não contêm contexto explícito do mapeador. Separadamente, `HTTPTransport.__exit__` e `AsyncHTTPTransport.__aexit__` envolvem a chamada de saída do pool nesse contexto. Essas diferenças locais não provam que uma implementação posterior de fechamento nunca possa traduzir erros.',
    ['current:ResponseStream.__iter__','current:AsyncResponseStream.__aiter__','current:ResponseStream.close','current:AsyncResponseStream.aclose','current:HTTPTransport.close','current:AsyncHTTPTransport.aclose','current:HTTPTransport.__exit__','current:AsyncHTTPTransport.__aexit__'])
add('request-context','errors',
    '`request_context` selects `RequestError`, assigns `exc.request = request` only under `request is not None`, then writes `raise exc`. `HTTPStatusError` is declared with base `HTTPError`, while `RequestError` is separately declared with base `HTTPError`. The selected handler therefore does not justify a promise about every declared `HTTPError` subtype; no runtime exception hierarchy was instantiated here.',
    '`request_context` seleciona `RequestError`, atribui `exc.request = request` apenas sob `request is not None` e depois escreve `raise exc`. `HTTPStatusError` é declarado com base `HTTPError`, enquanto `RequestError` é declarado separadamente com base `HTTPError`. Portanto, o handler selecionado não justifica uma promessa sobre todo subtipo declarado de `HTTPError`; nenhuma hierarquia de exceções em execução foi instanciada aqui.',
    ['current:request_context','current:HTTPStatusError','current:exception:RequestError'])
add('request-attachment-limit','errors',
    'The mapper constructs its selected exception with a message alone. `RequestError.__init__` declares an optional `request` defaulting to `None`, and the selected `HTTPError` property getter has a `RuntimeError` branch when its stored request is absent. These two files do not establish whether a higher client layer later attaches request context; the mapping call alone is not that guarantee.',
    'O mapeador constrói a exceção selecionada apenas com uma mensagem. `RequestError.__init__` declara `request` opcional com padrão `None`, e o getter de propriedade selecionado em `HTTPError` possui um ramo de `RuntimeError` quando a requisição armazenada está ausente. Esses dois arquivos não estabelecem se uma camada superior do cliente depois acrescenta contexto da requisição; a chamada de mapeamento sozinha não fornece essa garantia.',
    ['current:context','current:RequestError.__init__','current:exception:HTTPError'])
add('retry-configuration','configuration',
    'Both selected transport constructors declare `retries=0`. Their `ConnectionPool`/`AsyncConnectionPool` call forwards that keyword, while the selected HTTP/SOCKS proxy constructor calls omit it. This is a keyword-forwarding observation, not a verified retry count, failure policy, timeout unit, TLS guarantee or proxy authentication result. The imported SSL/configuration helpers and external pool implementation are outside this evidence closure.',
    'Ambos os construtores de transporte selecionados declaram `retries=0`. A chamada de `ConnectionPool`/`AsyncConnectionPool` encaminha essa opção, enquanto as chamadas selecionadas dos construtores de proxy HTTP/SOCKS a omitem. Isso é uma observação de encaminhamento de opção, sem verificar contagem de tentativas, política de falhas, unidade de timeout, garantia TLS ou resultado de autenticação de proxy. Os auxiliares importados de SSL/configuração e a implementação externa do pool ficam fora deste fechamento de evidências.',
    ['current:HTTPTransport.__init__','current:AsyncHTTPTransport.__init__'])
add('dependency-cut','configuration',
    'Both project manifests declare `requires-python = ">=3.8"` and dependency `httpcore==1.*`. The wildcard constraint is not an exact installed httpcore revision. No package installation, wheel compatibility matrix or supported-version execution was performed, and the later source tag is not presented as the latest release.',
    'Ambos os manifestos do projeto declaram `requires-python = ">=3.8"` e a dependência `httpcore==1.*`. A restrição com curinga não é uma revisão instalada exata do httpcore. Não houve instalação de pacote, matriz de compatibilidade de wheels nem execução de versões suportadas, e a tag de código posterior não é apresentada como a versão mais recente.',
    ['0.25.2:pyproject','0.28.1:pyproject'])
add('rights-and-scope','limitations',
    'The original three-clause redistribution notice is preserved. License presence is not owner approval for training. Prior local HTTPX-name references and post-inspection profile development are declared; these source cuts and chapter/FAQ candidates are excluded from training. Source hashes and declared class relationships do not establish complete application behavior.',
    'O aviso original de redistribuição com três cláusulas está preservado. A presença da licença não é aprovação do proprietário para treinamento. As referências locais anteriores ao nome HTTPX e o desenvolvimento do perfil depois da inspeção estão declarados; esses recortes de código e os candidatos de capítulo/perguntas frequentes estão excluídos do treinamento. Hashes de código e relações declaradas entre classes não estabelecem o comportamento completo da aplicação.',
    ['current:license','current:context'])
faq=[
    ('stable-map','Do the same mapping pairs make the whole chapter a NO-OP?','Os mesmos pares de mapeamento tornam o capítulo inteiro um NO-OP?','initialization'),
    ('all-errors','Does the mapper swallow or convert every exception?','O mapeador suprime ou converte toda exceção?','handler'),
    ('pool-boundary','Are request construction and response construction inside the pool-call mapper block?','A construção da requisição e a da resposta ficam dentro do bloco de mapeamento da chamada ao pool?','request-boundary'),
    ('close-context','Do all close and context-exit paths show the same local mapping scope?','Todos os caminhos de fechamento e saída de contexto mostram o mesmo escopo local de mapeamento?','iteration-and-close'),
    ('all-http-errors','Does request_context cover every HTTPError subtype?','request_context cobre todo subtipo de HTTPError?','request-context'),
    ('attached-request','Does mapping alone prove an attached request object?','Somente o mapeamento prova a presença de um objeto de requisição associado?','request-attachment-limit'),
    ('retry-policy','Does the retries parameter establish retries for every proxy or failure mode?','O parâmetro retries estabelece tentativas para todo proxy ou modo de falha?','retry-configuration'),
]
lookup={claim['id']:claim for claim in claims}
example="from httpx._transports.default import map_httpcore_exceptions\n\ndef pool_call_shape(pool, req):\n    with map_httpcore_exceptions():\n        resp = pool.handle_request(req)\n    return resp\n"
compile(example,'<illustrative-private-call-shape>','exec',dont_inherit=True)
output=P/'httpx-chapter-candidates-v2';output.mkdir(exist_ok=False)
headers=[('purpose','Purpose and evidence cut','Propósito e recorte de evidência'),('architecture','Architecture and map initialization','Arquitetura e inicialização do mapa'),('responsibilities','Responsibilities and local call boundaries','Responsabilidades e limites locais das chamadas'),('inputs_outputs','Written inputs and outputs','Entradas e saídas escritas'),('configuration','Declared configuration and dependencies','Configuração declarada e dependências'),('errors','Error translation and request context','Tradução de erros e contexto da requisição')]
for language in ['en','pt-br']:
    en=language=='en'
    paragraphs=['# '+('HTTPX default transport: exception-map ownership and boundaries'if en else'Transporte padrão do HTTPX: propriedade do mapa de exceções e limites'),('Source-reviewed isolated candidate; not published, owner-approved or training gold.'if en else'Candidato isolado revisado a partir do código; sem publicação, aprovação do proprietário ou gold de treinamento.'),('Source cuts: `'if en else'Recortes de código: `')+previous['revision']+'` → `'+current['revision']+'`.']
    for section,english,portuguese in headers:
        paragraphs.append('## '+(english if en else portuguese))
        for claim in claims:
            if claim['section']==section:paragraphs.append(claim[language]+' '+' '.join('[source:'+ref+']'for ref in claim['evidence']))
    paragraphs.append('## '+('Written mapping table'if en else'Tabela de mapeamento escrita'))
    table_rows=[]
    for row in current['result']['mapping_pairs']:
        declared=' → '.join('`'+name+'`'for name in row['target_declared_ancestry'])
        references=' '.join('[source:current:exception:'+name+']'for name in row['target_declared_ancestry']if 'current:exception:'+name in units)
        table_rows.append('| `'+row['source_expression']+'` | `'+row['target_declared_class']+'` | '+declared+' '+references+' |')
    paragraphs.append('| '+('Source expression | Target class name | Declared source path |'if en else'Expressão de origem | Nome da classe de destino | Caminho declarado no código |')+'\n|---|---|---|\n'+'\n'.join(table_rows))
    paragraphs.append('[source:current:mapping_provider] [source:previous:mapping_provider]')
    paragraphs.extend(['## '+('Selected written call relationships'if en else'Relações de chamadas escritas selecionadas'),'```mermaid\nflowchart LR\n  A["HTTPTransport.handle_request"] --> B["httpcore.Request before local context"]\n  A --> C["with map_httpcore_exceptions()"]\n  C --> D["self._pool.handle_request(req)"]\n  A --> E["Response after local context"]\n  M["map_httpcore_exceptions"] --> L["_load_httpcore_exceptions if cache empty"]\n  M --> R["raise mapped_exc(message) from exc"]\n  Q["request_context"] --> T["RequestError selected handler"]\n```',('Edges summarize source statements, not verified runtime receivers or a complete network execution trace.'if en else'As setas resumem instruções do código, sem verificar receptores em execução nem constituir um rastreamento completo de rede.'),'## '+('Illustrative call shape and syntax command'if en else'Forma ilustrativa de chamada e comando de sintaxe'),('This uses a pinned private helper and supplied placeholder pool/request bindings. It is syntax checked only, not a runnable public SDK recipe or an executed request. Imports and the displayed command were not run.'if en else'Este exemplo usa um auxiliar privado fixado e vinculações exemplificativas de pool/requisição fornecidas pelo chamador. Apenas a sintaxe foi verificada; não é uma receita executável da API pública nem uma requisição executada. As importações e o comando exibido não foram executados.'),'```python\n'+example+'```\n\n```sh\npython -m py_compile httpx-boundary-example.py\n```','## '+('FAQs'if en else'Perguntas frequentes')])
    for identity,english,portuguese,claim_id in faq:
        claim=lookup[claim_id];paragraphs.append('### '+(english if en else portuguese)+'\n\n'+claim[language]+' '+' '.join('[source:'+ref+']'for ref in claim['evidence']))
    paragraphs.append('## '+('Limits and rights'if en else'Limites e direitos'))
    paragraphs.append(lookup['rights-and-scope'][language]+' [source:current:license]')
    paragraphs.append(('No HTTPX/httpcore source was imported or executed. No application HTTP request, runtime exception instantiation, TLS/authentication check, actual retry observation or performance measurement occurred. The two source cuts are correlated development material, not certified neural holdout data.'if en else'Nenhum código HTTPX/httpcore foi importado nem executado. Não houve requisição HTTP de aplicação, instanciação de exceção em execução, verificação TLS/autenticação, observação real de tentativas nem medição de desempenho. Os dois recortes são material correlacionado de desenvolvimento, sem constituir dados de avaliação neural com independência certificada.'))
    paragraphs.append('## '+('Physical source references'if en else'Referências físicas de código'))
    for key,value in units.items():
        actual=P/'new-public-sources-v1/encode--httpx'/value['revision']/value['path'];link=os.path.relpath(actual,output)
        paragraphs.append('[source:'+key+']: '+link+'#L'+str(value['first_line'])+' "'+value['source_sha256']+'"')
    (output/(language+'.md')).write_text('\n\n'.join(paragraphs)+'\n')
(output/'httpx-boundary-example.py').write_text(example)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_revisions':{'previous':previous['revision'],'current':current['revision']},'claims':claims,'faq':[{'id':identity,'en_q':en,'pt-br_q':pt,'claim_id':claim_id,'en_a':lookup[claim_id]['en'],'pt-br_a':lookup[claim_id]['pt-br'],'evidence':lookup[claim_id]['evidence']}for identity,en,pt,claim_id in faq],'units':units,'deduplicated_unit_aliases':aliases,'constructor_source_facts':constructor_facts,'project_metadata':metadata,'files':{str(path.relative_to(P)):{'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}for path in output.iterdir()},'source_family':'encode/httpx','development_exposed':True,'certified_neural_holdout':False,'source_executed':False,'application_http_requests':0,'model_calls':0,'owner_approved':False,'training_gold':False,'training_exclusion':True,'published':False,'review_change_log':['V2adds an explicit relative-import citation and per-row declared ancestry source links;corrects Portuguese source-cut heading and avoids describing identity as executed. V1remains preserved.'],'scope':'Selected pinned private source contracts and local declared ancestry, not general semantic/runtime/package/API certification.'}
with(P/'httpx-chapter-ledger-v2.json').open('x')as stream:stream.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print({'claims':len(claims),'faq_pairs':len(faq),'unique_physical_units':len(units),'deduplicated_aliases':len(aliases),'source_execution':False})
