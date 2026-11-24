"""Owned research authoring only; never imports or runs Ruff."""
import datetime
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
REV = '0222c19dd8e0c9a927f2e47bf3774a108431da25'
OUT = P / 'ruff-fix-context-chapter-v1'
assert not OUT.exists(), 'Preserve every prior candidate'
OUT.mkdir()
BASE = 'https://github.com/astral-sh/ruff/blob/' + REV + '/'
cards = [
 ('S1','crates/ruff_linter/src/violation.rs',14,117),
 ('S2','crates/ruff_macros/src/violation_metadata.rs',8,60),
 ('S3','crates/ruff_db/src/diagnostic/mod.rs',60,80),
 ('S4','crates/ruff_db/src/diagnostic/mod.rs',373,402),
 ('S5','crates/ruff_linter/src/message/mod.rs',82,135),
 ('S6','crates/ruff_diagnostics/src/fix.rs',8,55),
 ('S7','crates/ruff_diagnostics/src/fix.rs',57,141),
 ('S8','crates/ruff_diagnostics/src/fix.rs',143,185),
 ('S9','crates/ruff_linter/src/checkers/ast/mod.rs',3889,3933),
 ('S10','crates/ruff_linter/src/settings/fix_safety_table.rs',23,42),
 ('S11','crates/ruff_linter/src/settings/types.rs',125,168),
 ('S12','crates/ruff_linter/src/fix/mod.rs',20,51),
 ('S13','crates/ruff_linter/src/fix/mod.rs',53,128),
 ('S14','crates/ruff_linter/src/fix/mod.rs',130,170),
 ('S15','crates/ruff_linter/src/fix/mod.rs',172,213),
]
# Each group is a paired editorial unit, not a runtime observation or independent task.
groups = [
 ('scope','Scope and evidence','Escopo e evidência',
  'This chapter describes the selected Ruff revision, not every released version. It follows rule metadata, diagnostic storage, fix policy and source reconstruction across separate crates. The repository is development-exposed. All conclusions below are source inferences; no Rust compilation, macro expansion, Ruff execution, upstream test execution or source-file modification was performed.',
  'Este capítulo descreve a revisão selecionada do Ruff, sem generalizar para todas as versões lançadas. Ele acompanha metadados de regras, armazenamento de diagnósticos, política de correções e reconstrução do texto entre crates distintos. O repositório já foi exposto em desenvolvimento. Todas as conclusões abaixo são inferências das fontes; não houve compilação Rust, expansão de macros, execução do Ruff, execução dos testes do projeto ou alteração de seus arquivos.',[]),
 ('metadata','Metadata is a separate interface','Metadados têm uma interface separada',
  '`ViolationMetadata` declares rule identity, explanation, status, category, declaration file and line. The selected `violation_metadata` generator emits those methods and requires status and category metadata, returning a `syn::Error` when either is missing. Its selected output does not attach a `Fix` or implement `FIX_AVAILABILITY`. This is a bounded statement about this generator, not a claim that fixes are absent everywhere.',
  '`ViolationMetadata` declara identidade, explicação, status, categoria, arquivo e linha de declaração da regra. O gerador `violation_metadata` selecionado emite esses métodos e exige metadados de status e categoria, retornando `syn::Error` quando algum falta. Sua saída selecionada não anexa um `Fix` nem implementa `FIX_AVAILABILITY`. A afirmação se limita a esse gerador; não significa que correções estejam ausentes em todo o projeto.',['S1','S2']),
 ('availability','Availability describes a rule','Disponibilidade descreve uma regra',
  '`FixAvailability` has `Sometimes`, `Always` and `None`. `Violation::FIX_AVAILABILITY` defaults to `None`; `fix_title` also defaults to `None`. The blanket implementation for `AlwaysFixableViolation` sets availability to `Always` and wraps its title in `Some`. These declarations do not themselves construct edit contents or store a fix in each diagnostic.',
  '`FixAvailability` possui `Sometimes`, `Always` e `None`. `Violation::FIX_AVAILABILITY` tem padrão `None`; `fix_title` também retorna `None` por padrão. A implementação abrangente para `AlwaysFixableViolation` define disponibilidade `Always` e envolve seu título em `Some`. Essas declarações, por si, não constroem o conteúdo das edições nem armazenam uma correção em cada diagnóstico.',['S1']),
 ('construction','Converting a violation does not attach a fix','Converter uma violação não anexa uma correção',
  '`Violation::into_diagnostic` calls `create_lint_diagnostic` with the fix argument set to `None`, even when the title is present. `Diagnostic::new` initializes its fix to `None`; the helper calls `set_fix` only when its optional fix argument is `Some`. A help title and an attached edit collection are therefore distinct in this selected path.',
  '`Violation::into_diagnostic` chama `create_lint_diagnostic` com argumento de correção `None`, mesmo quando há título. `Diagnostic::new` inicializa sua correção com `None`; o auxiliar chama `set_fix` somente quando seu argumento opcional de correção é `Some`. Portanto, nesse caminho selecionado, um título de ajuda e uma coleção de edições anexada são coisas distintas.',['S1','S3','S5']),
 ('storage','Storage setters have different meanings','Operações de armazenamento têm significados diferentes',
  '`Diagnostic::fix` returns an optional borrowed fix. `set_fix` assigns `Some(fix)` through `Arc::make_mut` and contains a `debug_assert!` requiring a primary span. Do not describe that assertion as an unconditional release-mode validation. `set_optional_fix(None)` does nothing and does not clear an existing fix; `remove_fix` explicitly stores `None`.',
  '`Diagnostic::fix` retorna uma referência opcional à correção. `set_fix` atribui `Some(fix)` por `Arc::make_mut` e contém `debug_assert!` exigindo um span primário. Essa asserção não deve ser descrita como validação incondicional em modo release. `set_optional_fix(None)` não faz nada e não apaga uma correção existente; `remove_fix` armazena `None` explicitamente.',['S4']),
 ('constructors','Constructors label and organize edits','Construtores classificam e organizam edições',
  '`Fix` stores edits, applicability and isolation. The safe, unsafe and display-only constructors assign the corresponding classification and default isolation; constructors accepting multiple edits sort them by start and end. `applicable_edit` and `applicable_edits` accept a classification explicitly. These bodies store data; they do not run the edits or prove that the author selected the correct semantic classification.',
  '`Fix` armazena edições, aplicabilidade e isolamento. Os construtores de correções seguras, inseguras e apenas para exibição atribuem a classificação correspondente e o isolamento padrão; os construtores de múltiplas edições ordenam por início e fim. `applicable_edit` e `applicable_edits` recebem a classificação explicitamente. Esses corpos armazenam dados; não executam as edições nem provam que o autor escolheu a classificação semântica correta.',['S6','S7']),
 ('guard','The AST diagnostic guard adds policy','A guarda de diagnóstico da AST acrescenta política',
  '`DiagnosticGuard::set_fix` first checks `should_fix(self.rule)`. When false it removes the diagnostic fix and returns. Otherwise it resolves applicability using the settings table and attaches the reclassified fix. This is a selected AST-checker path, not proof that every direct `Diagnostic::set_fix` call passes through the same policy.',
  '`DiagnosticGuard::set_fix` consulta primeiro `should_fix(self.rule)`. Quando falso, remove a correção do diagnóstico e retorna. Caso contrário, resolve a aplicabilidade pela tabela de configurações e anexa a correção reclassificada. Esse é um caminho selecionado do verificador de AST; não prova que toda chamada direta a `Diagnostic::set_fix` passe pela mesma política.',['S9']),
 ('fallible','Fallible construction still calls its closure','A construção falível ainda chama sua função',
  '`try_set_fix` invokes `func()` before matching its result. `Ok(fix)` delegates to `set_fix`; `Err` logs a debug message instead. Thus the rule-selection check inside `set_fix` does not establish that the construction closure is skipped. `try_set_optional_fix` additionally leaves the current state unchanged on `Ok(None)`. No observed closure side effects or panic recovery are claimed here.',
  '`try_set_fix` invoca `func()` antes de analisar seu resultado. `Ok(fix)` delega a `set_fix`; `Err` registra uma mensagem de depuração. Logo, a consulta de seleção de regra dentro de `set_fix` não estabelece que a função de construção deixe de ser chamada. `try_set_optional_fix` também mantém o estado atual em `Ok(None)`. Aqui não se afirma observação de efeitos dessa função nem recuperação de pânico.',['S9']),
 ('override','Safety overrides preserve display-only fixes','Sobrescritas de segurança preservam correções apenas para exibição',
  '`FixSafetyTable::resolve_applicability` preserves `DisplayOnly`. For an input classified as `Safe` or `Unsafe`, it consults forced-unsafe first, then forced-safe, otherwise retaining the input. This describes the resolver body; it does not certify that reclassification validates edit semantics or that both sets can actually contain the same rule through normal construction.',
  '`FixSafetyTable::resolve_applicability` preserva `DisplayOnly`. Para uma entrada `Safe` ou `Unsafe`, consulta primeiro a classificação forçada como insegura, depois a forçada como segura e, na ausência delas, mantém a entrada. Isso descreve o corpo do resolvedor; não certifica que a reclassificação valide a semântica das edições nem que os dois conjuntos possam conter a mesma regra pela construção normal.',['S10']),
 ('ordering','Applicability is an ordered threshold','Aplicabilidade usa um limiar ordenado',
  '`Applicability` derives `Ord` and `PartialOrd`, with implicit discriminants in declaration order: `DisplayOnly < Unsafe < Safe`. `Fix::applies` compares the stored classification with the argument using `>=`. The ordering follows the official Rust contract for derived enum ordering, not a local compiler observation. The method alone would admit a display-only fix at a display-only threshold.',
  '`Applicability` deriva `Ord` e `PartialOrd`, com discriminantes implícitos na ordem de declaração: `DisplayOnly < Unsafe < Safe`. `Fix::applies` compara a classificação armazenada com o argumento usando `>=`. A ordenação decorre do contrato oficial do Rust para ordenação derivada de enums, e não de uma observação de compilador local. Isoladamente, o método admitiria uma correção apenas para exibição com limiar de apenas exibição.',['S6','S8']),
 ('domain','The selected caller narrows the threshold domain','O chamador selecionado restringe o domínio do limiar',
  '`UnsafeFixes::required_applicability` returns `Unsafe` for `Enabled`, and `Safe` for both `Disabled` and the default `Hint`. Therefore the selected `fix_file` policy admits safe fixes in all three modes, also unsafe fixes in enabled mode, and no display-only fixes. This is an admission filter; overlap and isolation can still prevent edits from being selected. No global claim about every possible `applies` caller is made.',
  '`UnsafeFixes::required_applicability` retorna `Unsafe` para `Enabled` e `Safe` para `Disabled` e o padrão `Hint`. Assim, a política selecionada de `fix_file` admite correções seguras nos três modos, também inseguras no modo habilitado e nenhuma apenas para exibição. Trata-se de um filtro de admissão; sobreposição e isolamento ainda podem impedir a seleção das edições. Não se generaliza isso para todo chamador possível de `applies`.',['S8','S11','S12']),
 ('result','The selected function constructs a result','A função selecionada constrói um resultado',
  '`fix_file` filters diagnostics with an attached, admissible fix. With none it returns `None`; otherwise it returns `Some(apply_fixes(...))`. `FixResult` contains reconstructed code, fix counts and a source map. Despite its nearby comment mentioning writing to disk, the selected body does not perform a filesystem write. Outer persistence and repeated lint/fix iterations are outside this chapter.',
  '`fix_file` filtra diagnósticos com correção anexada e admitida. Sem nenhum, retorna `None`; caso contrário, retorna `Some(apply_fixes(...))`. `FixResult` contém texto reconstruído, contagens de correções e um mapa de origem. Embora o comentário próximo mencione gravação em disco, o corpo selecionado não faz uma gravação no sistema de arquivos. Persistência externa e iterações de análise e correção ficam fora deste capítulo.',['S12','S13']),
 ('conflicts','Ordering, duplicate edits and conflicts','Ordenação, edições duplicadas e conflitos',
  '`apply_fixes` sorts fixes with `cmp_fix`, including special rule precedence, start position and selected tie breakers. It removes edits already present in the applied-edit set before checking whether a first new edit remains. For a first new edit, it checks isolation group membership and then rejects a start position when `last_pos >= first.start()`. Do not reduce this boundary check to a generic interval-overlap theorem or claim every admitted diagnostic changes the text.',
  '`apply_fixes` ordena correções por `cmp_fix`, incluindo precedência especial de regras, posição inicial e desempates selecionados. Remove edições já presentes no conjunto de edições aplicadas antes de verificar se resta uma primeira edição nova. Para essa primeira edição, verifica o grupo de isolamento e então rejeita a posição inicial quando `last_pos >= first.start()`. Essa condição de fronteira não deve ser reduzida a um teorema genérico de sobreposição de intervalos, nem implica que todo diagnóstico admitido altere o texto.',['S13','S14']),
 ('reservation','Group reservation precedes positional rejection','A reserva do grupo precede a rejeição por posição',
  'For a fix with a new edit and `IsolationLevel::Group(id)`, the code inserts the group ID before checking `last_pos`. A positional rejection afterwards does not remove that ID in the selected body. Thus the source does not support a simplified description saying groups are reserved only after successful edit application. This ordering observation is not an executed counterexample or an assessment of the maintainers’ intended policy.',
  'Para uma correção com edição nova e `IsolationLevel::Group(id)`, o código insere o identificador do grupo antes de consultar `last_pos`. Uma rejeição posterior por posição não remove esse identificador no corpo selecionado. Portanto, a fonte não sustenta uma descrição simplificada segundo a qual os grupos só são reservados após aplicar uma edição com sucesso. Essa observação de ordem não é um contraexemplo executado nem uma avaliação da política pretendida pelos mantenedores.',['S13']),
 ('output','Reconstruction is not semantic verification','Reconstrução não é verificação semântica',
  'For selected edits the implementation appends untouched slices, replacement contents or an empty replacement, records source-map markers and advances `last_pos` to the edit end. After the fix it extends the applied-edit set and increments a diagnostic count; it finally appends the remaining source. Counting a diagnostic is distinct from counting newly emitted edits, including when all its edits were duplicates. These bodies do not establish whole-program correctness of the resulting Python.',
  'Para as edições selecionadas, a implementação acrescenta trechos intactos, conteúdo de substituição ou uma substituição vazia, registra marcadores do mapa de origem e avança `last_pos` até o fim da edição. Depois da correção, amplia o conjunto de edições aplicadas e incrementa uma contagem de diagnóstico; ao final, acrescenta o restante da fonte. Contar um diagnóstico difere de contar novas edições emitidas, inclusive quando todas as suas edições eram duplicadas. Esses corpos não estabelecem a correção do programa Python resultante.',['S13']),
 ('tests','Existing tests and actual observations','Testes existentes e observações efetivas',
  'The selected module contains a `#[cfg(test)]` test module, a helper constructing diagnostics, and an `empty_file` test asserting empty output, zero counts and an empty source map. These are inspected test declarations, not passing test results from this campaign. The actual observations were read-only Git source retrieval and editorial source tracing. A Rust toolchain was not available on the host PATH; no installation or repository build was attempted.',
  'O módulo selecionado contém um módulo de testes `#[cfg(test)]`, um auxiliar que constrói diagnósticos e o teste `empty_file`, que verifica saída vazia, contagens zeradas e mapa de origem vazio. São declarações de testes inspecionadas, e não resultados de aprovação obtidos nesta campanha. As observações efetivas foram recuperação de fontes por Git somente para leitura e acompanhamento editorial das fontes. Não havia ferramenta Rust disponível no PATH do host; não se tentou instalar ferramentas nem compilar o repositório.',['S15']),
]
faqs = [
 ('Does Always mean every diagnostic already has edits?','Always significa que todo diagnóstico já tem edições?',
  'No. The blanket implementation sets rule availability and a title, whereas `into_diagnostic` passes `None` as the fix. An attached fix is separate optional state.',
  'Não. A implementação abrangente define disponibilidade da regra e título, enquanto `into_diagnostic` passa `None` como correção. Uma correção anexada é um estado opcional separado.',['S1','S3','S5']),
 ('Does Safe prove correctness or guarantee application?','Safe prova correção ou garante aplicação?',
  'No. The constructors assign a classification without semantic verification, and the consumer still enforces admission, isolation and positional checks. Classification expresses policy and author intent; it is not an observed correctness proof.',
  'Não. Os construtores atribuem uma classificação sem verificação semântica, e o consumidor ainda verifica admissão, isolamento e posição. A classificação expressa política e intenção do autor; não é prova observada de correção.',['S7','S12','S13']),
 ('Can display-only fixes pass applies?','Correções apenas para exibição podem passar por applies?',
  'The method alone returns true at a `DisplayOnly` threshold. The selected `fix_file` caller obtains only `Safe` or `Unsafe` from `required_applicability`, excluding display-only fixes there. The method domain and caller domain must be distinguished.',
  'O método isolado retorna verdadeiro com limiar `DisplayOnly`. O chamador `fix_file` selecionado obtém somente `Safe` ou `Unsafe` de `required_applicability`, excluindo ali correções apenas para exibição. É necessário distinguir o domínio do método do domínio do chamador.',['S6','S8','S11','S12']),
 ('Does try_set_fix avoid construction when fixing is disabled?','try_set_fix evita a construção quando a correção está desabilitada?',
  'Its selected body does not establish that. It invokes `func()` first and delegates only an `Ok` result to `set_fix`, where the rule-selection check occurs. An error is logged rather than attached as a fix.',
  'O corpo selecionado não estabelece isso. Ele invoca `func()` primeiro e só delega um resultado `Ok` a `set_fix`, onde ocorre a consulta de seleção da regra. Um erro é registrado em vez de ser anexado como correção.',['S9']),
 ('Does a skipped positional conflict leave the group unreserved?','Um conflito de posição ignorado deixa o grupo sem reserva?',
  'Not necessarily in the selected body. When a new edit remains, group insertion precedes the positional check, and that later rejection has no corresponding group removal. This is a source-order observation, not an executed Ruff scenario.',
  'Não necessariamente no corpo selecionado. Quando resta uma edição nova, a inserção do grupo precede a consulta de posição, e essa rejeição posterior não tem remoção correspondente do grupo. É uma observação da ordem na fonte, e não um cenário executado no Ruff.',['S13']),
 ('Did this campaign run fixes, tests or filesystem writes through fix_file?','Esta campanha executou correções, testes ou gravações por fix_file?',
  'No. Source and test bodies were inspected without executing Ruff. The selected `fix_file` body constructs an optional result; it does not itself write a file. No upstream passing-test, macro-expansion, persistence or whole-program semantic claim follows from this review.',
  'Não. Corpos de fontes e testes foram inspecionados sem executar o Ruff. O corpo selecionado de `fix_file` constrói um resultado opcional; não grava um arquivo por si. Esta revisão não sustenta afirmações de testes aprovados, expansão de macros, persistência ou semântica do programa completo.',['S12','S15']),
]
card_data=[]
for ident,path,start,end in cards:
    source=P/'ruff-fix-context-source-v1'/path
    raw=source.read_bytes()
    excerpt='\n'.join(raw.decode().splitlines()[start-1:end])+'\n'
    card_data.append(dict(id=ident,path=path,start=start,end=end,file_sha256=hashlib.sha256(raw).hexdigest(),excerpt_sha256=hashlib.sha256(excerpt.encode()).hexdigest(),excerpt=excerpt,url=f'{BASE}{path}#L{start}-L{end}'))
(OUT/'source-cards.json').write_text(json.dumps(card_data,ensure_ascii=False,indent=2)+'\n')
for lang in ('en','pt'):
    en=lang=='en'
    title='Ruff: from rule fix availability to selected source edits' if en else 'Ruff: da disponibilidade declarada às edições selecionadas'
    chunks=[f'# {title}',f'`astral-sh/ruff` · `{REV}`',
        'Status: CANDIDATE_FOR_SOURCE_REVIEW; not owner-approved, not Gold, not training data.' if en else 'Status: CANDIDATE_FOR_SOURCE_REVIEW; sem aprovação do proprietário, sem Gold, fora dos dados de treinamento.']
    for ident,he,hp,te,tp,refs in groups:
        chunks.extend(['## '+(he if en else hp),te if en else tp])
        if refs:chunks.append(' '.join('['+r+'](#'+r.lower()+')' for r in refs))
    chunks.append('## FAQ')
    for qe,qp,ae,ap,refs in faqs:
        chunks.extend(['### '+(qe if en else qp),ae if en else ap,' '.join('['+r+'](#'+r.lower()+')' for r in refs)])
    chunks.extend(['## '+('Read-only reproduction example' if en else 'Exemplo de reprodução somente para leitura'),
      'The equivalent Git retrieval was executed during source acquisition. Run from the Ruff checkout only to display the pinned source; it does not invoke the program. This is not a Rust example or a test result.' if en else 'A recuperação Git equivalente foi executada na aquisição das fontes. Execute no checkout do Ruff apenas para exibir a fonte fixada; o comando não invoca o programa. Não é exemplo Rust nem resultado de teste.',
      '```sh\ngit -c core.fsmonitor=false show '+REV+':crates/ruff_linter/src/fix/mod.rs\n```',
      '## '+('Source references and rights' if en else 'Referências às fontes e direitos')])
    for c in card_data:chunks.append(f'<a id="{c["id"].lower()}"></a> [{c["id"]}: {c["path"]}:{c["start"]}–{c["end"]}]({c["url"]})')
    chunks.extend([
      '[R1: Rust derived enum ordering](https://doc.rust-lang.org/std/cmp/trait.Ord.html#derivable). '+('Current primary-language reference, not evidence of executing a historical toolchain.' if en else 'Referência primária atual da linguagem; não é evidência de execução de ferramenta histórica.'),
      ('The full root LICENSE, including third-party notices, is retained with the source package. The selected repository uses an MIT root license; no blanket file-level, training or public-publication authorization is inferred. Campaign artifacts remain restricted internal review material.' if en else 'A LICENSE completa da raiz, incluindo avisos de terceiros, foi preservada com as fontes. O repositório selecionado usa licença MIT na raiz; não se infere autorização geral por arquivo, para treinamento ou para publicação pública. Os artefatos da campanha permanecem material interno restrito de revisão.')])
    (OUT/(lang+'.md')).write_text('\n\n'.join(chunks)+'\n')
manifest={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':REV,'status':'CANDIDATE_FOR_SOURCE_REVIEW','method':'manual source-first bilingual authoring; owned formatting script','logical_groups':len(groups)+len(faqs),'faq_pairs':len(faqs),'source_cards':len(cards),'neural_calls':0,'runtime_observations':0,'rust_compilation':False,'owner_approved':False,'training_eligible':False,'files':{q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in OUT.iterdir()}}
(OUT/'candidate-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
