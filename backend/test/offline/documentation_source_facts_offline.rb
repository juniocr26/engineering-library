require 'bundler/setup'
require 'minitest/autorun'
require 'tmpdir'
require 'fileutils'
require_relative '../../lib/documentation/source_fact_command'

class DocumentationSourceFactsTest < Minitest::Test
  class ObservedCommand < Documentation::SourceFactCommand
    attr_reader :analyses, :model_requests
    attr_accessor :interrupt

    def infer(files, skills)
      @analyses = (@analyses || 0) + 1
      super
    end

    def call_model(_body)
      @model_requests = (@model_requests || 0) + 1
      raise 'unexpected model transport in source-fact mode'
    end

    def atomic(path, bytes)
      super
      if interrupt && path == File.join(@env.fetch('DOCS_SOURCES'), 'project/docs/en', DOCUMENT)
        self.interrupt = false
        raise IOError, 'synthetic interruption after output rename'
      end
    end
  end

  def setup
    @root = Dir.mktmpdir('documentation-source-facts-')
    @library = File.join(@root, 'library')
    @source = File.join(@root, 'project')
    FileUtils.mkdir_p([@library, File.join(@source, 'docs')])
    @text = "class Worker:\n    async def dispatch(self):\n        if self.flag:\n            await self.direct(*self.args, **self.kwargs)\n        else:\n            await fallback(self.direct, *self.args, **self.kwargs)\n"
    File.write(File.join(@source, 'main.py'), @text)
    @project = { 'slug' => 'sample', 'source' => @source, 'destination' => File.join(@source, 'docs'),
      'lifecycle' => 'temporary', 'files' => ['main.py'], 'units' => { 'main.py' => ['Worker.dispatch'] } }
    @config = File.join(@root, 'project.json')
    @env = { 'DOCS_LIBRARY' => @library, 'DOCS_SOURCES' => @root,
      'DOCS_AGENT' => File.join(@root, 'absent-agent'), 'DOCS_CONTEXT' => 'baseline' }
  end

  def teardown
    FileUtils.remove_entry(@root)
  end

  def execute(command = ObservedCommand.new(@env), *args)
    File.write(@config, JSON.generate('projects' => [@project]))
    status = nil
    out, err = capture_io { status = command.run(['--config', @config, *args]) }
    [status, out, err]
  end

  def documents
    [File.join(@library, '.evaluations/sample'), File.join(@source, 'docs')].flat_map do |root|
      %w[en pt-br].map { |lang| File.join(root, lang, Documentation::Command::DOCUMENT) }
    end
  end

  def fingerprints
    documents.to_h { |path| [path, [File.binread(path), File.stat(path).mtime]] }
  end

  def test_unicode_or_control_separators_in_prior_literal_preserve_exact_physical_quote
    ["\u2028", "\u2029", "\u0085", "\v", "\f"].each do |separator|
      File.write(File.join(@source, 'main.py'), "marker = \"a#{separator}b\"\n" + @text)
      command = ObservedCommand.new(@env)
      status, log, = execute(command)
      assert_equal 0, status, log
      assert_nil command.model_requests
      en, pt = documents.first(2).map { |path| File.read(path) }
      assert_includes en, "    async def dispatch(self):\n"
      assert_includes en, 'Source: `main.py:3`'
      assert_equal en.scan(/`([^`\r\n]+)`/), pt.scan(/`([^`\r\n]+)`/)
    end
  end

  def test_bare_carriage_return_source_is_refused_without_model_or_outputs
    File.write(File.join(@source, 'main.py'), @text.gsub("\n", "\r"))
    command = ObservedCommand.new(@env)
    assert_equal 1, execute(command).first
    assert_nil command.model_requests
    assert documents.none? { |path| File.exist?(path) }
  end

  def test_real_ast_facts_write_honest_bilingual_provenance_without_model_transport
    command = ObservedCommand.new(@env)
    status, log, = execute(command)
    assert_equal 0, status
    assert_includes log, '"inference":false'
    assert_nil command.model_requests
    assert_equal 1, command.analyses
    assert_equal 4, documents.count { |path| File.file?(path) }
    en, pt = documents.first(2).map { |path| File.read(path) }
    assert_includes en, 'Origin: deterministic source-derived fact'
    assert_includes pt, 'Origem: fato determinístico derivado da fonte'
    assert_includes en, 'model inference: not invoked'
    assert_includes pt, 'inferência de modelo: não invocada'
    assert_includes en, '`Worker.dispatch`'
    assert_includes en, '`self.direct(*self.args, **self.kwargs)`'
    assert_includes en, '`fallback(self.direct, *self.args, **self.kwargs)`'
    assert_includes en, '`main.py:2`'
    refute_includes en, 'model: llama3.2'
    manifest = JSON.parse(File.read(File.join(@library, '.docs-state/evaluations/sample.json')))
    assert_equal false, manifest.fetch('coverage').fetch('source_analysis').fetch('model_inference')
    assert_equal Documentation::SourceFactCommand::PROFILE, manifest['coverage']['source_analysis']['profile']
  end

  def test_noop_preserves_all_document_bytes_and_mtimes_without_new_analysis
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    before = fingerprints
    status, log, = execute(command)
    assert_equal 0, status
    assert_includes log, '"status":"no-op"'
    assert_equal 1, command.analyses
    assert_nil command.model_requests
    assert_equal before, fingerprints
  end

  def guarded_iteration_source
    "async def stream(values):\n    cursor = adapt(values)\n    while True:\n        try:\n            yield await backend.stream(advance, cursor)\n        except Finished:\n            break\n"
  end

  def test_guarded_iteration_writes_exact_yield_and_break_then_noops_without_model
    File.write(File.join(@source, 'main.py'), guarded_iteration_source)
    @project['units'] = { 'main.py' => ['stream'] }
    command = ObservedCommand.new(@env)
    status, log, = execute(command)
    assert_equal 0, status, log
    en, pt = documents.first(2).map { |path| File.read(path) }
    assert_includes en, '`yield await backend.stream(advance, cursor)`'
    assert_includes en, '`except Finished`'
    assert_includes en, '`break`'
    assert_includes en, 'not returned as a final value'
    assert_includes en, 'exception matching'
    assert_equal en.scan(/`([^`\r\n]+)`/), pt.scan(/`([^`\r\n]+)`/)
    assert_nil command.model_requests
    before = fingerprints
    status, log, = execute(command)
    assert_equal 0, status, log
    assert_includes log, '"status":"no-op"'
    assert_equal 1, command.analyses
    assert_equal before, fingerprints
    assert_nil command.model_requests
  end

  def test_guarded_iteration_changed_to_raise_refuses_and_preserves_all_prior_outputs
    File.write(File.join(@source, 'main.py'), guarded_iteration_source)
    @project['units'] = { 'main.py' => ['stream'] }
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    before = fingerprints
    File.write(File.join(@source, 'main.py'), guarded_iteration_source.sub('            break', '            raise'))
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'source facts refused'
    assert_equal before, fingerprints
    assert_nil command.model_requests
  end

  def test_unknown_construct_refuses_the_entire_project_without_model_fallback
    File.write(File.join(@source, 'main.py'), @text + "\n    async def unsupported(self):\n        await first()\n        await second()\n")
    @project['units']['main.py'] << 'Worker.unsupported'
    command = ObservedCommand.new(@env)
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'source facts refused'
    assert documents.none? { |path| File.exist?(path) }
    assert_nil command.model_requests
  end

  def test_decorated_method_is_refused
    File.write(File.join(@source, 'main.py'), @text.sub('    async def', "    @override\n    async def"))
    status, log, = execute
    assert_equal 1, status
    assert_includes log, 'undecorated'
    assert documents.none? { |path| File.exist?(path) }
  end

  def test_human_edit_blocks_before_another_analysis_and_preserves_other_language
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    before = fingerprints
    File.write(documents.first, 'human annotation')
    File.write(File.join(@source, 'main.py'), @text.sub('if self.flag:', 'if not self.flag:'))
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'human edit'
    assert_equal 'human annotation', File.read(documents.first)
    documents.drop(1).each { |path| assert_equal before.fetch(path), fingerprints.fetch(path) }
    assert_equal 1, command.analyses
    assert_nil command.model_requests
  end

  def test_source_fact_output_uses_existing_interruption_and_complete_recovery
    command = ObservedCommand.new(@env)
    command.interrupt = true
    assert_equal 1, execute(command).first
    journal = File.join(@library, '.docs-state/evaluations/sample.pending.json')
    assert File.file?(journal)
    recovery = ObservedCommand.new(@env)
    assert_equal 0, execute(recovery, '--project', 'sample', '--recover', 'complete').first
    refute File.exist?(journal)
    assert documents.all? { |path| File.file?(path) }
    assert_includes File.read(documents.first), 'deterministic source-derived fact'
    assert_nil recovery.analyses
    assert_nil recovery.model_requests
  end

  def test_question_feedback_and_online_research_are_not_silently_ignored
    @project['question'] = 'Explain a different contract instead.'
    assert_equal 1, execute.first
    @project.delete('question')
    @project['feedback'] = { 'kind' => 'reviewer-feedback', 'text' => 'Replace facts' }
    assert_equal 1, execute.first
    @project.delete('feedback')
    command = ObservedCommand.new(@env.merge('DOCS_RESEARCH' => 'urls'))
    assert_equal 1, execute(command).first
    assert documents.none? { |path| File.exist?(path) }
    assert_nil command.model_requests
  end

  def test_a_source_fact_cannot_be_replaced_by_model_prose_with_same_evidence_id
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    snapshot = command.evidence(@project)
    result = command.infer(snapshot['files'], '')['result']
    result['facts'].first['en'] = 'Worker.dispatch guarantees that every operation succeeds without any exception.'
    assert_raises(Documentation::Error) do
      command.validate_and_render(result, snapshot['files'], 'revision', snapshot, @project)
    end
  end

  def delegated_source
    "class Worker:\n    async def dispatch(self):\n        if self.flag:\n            await self.runner.dispatch(self.value)\n        else:\n            await self.fallback.dispatch(self.value)\n"
  end

  def test_verified_source_facts_can_cite_same_named_awaited_callees
    File.write(File.join(@source, 'main.py'), delegated_source)
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    en = File.read(documents.first)
    assert_includes en, '`self.runner.dispatch(self.value)`'
    assert_includes en, '`self.fallback.dispatch(self.value)`'
    assert_nil command.model_requests
  end

  def test_default_model_guard_does_not_receive_the_source_fact_exception
    command = Documentation::Command.new
    card = command.source_units('main.py', delegated_source, ['Worker.dispatch']).values.first
    command.define_singleton_method(:evidence_cards) { |_| { 'S1' => card } }
    result = { 'facts' => [{ 'evidence_id' => 'S1',
      'en' => '`Worker.dispatch` awaits `self.runner.dispatch(self.value)` in one source branch.',
      'pt-br' => '`Worker.dispatch` aguarda `self.runner.dispatch(self.value)` em um ramo da fonte.' }] }
    assert_raises(Documentation::Error) do
      command.validate_and_render(result, { 'main.py' => delegated_source }, 'revision',
        { 'candidate_count' => 1, 'selection' => 'explicit', 'omitted_count' => 0 }, @project)
    end
  end
  def test_declaration_preserves_parameter_kinds_defaults_and_annotations
    text = "class Worker:\n    async def dispatch(self, flag, /, value: int = 3, *, enabled: bool = True, **kwargs) -> None:\n        if flag:\n            await left(value)\n        else:\n            await right(value)\n"
    File.write(File.join(@source, 'main.py'), text)
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    expected = '`async def dispatch(self, flag, /, value: int=3, *, enabled: bool=True, **kwargs) -> None`'
    documents.first(2).each { |path| assert_includes File.read(path), expected }
    assert_includes File.read(documents.first), 'not runtime validation or evaluated values'
    assert_nil command.model_requests
  end

  def test_unknown_default_call_and_annotation_are_recorded_without_evaluation
    text = "class Worker:\n    async def dispatch(self, value: 'UndefinedType' = absent_factory()) -> 'UnknownResult':\n        if self.flag:\n            await left(value)\n        else:\n            await right(value)\n"
    File.write(File.join(@source, 'main.py'), text)
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    en = File.read(documents.first)
    assert_includes en, "value: 'UndefinedType'=absent_factory()"
    assert_includes en, "-> 'UnknownResult'"
    assert_includes en, 'The body has no explicit return statement or try/except'
    assert_nil command.model_requests
  end

  def test_backtick_in_declaration_is_refused_without_fallback
    text = @text.sub('dispatch(self)', 'dispatch(self, value: "Bad`Type")')
    File.write(File.join(@source, 'main.py'), text)
    command = ObservedCommand.new(@env)
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'source facts refused'
    assert documents.none? { |path| File.exist?(path) }
    assert_nil command.model_requests
  end

  def test_unbounded_declaration_is_refused_without_fallback
    text = @text.sub('dispatch(self)', 'dispatch(self, value: "' + ('A' * 650) + '")')
    File.write(File.join(@source, 'main.py'), text)
    command = ObservedCommand.new(@env)
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'source facts refused'
    assert documents.none? { |path| File.exist?(path) }
    assert_nil command.model_requests
  end

  def forwarded_return_source
    "async def run_in_threadpool(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:\n    func = functools.partial(func, *args, **kwargs)\n    return await anyio.to_thread.run_sync(func)\n"
  end

  def select_forwarded_return(text = forwarded_return_source)
    File.write(File.join(@source, 'main.py'), text)
    @project['units']['main.py'] = ['run_in_threadpool']
  end

  def test_forwarded_return_records_conditional_result_propagation_without_model_or_helper_claims
    select_forwarded_return
    command = ObservedCommand.new(@env)
    status, log, = execute(command)
    assert_equal 0, status, log
    assert_nil command.model_requests
    en, pt = documents.first(2).map { |path| File.read(path) }
    assert_includes en, '`functools.partial(func, *args, **kwargs)`'
    assert_includes en, '`return await anyio.to_thread.run_sync(func)`'
    assert_includes en, 'If that awaited expression completes normally, its result is returned'
    assert_includes pt, 'Se essa expressão aguardada termina normalmente, seu resultado é retornado'
    assert_equal en.scan(/`([^`\r\n]+)`/), pt.scan(/`([^`\r\n]+)`/)
    assert_includes en, 'thread scheduling and successful runtime completion are not verified'
    before = fingerprints
    assert_equal 0, execute(command).first
    assert_equal before, fingerprints
    assert_equal 1, command.analyses
  end

  def test_forwarded_return_source_change_invalidates_analysis_and_preserves_written_helper_names
    select_forwarded_return
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    select_forwarded_return(forwarded_return_source.sub('anyio.to_thread.run_sync', 'custom.run_sync'))
    assert_equal 0, execute(command).first
    assert_equal 2, command.analyses
    en = File.read(documents.first)
    assert_includes en, '`return await custom.run_sync(func)`'
    refute_includes en, '`return await anyio.to_thread.run_sync(func)`'
    assert_nil command.model_requests
  end

  def test_similar_unsupported_return_shapes_preserve_owned_outputs_without_model_fallback
    select_forwarded_return
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    before = fingerprints
    variants = [
      forwarded_return_source.sub('return await', 'await'),
      forwarded_return_source.sub('return await', 'return'),
      forwarded_return_source.sub('    return await', "    side_effect()\n    return await"),
      forwarded_return_source.sub('functools.partial', 'factory().partial'),
      forwarded_return_source.sub('run_sync(func)', 'run_sync(other)'),
      forwarded_return_source.sub('**kwargs)', 'key=kwargs)'),
      forwarded_return_source.sub('func: Callable[P, T]', 'func: Callable[P, T] = absent()'),
      "@decorate\n" + forwarded_return_source,
      forwarded_return_source.sub('func =', 'other ='),
      forwarded_return_source.sub('run_sync(func)', 'run_sync(func, *args)')
    ]
    variants.each do |text|
      select_forwarded_return(text)
      status, log, = execute(command)
      assert_equal 1, status, log
      assert_equal before, fingerprints
      assert_nil command.model_requests
    end
  end

end
