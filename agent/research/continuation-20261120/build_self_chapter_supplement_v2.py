"""Append-only technical selfchapter candidate, preserving frozen historical text."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
pack_path=P/'self-chapter-supplement-evidence-v2.json';pack=json.loads(pack_path.read_text())
units={u['id']:u for u in pack['units']};claims=[]


def add(i,en,pt,refs):
    if re.findall(r'`([^`]+)`',en)!=re.findall(r'`([^`]+)`',pt):raise ValueError('bilingual code identifiers differ:'+i)
    if any(ref not in units for ref in refs):raise ValueError('unregistered source unit')
    claims.append({'id':i,'en':en,'pt-br':pt,'evidence_ids':refs,'scope':'SOURCE_REVIEWED_TECHNICAL_SUPPLEMENT_NOT_GENERAL_SEMANTIC_CERTIFICATE'})


add('current-cut',
    'The current caller source declares `VERSION = \'1.9.42\'`. The inspected planner, maintenance and optional helper declare `0.3.6`, `0.1.5` and `0.1.3`, respectively. Their exact working-file hashes identify this cut; the observed Git HEAD alone does not assert that the new caller bytes are committed.',
    'O código atual do chamador declara `VERSION = \'1.9.42\'`. O planejador, a manutenção e o auxiliar opcional inspecionados declaram `0.3.6`, `0.1.5` e `0.1.3`, respectivamente. Os hashes exatos dos arquivos de trabalho identificam este recorte; o HEAD Git observado, isoladamente, não afirma que os novos bytes do chamador estão commitados.',
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
    ['E3','E4'])
add('limits',
    'This refusal is conditional on AST metadata being present in the card. It is not a general validator for prose without quoted source identifiers, code keys, all exception expressions, execution order or factual equivalence. Citation integrity, identifier preservation and full semantic review are separate obligations.',
    'Essa recusa depende da presença de metadados AST no cartão. Não é um validador geral para prosa sem identificadores da fonte entre crases, chaves de código, todas as expressões de exceção, ordem de execução ou equivalência factual. Integridade de citações, preservação de identificadores e revisão semântica completa são obrigações separadas.',
    ['E1','E3','E4','E5'])
faq=[{'id':'quoted-exception-preservation','en_q':'Do correct source citations alone prove that exception names were preserved in translation?',
      'pt-br_q':'Citações corretas da fonte, sozinhas, provam que os nomes de exceções foram preservados na tradução?',
      'answer_claim':'bounded-refusal','proposal':'ADD_SOURCE_REVIEWED_SUPPLEMENT_CANDIDATE'},
     {'id':'ast-card-coverage','en_q':'Does the new refusal cover every evidence mode and every kind of prose?',
      'pt-br_q':'A nova recusa cobre todos os modos de evidência e todos os tipos de prosa?',
      'answer_claim':'limits','proposal':'ADD_SOURCE_REVIEWED_SUPPLEMENT_CANDIDATE'}]
lookup={c['id']:c for c in claims}
for row in faq:
    row.update({'pt-br_a':lookup[row['answer_claim']]['pt-br']},en_a=lookup[row['answer_claim']]['en'],
               evidence_ids=lookup[row['answer_claim']]['evidence_ids'],owner_approved=False,training_gold=False,
               automatic_faq_engine_admitted=False,not_a_source_evolution_classifier_target=True)
output=P/'self-chapter-supplement-v1';output.mkdir(exist_ok=False);files={};historical_checks=[]
for lang in ['en','pt-br']:
    old=pack['historical_documents'][lang];ref=old['candidate_documentation_ref'];old_path=ROOT/ref['path'];old_raw=old_path.read_bytes()
    if hashlib.sha256(old_raw).hexdigest()!=ref['sha256']:raise ValueError('historical chapter drift')
    historical_checks.append({'language':lang,'path':ref['path'],'sha256':ref['sha256'],'unchanged':True})
    historical_link=os.path.relpath(old_path,output)
    lines=['# '+('Current source supplement: quoted exception identifiers'if lang=='en'else'Suplemento do código atual: identificadores de exceção entre crases'),'',
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
with(P/'self-chapter-supplement-ledger-v1.json').open('x')as stream:json.dump(record,stream,indent=2,ensure_ascii=False)
print(json.dumps({'claims':len(claims),'faq_pairs':len(faq),'historical_bodies_preserved':True,'files':files}))
