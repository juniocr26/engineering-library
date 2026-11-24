require 'bundler/setup'
require 'minitest/autorun'
require 'tmpdir'
require 'fileutils'
require_relative '../../lib/documentation/source_fact_command'

class DocumentationSourceReuseTest < Minitest::Test
  class ObservedCommand < Documentation::Command
    attr_reader :inferences
    attr_accessor :interrupt, :skill_revision

    def skill_context
      ['', { 'controlled-skill' => skill_revision || 'first' }]
    end

    def infer(files, _skills)
      @inferences = (@inferences || 0) + 1
      quote = evidence_cards(files).values.first.fetch('quote')
      value = quote[/return (\d+)/, 1]
      { 'result' => { 'facts' => [{ 'evidence_id' => 'S1',
        'en' => "`Worker.limit` returns the literal value `#{value}` in the selected source method.",
        'pt-br' => "`Worker.limit` retorna o valor literal `#{value}` no método selecionado da fonte." }] },
        'request' => { 'kind' => 'explicit infer stub, zero model calls' }, 'response' => {} }
    end

    def atomic(path, bytes)
      super
      if interrupt && path == File.join(@env.fetch('DOCS_SOURCES'), 'project/docs/en', DOCUMENT)
        self.interrupt = false
        raise IOError, 'synthetic interruption after document rename'
      end
    end
  end

  def setup
    @root = Dir.mktmpdir('documentation-source-reuse-')
    @library = File.join(@root, 'library')
    @source = File.join(@root, 'project')
    FileUtils.mkdir_p([@library, File.join(@source, 'docs')])
    @text = "class Worker:\n    def limit(self):\n        return 7\n\ndef unrelated():\n    return 8\n"
    File.write(File.join(@source, 'main.py'), @text)
    @project = { 'slug' => 'sample', 'source' => @source, 'destination' => File.join(@source, 'docs'),
      'files' => ['main.py'], 'units' => { 'main.py' => ['Worker.limit'] }, 'reuse_selected_unit_facts' => true }
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
    [File.join(@library, 'sample'), File.join(@source, 'docs')].flat_map do |root|
      %w[en pt-br].map { |lang| File.join(root, lang, Documentation::Command::DOCUMENT) }
    end
  end

  def snapshots
    documents.to_h { |path| [path, [File.binread(path), File.stat(path).mtime]] }
  end

  def manifest_path
    File.join(@library, '.docs-state/sample.json')
  end

  def change_unselected_function
    File.write(File.join(@source, 'main.py'), @text.sub('return 8', 'return 9'))
  end

  def test_metadata_refresh_reuses_explanations_but_updates_file_hashes
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    before = File.read(documents.first)
    change_unselected_function
    status, log, = execute(command)
    assert_equal 0, status
    assert_equal 1, command.inferences
    assert_includes log, '"inference":false'
    refute_equal before, File.read(documents.first)
    assert_includes File.read(documents.first), 'cached model explanation'
    assert_includes File.read(documents[1]), 'explicação de modelo reutilizada'
    expected = Digest::SHA256.file(File.join(@source, 'main.py')).hexdigest
    assert_includes File.read(documents.first), expected
  end

  def test_changed_positions_invalidate_reuse_and_keep_the_new_exact_line
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    File.write(File.join(@source, 'main.py'), "# unrelated prefix\n" + @text)
    assert_equal 0, execute(command).first
    assert_equal 2, command.inferences
    assert_includes File.read(documents.first), '`main.py:3`'
    refute_includes File.read(documents.first), '`main.py:2`'
  end

  def test_unchanged_input_is_still_a_true_noop
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    before = snapshots
    status, log, = execute(command)
    assert_equal 0, status
    assert_includes log, '"status":"no-op"'
    assert_equal 1, command.inferences
    assert_equal before, snapshots
  end

  def test_changed_selected_unit_does_not_reuse_stale_facts
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    File.write(File.join(@source, 'main.py'), @text.sub('return 7', 'return 11'))
    assert_equal 0, execute(command).first
    assert_equal 2, command.inferences
    assert_includes File.read(documents.first), 'literal value `11`'
  end

  def test_changed_selected_helper_invalidates_the_shared_context
    File.write(File.join(@source, 'helper.py'), "def helper():\n    return 19\n")
    @project['files'] << 'helper.py'
    @project['units']['helper.py'] = ['helper']
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    File.write(File.join(@source, 'helper.py'), "def helper():\n    return 23\n")
    assert_equal 0, execute(command).first
    assert_equal 2, command.inferences
  end

  def test_changed_question_or_skill_requires_new_generation
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    @project['question'] = 'Explain the selected method return value.'
    assert_equal 0, execute(command).first
    assert_equal 2, command.inferences
    command.skill_revision = 'second'
    assert_equal 0, execute(command).first
    assert_equal 3, command.inferences
  end

  def test_human_content_blocks_before_reuse_and_preserves_both_languages
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    before = snapshots
    File.write(documents.first, 'human revision')
    change_unselected_function
    assert_equal 1, execute(command).first
    assert_equal 1, command.inferences
    assert_equal 'human revision', File.read(documents.first)
    documents.drop(1).each { |path| assert_equal before.fetch(path), snapshots.fetch(path) }
  end

  def test_corrupt_cache_is_refused_without_model_fallback_or_document_writes
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    state = JSON.parse(File.read(manifest_path))
    assert_kind_of Hash, state['source_unit_cache']
    state['source_unit_cache']['result']['facts'].first['en'] = 'Worker.limit now returns a different unsupported value.'
    File.write(manifest_path, JSON.generate(state))
    before = snapshots
    change_unselected_function
    assert_equal 1, execute(command).first
    assert_equal 1, command.inferences
    assert_equal before, snapshots
  end

  def test_default_disabled_mode_keeps_existing_regeneration_behavior
    @project.delete('reuse_selected_unit_facts')
    command = ObservedCommand.new(@env)
    assert_equal 0, execute(command).first
    change_unselected_function
    assert_equal 0, execute(command).first
    assert_equal 2, command.inferences
    refute JSON.parse(File.read(manifest_path)).key?('source_unit_cache')
    refute_includes File.read(documents.first), 'cached model explanation'
  end

  def test_cache_option_requires_a_boolean_and_complete_unit_plan
    @project['reuse_selected_unit_facts'] = 'true'
    command = ObservedCommand.new(@env)
    assert_equal 1, execute(command).first
    assert_nil command.inferences
    @project['reuse_selected_unit_facts'] = true
    @project.delete('units')
    assert_equal 1, execute(command).first
    assert_nil command.inferences
  end

  def test_feedback_and_online_research_are_outside_the_initial_cache_profile
    @project['feedback'] = { 'kind' => 'reviewer-feedback', 'text' => 'Explain only source facts.',
      'source_hashes' => { 'main.py' => Digest::SHA256.hexdigest(@text) } }
    command = ObservedCommand.new(@env)
    assert_equal 1, execute(command).first
    assert_nil command.inferences
    @project.delete('feedback')
    online = ObservedCommand.new(@env.merge('DOCS_RESEARCH' => 'urls'))
    assert_equal 1, execute(online).first
    assert_nil online.inferences
  end

  def test_existing_journal_recovery_retains_the_seed_cache
    command = ObservedCommand.new(@env)
    command.interrupt = true
    assert_equal 1, execute(command).first
    assert File.file?(File.join(@library, '.docs-state/sample.pending.json'))
    recovered = ObservedCommand.new(@env)
    assert_equal 0, execute(recovered, '--project', 'sample', '--recover', 'complete').first
    assert_nil recovered.inferences
    change_unselected_function
    next_invocation = ObservedCommand.new(@env)
    assert_equal 0, execute(next_invocation).first
    assert_nil next_invocation.inferences
  end

  def test_source_fact_mode_rejects_a_model_reuse_option
    File.write(File.join(@source, 'main.py'), "class Worker:\n    async def dispatch(self):\n        if self.flag:\n            await first()\n        else:\n            await second()\n")
    @project['units']['main.py'] = ['Worker.dispatch']
    command = Documentation::SourceFactCommand.new(@env)
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'model-fact reuse'
    assert documents.none? { |path| File.exist?(path) }
  end

  def test_reused_state_does_not_leak_into_the_next_project_in_a_batch
    other_source = File.join(@root, 'other')
    FileUtils.mkdir_p(other_source+'/docs')
    File.write(other_source+'/main.py', @text)
    other = @project.merge('slug'=>'other', 'source'=>other_source, 'destination'=>other_source+'/docs', 'reuse_selected_unit_facts'=>false)
    command = ObservedCommand.new(@env)
    run_batch = lambda do
      File.write(@config, JSON.generate('projects'=>[@project,other]))
      status = nil
      output, = capture_io { status = command.run(['--config',@config]) }
      [status,output]
    end
    assert_equal 0, run_batch.call.first
    assert_equal 2, command.inferences
    change_unselected_function
    File.write(other_source+'/main.py', @text.sub('return 7','return 13'))
    status, log = run_batch.call
    assert_equal 0, status
    assert_equal 3, command.inferences
    written = log.lines.filter_map { |line| JSON.parse(line) rescue nil }.select { |row| row['status']=='written' }
    assert_equal false, written.find { |row| row['project']=='sample' }['inference']
    assert_equal true, written.find { |row| row['project']=='other' }['inference']
    assert_includes File.read(@library+'/other/en/'+Documentation::Command::DOCUMENT), 'literal value `13`'
  end
  def test_explicit_fact_limit_change_invalidates_cached_model_facts
    first = ObservedCommand.new(@env)
    assert_equal 0, execute(first).first
    previous = JSON.parse(File.read(manifest_path))['source_unit_cache']['context_sha256']
    changed = ObservedCommand.new(@env.merge('DOCS_FACT_LIMIT' => '5'))
    assert_equal 0, execute(changed).first
    assert_equal 1, changed.inferences
    state = JSON.parse(File.read(manifest_path))
    refute_equal previous, state['source_unit_cache']['context_sha256']
    assert_equal 5, state['fact_limit']
    assert_equal 0, execute(changed).first
    assert_equal 1, changed.inferences
  end

end
