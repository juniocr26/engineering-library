"""Extend the retained static chapter with explicit confined runtime evidence."""
import ast,datetime,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
ledger=json.loads((P/'httpx-chapter-ledger-v2.json').read_text())
mac=json.loads((P/'httpx-exception-composition-macos-v1.json').read_text())
linux=json.loads((P/'httpx-exception-composition-linux-v1.json').read_text())
edge=json.loads((P/'httpx-exception-edge-results-v1.json').read_text())
assert mac['all_pass']and linux['observation']['all_pass']and edge['all_pass']
revision='98209758cc14e1a5f966fe1dfdc1064b94055d8c'
base=P/'new-public-sources-v1/encode--httpcore'/revision
for key,path in [('core:classes','httpcore/_exceptions.py'),('core:reexports','httpcore/__init__.py')]:
 raw=(base/path).read_bytes();text=raw.decode();lines=text.splitlines(keepends=True)
 if key=='core:reexports':
  node=next(n for n in ast.parse(text).body if isinstance(n,ast.ImportFrom)and n.module=='_exceptions');first=node.lineno;last=node.end_lineno;quote=''.join(lines[first-1:last])
 else:first=1;last=len(lines);quote=text
 ledger['units'][key]={'repository':'encode/httpcore','path':path,'revision':revision,'source_sha256':hashlib.sha256(raw).hexdigest(),'first_line':first,'last_line':last,'quote':quote,'quote_sha256':hashlib.sha256(quote.encode()).hexdigest(),'kind':'complete-frozen-exception-file'if first==1 else'complete-exception-reexport-statement'}
replacements={
'The external classes were not imported; their runtime identities and matching behavior remain unverified.':'The initial phase did not import or execute the external classes. The later confined phase below instantiates selected source definitions in owned namespaces; it does not verify installed package bindings.',
'As classes externas não foram importadas; suas identidades e seu comportamento de correspondência em execução continuam sem verificação.':'A fase inicial não importou nem executou as classes externas. A fase isolada posterior abaixo instancia definições selecionadas do código em namespaces próprios; ela não verifica as vinculações dos pacotes instalados.',
'no runtime exception hierarchy was instantiated here.':'the initial phase did not instantiate the runtime exception hierarchy; the confined follow-up below observes selected class definitions.',
'nenhuma hierarquia de exceções em execução foi instanciada aqui.':'a fase inicial não instanciou a hierarquia de exceções em execução; a etapa isolada abaixo observa definições selecionadas de classes.'}
for claim in ledger['claims']:
 for lang in ['en','pt-br']:
  for old,new in replacements.items():claim[lang]=claim[lang].replace(old,new)
for faq in ledger['faq']:
 for lang in ['en','pt-br']:
  for old,new in replacements.items():faq[lang+'_a']=faq[lang+'_a'].replace(old,new)
claims=[
{'id':'confined-closure','en':'The confined follow-up uses HTTPX 0.28.1 and httpcore 1.0.9 at the pinned revisions. It executes 15 plain httpcore exception class definitions, 18 HTTPX exception classes and three selected functions in owned namespaces. The source reexport statement covers all 15 classes. The real package initializer is not imported; its later class `__module__` rewriting is not executed. This is not an assertion about the installed dependency version.','pt-br':'A etapa isolada usa HTTPX 0.28.1 e httpcore 1.0.9 nas revisões fixadas. Ela executa 15 definições simples de classes de exceção do httpcore, 18 classes de exceção do HTTPX e três funções selecionadas em namespaces próprios. A instrução de reexportação do código cobre as 15 classes. O inicializador real do pacote não é importado; sua reescrita posterior de `__module__` das classes não é executada. Isso não afirma qual versão da dependência está instalada.','evidence':['core:classes','core:reexports','current:context','current:mapping_provider']},
{'id':'confined-normal-mapping','en':'For each of the 14 exact source classes, an owned message maps to the expected exact HTTPX target, preserving the message and original object as explicit cause. The mapped request property is unset. The same 21 frozen cases and 70 assertions pass on Python 3.14/macOS and Python 3.11/Linux; these are 21 distinct cases, not 42. A separate owned subclass of `ReadTimeout` also maps to `ReadTimeout`.','pt-br':'Para cada uma das 14 classes exatas do código, uma mensagem própria é mapeada ao alvo HTTPX exato esperado, preservando a mensagem e o objeto original como causa explícita. A propriedade de requisição da exceção mapeada fica sem valor. Os mesmos 21 casos congelados e 70 asserções passam em Python 3.14/macOS e Python 3.11/Linux; são 21 casos distintos, sem dobrar para 42. Uma subclasse própria separada de `ReadTimeout` também é mapeada para `ReadTimeout`.','evidence':['core:classes','current:context','current:RequestError.__init__','current:exception:HTTPError']},
{'id':'confined-context-cache','en':'The owned observations preserve unmatched exception identity and a synthetic `KeyboardInterrupt` object, attach an exact request sentinel through `request_context`, preserve an existing request when its argument is absent, and leave `HTTPStatusError` outside that handler. A deliberately failing intercepted import escapes before the context body begins. Two successful contexts in one owned namespace call the intercepted loader import once and reuse the same 14-pair dictionary. No installed-package startup, concurrency or network behavior is established.','pt-br':'As observações próprias preservam a identidade de uma exceção sem correspondência e de um objeto sintético `KeyboardInterrupt`, acrescentam uma sentinela exata de requisição por `request_context`, preservam uma requisição existente quando seu argumento está ausente e deixam `HTTPStatusError` fora desse handler. Uma importação interceptada que falha deliberadamente escapa antes do início do corpo do contexto. Dois contextos bem-sucedidos no mesmo namespace próprio chamam a importação interceptada do carregador uma vez e reutilizam o mesmo dicionário de 14 pares. Isso não estabelece inicialização de pacote instalado, concorrência nem comportamento de rede.','evidence':['current:context','current:mapping_provider','current:request_context','current:HTTPStatusError']},
{'id':'confined-edge-limits','en':'Six additional owned subclass/message cases bound broader promises. Multiple inheritance across unrelated target branches keeps the first matching unrelated target in map order: `ReadTimeout` with `ReadError` maps to `ReadTimeout`, and `LocalProtocolError` with `RemoteProtocolError` maps to `LocalProtocolError`. If `__str__` raises an owned `ValueError` or returns an integer, message conversion escapes as `ValueError` or `TypeError` before the mapped exception is built; the original remains implicit context rather than explicit cause. A valid custom Unicode string is preserved. These are synthetic edge observations, not an upstream defect claim.','pt-br':'Seis casos adicionais próprios de subclasses/mensagens limitam promessas mais amplas. A herança múltipla entre ramos de alvos sem relação conserva o primeiro alvo correspondente sem relação na ordem do mapa: `ReadTimeout` com `ReadError` é mapeado para `ReadTimeout`, e `LocalProtocolError` com `RemoteProtocolError` é mapeado para `LocalProtocolError`. Se `__str__` lança um `ValueError` próprio ou retorna um inteiro, a conversão da mensagem escapa como `ValueError` ou `TypeError` antes da construção da exceção mapeada; a original permanece como contexto implícito, em vez de causa explícita. Uma string Unicode personalizada válida é preservada. São observações sintéticas de limites, sem afirmar defeito do projeto externo.','evidence':['current:context','current:mapping_provider','core:classes']}
]
for claim in claims:claim.update(section='confined-runtime-followup',review='CODEX_SOURCE_AND_OWNED_OBSERVATION_REVIEWED_NOT_OWNER_APPROVED')
faq={'id':'universal-mapping-limit','en_q':'Does the mapper always produce one universally most-specific translated exception?','pt-br_q':'O mapeador sempre produz uma exceção traduzida universalmente mais específica?','en_a':claims[-1]['en'],'pt-br_a':claims[-1]['pt-br'],'evidence':claims[-1]['evidence']}
old_claims=ledger['claims'];ledger['claims']+=claims;ledger['faq'].append(faq)
out=P/'httpx-chapter-candidates-v3';out.mkdir(exist_ok=False)
files={}
for lang in ['en','pt-br']:
 text=(P/'httpx-chapter-candidates-v2'/(lang+'.md')).read_text()
 for old,new in replacements.items():text=text.replace(old,new)
 # Scope older phase statements without rewriting its frozen V2 artifact.
 old='No HTTPX/httpcore source was imported or executed.'if lang=='en'else'Nenhum código HTTPX/httpcore foi importado nem executado.'
 if old in text:text=text.replace(old,('The initial static phase imported or executed no HTTPX/httpcore source.'if lang=='en'else'A fase estática inicial não importou nem executou código HTTPX/httpcore.'))
 text=text.replace('runtime exception instantiation,','runtime exception instantiation in that phase,').replace('instanciação de exceção em execução,','instanciação de exceção em execução naquela fase,')
 heading='## Confined runtime follow-up'if lang=='en'else'## Etapa posterior com execução isolada'
 addition='\n'+heading+'\n\n'+'\n\n'.join(c[lang]+' '+' '.join('[source:'+e+']'for e in c['evidence'])for c in claims)
 addition+='\n\n### '+faq[lang+'_q']+'\n\n'+faq[lang+'_a']+' '+' '.join('[source:'+e+']'for e in faq['evidence'])+'\n\n'
 addition+=('Observation receipts: 'if lang=='en'else'Registros das observações: ')+', '.join('['+name+'](../'+name+')'for name in ['httpx-exception-composition-protocol-v1.json','httpx-exception-composition-macos-v1.json','httpx-exception-composition-linux-v1.json','httpx-exception-edge-protocol-v1.json','httpx-exception-edge-results-v1.json'])+'.\n'
 for key in ['core:classes','core:reexports']:
  u=ledger['units'][key];addition+='\n[source:'+key+']: ../new-public-sources-v1/encode--httpcore/'+revision+'/'+u['path']+'#L'+str(u['first_line'])+' "'+u['source_sha256']+'"\n'
 text+=addition;path=out/(lang+'.md');path.write_text(text);raw=path.read_bytes();files[str(path.relative_to(P))]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
example=out/'httpx-boundary-example.py';example.write_bytes((P/'httpx-chapter-candidates-v2/httpx-boundary-example.py').read_bytes());files[str(example.relative_to(P))]={'bytes':example.stat().st_size,'sha256':hashlib.sha256(example.read_bytes()).hexdigest()}
ledger.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=files,source_executed=True,whole_packages_imported=False,confined_runtime_receipts={name:hashlib.sha256((P/name).read_bytes()).hexdigest()for name in ['httpx-exception-composition-macos-v1.json','httpx-exception-composition-linux-v1.json','httpx-exception-edge-results-v1.json']},source_revision_httpcore=revision)
ledger['review_change_log'].append('V3 distinguishes original static phase from explicitly confined selected-definition execution; adds 4 reviewed claims and one paired FAQ. V2 remains immutable.')
with(P/'httpx-chapter-ledger-v3.json').open('x')as f:f.write(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n')
print({'claims':len(ledger['claims']),'faq_pairs':len(ledger['faq']),'units':len(ledger['units'])})
