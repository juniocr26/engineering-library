"""Render an isolated fixed-text topic from the six verified written-source rules."""
import ast
import hashlib
import json
from pathlib import Path

P=Path(__file__).resolve().parent
TEXT={
'PF01':{
'en':'The written Dependant class declares use_cache: bool = True and a scope field whose declared value is None. This records the selected class statements; it is not observation of a live dependency object.',
'pt-BR':'A classe escrita Dependant declara use_cache: bool = True e um campo scope cujo valor declarado é None. Isso registra as instruções da classe selecionada; não é observação de um objeto de dependência em execução.'},
'PF02':{
'en':'At the initialization branch, dependency_cache is None guards assignment of an empty dictionary to dependency_cache. The selected function has no other direct assignment to that local name. This does not establish process-wide or cross-request cache lifetime.',
'pt-BR':'No ramo de inicialização, dependency_cache is None condiciona a atribuição de um dicionário vazio a dependency_cache. A função selecionada não possui outra atribuição direta a esse nome local. Isso não estabelece duração do cache no processo inteiro ou entre requisições.'},
'PF03':{
'en':'Inside the selected loop over dependant.dependencies, the written awaited solve_dependencies call passes dependency_cache=dependency_cache. This connects the local cache variable to subdependency solving in the written data flow; dynamic bindings and actual completion remain unverified.',
'pt-BR':'Dentro do laço selecionado sobre dependant.dependencies, a chamada escrita e aguardada de solve_dependencies passa dependency_cache=dependency_cache. Isso conecta a variável local de cache à resolução de subdependências no fluxo de dados escrito; vínculos dinâmicos e conclusão efetiva permanecem não verificados.'},
'PF04':{
'en':'The selected reuse branch requires sub_dependant.use_cache and sub_dependant_cache_key in dependency_cache. Its body assigns solved = dependency_cache[sub_dependant_cache_key]. The conjunction is a read/reuse condition; it is not a guarantee that every dependency executes exactly once.',
'pt-BR':'O ramo selecionado de reutilização exige sub_dependant.use_cache and sub_dependant_cache_key in dependency_cache. Seu corpo atribui solved = dependency_cache[sub_dependant_cache_key]. A conjunção é uma condição de leitura/reutilização; não é garantia de que cada dependência execute exatamente uma vez.'},
'PF05':{
'en':'When control reaches the later write guard and the key is absent, the written body assigns dependency_cache[sub_dependant_cache_key] = solved. This guard does not mention use_cache. Therefore the selected source does not implement use_cache=False as a general ban on cache writes. Earlier errors, exceptions or control flow can prevent reaching this guard.',
'pt-BR':'Quando o controle alcança a condição posterior de escrita e a chave está ausente, o corpo escrito atribui dependency_cache[sub_dependant_cache_key] = solved. Essa condição não menciona use_cache. Portanto, a fonte selecionada não implementa use_cache=False como proibição geral de escritas no cache. Erros, exceções ou fluxo de controle anteriores podem impedir que essa condição seja alcançada.'},
'PF06':{
'en':'The selected function contains two written assertions using isinstance with AsyncExitStack: one for request_astack and one for function_astack. These statements do not prove that assertions are enabled in a deployed interpreter, that request composition satisfies them, or that dependency callbacks cannot raise other exceptions.',
'pt-BR':'A função selecionada contém duas asserções escritas que usam isinstance com AsyncExitStack: uma para request_astack e outra para function_astack. Essas instruções não comprovam que as asserções estejam habilitadas no interpretador implantado, que a composição da requisição as satisfaça ou que callbacks de dependências não possam lançar outras exceções.'}}
FAQ=[
{'refs':['PF04','PF05'],'en':('Does use_cache=False forbid every cache write?','The selected read condition uses use_cache, but the later write guard does not. If execution reaches that guard with an absent key, the written assignment stores solved. This is a source-level distinction, not an observation that every invocation succeeds.'),'pt-BR':('use_cache=False proíbe toda escrita no cache?','A condição selecionada de leitura usa use_cache, mas a condição posterior de escrita não. Se a execução alcançar essa condição com uma chave ausente, a atribuição escrita armazena solved. Essa é uma distinção da fonte, não observação de que toda invocação tenha sucesso.')},
{'refs':['PF02','PF03'],'en':('Is a global cache lifetime established?','No global lifetime is established by this profile. It observes initialization when the local value is None and passage of the same local name to the written recursive call. Caller composition, external aliases and actual reuse across requests require separate evidence.'),'pt-BR':('Uma duração global do cache foi estabelecida?','Nenhuma duração global foi estabelecida por este perfil. Ele observa a inicialização quando o valor local é None e a passagem do mesmo nome local à chamada recursiva escrita. Composição do chamador, aliases externos e reutilização efetiva entre requisições exigem evidências separadas.')},
{'refs':['PF03','PF04','PF05'],'en':('Does this prove exactly-once dependency execution?','No. The rules describe selected cache data flow and guards. They do not establish callback completion, concurrent invocation counts, effective cache-key equivalence or live override behavior. Written test assertions are separate from executed results.'),'pt-BR':('Isso comprova execução exatamente uma vez das dependências?','Não. As regras descrevem fluxo de dados e condições selecionados do cache. Elas não estabelecem conclusão de callbacks, contagens de invocações concorrentes, equivalência efetiva de chaves de cache ou comportamento real de overrides. Asserções de testes escritos são diferentes de resultados executados.')},
{'refs':['PF06'],'en':('Do the stack assertions establish complete error handling?','No. They are two specific written assertions. This profile does not establish interpreter assertion settings, caller correctness, callback exception translation, cleanup completion or every possible error path.'),'pt-BR':('As asserções de stack estabelecem tratamento completo de erros?','Não. Elas são duas asserções escritas específicas. Este perfil não estabelece as configurações de asserções do interpretador, correção do chamador, tradução de exceções de callbacks, conclusão de cleanup ou todos os caminhos possíveis de erro.')}
]
EXAMPLE='from fastapi import Depends\n\nasync def synthetic_value():\n    return 1\n\nasync def synthetic_endpoint(value: int = Depends(synthetic_value, use_cache=False)):\n    return {"value": value}\n'

def render(observation):
    if observation.get('profile')!='fastapi-written-dependency-cache-flow/1' or {f['id'] for f in observation['facts']}!=set(TEXT) or len(observation['facts'])!=6:
        raise ValueError('unregistered written-flow profile')
    outputs={}
    for language in ['en','pt-BR']:
        en=language=='en'
        title='FastAPI dependency-cache data flow' if en else 'Fluxo de dados do cache de dependências do FastAPI'
        text='# '+title+'\n\n'
        text+=('Isolated source-verified research candidate; owner review, publication and training approval are pending.\n\n' if en else 'Candidato isolado de pesquisa com verificação de fonte; revisão do proprietário e aprovações de publicação e treino estão pendentes.\n\n')
        text+='## '+('Scope and architecture' if en else 'Escopo e arquitetura')+'\n\n'
        text+=('Pinned source: fastapi/fastapi @ 05e6df7e906c3decba377c37548019973f40bf15. This chapter follows six rule groups: one selected Dependant declaration group and five cache-flow/assertion groups in solve_dependencies. It connects the model declaration, solver loop, recursive passage, reuse guard and later write guard. It does not document all FastAPI architecture, an installed release or observed service behavior.\n\n' if en else 'Fonte fixada: fastapi/fastapi @ 05e6df7e906c3decba377c37548019973f40bf15. Este capítulo acompanha seis grupos de regras: um grupo de declarações selecionadas de Dependant e cinco grupos de fluxo de cache/asserções em solve_dependencies. Ele conecta a declaração do modelo, o laço do solver, a passagem recursiva, a condição de reutilização e a condição posterior de escrita. Ele não documenta toda a arquitetura do FastAPI, uma release instalada ou comportamento observado de serviço.\n\n')
        text+='## '+('Declarations, flow and error boundaries' if en else 'Declarações, fluxo e limites de erro')+'\n\n'
        for fact in observation['facts']:
            text+='### '+fact['id']+'\n\n'+TEXT[fact['id']][language]+'\n\n'
            text+=('Evidence: ' if en else 'Evidência: ')+', '.join(f"`{e['path']}:{e['first_line']}-{e['last_line']}`" for e in fact['evidence'])+'.\n\n'
        text+='## '+('Example and written tests' if en else 'Exemplo e testes escritos')+'\n\n'
        text+=('Synthetic dependency-declaration fragment, not a running service. It follows the written use_cache=False call pattern in tests/test_dependency_cache.py:30-35. Its Python syntax was parsed; imports, dependency resolution, type compatibility and execution were not tested. No route is registered here.\n\n' if en else 'Fragmento sintético de declaração de dependência, não um serviço em execução. Ele segue o padrão escrito de chamada com use_cache=False em tests/test_dependency_cache.py:30-35. Sua sintaxe Python foi analisada; imports, resolução de dependências, compatibilidade de tipos e execução não foram testados. Nenhuma rota está registrada aqui.\n\n')
        text+='```python\n'+EXAMPLE+'```\n\n'
        text+=('The pinned tests/test_dependency_cache.py contains written assertions for repeated requests, nested dependencies and disabled reuse. These external project tests were not executed. Assertions in a file are not passing results or production acceptance. No installer/startup/test command is certified by this chapter.\n\n' if en else 'O arquivo fixado tests/test_dependency_cache.py contém asserções escritas sobre requisições repetidas, dependências aninhadas e reutilização desabilitada. Esses testes do projeto externo não foram executados. Asserções em um arquivo não são resultados aprovados nem aceite de produção. Nenhum comando de instalação, inicialização ou teste é certificado por este capítulo.\n\n')
        text+='## FAQ\n\n'
        for i,faq in enumerate(FAQ,1):
            q,a=faq[language];text+=f'### Q{i:03} — {q}\n\n{a} ['+', '.join(faq['refs'])+']\n\n'
        text+='## '+('Unresolved context and preservation' if en else 'Contexto não resolvido e preservação')+'\n\n'
        text+=('This closed profile does not reconstruct cache-key construction, override resolution, effective generator scopes, concurrency limits or complete cleanup behavior. In particular, it does not say keys are merely function names. Those contracts need their own evidence. Source syntax, fixed text and exact quotations do not prove arbitrary prose truth or runtime integration.\n\nThe frozen inventory recorded a shallow clone with no local parent revision. No historical MODIFY decision is inferred from this one revision. Missing symbols in partial source never authorize REMOVE. Existing project documentation remains unchanged. MIT license notices are retained in the pinned source evidence. This candidate and its source family remain outside training; source verification is not owner-approved gold.\n' if en else 'Este perfil fechado não reconstrói a construção de chaves de cache, a resolução de overrides, os escopos efetivos de generators, os limites de concorrência ou o comportamento completo de cleanup. Em particular, ele não afirma que as chaves sejam apenas nomes de funções. Esses contratos precisam de evidências próprias. Sintaxe de fonte, texto fixo e citações exatas não comprovam a verdade de prosa arbitrária ou integração em runtime.\n\nO inventário congelado registrou um clone raso sem revisão pai local. Nenhuma decisão histórica MODIFY é inferida desta única revisão. Símbolos ausentes em fonte parcial nunca autorizam REMOVE. A documentação existente do projeto permanece sem alterações. Os avisos da licença MIT estão preservados na evidência fixada de fonte. Este candidato e sua família de fonte permanecem fora de treino; verificação de fonte não é gold aprovado pelo proprietário.\n')
        outputs[language]=text.encode()
    return outputs

if __name__=='__main__':
    observation=json.loads((P/'python-cache-flow-observation-v2.json').read_text());review=json.loads((P/'python-cache-flow-independent-source-review-v4.json').read_text())
    if review['status']!='SIX_WRITTEN_AST_RULES_AND_TYPED_FACTS_VERIFIED' or len(review['checks'])!=6:raise ValueError('independent typed-source review required')
    ast.parse(EXAMPLE)
    files=[]
    for language,data in render(observation).items():
        f=P/'python-cache-flow-candidate-v2'/(language+'.md');f.parent.mkdir(parents=True,exist_ok=True)
        with f.open('xb') as out:out.write(data)
        files.append({'language':language,'path':str(f),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
    record={'profile':'fastapi-written-dependency-cache-flow/1','files':files,'source_rule_groups':6,'faq_pairs':4,'status':'PENDING_SEPARATE_COMPLETE_DOCUMENT_REVIEW','generator':'Fixed bilingual templates over verified typed written-flow records; zero Ollama calls','not_neural_improvement':True,'source_program_executed':False,'owner_approved':False,'training_gold':False,'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with (P/'python-cache-flow-candidate-index-v2.json').open('x') as out:out.write(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'files':len(files),'status':record['status']}))
