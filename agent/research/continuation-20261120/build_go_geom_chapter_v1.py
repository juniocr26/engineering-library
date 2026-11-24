"""Complete bilingual isolated Go source walkthrough with explicit claim ledger."""
import datetime
import hashlib
import json
from pathlib import Path
import re

P=Path(__file__).resolve().parent
pack_path=P/'go-geom-chapter-evidence-pack-v1.json'
pack=json.loads(pack_path.read_text())
ranges_path=P/'go-geom-chapter-context-ranges-v2.json'
ranges=json.loads(ranges_path.read_text())
REV=pack['revision'];BASE=P/'new-public-sources-v1/twpayne--go-geom'/REV
units={row['unit']['selector']:{'source_path':row['source_path'],'source_sha256':row['source_sha256'],
       'first_line':row['unit']['start_line'],'last_line':row['unit']['end_line'],'quote':row['unit']['quote'],
       'quote_sha256':hashlib.sha256(row['unit']['quote'].encode()).hexdigest(),'complete_callable_or_type':True}for row in pack['units']}
for row in ranges['ranges']:units[row['id']]=dict(row,complete_callable_or_type=False)
claims=[]


def add(identifier,section,en,pt,refs):
    if not refs or any(ref not in units for ref in refs):raise ValueError('unregistered source evidence')
    if re.findall(r'`([^`]+)`',en)!=re.findall(r'`([^`]+)`',pt):raise ValueError('bilingual code identifiers differ:'+identifier)
    claims.append({'id':identifier,'section':section,'en':en,'pt-br':pt,'evidence_ids':refs,
                   'review_status':'AGENT_SOURCE_REVIEWED_CANDIDATE_NOT_OWNER_GOLD','scope':'Written source and explicitly qualified control-flow consequences;no executed module or general runtime guarantee.'})


add('purpose','purpose',
    'This chapter follows the pinned `Point` implementation through its embedded state, coordinate helpers and generated clone path. It separates written copying, direct slice assignment and error propagation instead of treating every accessor or constructor as equivalent.',
    'Este capítulo acompanha a implementação fixada de `Point` pelo estado incorporado, pelos auxiliares de coordenadas e pelo caminho de clonagem gerado. Distingue cópia escrita, atribuição direta de fatia e propagação de erros, sem tratar todo acessor ou construtor como equivalente.',
    ['Point','NewPointFlat','geom0.Coords','Point.Clone'])
add('architecture','architecture',
    '`Point` embeds `geom0`. The latter declares `layout`, `stride`, `flatCoords` and `srid`. The selected constructors and methods read or write that shared representation; a complete package/type check was not performed.',
    '`Point` incorpora `geom0`. Essa estrutura declara `layout`, `stride`, `flatCoords` e `srid`. Os construtores e métodos selecionados leem ou escrevem essa representação compartilhada; não foi realizada uma verificação completa de pacote e tipos.',
    ['Point','geom0','NewPointFlat','Point.SetSRID'])
add('constructor','responsibilities',
    '`NewPointFlat(l, flatCoords)` writes `g.layout = l`, `g.stride = l.Stride()` and `g.flatCoords = flatCoords`, then returns `g`. Its selected body contains direct assignment of the supplied slice and no copying call. This differs from the separate clone-helper path.',
    '`NewPointFlat(l, flatCoords)` escreve `g.layout = l`, `g.stride = l.Stride()` e `g.flatCoords = flatCoords`, e então retorna `g`. O corpo selecionado contém atribuição direta da fatia recebida, sem chamada de cópia. Isso difere do caminho separado dos auxiliares de clonagem.',
    ['NewPointFlat','Point.Clone','deriveClonePoint'])
add('new-and-empty','responsibilities',
    '`NewPoint` passes `make([]float64, l.Stride())` to `NewPointFlat`. `NewPointEmpty` passes `nil` to that constructor. These are different written constructor inputs; no sample allocation or empty-point operation was executed here.',
    '`NewPoint` passa `make([]float64, l.Stride())` para `NewPointFlat`. `NewPointEmpty` passa `nil` para esse construtor. São entradas distintas nos construtores escritos; nenhuma alocação de exemplo ou operação com ponto vazio foi executada aqui.',
    ['NewPoint','NewPointEmpty','NewPointFlat'])
add('generated-dependency','dependencies',
    '`Point.Clone` returns `deriveClonePoint(g)`. The generated source then contains a `nil` check, `new(Point)` and `deriveDeepCopy_6(dst, src)`. That helper calls `deriveDeepCopy_11` for the embedded `geom0`. The generator directive names `derived.gen.go`; the generator was not run and its executable/version was not verified.',
    '`Point.Clone` retorna `deriveClonePoint(g)`. O código gerado contém então uma verificação de `nil`, `new(Point)` e `deriveDeepCopy_6(dst, src)`. Esse auxiliar chama `deriveDeepCopy_11` para a estrutura incorporada `geom0`. A diretiva do gerador nomeia `derived.gen.go`; o gerador não foi executado e seu executável e sua versão não foram verificados.',
    ['Point.Clone','deriveClonePoint','deriveDeepCopy_6','package-and-generation'])
add('copy-path','dependencies',
    '`deriveDeepCopy_11` assigns `layout`, `stride` and `srid`, distinguishes `nil` coordinate slices, and contains resizing/allocation branches followed by `copy(dst.flatCoords, src.flatCoords)`. This is concrete helper evidence beyond a clone comment; it is not a measured concurrent-safety or full-package binding guarantee.',
    '`deriveDeepCopy_11` atribui `layout`, `stride` e `srid`, distingue fatias de coordenadas `nil` e contém ramificações de redimensionamento e alocação seguidas de `copy(dst.flatCoords, src.flatCoords)`. Isso fornece evidência concreta do auxiliar além de um comentário de clonagem; não é uma garantia medida de segurança concorrente ou de vínculo completo do pacote.',
    ['deriveDeepCopy_11','deriveDeepCopy_6'])
add('configuration','configuration',
    'The module declaration is `github.com/twpayne/go-geom` and the recorded Go directive is `go 1.26.3`. `Layout.Stride` writes returns 0, 2, 3, 3 and 4 for `NoLayout`, `XY`, `XYZ`, `XYM` and `XYZM`, respectively; the default returns `int(l)`. These source values do not validate arbitrary caller-provided layouts.',
    'A declaração do módulo é `github.com/twpayne/go-geom` e a diretiva Go registrada é `go 1.26.3`. `Layout.Stride` escreve retornos 0, 2, 3, 3 e 4 para `NoLayout`, `XY`, `XYZ`, `XYM` e `XYZM`, respectivamente; o caso padrão retorna `int(l)`. Esses valores no código não validam layouts arbitrários recebidos do chamador.',
    ['module-toolchain','Layout.Stride','layout-constants'])
add('coordinate-views','inputs_outputs',
    '`geom0.FlatCoords` directly returns `g.flatCoords`. `geom0.Coords` instead calls `inflate0(g.flatCoords, 0, len(g.flatCoords), g.stride)`; that helper checks its offset/stride/end relation and then contains `make`, `copy` and a return of the new local slice. The two written paths should not be documented as the same copying contract.',
    '`geom0.FlatCoords` retorna diretamente `g.flatCoords`. Já `geom0.Coords` chama `inflate0(g.flatCoords, 0, len(g.flatCoords), g.stride)`; esse auxiliar verifica a relação entre deslocamento, passo e limite, e então contém `make`, `copy` e o retorno da nova fatia local. Os dois caminhos escritos não devem ser documentados como o mesmo contrato de cópia.',
    ['geom0.FlatCoords','geom0.Coords','inflate0'])
add('setcoords-error','error_handling',
    '`Point.SetCoords` calls `g.setCoords(coords)` and returns `nil, err` on error or `g, nil` otherwise. The delegated `geom0.setCoords` first assigns both `g.flatCoords` and `err` from `deflate0(nil, coords0, g.stride)`. On its written length-mismatch branch, `deflate0` returns `nil` with `ErrStrideMismatch`. Thus the shown error route includes assignment of that returned value to the field; the selected code does not encode rollback to the previous slice.',
    '`Point.SetCoords` chama `g.setCoords(coords)` e retorna `nil, err` no erro ou `g, nil` no outro caso. O método delegado `geom0.setCoords` primeiro atribui tanto `g.flatCoords` quanto `err` a partir de `deflate0(nil, coords0, g.stride)`. Na ramificação escrita de incompatibilidade de comprimento, `deflate0` retorna `nil` com `ErrStrideMismatch`. Assim, o caminho de erro mostrado inclui a atribuição desse valor retornado ao campo; o código selecionado não codifica rollback para a fatia anterior.',
    ['Point.SetCoords','geom0.setCoords','deflate0','ErrStrideMismatch'])
add('panic-paths','error_handling',
    '`Point.MustSetCoords` passes the `SetCoords` result to `Must`; that helper contains `panic(err)` when its error argument is not `nil`. Separately, `inflate0` contains `panic("geom: stride mismatch")` when its offset/stride/end relation fails. These are different local panic routes, not proof that every geometry error becomes the same exception or return value.',
    '`Point.MustSetCoords` passa o resultado de `SetCoords` para `Must`; esse auxiliar contém `panic(err)` quando seu argumento de erro não é `nil`. Separadamente, `inflate0` contém `panic("geom: stride mismatch")` quando falha a relação entre deslocamento, passo e limite. São caminhos locais distintos de panic, sem constituir prova de que todo erro de geometria vira a mesma exceção ou valor retornado.',
    ['Point.MustSetCoords','Must','inflate0'])
add('srid','responsibilities',
    '`Point.SetSRID` writes `g.srid = srid` and returns `g`. The selected setter contains no validation branch; it does not establish the validity of an SRID or a coordinate reference system.',
    '`Point.SetSRID` escreve `g.srid = srid` e retorna `g`. O setter selecionado não contém ramificação de validação; ele não estabelece a validade de um SRID ou de um sistema de referência de coordenadas.',
    ['Point.SetSRID'])
add('limits','limitations',
    'The source pack includes complete selected declarations and separate explicit metadata ranges. It does not establish full build selection, dependency resolution, runtime identity, race freedom, thread safety, generator reproducibility or Windows execution. Illustrative examples and commands below were not compiled or executed; no output or successful module installation is claimed.',
    'O conjunto de código inclui declarações selecionadas completas e intervalos explícitos separados de metadados. Não estabelece seleção completa de build, resolução de dependências, identidade em execução, ausência de condições de corrida, segurança entre threads, reprodutibilidade do gerador ou execução no Windows. Os exemplos e comandos ilustrativos abaixo não foram compilados nem executados; nenhuma saída ou instalação bem-sucedida do módulo é afirmada.',
    ['package-and-generation','module-toolchain','deriveClonePoint','deriveDeepCopy_11'])
faq_specs=[('input-copy','Does the selected flat constructor copy its input?','O construtor selecionado de coordenadas planas copia sua entrada?','constructor'),
('accessor-copy','Do both coordinate accessors show the same copying path?','Os dois acessores de coordenadas mostram o mesmo caminho de cópia?','coordinate-views'),
('error-rollback','Does the shown coordinate error route preserve the previous slice by rollback?','O caminho de erro de coordenadas mostrado preserva a fatia anterior por rollback?','setcoords-error'),
('clone-evidence','What evidence supports the clone path beyond its comment?','Que evidência sustenta o caminho de clonagem além de seu comentário?','copy-path'),
('panic-owner','Where do the selected panic routes appear?','Onde aparecem os caminhos de panic selecionados?','panic-paths'),
('empty-input','What does the empty constructor pass to the flat constructor?','O que o construtor vazio passa para o construtor de coordenadas planas?','new-and-empty'),
('srid-validation','Does the selected SRID setter validate the identifier?','O setter de SRID selecionado valida o identificador?','srid')]
byid={c['id']:c for c in claims};faq=[]
for i,en,pt,claim in faq_specs:faq.append({'id':i,'en_q':en,'pt-br_q':pt,'claim_id':claim,'en_a':byid[claim]['en'],'pt-br_a':byid[claim]['pt-br'],'evidence_ids':byid[claim]['evidence_ids']})
example='''package main

import "github.com/twpayne/go-geom"

func main() {
    p := geom.NewPointFlat(geom.XY, []float64{1, 2})
    q := p.Clone()
    if _, err := q.SetCoords(geom.Coord{3, 4}); err != nil {
        panic(err)
    }
}'''
# Coord declaration is outside the current unit pack; use the parameter's accepted
# slice syntax instead of silently claiming an uncited named-type construction.
example=example.replace('geom.Coord{3, 4}', '[]float64{3, 4}')
command='go doc github.com/twpayne/go-geom.Point'
diagram='''flowchart LR
    A["Point.Clone"] --> B["deriveClonePoint"]
    B --> C["deriveDeepCopy_6"]
    C --> D["deriveDeepCopy_11"]
    E["Point.SetCoords"] --> F["geom0.setCoords"]
    F --> G["deflate0"]
    H["geom0.Coords"] --> I["inflate0"]'''
headers={'purpose':('Purpose','Propósito'),'architecture':('Architecture','Arquitetura'),'responsibilities':('Responsibilities','Responsabilidades'),
'dependencies':('Dependencies and generated helpers','Dependências e auxiliares gerados'),'configuration':('Configuration','Configuração'),
'inputs_outputs':('Inputs and outputs','Entradas e saídas'),'error_handling':('Errors and state changes','Erros e mudanças de estado'),
'examples':('Illustrative example','Exemplo ilustrativo'),'commands':('Illustrative command','Comando ilustrativo'),
'source_table':('Source map','Mapa do código'),'diagram':('Written helper relationships','Relações escritas entre auxiliares'),
'faq':('FAQ','Perguntas frequentes'),'limitations':('Limitations','Limitações'),'citations':('Physical source citations','Citações físicas do código')}
out=P/'go-geom-chapter-candidates-v1';out.mkdir(exist_ok=False);files={}
for lang,col in [('en',0),('pt-br',1)]:
    title='Point constructors, coordinate state and generated copying'if lang=='en'else'Construtores de Point, estado das coordenadas e cópia gerada'
    lines=['# '+title,'','Research candidate;not published,owner-approved or training gold.'if lang=='en'else'Candidato de pesquisa;não publicado,aprovado pelo proprietário ou gold de treinamento.','','Revision: `'+REV+'`.','']
    for section,pair in headers.items():
        lines+=['## '+pair[col],'']
        for c in claims:
            if c['section']==section:lines+=[c[lang]+' '+' '.join('[source:'+r+']'for r in c['evidence_ids']),'']
        if section in ['examples','commands']:
            lines+=['Illustrative only;not compiled or executed,no output claimed.'if lang=='en'else'Apenas ilustrativo;não compilado nem executado,sem saída afirmada.','','```'+('go'if section=='examples'else'sh'),example if section=='examples'else command,'```','','[source:module-toolchain] [source:layout-constants] [source:NewPointFlat] [source:Point.Clone] [source:Point.SetCoords]','']
        if section=='source_table':
            lines+=['| Unit | File |','|---|---|']+['| `'+name+'` | `'+units[name]['source_path']+'` |'for name in ['Point','geom0','Layout.Stride','Point.SetCoords','deflate0','Point.Clone','deriveClonePoint','deriveDeepCopy_6','deriveDeepCopy_11']]+['']
        if section=='diagram':lines+=['Written call relationships;not a measured execution trace.'if lang=='en'else'Relações de chamadas escritas;sem representar rastreamento de execução medido.','','```mermaid',diagram,'```','','[source:Point.Clone] [source:deriveClonePoint] [source:deriveDeepCopy_6] [source:Point.SetCoords] [source:geom0.setCoords] [source:geom0.Coords]','']
        if section=='faq':
            for item in faq:lines+=['### '+item[lang+'_q'],'',item[lang+'_a']+' '+' '.join('[source:'+r+']'for r in item['evidence_ids']),'']
        if section=='citations':
            for name,u in units.items():
                url='https://github.com/twpayne/go-geom/blob/'+REV+'/'+u['source_path']+'#L'+str(u['first_line'])+'-L'+str(u['last_line'])
                lines+=['- [source:'+name+'] ['+u['source_path']+':'+str(u['first_line'])+'–'+str(u['last_line'])+']('+url+'); SHA-256 `'+u['source_sha256']+'`.','']
    text='\n'.join(lines).rstrip()+'\n';path=out/(lang+'.md');path.write_text(text);files[str(path.relative_to(P))]={'sha256':hashlib.sha256(text.encode()).hexdigest(),'bytes':len(text.encode())}
ledger={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':REV,'claims':claims,'faq':faq,'units':units,'files':files,
        'source_pack_sha256':hashlib.sha256(pack_path.read_bytes()).hexdigest(),'range_pack_sha256':hashlib.sha256(ranges_path.read_bytes()).hexdigest(),
        'whole_source_units':21,'extra_explicit_ranges':3,'source_quote_bytes':sum(len(u['quote'].encode())for u in units.values()),
        'owner_approved':False,'training_gold':False,'training_exclusion':True,'model_calls':0,
        'faq_overlap':'Seven answers reuse chapter claims;not seven independent targets.','runtime_or_type_verification':False}
with(P/'go-geom-chapter-ledger-v1.json').open('x')as stream:json.dump(ledger,stream,indent=2,ensure_ascii=False)
print(json.dumps({'claims':len(claims),'faq_pairs':len(faq),'source_quote_bytes':ledger['source_quote_bytes'],'files':files}))
