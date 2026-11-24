"""Append-only technical selfchapter candidate, preserving frozen historical text."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
pack_path=P/'self-chapter-supplement-evidence-v4.json';pack=json.loads(pack_path.read_text())
units={u['id']:u for u in pack['units']};claims=[]


def add(i,en,pt,refs):
    if re.findall(r'`([^`]+)`',en)!=re.findall(r'`([^`]+)`',pt):raise ValueError('bilingual code identifiers differ:'+i)
    if any(ref not in units for ref in refs):raise ValueError('unregistered source unit')
    claims.append({'id':i,'en':en,'pt-br':pt,'evidence_ids':refs,'scope':'SOURCE_REVIEWED_TECHNICAL_SUPPLEMENT_NOT_GENERAL_SEMANTIC_CERTIFICATE'})


add('current-cut',
    'The current caller source declares `VERSION = \'1.9.43\'`. The inspected planner, maintenance and optional helper declare `0.3.6`, `0.1.5` and `0.1.5`, respectively. Their exact working-file hashes identify this cut; the observed Git HEAD alone does not assert that the new caller bytes are committed.',
    'O código atual do chamador declara `VERSION = \'1.9.43\'`. O planejador, a manutenção e o auxiliar opcional inspecionados declaram `0.3.6`, `0.1.5` e `0.1.5`, respectivamente. Os hashes exatos dos arquivos de trabalho identificam este recorte; o HEAD Git observado, isoladamente, não afirma que os novos bytes do chamador estão commitados.',
    ['E6','E7','E8','E9'])
add('routing-scope',
    '`evidence_cards` uses `source_units` for explicit unit selections. Structural Python mode uses `python_fragments`; other cards can omit AST catch metadata. The inspected `infer` path still calls `call_model(source_model_request(files, skills))`. This supplement does not turn optional helper research into autonomous tool routing.',
    '`evidence_cards` usa `source_units` para seleções explícitas de unidades. O modo estrutural Python usa `python_fragments`; outros cartões podem omitir metadados AST de captura. O caminho `infer` inspecionado continua chamando `call_model(source_model_request(files, skills))`. Este suplemento não transforma pesquisa com o auxiliar opcional em roteamento autônomo de ferramentas.',
    ['E1','E2','E10','E11'])
add('source-metadata',
    '`caught_exception_identifiers` traverses the selected function’s lexical AST subtree and collects bounded static names from catch clauses. It can record simple names, attribute chains and direct tuple elements. It does not resolve exception classes or establish which nested body executes. Bare catches and dynamic type expressions do not become resolved class facts.',
    '`caught_exception_identifiers` percorre a subárvore AST lexical da função selecionada e coleta nomes estáticos limitados das cláusulas de captura. Pode registrar nomes simples, cadeias de atributos e elementos diretos de tuplas. Não resolve classes de exceção nem estabelece qual corpo aninhado é executado. Capturas sem tipo e expressões dinâmicas de tipo não viram fatos de classes resolvidas.',
    ['E5'])
add('bounded-refusal',
    '`quoted_caught_identifier_mismatch?` activates for a backticked source catch identifier and requires its admitted spelling in both language explanations. A source-qualified spelling and its terminal name can agree when unambiguous. Distinct qualified names sharing a terminal require the same named reference sets across languages; an unsupported owner is refused.',
    '`quoted_caught_identifier_mismatch?` atua para um identificador de captura da fonte entre crases e exige sua grafia admitida nas explicações dos dois idiomas. A grafia qualificada da fonte e seu nome terminal podem concordar quando não há ambiguidade. Nomes qualificados distintos com o mesmo terminal exigem os mesmos conjuntos de referências nomeadas entre os idiomas; um proprietário não sustentado é recusado.',
    ['E3','E4','E12'])
add('limits',
    'These refusals require supported AST metadata in the card. They do not certify map-pair direction, reference roles, arbitrary new identifiers, every code key, nested or mixed dictionaries, runtime bindings, execution order or full EN/PT factual equivalence. The shared helper checks source-reference presence in the explanation; it is not a complete semantic parser of every code span. Citation integrity, reference preservation and semantic review remain separate obligations.',
    'Essas recusas exigem metadados AST suportados no cartão. Elas não certificam direção dos pares do mapa, papéis das referências, identificadores novos arbitrários, toda chave de código, dicionários aninhados ou mistos, vinculações em execução, ordem de execução nem equivalência factual completa EN/PT. O auxiliar compartilhado verifica a presença de referências da fonte na explicação; ele não é um analisador semântico completo de cada trecho de código. Integridade das citações, preservação das referências e revisão semântica continuam sendo obrigações separadas.',
    ['E1','E3','E4','E5'])
add('returned-map-metadata',
    '`direct_return_mapping_identifiers` records bounded ASCII name/attribute references when direct return statements contain literal dictionaries made entirely from those references. The profile permits up to 32 pairs and 64 unique references; unpacked, mixed, nested-only and oversized maps are outside its coverage. It records lexical spelling rather than resolved class identities or an executed return value.',
    '`direct_return_mapping_identifiers` registra referências ASCII limitadas de nomes/atributos quando instruções diretas de retorno contêm dicionários literais inteiramente formados por essas referências. O perfil permite até 32 pares e 64 referências únicas; mapas com expansão, mistos, apenas aninhados ou grandes demais ficam fora da cobertura. Ele registra grafia lexical, em vez de identidades de classes resolvidas ou um valor de retorno executado.',
    ['E5'])
add('returned-map-refusal',
    '`quoted_return_mapping_identifier_mismatch?` sends the known map references to `quoted_identifier_reference_mismatch?`; the existing catch-reference entry uses the same helper. A backticked known reference triggers a cross-language presence/allowed-owner check. When distinct source spellings share a terminal, both explanations must preserve the same named-reference set. This does not verify which reference is the dictionary key or value.',
    '`quoted_return_mapping_identifier_mismatch?` envia as referências conhecidas do mapa para `quoted_identifier_reference_mismatch?`; a entrada existente de referências de captura usa o mesmo auxiliar. Uma referência conhecida entre crases aciona uma verificação de presença entre idiomas e de proprietário admitido. Quando grafias distintas da fonte compartilham um terminal, ambas as explicações devem preservar o mesmo conjunto de referências nomeadas. Isso não verifica qual referência é a chave ou o valor do dicionário.',
    ['E3','E4','E12','E13'])
add('cached-lexical-unit-integrity',
    'HelperRetrieval `validate_unit` now reconstructs the expected selected Python unit with `python_unit`, and the selected Go unit with `extract`, before comparing canonical evidence. A physically real quote, source hash and matching receipt do not alone establish that the quote belongs to the requested complete callable. The comparison also binds admitted declaration metadata and Go producer fields; it is not runtime symbol or upstream Git authentication.',
    'O `validate_unit` do HelperRetrieval agora reconstrói a unidade Python selecionada esperada com `python_unit`, e a unidade Go selecionada com `extract`, antes de comparar a evidência canônica. Uma citação fisicamente real, um hash da fonte e um recibo correspondente não estabelecem, sozinhos, que a citação pertence à unidade chamável completa solicitada. A comparação também vincula os metadados admitidos da declaração e os campos do produtor Go; ela não autentica símbolos em execução nem Git externo.',
    ['E14','E15','E16','E18'])
add('legacy-journal-review',
    'For a matching registered request and source, an earlier result version reaches `LEGACY_RESULT_REVIEW_REQUIRED` before cached-result validation. That branch preserves the old journal for explicit review without automatic migration, repeat quote injection or retry. Current duplicate entries are revalidated; Go revalidation therefore still depends on the local extraction tool. These rules do not refund or migrate a separate job budget.',
    'Para uma solicitação e fonte registradas correspondentes, uma versão anterior do resultado chega a `LEGACY_RESULT_REVIEW_REQUIRED` antes da validação do resultado em cache. Esse ramo preserva o journal antigo para revisão explícita, sem migração automática, nova injeção da citação ou repetição da tentativa. Entradas duplicadas atuais são revalidadas; portanto, a revalidação Go ainda depende da ferramenta local de extração. Essas regras não devolvem nem migram um orçamento separado de job.',
    ['E17','E14','E15','E18'])
add('retrieval-not-entailment',
    'Selected lexical-unit integrity does not certify a prose claim, map-pair direction, runtime object identity, training approval or automatic application. The Ruby quotation guards and optional retrieval checks address different boundaries. The inspected `infer` path remains direct model inference, and planner/maintenance source versions remain unchanged. The isolated role-aware map profile is research rather than newly published production routing.',
    'A integridade da unidade lexical selecionada não certifica uma afirmação em prosa, direção dos pares do mapa, identidade de objetos em execução, aprovação de treinamento ou aplicação automática. As guardas de citações Ruby e as verificações opcionais de recuperação tratam de fronteiras distintas. O caminho `infer` inspecionado continua sendo inferência direta do modelo, e as versões do código do planejador e da manutenção permanecem inalteradas. O perfil isolado de mapas que distingue papéis é pesquisa, e não um novo roteamento de produção publicado.',
    ['E3','E12','E13','E14','E6','E7','E10'])
faq=[{'id':'quoted-exception-preservation','en_q':'Do correct source citations alone prove that exception names were preserved in translation?',
      'pt-br_q':'Citações corretas da fonte, sozinhas, provam que os nomes de exceções foram preservados na tradução?',
      'answer_claim':'bounded-refusal','proposal':'ADD_SOURCE_REVIEWED_SUPPLEMENT_CANDIDATE'},
     {'id':'ast-card-coverage','en_q':'Does the new refusal cover every evidence mode and every kind of prose?',
      'pt-br_q':'A nova recusa cobre todos os modos de evidência e todos os tipos de prosa?',
      'answer_claim':'limits','proposal':'ADD_SOURCE_REVIEWED_SUPPLEMENT_CANDIDATE'}]
faq.extend([
    {'id':'returned-map-reference-profile','en_q':'Which returned dictionary references does the new metadata cover?',
     'pt-br_q':'Quais referências de dicionários retornados os novos metadados cobrem?',
     'answer_claim':'returned-map-metadata','proposal':'ADD_SOURCE_REVIEWED_SUPPLEMENT_CANDIDATE'},
    {'id':'mapping-direction-limit','en_q':'Does preserving mapping reference names establish their key/value direction?',
     'pt-br_q':'Preservar nomes de referências do mapa estabelece sua direção entre chave e valor?',
     'answer_claim':'returned-map-refusal','proposal':'ADD_SOURCE_REVIEWED_SUPPLEMENT_CANDIDATE'}
])
faq.extend([
    {'id':'cached-callable-ownership','en_q':'Can matching physical bytes and a rewritten receipt replace complete selected-callable validation?',
     'pt-br_q':'Bytes físicos correspondentes e um recibo reescrito podem substituir a validação da unidade chamável completa selecionada?',
     'answer_claim':'cached-lexical-unit-integrity','proposal':'ADD_SOURCE_REVIEWED_SUPPLEMENT_CANDIDATE'},
    {'id':'legacy-journal-upgrade','en_q':'Are older helper journals silently upgraded after a version change?',
     'pt-br_q':'Journals antigos do auxiliar são atualizados silenciosamente após uma mudança de versão?',
     'answer_claim':'legacy-journal-review','proposal':'ADD_SOURCE_REVIEWED_SUPPLEMENT_CANDIDATE'}
])
lookup={c['id']:c for c in claims}
for row in faq:
    row.update({'pt-br_a':lookup[row['answer_claim']]['pt-br']},en_a=lookup[row['answer_claim']]['en'],
               evidence_ids=lookup[row['answer_claim']]['evidence_ids'],owner_approved=False,training_gold=False,
               automatic_faq_engine_admitted=False,not_a_source_evolution_classifier_target=True)
output=P/'self-chapter-supplement-v3';output.mkdir(exist_ok=False);files={};historical_checks=[]
for lang in ['en','pt-br']:
    old=pack['historical_documents'][lang];ref=old['candidate_documentation_ref'];old_path=ROOT/ref['path'];old_raw=old_path.read_bytes()
    if hashlib.sha256(old_raw).hexdigest()!=ref['sha256']:raise ValueError('historical chapter drift')
    historical_checks.append({'language':lang,'path':ref['path'],'sha256':ref['sha256'],'unchanged':True})
    historical_link=os.path.relpath(old_path,output)
    lines=['# '+('Current source supplement: reference preservation and cached callable integrity'if lang=='en'else'Suplemento do código atual: preservação de referências e integridade de unidades em cache'),'',
           'Isolated technical candidate;not published,owner-approved or training gold.'if lang=='en'else'Candidato técnico isolado;não publicado,aprovado pelo proprietário ou gold de treinamento.','',
           ('This supplements the [frozen historical chapter]('+historical_link+'). Its original bytes and source cut remain unchanged; this is a new working-source cut, not a rewritten historical chapter.'if lang=='en'else'Este texto complementa o [capítulo histórico congelado]('+historical_link+'). Seus bytes originais e seu recorte de fonte permanecem intactos; este é um novo recorte dos arquivos de trabalho, não uma reescrita histórica.'),'']
    for claim in claims:lines+=[claim[lang]+' '+' '.join('[source:'+ref+']'for ref in claim['evidence_ids']),'']
    lines+=['## '+('FAQ candidates'if lang=='en'else'Candidatos de perguntas frequentes'),'']
    for row in faq:lines+=['<!-- reading-section: faq:'+row['id']+' -->','### '+row[lang+'_q'],'',row[lang+'_a']+' '+' '.join('[source:'+ref+']'for ref in row['evidence_ids']),'']
    lines+=['## '+('Physical source references'if lang=='en'else'Referências físicas da fonte'),'']
    for key,u in units.items():
        target=ROOT/u['source_path'];link=os.path.relpath(target,output)
        lines+=['- [source:'+key+'] ['+u['source_path']+']('+link+'), lines '+str(u['first_line'])+'–'+str(u['last_line'])+'; SHA-256 `'+u['source_sha256']+'`.','']
    text='\n'.join(lines).rstrip()+'\n';dest=output/(lang+'.md');dest.write_text(text);files[str(dest.relative_to(P))]={'bytes':len(text.encode()),'sha256':hashlib.sha256(text.encode()).hexdigest()}
    if old_path.read_bytes()!=old_raw:raise ValueError('historical body changed during supplement creation')
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'claims':claims,'faq':faq,'historical_checks':historical_checks,
        'source_evidence_sha256':hashlib.sha256(pack_path.read_bytes()).hexdigest(),'files':files,'owner_approved':False,
        'training_gold':False,'training_exclusion':True,'published_catalog_written':False,'frozen_v10_modified':False,
        'not_a_source_evolution_classifier_target':True,'source_family':'source-repository:engineering-library',
        'review_status':'AGENT_SOURCE_REVIEWED_OWNER_APPROVAL_PENDING','privacy_license_status':'OWNER_REVIEW_REQUIRED',
        'existing_faq_policy':'Historical questions are preserved. New arbitrary FAQs are not automatically admitted by the narrow conditional FAQ API;do not certify a physical NO-OP from conceptual similarity alone.'}
with(P/'self-chapter-supplement-ledger-v3.json').open('x')as stream:json.dump(record,stream,indent=2,ensure_ascii=False)
print(json.dumps({'claims':len(claims),'faq_pairs':len(faq),'historical_bodies_preserved':True,'files':files}))
