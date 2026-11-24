"""Owned editorial script; original Prometheus sources and tests are never run."""
from pathlib import Path
import datetime
import json
import hashlib
import re
from collections import Counter

P=Path(__file__).resolve().parent
OUT=P/'prometheus-query-maintenance-note-v1'
assert not OUT.exists()
OUT.mkdir()
selection=json.loads((P/'prometheus-query-revision-selection-v1.json').read_text())
cards=[]
for f in sorted((P/'prometheus-query-revision-native-v1').glob('*-response.json')):
    if not f.stat().st_size:
        continue
    role=f.name.split('-')[0]
    d=json.loads(f.read_text())
    source=P/'prometheus-query-revision-source-v1'/role/d['path']
    for u in d['units']:
        cards.append(dict(id='S'+str(len(cards)+1),role=role,revision=selection[role],path=d['path'],selector=u['selector'],start=u['start_line'],end=u['end_line'],quote=u['quote'],quote_sha256=hashlib.sha256(u['quote'].encode()).hexdigest(),file_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),kind='complete-native-syntax-declaration-not-runtime'))
assert len(cards)==23
for role,needle in [('before','func testEngine('),('before','func newQueryCostTestAPI('),('after','func newQueryCostTestAPI('),('after','func TestQueryCostEstimationQueueTimeout(')]:
    path='web/api/v1/api_test.go'
    q=P/'prometheus-query-revision-source-v1'/role/path
    lines=q.read_text().splitlines()
    indices=[i for i,l in enumerate(lines) if l.startswith(needle)]
    assert len(indices)==1
    lo=indices[0]
    hi=next((j for j in range(lo+1,len(lines)) if lines[j].startswith('func ')),len(lines))
    quote='\n'.join(lines[lo:hi])+'\n'
    cards.append(dict(id='S'+str(len(cards)+1),role=role,revision=selection[role],path=path,selector=needle,start=lo+1,end=hi,quote=quote,quote_sha256=hashlib.sha256(quote.encode()).hexdigest(),file_sha256=hashlib.sha256(q.read_bytes()).hexdigest(),kind='manual-test-source-span-not-executed'))
(OUT/'source-cards.json').write_text(json.dumps(cards,ensure_ascii=False,indent=2)+'\n')
groups=[
 ('scope','A real API revision, not a runtime experiment','Uma revisão real da API, sem experimento de execução',
  'This note compares the selected parent/child revisions of development-exposed Prometheus. The commit changes thirteen files; eighteen selected before/after source, test, documentation and license files are preserved. Twenty-three native complete declaration quotes and four manually selected test spans bind the analysis to source. No actual request, database, upstream test, benchmark or Go compilation ran. The paired clauses were authored after inspection; they are not blind predictions or an autonomous maintenance-agent result.',
  'Esta nota compara as revisões anterior e posterior selecionadas do Prometheus já exposto em desenvolvimento. O commit muda treze arquivos; dezoito arquivos selecionados de fontes, testes, documentação e licença foram preservados entre as duas revisões. Vinte e três citações nativas de declarações completas e quatro trechos de testes selecionados manualmente vinculam a análise às fontes. Não houve requisição efetiva, banco de dados, teste do projeto, benchmark ou compilação Go. As cláusulas pareadas foram escritas após a inspeção; não são previsões cegas nem resultado de um agente autônomo de manutenção.'),
 ('timeout','HTTP timeout is not a cost-limit override','Timeout HTTP não é uma sobrescrita de limite de custo',
  'Before, `API.queryTimeout` rejects a positive request above a positive effective ceiling. After, it parses the parameter and rejects nonpositive values but no longer performs that ceiling comparison. `max_query_duration` remains a different per-query override; the after API also explicitly rejects its negative values. Do not document the two parameters as sharing the same above-ceiling rejection rule after this revision.',
  'Antes, `API.queryTimeout` rejeita uma solicitação positiva acima de um teto efetivo positivo. Depois, analisa o parâmetro e rejeita valores não positivos, mas não faz mais essa comparação com o teto. `max_query_duration` continua sendo uma sobrescrita diferente por consulta; a API posterior também rejeita explicitamente seus valores negativos. Depois desta revisão, os dois parâmetros não devem ser documentados como se compartilhassem a mesma regra de rejeição acima do teto.'),
 ('cap','Parsing acceptance does not disable execution deadlines','Aceitação na análise não desabilita prazos de execução',
  'A longer positive HTTP timeout is accepted by the after parser, not a promise of unlimited execution. The unchanged selected engine still creates its execution context from its own timeout or stored deadline. Under the standard Go context contract, deriving a later deadline does not extend an earlier parent deadline. Effective server behavior still depends on feature/configuration state and the actual engine implementation; parser code alone does not prove a global cap for arbitrary collaborators.',
  'Um timeout HTTP positivo mais longo é aceito pela análise posterior; isso não promete execução ilimitada. O engine selecionado, que não mudou, ainda cria seu contexto de execução a partir de seu próprio timeout ou prazo armazenado. Pelo contrato padrão de contexto do Go, derivar um prazo posterior não estende um prazo anterior do contexto pai. O comportamento efetivo do servidor ainda depende da funcionalidade, da configuração e da implementação real do engine; o código de análise isolado não prova um teto global para colaboradores arbitrários.'),
 ('sequence','The estimator moves before execution','O estimador passa para antes da execução',
  'Before, successful `Exec` is followed by `costComparison`. After, both handlers record `limitStart`, build the query, call `estimateForComparison` when cost comparison is enabled, and only then call `Exec`. `pendingCostComparison.finish` later pairs the estimate with actual statistics. This changes caller orchestration even though the engine file is byte-identical. The selected after order avoids holding a finished query result while this estimation waits for its slot; no memory or speed improvement was measured.',
  'Antes, um `Exec` bem-sucedido é seguido por `costComparison`. Depois, ambos os manipuladores registram `limitStart`, constroem a consulta, chamam `estimateForComparison` quando a comparação de custo está habilitada e só então chamam `Exec`. Mais tarde, `pendingCostComparison.finish` combina a estimativa com as estatísticas efetivas. Isso muda a orquestração do chamador embora o arquivo do engine seja idêntico byte a byte. A ordem posterior selecionada evita manter um resultado de consulta já concluído enquanto essa estimativa aguarda sua vaga; nenhuma melhoria de memória ou velocidade foi medida.'),
 ('budget','An explicit start differs from resetting a timer','Um início explícito difere de reiniciar o temporizador',
  'Before, the estimator derives its cost context with `WithTimeout` when it starts. After, it uses `WithDeadline` at `limitStart.Add(duration)`, where the executed-query handlers sampled the start before construction. This avoids granting a fresh full estimation duration after construction. API and engine timestamps are separate samples, and their configurations can differ; this source review does not equate their exact deadlines or prove every collaborator stops at expiration.',
  'Antes, o estimador deriva seu contexto de custo com `WithTimeout` quando começa. Depois, usa `WithDeadline` em `limitStart.Add(duration)`, com início registrado pelos manipuladores de consultas executadas antes da construção. Isso evita conceder uma nova duração completa à estimativa após construir a consulta. Timestamps da API e do engine são amostras separadas, e suas configurações podem diferir; esta revisão de fontes não iguala seus prazos exatos nem prova que todo colaborador pare na expiração.'),
 ('failures','An estimation warning does not guarantee query success','Um aviso de estimativa não garante sucesso da consulta',
  'On the selected successful execution path, `pendingCostComparison.finish` merges estimator annotations and turns an estimation error into a warning with no comparison. But `Exec` still runs using its request/engine context and can fail independently. Execution-error returns occur before that finish call and do not merge the pending estimation annotations there. The changed test declaration distinguishes an estimation-only duration failure from a request timeout or cancellation; the former can preserve success in its fixture, which does not install the same duration ceiling on the engine.',
  'No caminho selecionado de execução bem-sucedida, `pendingCostComparison.finish` combina anotações do estimador e transforma um erro de estimativa em aviso sem comparação. Porém, `Exec` ainda roda com seu contexto de requisição e engine e pode falhar independentemente. Os retornos de erro de execução ocorrem antes dessa finalização e ali não combinam as anotações pendentes da estimativa. A declaração de teste alterada distingue uma falha de duração apenas da estimativa de um timeout ou cancelamento da requisição; a primeira pode preservar o sucesso nessa configuração de teste, que não instala o mesmo teto de duração no engine.'),
 ('errors','Construction preserves selected typed error categories','A construção preserva categorias selecionadas de erro tipado',
  'Before, `queryConstructionError` handles an above-ceiling error specially and otherwise wraps the error as an invalid query parameter. After, it also recognizes `ErrQueryTimeout` and `ErrQueryCanceled` and delegates those cases to the unchanged `returnAPIError`. This does not classify every raw context error or arbitrary custom-engine error the same way. The source change supports documenting these selected typed paths; it is not an observed HTTP status result.',
  'Antes, `queryConstructionError` trata especialmente um erro acima do teto e, nos demais casos, envolve o erro como parâmetro de consulta inválido. Depois, reconhece também `ErrQueryTimeout` e `ErrQueryCanceled` e delega esses casos ao `returnAPIError`, que não mudou. Isso não classifica todo erro bruto de contexto ou de um engine personalizado da mesma forma. A mudança na fonte sustenta documentar esses caminhos tipados selecionados; não é resultado observado de status HTTP.'),
 ('callees','Unchanged callees do not imply unchanged documentation','Funções chamadas inalteradas não implicam documentação inalterada',
  'The engine file and the complete native quotes for `queryCostCeilings`, `costRequested` and `returnAPIError` match byte for byte across this pair. Their callers nevertheless change deadline validation, estimation order and construction-error routing. Clauses describing those changed policies require `MODIFY`; source pins also need updating for a new target. Do not infer a whole-chapter `NO-OP` or remove the chapter solely because the old `costComparison` helper disappears and is replaced.',
  'O arquivo do engine e as citações nativas completas de `queryCostCeilings`, `costRequested` e `returnAPIError` coincidem byte a byte entre essas revisões. Mesmo assim, seus chamadores mudam a validação de prazo, a ordem de estimativa e o encaminhamento de erros de construção. Cláusulas que descrevem essas políticas alteradas exigem `MODIFY`; referências de fonte também precisam mudar para um novo alvo. Não se deve inferir `NO-OP` do capítulo inteiro nem remover o capítulo apenas porque o auxiliar antigo `costComparison` desaparece e é substituído.'),
 ('docs','Existing documentation and test fixtures have a limited review','Documentação existente e configurações de teste têm revisão delimitada',
  'The selected existing documentation changes distinguish HTTP timeout from cost overrides and move estimation before execution, matching the inspected source paths. This review does not accept all three large documentation pages: remote-read estimation, physical versus evaluator sample accounting, every rule-evaluation caller and all timeout status paths require further tracing. The test helper now explicitly supplies `EnableQueryCost` from its enabled argument; the earlier generic engine initializer omitted that field. Those declarations explain fixture intent, not passing test results or production configuration synchronization.',
  'As mudanças selecionadas na documentação existente distinguem timeout HTTP de sobrescritas de custo e movem a estimativa para antes da execução, em acordo com os caminhos de fonte inspecionados. Esta revisão não aprova integralmente as três páginas extensas: estimativas de leitura remota, contagem de amostras físicas ou do avaliador, todos os chamadores de avaliação de regras e todos os caminhos de status de timeout exigem investigação adicional. O auxiliar de teste agora fornece explicitamente `EnableQueryCost` a partir de seu argumento de habilitação; o inicializador genérico anterior do engine omitia esse campo. Essas declarações explicam a intenção da configuração de teste, e não resultados de aprovação ou sincronização da configuração de produção.'),
]
faqs=[
 ('Can a larger HTTP timeout now bypass every server limit?','Um timeout HTTP maior agora pode ignorar todo limite do servidor?',
  'No. Parser acceptance differs from the selected engine/parent-context limits. The unchanged engine still constructs a bounded execution context; exact effective behavior requires the relevant configuration and engine implementation.',
  'Não. A aceitação na análise difere dos limites selecionados do engine e do contexto pai. O engine inalterado ainda constrói um contexto de execução com limite; o comportamento efetivo exato exige considerar configuração e implementação do engine.'),
 ('Are timeout and max_query_duration interchangeable?','timeout e max_query_duration são intercambiáveis?',
  'No. The after timeout parser drops the above-ceiling rejection while still requiring positivity. The cost override retains its ceiling semantics and gains an explicit negative-value API rejection. Do not silently apply one parameter’s policy to the other.',
  'Não. A análise posterior de timeout remove a rejeição acima do teto, mas continua exigindo valor positivo. A sobrescrita de custo mantém sua semântica de teto e ganha uma rejeição explícita de valor negativo na API. Não se deve aplicar silenciosamente a política de um parâmetro ao outro.'),
 ('Does every failed estimate leave a successful query with a warning?','Toda estimativa que falha deixa uma consulta bem-sucedida com aviso?',
  'No. Warning conversion happens after successful execution. Request cancellation or timeout can still fail the execution, and the error-return path does not call the pending comparison’s finish method.',
  'Não. A conversão em aviso ocorre após execução bem-sucedida. Cancelamento ou timeout da requisição ainda pode fazer a execução falhar, e o caminho de retorno de erro não chama a finalização da comparação pendente.'),
 ('Do the API and engine now share one identical timestamp?','A API e o engine agora compartilham um timestamp idêntico?',
  'That is not established. The API samples its start before construction; the engine records its own deadline during construction. The explicit earlier-start calculation constrains estimation, but exact equality and actual stop timing were not verified.',
  'Isso não foi estabelecido. A API registra seu início antes da construção; o engine registra seu próprio prazo durante a construção. O cálculo explícito com início anterior restringe a estimativa, mas igualdade exata e tempo efetivo de parada não foram verificados.'),
 ('Can an unchanged engine justify retaining every lifecycle paragraph?','Um engine inalterado justifica manter todo parágrafo sobre o ciclo de vida?',
  'No. The API caller changes the order and error-routing context around that engine. Retained callee text and modified caller explanations require separate decisions, with source provenance bound to the actual target revision.',
  'Não. O chamador da API muda a ordem e o contexto de encaminhamento de erros em torno desse engine. Manter texto sobre a função chamada e modificar explicações sobre o chamador exige decisões separadas, com proveniência vinculada à revisão-alvo efetiva.'),
 ('Were existing tests or documentation accepted wholesale?','Os testes ou a documentação existentes foram aprovados integralmente?',
  'No. Test declarations were inspected without execution. Six existing-document clause groups were assessed with explicit limits; broader changed topics remain inconclusive here. This note is same-agent source review, not independent or owner acceptance.',
  'Não. Declarações de teste foram inspecionadas sem execução. Seis grupos de cláusulas da documentação existente foram avaliados com limites explícitos; outros tópicos alterados permanecem inconclusivos aqui. Esta nota tem revisão de fontes pelo mesmo agente, e não aprovação independente ou do proprietário.'),
]
for lang in ['en','pt']:
    en=lang=='en'
    chunks=['# '+('Prometheus maintenance: timeout policy, estimation order and caller context' if en else 'Manutenção do Prometheus: política de timeout, ordem de estimativa e contexto do chamador'),
      '`prometheus/prometheus`: `'+selection['before']+'` → `'+selection['after']+'`',
      'CANDIDATE_FOR_SOURCE_REVIEW · not owner-approved, Gold or training data.' if en else 'CANDIDATE_FOR_SOURCE_REVIEW · sem aprovação do proprietário, sem Gold, fora dos dados de treinamento.']
    for ident,he,hp,te,tp in groups:chunks.extend(['## '+(he if en else hp),te if en else tp])
    chunks.append('## FAQ')
    for qe,qp,ae,ap in faqs:chunks.extend(['### '+(qe if en else qp),ae if en else ap])
    chunks.extend(['## '+('Read-only reproduction and source references' if en else 'Reprodução somente para leitura e referências às fontes'),
      'An equivalent pinned Git diff was inspected. This command displays source changes only; it does not run an API, tests, storage or an estimator.' if en else 'Uma comparação Git equivalente com revisões fixadas foi inspecionada. Este comando apenas exibe mudanças de fonte; não executa API, testes, armazenamento ou estimador.',
      '```sh\ngit -c core.fsmonitor=false diff --no-ext-diff --no-renames '+selection['before']+' '+selection['after']+' -- web/api/v1/api.go\n```'])
    for c in cards:chunks.append(f'[{c["id"]}: {c["role"]} {c["selector"]}](https://github.com/prometheus/prometheus/blob/{c["revision"]}/{c["path"]}#L{c["start"]}-L{c["end"]})')
    chunks.append('[R1: Go context deadline contract](https://pkg.go.dev/context#WithDeadline). '+('Current primary API contract, not a Prometheus runtime observation.' if en else 'Contrato primário atual da API; não é observação de execução do Prometheus.'))
    chunks.append('The complete root Apache-2.0 license and file notices are retained. All campaign artifacts remain restricted internal review material, without blanket file-level, training or public-publication clearance.' if en else 'A licença Apache-2.0 completa da raiz e os avisos dos arquivos foram preservados. Todos os artefatos da campanha permanecem material interno restrito de revisão, sem liberação geral por arquivo, para treinamento ou para publicação pública.')
    (OUT/(lang+'.md')).write_text('\n\n'.join(chunks)+'\n')
en=(OUT/'en.md').read_text();pt=(OUT/'pt.md').read_text()
assert Counter(re.findall(r'`([^`\n]+)`',en))==Counter(re.findall(r'`([^`\n]+)`',pt))
manifest={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'CANDIDATE_FOR_SOURCE_REVIEW','groups':len(groups)+len(faqs),'faq_pairs':len(faqs),'native_declaration_quotes':23,'manual_test_spans':4,'source_cards':len(cards),'source_files':18,'inline_literals_per_language':len(re.findall(r'`([^`\n]+)`',en)),'files':{q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in OUT.iterdir()},'population':'Separate paired maintenance note, not a new full architecture topic, actual agent decision or independent task.','owner_approved':False,'training_eligible':False,'neural_calls':0,'upstream_execution':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
