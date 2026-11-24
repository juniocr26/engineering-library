require 'bundler/setup'
require 'minitest/autorun'
require 'tmpdir'
require_relative '../../lib/documentation/project_command'

class DocumentationSelectedCoverageTest < Minitest::Test
  class ObservedCommand < Documentation::SectionCommand
    attr_accessor :response_mode
    attr_reader :inferences

    def infer(files, skills)
      @inferences = (@inferences || 0) + 1
      facts = [
        { 'evidence_id' => 'S1', 'en' => '`first` returns the written expression `1`.',
          'pt-br' => '`first` retorna a expressão escrita `1`.' },
        { 'evidence_id' => 'S2', 'en' => '`second` returns the written expression `2`.',
          'pt-br' => '`second` retorna a expressão escrita `2`.' }
      ]
      facts = [facts.first] if response_mode == :partial
      facts = [facts.first, facts.first.dup] if response_mode == :duplicate
      { 'result' => { 'facts' => facts }, 'request' => source_model_request(files, skills), 'response' => {} }
    end

    def call_model(_body)
      raise 'unexpected model transport in coverage controls'
    end
  end

  def setup
    @root = Dir.mktmpdir('documentation-selected-coverage-')
    @source = @root + '/source'
    @library = @root + '/library'
    FileUtils.mkdir_p([@source + '/docs', @library])
    File.write(@source + '/main.py', "def first():\n    return 1\n\ndef second():\n    return 2\n")
    @project = { 'slug' => 'sample', 'source' => @source, 'destination' => @source + '/docs',
      'lifecycle' => 'temporary', 'files' => ['main.py'], 'units' => { 'main.py' => %w[first second] } }
    @env = { 'DOCS_LIBRARY' => @library, 'DOCS_SOURCES' => @root,
      'DOCS_AGENT' => @root + '/absent-agent', 'DOCS_CONTEXT' => 'baseline' }
    @config = @root + '/config.json'
  end

  def teardown
    FileUtils.remove_entry(@root)
  end

  def execute(command)
    File.write(@config, JSON.generate('projects' => [@project]))
    status = nil
    out, err = capture_io { status = command.run(['--config', @config]) }
    [status, out, err]
  end

  def preserved
    paths = Dir[@library + '/.evaluations/sample/**/*', @source + '/docs/**/*']
    paths << @library + '/.docs-state/evaluations/sample.json'
    paths.select { |path| File.file?(path) }.to_h { |path| [path, [File.binread(path), File.mtime(path)]] }
  end

  def test_default_and_explicit_false_keep_partial_response_and_identical_request
    command = ObservedCommand.new(@env)
    command.response_mode = :partial
    assert_equal 0, execute(command).first
    command.validate_project(@project)
    files = command.evidence(@project)['files']
    default = JSON.generate(command.source_model_request(files, ''))
    @project['require_selected_evidence_coverage'] = false
    command.validate_project(@project)
    assert_equal default, JSON.generate(command.source_model_request(files, ''))
    before = preserved
    status, log, = execute(command)
    assert_equal 0, status, log
    assert_includes log, '"status":"no-op"'
    assert_equal 1, command.inferences
    assert_equal before, preserved
  end

  def test_explicit_coverage_writes_all_cards_then_noops_with_recorded_policy
    @project['require_selected_evidence_coverage'] = true
    command = ObservedCommand.new(@env)
    status, log, = execute(command)
    assert_equal 0, status, log
    manifest = JSON.parse(File.read(@library + '/.docs-state/evaluations/sample.json'))
    assert_equal true, manifest['require_selected_evidence_coverage']
    before = preserved
    assert_equal 0, execute(command).first
    assert_equal 1, command.inferences
    assert_equal before, preserved
    command.validate_project(@project)
    request = command.source_model_request(command.evidence(@project)['files'], '')
    assert_equal 2, request[:format][:properties][:facts][:minItems]
    assert_includes request[:messages].last[:content], 'Cover every supplied evidence_id'
  end

  def test_partial_and_duplicate_responses_refuse_without_creating_outputs
    @project['require_selected_evidence_coverage'] = true
    %i[partial duplicate].each do |mode|
      command = ObservedCommand.new(@env)
      command.response_mode = mode
      status, log, = execute(command)
      assert_equal 1, status
      assert_includes log, 'selected evidence coverage missing: S2'
      assert_empty preserved
    end
  end

  def test_policy_change_invalidates_noop_and_preserves_prior_files_on_refusal
    command = ObservedCommand.new(@env)
    command.response_mode = :partial
    assert_equal 0, execute(command).first
    before = preserved
    @project['require_selected_evidence_coverage'] = true
    assert_equal 1, execute(command).first
    assert_equal 2, command.inferences
    assert_equal before, preserved
    @project['require_selected_evidence_coverage'] = false
    status, log, = execute(command)
    assert_equal 0, status, log
    assert_includes log, '"status":"no-op"'
    assert_equal 2, command.inferences
    assert_equal before, preserved
  end

  def test_policy_change_cannot_reuse_a_partial_cached_result
    @project['reuse_selected_unit_facts'] = true
    command = ObservedCommand.new(@env)
    command.response_mode = :partial
    assert_equal 0, execute(command).first
    before = preserved
    @project['require_selected_evidence_coverage'] = true
    assert_equal 1, execute(command).first
    assert_equal 2, command.inferences
    assert_equal before, preserved
    command.response_mode = nil
    assert_equal 0, execute(command).first
    assert_equal 3, command.inferences
    assert_equal 0, execute(command).first
    assert_equal 3, command.inferences
  end

  def test_impossible_fact_budget_refuses_before_inference
    @project['require_selected_evidence_coverage'] = true
    command = ObservedCommand.new(@env.merge('DOCS_FACT_LIMIT' => '1'))
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'within the fact limit'
    assert_nil command.inferences
    assert_empty preserved
  end

  def test_nonboolean_policy_is_refused_before_inference
    [nil, 1, 'true', [], {}].each do |value|
      @project['require_selected_evidence_coverage'] = value
      command = ObservedCommand.new(@env)
      status, log, = execute(command)
      assert_equal 1, status
      assert_includes log, 'must be a Boolean'
      assert_nil command.inferences
      assert_empty preserved
    end
  end
end
