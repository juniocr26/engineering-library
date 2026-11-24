"""Own research authoring; Ruff sources remain inert text."""
from pathlib import Path
import json
import datetime
import hashlib
import re
from collections import Counter

P = Path(__file__).resolve().parent
OUT = P / 'ruff-fix-policy-maintenance-note-v1'
assert not OUT.exists()
OUT.mkdir()
BEFORE = '47a28e3a2e2cfcc711f6f68eb7267731478e4a81'
AFTER = '0e1bf0d2f6bf100ec93f164efcd98514fb12b348'
groups = [
 ('scope', 'A real revision, with bounded conclusions', 'Uma revisão real, com conclusões delimitadas',
  'This manually reviewed maintenance note compares a local parent/child revision of development-exposed Ruff. The commit changes ten files; the preserved source packet contains eleven selected files at each revision. Five changed dependency files were read alongside unchanged fix-policy files. No Rust compiler, generated macro output, Ruff application, upstream tests, linker or binary-size experiment was executed. The EN/PT clauses below are authored after inspection, not blind predictions or an autonomous maintenance-agent result.',
  'Esta nota de manutenção revisada manualmente compara uma revisão local e sua revisão anterior no Ruff já exposto em desenvolvimento. O commit muda dez arquivos; o pacote preservado contém onze arquivos selecionados em cada revisão. Cinco dependências alteradas foram lidas junto aos arquivos inalterados de política de correções. Não houve execução de compilador Rust, saída gerada de macros, aplicação Ruff, testes do projeto, vinculador ou experimento de tamanho de binário. As cláusulas EN/PT abaixo foram escritas após a inspeção; não são previsões cegas nem resultado de um agente autônomo de manutenção.'),
 ('explain', 'The explanation interface changes', 'A interface da explicação muda',
  'Before: `ViolationMetadata::explain` returns `Option<&\'static str>`. After: it returns `&\'static str`. The selected metadata generator changes from wrapping the collected docs in `Some` to emitting the docs directly, and the generated `Rule::explanation` signature changes correspondingly. A clause documenting the optional return type needs modification for the after revision. This is a source-level interface change, not an observed downstream compile failure.',
  'Antes: `ViolationMetadata::explain` retorna `Option<&\'static str>`. Depois: retorna `&\'static str`. O gerador de metadados selecionado deixa de envolver a documentação coletada em `Some` e passa a emiti-la diretamente, enquanto a assinatura gerada de `Rule::explanation` muda de forma correspondente. Uma cláusula que documente o retorno opcional precisa ser modificada para a revisão posterior. É uma mudança de interface na fonte, e não uma falha de compilação observada em um consumidor.'),
 ('url', 'URL construction no longer consults explanation', 'A construção da URL deixa de consultar a explicação',
  'Before: `Rule::url` returns `Option<String>` and constructs the URL conditionally on `self.explanation().is_some()`. After: it returns `String` using the same homepage/rule-name formatting pattern without that explanation call. The diagnostic helper correspondingly changes from passing `rule.url()` to passing `Some(rule.url())`. The optional storage API is not shown becoming mandatory. The source comment gives avoiding retention of documentation strings as motivation; this campaign did not measure allocation, linking, binary size or speed.',
  'Antes: `Rule::url` retorna `Option<String>` e constrói a URL sob a condição `self.explanation().is_some()`. Depois: retorna `String` usando o mesmo padrão de formatação com página inicial e nome da regra, sem consultar a explicação. O auxiliar de diagnóstico muda de forma correspondente: deixa de passar `rule.url()` e passa a fornecer `Some(rule.url())`. Não se demonstrou que a API de armazenamento opcional tenha se tornado obrigatória. O comentário da fonte aponta evitar a retenção de textos de documentação como motivação; esta campanha não mediu alocação, vinculação, tamanho de binário ou velocidade.'),
 ('nonempty', 'A string return type is not a nonempty-content proof', 'Retornar texto não prova conteúdo não vazio',
  'The inspected `get_docs` implementation starts with an empty string, appends recognized doc attributes and returns the accumulated string. With no such attributes it contains no selected-body rejection of an empty result. Before, the selected generator already wrapped that string in `Some`, which can still contain an empty string. The registry test changes from checking `is_some()` to checking `!trim().is_empty()`. That strengthens the inspected assertion about content, but the test was not executed and does not establish that all current rule documentation passed.',
  'A implementação de `get_docs` inspecionada começa com texto vazio, acrescenta atributos de documentação reconhecidos e retorna o texto acumulado. Sem esses atributos, o corpo selecionado não rejeita um resultado vazio. Antes, o gerador selecionado já envolvia esse texto em `Some`, que ainda pode conter texto vazio. O teste do registro deixa de consultar `is_some()` e passa a verificar `!trim().is_empty()`. Isso fortalece a asserção inspecionada sobre o conteúdo, mas o teste não foi executado e não estabelece que a documentação de todas as regras atuais tenha passado.'),
 ('fix', 'Unchanged fix-policy bodies support a local retained clause', 'Corpos inalterados de política sustentam uma cláusula local mantida',
  'The complete files defining `Fix`, `fix_file`/`apply_fixes` and `FixSafetyTable` are byte-identical across this pair. The settings file is also byte-identical across the pair; its selected `UnsafeFixes` enum/implementation additionally matches the later HEAD snapshot even though that entire later settings file differs. Thus the source-scoped clause about `Enabled` selecting `Unsafe` and `Disabled`/`Hint` selecting `Safe` can remain textually unchanged for this pair. This does not prove whole-program behavioral equivalence or unchanged call reachability.',
  'Os arquivos completos que definem `Fix`, `fix_file`/`apply_fixes` e `FixSafetyTable` são idênticos byte a byte entre essas revisões. O arquivo de configurações também é idêntico entre elas; seu enum e implementação selecionados de `UnsafeFixes` correspondem ainda à captura posterior de HEAD, embora o arquivo completo posterior de configurações seja diferente. Portanto, a cláusula delimitada às fontes sobre `Enabled` selecionar `Unsafe` e `Disabled`/`Hint` selecionarem `Safe` pode manter o texto nesse par. Isso não prova equivalência comportamental do programa inteiro nem alcance inalterado das chamadas.'),
 ('action', 'Maintenance actions depend on the exact clause', 'Ações de manutenção dependem da cláusula exata',
  'For an explanation-return or URL-return signature clause, the action is `MODIFY`. For the selected fix-threshold body description, the semantic text action is `NO-OP` within this source-only scope. If a document must cite the new target revision, its source pin and bound evidence must still be updated even for retained text. The entire chapter must not be labelled unchanged solely because selected fix files match. No `ADD` or `REMOVE` claim, actual agent decision or independent score is inferred from these authored clauses.',
  'Para uma cláusula sobre a assinatura de retorno da explicação ou da URL, a ação é `MODIFY`. Para a descrição do corpo selecionado do limiar de correções, a ação sobre o texto semântico é `NO-OP` dentro desse escopo limitado às fontes. Se o documento deve citar a nova revisão-alvo, sua referência de revisão e as evidências vinculadas ainda precisam mudar mesmo quando o texto permanece. O capítulo inteiro não deve ser classificado como inalterado somente porque arquivos selecionados de correções coincidem. Não se infere dessas cláusulas escritas nenhuma afirmação de `ADD` ou `REMOVE`, decisão efetiva de agente ou pontuação independente.'),
]
faqs = [
 ('Did the before generator necessarily return None for missing docs?', 'O gerador anterior necessariamente retornava None quando faltava documentação?',
  'No. Its selected output wraps the collected string in `Some`; the collection body can produce an empty string. Optionality and nonempty content are different properties.',
  'Não. Sua saída selecionada envolve o texto coletado em `Some`; o corpo de coleta pode produzir texto vazio. Opcionalidade e conteúdo não vazio são propriedades diferentes.'),
 ('Does the new string signature guarantee all docs are nonempty?', 'A nova assinatura de texto garante que toda documentação seja não vazia?',
  'No. The return type alone does not express nonempty content. The strengthened registry test checks trimmed content, but this campaign only inspected its declaration.',
  'Não. O tipo de retorno isolado não expressa conteúdo não vazio. O teste fortalecido do registro verifica conteúdo após remover espaços das extremidades, mas esta campanha apenas inspecionou sua declaração.'),
 ('Did diagnostic URL storage lose its optional type?', 'O armazenamento da URL do diagnóstico perdeu seu tipo opcional?',
  'That does not follow. The selected caller now explicitly wraps the returned URL in `Some`. This note does not establish a storage-schema migration or execute a consumer.',
  'Isso não decorre da mudança. O chamador selecionado agora envolve explicitamente a URL retornada em `Some`. Esta nota não estabelece migração do esquema de armazenamento nem executa um consumidor.'),
 ('Did the fix application files change in this commit?', 'Os arquivos de aplicação de correções mudaram neste commit?',
  'The selected complete `fix.rs`, `fix/mod.rs` and safety-table files did not change. Other files did, including metadata interfaces and consumers; local equality is not whole-commit equivalence.',
  'Os arquivos completos selecionados `fix.rs`, `fix/mod.rs` e da tabela de segurança não mudaram. Outros arquivos mudaram, incluindo interfaces de metadados e consumidores; igualdade local não é equivalência do commit inteiro.'),
 ('Can unchanged prose keep stale source pins?', 'Texto inalterado pode manter referências desatualizadas à revisão?',
  'Not when the documentation contract requires the new revision. Retaining a semantic clause and refreshing its provenance are separate maintenance decisions; hashes must bind the actual target bytes.',
  'Não quando o contrato de documentação exige a nova revisão. Manter uma cláusula semântica e atualizar sua proveniência são decisões separadas de manutenção; os hashes precisam vincular os bytes efetivos do alvo.'),
 ('Was the claimed documentation-retention benefit measured?', 'O benefício alegado sobre retenção de documentação foi medido?',
  'No. The changed call path and its source comment were inspected. There was no build, linker observation, binary comparison or benchmark; the intended benefit remains unmeasured here.',
  'Não. O caminho de chamada alterado e seu comentário foram inspecionados. Não houve compilação, observação do vinculador, comparação de binários ou benchmark; o benefício pretendido permanece sem medição aqui.'),
]
for lang in ['en','pt']:
    en=lang=='en'
    chunks=['# '+('Ruff maintenance: explanation presence, content and fix-policy boundaries' if en else 'Manutenção do Ruff: presença da explicação, conteúdo e limites da política de correções'),
       '`astral-sh/ruff`: `'+BEFORE+'` → `'+AFTER+'`',
       'READY_FOR_OWNER_REVIEW · source-only · no owner approval, Gold, neural inference or training.' if en else 'READY_FOR_OWNER_REVIEW · somente fontes · sem aprovação do proprietário, Gold, inferência neural ou treinamento.']
    for ident,he,hp,te,tp in groups:chunks.extend(['## '+(he if en else hp),te if en else tp])
    chunks.append('## FAQ')
    for qe,qp,ae,ap in faqs:chunks.extend(['### '+(qe if en else qp),ae if en else ap])
    chunks.extend(['## '+('Evidence and reproduction' if en else 'Evidência e reprodução'),
      'Read-only Git retrieval and diff inspection were performed. The source-cards JSON preserves eighteen file-bound excerpts with native line ranges; the manifest preserves twenty-two selected source files, including both full root licenses and third-party notices. The commands below inspect the interface change and do not run Ruff.' if en else 'Foram realizadas recuperação Git somente para leitura e inspeção de diferenças. O JSON de trechos preserva dezoito excertos vinculados a arquivos e intervalos de linhas nativas; o manifesto preserva vinte e dois arquivos selecionados, incluindo ambas as licenças completas da raiz e avisos de terceiros. Os comandos abaixo inspecionam a mudança de interface e não executam o Ruff.',
      '```sh\ngit -c core.fsmonitor=false diff --no-ext-diff --no-renames '+BEFORE+' '+AFTER+' -- crates/ruff_linter/src/violation.rs\n```'])
    for role,rev in [('before',BEFORE),('after',AFTER)]:
        for path in ['crates/ruff_linter/src/violation.rs','crates/ruff_macros/src/violation_metadata.rs','crates/ruff_linter/src/registry.rs','crates/ruff_macros/src/map_codes.rs','crates/ruff_linter/src/message/mod.rs']:
            chunks.append(f'[{role}: {path}](https://github.com/astral-sh/ruff/blob/{rev}/{path})')
    chunks.append('Internal review artifact; rights and independence remain restricted as recorded in the campaign.' if en else 'Artefato interno de revisão; direitos e independência permanecem restritos conforme os registros da campanha.')
    (OUT/(lang+'.md')).write_text('\n\n'.join(chunks)+'\n')
en=(OUT/'en.md').read_text();pt=(OUT/'pt.md').read_text()
assert Counter(re.findall(r'`([^`\n]+)`',en))==Counter(re.findall(r'`([^`\n]+)`',pt))
manifest={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'READY_FOR_OWNER_REVIEW','before':BEFORE,'after':AFTER,'groups':len(groups)+len(faqs),'faq_pairs':len(faqs),'literal_occurrences_per_language':len(re.findall(r'`([^`\n]+)`',en)),'source_cards':'ruff-fix-policy-revision-source-cards-v1.json','source_manifest':'ruff-fix-policy-revision-source-manifest-v1.json','files':{q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in OUT.iterdir()},'population':'Separate paired maintenance note; not a new full architecture chapter, blind task, actual agent lifecycle result or model output.','owner_approved':False,'training_eligible':False,'neural_calls':0,'rust_execution':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
