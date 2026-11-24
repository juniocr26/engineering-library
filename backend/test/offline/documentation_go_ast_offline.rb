require 'bundler/setup'
require 'minitest/autorun'
require 'tmpdir'
require 'fileutils'
require_relative '../../lib/documentation/go_ast_command'

class DocumentationGoAstTest < Minitest::Test
  class StoredResponse < Documentation::GoAstCommand
    attr_reader :inferences
    def infer(files, _skills)
      @inferences = (@inferences || 0) + 1
      facts = evidence_cards(files).map do |id, card|
        symbol = card.fetch('qualified_symbol')
        { 'evidence_id' => id,
          'en' => "The selected `#{symbol}` method returns the literal `7`. This description is limited to the supplied source; type checking, imports and runtime behavior were not verified.",
          'pt-br' => "O método selecionado `#{symbol}` retorna o literal `7`. Esta descrição se limita à fonte fornecida; tipos, importações e comportamento em execução não foram verificados." }
      end
      { 'result' => { 'facts' => facts }, 'request' => { 'stored_test_response' => true }, 'response' => {} }
    end
    def call_model(_body)
      raise 'unexpected actual model transport'
    end
  end

  def setup
    @root = Dir.mktmpdir('documentation-go-ast-')
    @source = File.join(@root, 'project')
    @library = File.join(@root, 'library')
    FileUtils.mkdir_p([File.join(@source, 'docs'), @library])
    @text = "package p\nfunc (w *Worker) F() int { return 7 }\n"
    File.write(File.join(@source, 'main.go'), @text)
    agent = File.expand_path('../../../agent', __dir__)
    agent = '/agent' unless File.directory?(agent)
    @env = { 'DOCS_LIBRARY' => @library, 'DOCS_SOURCES' => @root, 'DOCS_AGENT' => agent, 'DOCS_CONTEXT' => 'baseline' }
    @project = { 'slug' => 'go-ast', 'source' => @source, 'destination' => File.join(@source, 'docs'),
      'lifecycle' => 'temporary', 'files' => ['main.go'], 'units' => { 'main.go' => ['Worker.F'] } }
    @config = File.join(@root, 'config.json')
  end

  def teardown
    FileUtils.remove_entry(@root)
  end

  def execute(command = StoredResponse.new(@env))
    File.write(@config, JSON.generate('projects' => [@project]))
    status = nil
    out, err = capture_io { status = command.run(['--config', @config]) }
    [status, out, err]
  end

  def documents
    [File.join(@library, '.evaluations/go-ast'), File.join(@source, 'docs')].flat_map do |root|
      %w[en pt-br].map { |lang| File.join(root, lang, Documentation::Command::DOCUMENT) }
    end
  end

  def test_real_packaged_parser_preserves_exact_method_card_and_provenance
    card = Documentation::GoAstCommand.new(@env).source_units('main.go', @text, ['Worker.F']).fetch('Worker.F')
    assert_equal 2, card['line']
    assert_equal @text.lines.last, card['quote']
    assert_equal 'F', card['symbol']
    assert_equal 'p.Worker.F', card['qualified_symbol']
    assert_equal 'p.Worker.F', card['required_symbol']
    assert_equal true, card['complete_unit']
    assert_match(/syntax only/, card['preparation'])
    assert_match(/\A[0-9a-f]{64}\z/, card['syntax_producer']['binary_sha256'])
  end

  def test_pipeline_writes_and_noop_preserves_bytes_and_mtimes_without_second_inference
    command = StoredResponse.new(@env)
    status, log, = execute(command)
    assert_equal 0, status, log
    assert_equal 1, command.inferences
    before = documents.to_h { |path| [path, [File.binread(path), File.stat(path).mtime]] }
    status, log, = execute(command)
    assert_equal 0, status, log
    assert_includes log, '"status":"no-op"'
    assert_equal 1, command.inferences
    documents.each { |path| assert_equal before[path], [File.binread(path), File.stat(path).mtime] }
    assert_includes File.read(documents.first), '`p.Worker.F`'
  end

  def test_human_edit_blocks_before_next_inference
    command = StoredResponse.new(@env)
    assert_equal 0, execute(command).first
    File.write(documents.first, 'human revision')
    File.write(File.join(@source, 'main.go'), @text.sub('return 7', 'return 8'))
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'human edit'
    assert_equal 1, command.inferences
    assert_equal 'human revision', File.read(documents.first)
  end

  def test_syntax_error_refuses_before_inference_and_outputs
    File.write(File.join(@source, 'main.go'), @text + "func Broken( {\n")
    command = StoredResponse.new(@env)
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'Go AST producer refused'
    assert_nil command.inferences
    assert documents.none? { |path| File.exist?(path) }
  end

  def test_ambiguous_methods_require_receiver_qualification
    text = "package p\nfunc (a A) F() {}\nfunc (b B) F() {}\n"
    command = Documentation::GoAstCommand.new(@env)
    assert_raises(Documentation::Error) { command.source_units('main.go', text, ['F']) }
    card = command.source_units('main.go', text, ['B.F']).fetch('B.F')
    assert_equal 3, card['line']
    assert_equal 'p.B.F', card['qualified_symbol']
  end

  def test_go_ast_mode_refuses_mixed_files_ranges_and_missing_units
    variants = [@project.merge('files' => ['main.py']), @project.merge('ranges' => {}), @project.reject { |key, _| key == 'units' }]
    variants.each do |project|
      @project = project
      command = StoredResponse.new(@env)
      status, log, = execute(command)
      assert_equal 1, status
      assert_match(/Go AST mode requires|units require explicit files/, log)
      assert_nil command.inferences
    end
  end

  def test_verified_receiver_short_alias_passes_but_wrong_owner_stays_rejected
    @text = "package p\nfunc (w *Worker) Fetch() int { return 7 }\nfunc (x *Other) Fetch() int { return 9 }\n"
    File.write(File.join(@source, 'main.go'), @text)
    @project['units'] = { 'main.go' => ['Worker.Fetch'] }
    command = StoredResponse.new(@env)
    command.define_singleton_method(:infer) do |files, skills|
      result = super(files, skills)
      result['result']['facts'].each do |fact|
        %w[en pt-br].each { |lang| fact[lang].gsub!('p.Worker.Fetch', 'Worker.Fetch') }
      end
      result
    end
    status, log, = execute(command)
    assert_equal 0, status, log
    assert_includes File.read(documents.first), '`Worker.Fetch`'
    File.write(File.join(@source, 'main.go'), @text + "// source metadata changed\n")
    command.define_singleton_method(:infer) do |files, skills|
      result = super(files, skills)
      result['result']['facts'].each do |fact|
        %w[en pt-br].each { |lang| fact[lang].gsub!('p.Worker.Fetch', 'Other.Fetch') }
      end
      result
    end
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'different owner'
  end

  def test_standalone_type_context_has_exact_complete_card_and_alias_kind
    source = "package p\ntype Record struct {\n Value int\n}\ntype Alias = int\n"
    command = Documentation::GoAstCommand.new(@env)
    cards = command.source_units('main.go', source, ['p.Record', 'Alias'])
    assert_equal "type Record struct {\n Value int\n}\n", cards['p.Record']['quote']
    assert_equal 2, cards['p.Record']['line']
    assert_equal 'type', cards['p.Record']['declaration_kind']
    assert_equal true, cards['p.Record']['complete_unit']
    assert_equal 'p.Record', cards['p.Record']['qualified_symbol']
    assert_equal 'type-alias', cards['Alias']['declaration_kind']
  end

  def test_grouped_type_context_refuses_instead_of_selecting_partial_spec
    command = Documentation::GoAstCommand.new(@env)
    assert_raises(Documentation::Error) do
      command.source_units('main.go', "package p\ntype (\n A int\n B string\n)\n", ['A'])
    end
  end

  def test_type_and_method_context_flow_through_bilingual_renderer
    @text = "package p\ntype Record struct { Value int }\nfunc (r *Record) Fetch() int { return 7 }\n"
    File.write(File.join(@source, 'main.go'), @text)
    @project['units'] = { 'main.go' => ['Record', 'Record.Fetch'] }
    command = StoredResponse.new(@env)
    command.define_singleton_method(:infer) do |files, skills|
      result = super(files, skills)
      cards = evidence_cards(files)
      result['result']['facts'].each do |fact|
        next unless cards.fetch(fact['evidence_id'])['declaration_kind'] == 'type'
        fact['en'] = 'The selected `p.Record` declaration contains a field `Value` with the written type `int`. This is source syntax, without type or runtime verification.'
        fact['pt-br'] = 'A declaração selecionada `p.Record` contém um campo `Value` com o tipo escrito `int`. Trata-se de sintaxe da fonte, sem verificação de tipos ou de execução.'
      end
      result
    end
    status, log, = execute(command)
    assert_equal 0, status, log
    assert_includes File.read(documents.first), '`p.Record`'
    assert_includes File.read(documents.first), '`p.Record.Fetch`'
    assert_includes File.read(documents.first), 'type Record struct'
  end

  def test_absent_launcher_does_not_fall_back_to_lexical_selection
    command = Documentation::GoAstCommand.new(@env.merge('DOCS_AGENT' => File.join(@root, 'absent')))
    error = assert_raises(Documentation::Error) { command.source_units('main.go', @text, ['Worker.F']) }
    assert_includes error.message, 'launcher unavailable'
  end

  def test_generic_and_callback_tuple_source_units_are_exact_without_type_claim
    text = "package p\nfunc F[T any](x T) func() (T,error) { return func() (T,error) { return x,nil } }\n"
    card = Documentation::GoAstCommand.new(@env).source_units('main.go', text, ['F']).fetch('F')
    assert_equal text.lines.last, card['quote']
    assert_equal 'p.F', card['qualified_symbol']
    assert_includes card['preparation'], 'not type/import/runtime verification'
  end

  def handler_order_source(nested: false, comment: false)
    body = if comment
      "defer func() {\n // The Recoverer function uses a defer statement to ensure that the panic is handled before the next function in the pipeline is called.\n _ = recover()\n }()"
    elsif nested
      'func() { defer func() { _ = recover() }(); panic("synthetic") }()'
    else
      'defer func() { _ = recover() }()'
    end
    "package p\nfunc Recoverer(next http.Handler) http.Handler {\n fn := func(w http.ResponseWriter, r *http.Request) {\n  #{body}\n  next.ServeHTTP(w, r)\n }\n return http.HandlerFunc(fn)\n}\n"
  end

  def render_handler_order(fact, nested: false, comment: false)
    source = handler_order_source(nested: nested, comment: comment)
    File.write(File.join(@source, 'main.go'), source)
    @project['units'] = { 'main.go' => ['Recoverer'] }
    command = Documentation::GoAstCommand.new(@env)
    snapshot = command.evidence(@project)
    command.validate_and_render({ 'facts' => [fact] }, snapshot['files'], 'revision', snapshot, @project)
  end

  def test_observed_defer_execution_order_error_is_refused_in_either_language
    correct = { 'evidence_id' => 'S1',
      'en' => 'Recoverer registers the defer before calling the next handler; its deferred body runs when the callback exits.',
      'pt-br' => 'Recoverer registra o defer antes de chamar o próximo handler; o corpo adiado executa na saída do callback.' }
    wrong = {
      'en' => 'The Recoverer function uses a defer statement to ensure that the panic is handled before the next function in the pipeline is called.',
      'pt-br' => 'A função Recoverer usa uma declaração de defer para garantir que o panic seja lidado antes que a próxima função no pipeline seja chamada.' }
    wrong.each do |lang, prose|
      error = assert_raises(Documentation::Error) { render_handler_order(correct.merge(lang => prose)) }
      assert_includes error.message, 'deferred execution order contradicts the verified callback scope'
    end
  end

  def test_correct_registration_and_negated_defer_claims_remain_valid
    fact = { 'evidence_id' => 'S1',
      'en' => 'Recoverer registers the defer before calling the next handler; its deferred body runs when the callback exits.',
      'pt-br' => 'Recoverer registra o defer antes de chamar o próximo handler; o corpo adiado executa na saída do callback.' }
    assert_kind_of Hash, render_handler_order(fact)
    fact['en'] = 'Recoverer does not ensure that the panic is handled before the next function in the pipeline is called; the defer executes on callback exit.'
    fact['pt-br'] = 'Recoverer não garante que o panic seja lidado antes que a próxima função no pipeline seja chamada; o defer executa na saída do callback.'
    assert_kind_of Hash, render_handler_order(fact)
  end

  def test_same_words_in_valid_immediate_inner_scope_are_not_refused
    fact = { 'evidence_id' => 'S1',
      'en' => 'The Recoverer function uses a defer statement to ensure that the panic is handled before the next function in the pipeline is called.',
      'pt-br' => 'A função Recoverer usa uma declaração de defer para garantir que o panic seja lidado antes que a próxima função no pipeline seja chamada.' }
    assert_kind_of Hash, render_handler_order(fact, nested: true)
  end

  def test_quoted_source_comment_is_not_treated_as_an_asserted_execution_order
    text = 'The Recoverer function uses a defer statement to ensure that the panic is handled before the next function in the pipeline is called.'
    fact = { 'evidence_id' => 'S1',
      'en' => "Recoverer contains the comment `#{text}` inside its deferred function.",
      'pt-br' => "Recoverer contém o comentário `#{text}` dentro de sua função adiada." }
    assert_kind_of Hash, render_handler_order(fact, comment: true)
  end
end
