require 'bundler/setup'
require 'minitest/autorun'
require 'tmpdir'
require 'fileutils'
require_relative '../../lib/documentation/go_deferred_fact_command'

class DocumentationGoDeferredFactsTest < Minitest::Test
  class Observed < Documentation::GoDeferredFactCommand
    attr_accessor :change_fact, :change_source
    attr_reader :analyses, :model_calls
    def infer(files, skills)
      @analyses = (@analyses || 0) + 1
      result = super
      result['result']['facts'].first['en'] += ' Changed.' if change_fact
      if change_source
        source = File.join(@env.fetch('DOCS_SOURCES'), 'project/main.go')
        File.write(source, File.read(source).sub('s.cancel != nil', 's.cancel == nil'))
      end
      result
    end
    def call_model(_body)
      @model_calls = (@model_calls || 0) + 1
      raise 'unexpected actual model transport'
    end
  end

  def setup
    @root = Dir.mktmpdir('documentation-go-deferred-')
    @source = File.join(@root, 'project')
    @library = File.join(@root, 'library')
    FileUtils.mkdir_p([File.join(@source, 'docs'), @library])
    @body = "s.mu.RLock()\n defer s.mu.RUnlock()\n return s.cancel != nil"
    write_source(@body)
    @project = { 'slug' => 'deferred-facts', 'source' => @source, 'destination' => File.join(@source, 'docs'),
      'lifecycle' => 'temporary', 'files' => ['main.go'], 'units' => { 'main.go' => ['State.Started'] } }
    agent = File.expand_path('../../../agent', __dir__)
    agent = '/agent' unless File.directory?(agent)
    @env = { 'DOCS_LIBRARY' => @library, 'DOCS_SOURCES' => @root,
      'DOCS_AGENT' => agent, 'DOCS_CONTEXT' => 'baseline' }
  end

  def teardown
    FileUtils.remove_entry(@root)
  end

  def write_source(body)
    # Syntax inspection intentionally does not need State/mu definitions.
    File.write(File.join(@source, 'main.go'), "package p\nfunc (s *State) Started() bool {\n #{body}\n}\n")
  end

  def execute(command = Observed.new(@env))
    config = File.join(@root, 'config.json')
    File.write(config, JSON.generate('projects' => [@project]))
    status = nil
    out, = capture_io { status = command.run(['--config', config]) }
    [status, out]
  end

  def documents
    %w[en pt-br].map { |lang| File.join(@library, '.evaluations/deferred-facts', lang, Documentation::Command::DOCUMENT) }
  end

  def test_exact_deferred_order_nil_polarity_and_bilingual_origin_without_model
    command = Observed.new(@env)
    status, log = execute(command)
    assert_equal 0, status, log
    assert_nil command.model_calls
    en, pt = documents.map { |file| File.read(file) }
    assert_includes en, 'call `s.mu.RLock()`; defer `s.mu.RUnlock()`; return'
    assert_includes en, '`s.cancel != nil`'
    assert_includes en, 'deferred invocation is not an immediate second invocation'
    assert_includes en, 'concurrency safety and runtime effects remain unverified'
    assert_includes en, 'model inference: not invoked'
    assert_equal en.scan(/`([^`\r\n]+)`/), pt.scan(/`([^`\r\n]+)`/)
    state = JSON.parse(File.read(File.join(@library, '.docs-state/evaluations/deferred-facts.json')))
    assert_equal 'go-call-defer-return-syntax-v1', state['coverage']['source_analysis']['profile']
    assert_equal false, state['coverage']['source_analysis']['model_inference']
  end

  def test_mismatched_receiver_or_immediate_unlock_is_not_a_deferred_contract
    [@body.sub('defer s.mu.RUnlock()', 'defer s.other.RUnlock()'), @body.sub('defer ', '')].each do |body|
      write_source(body)
      command = Observed.new(@env)
      status, = execute(command)
      assert_equal 1, status
      assert_nil command.model_calls
      assert documents.none? { |file| File.exist?(file) }
    end
  end

  def test_plain_return_and_extra_computation_do_not_silently_enter_this_profile
    ['return s.cancel != nil', "s.work()\n" + @body].each do |body|
      write_source(body)
      command = Observed.new(@env)
      assert_equal 1, execute(command).first
      assert_nil command.model_calls
      assert documents.none? { |file| File.exist?(file) }
    end
  end

  def test_changed_prose_cannot_keep_source_derived_origin
    command = Observed.new(@env)
    command.change_fact = true
    status, log = execute(command)
    assert_equal 1, status
    assert_includes log, 'source-derived explanation or citation was changed'
    assert_nil command.model_calls
    assert documents.none? { |file| File.exist?(file) }
  end

  def test_source_polarity_changed_after_analysis_prevents_old_fact_write
    command = Observed.new(@env)
    command.change_source = true
    status, log = execute(command)
    assert_equal 1, status
    assert_includes log, 'source changed'
    assert_nil command.model_calls
    assert documents.none? { |file| File.exist?(file) }
  end

  def test_questions_and_cached_neural_results_are_rejected_before_analysis
    [{ 'question' => 'Explain the supplied source only' }, { 'reuse_selected_unit_facts' => true }].each do |extra|
      @project = @project.reject { |key, _| %w[question reuse_selected_unit_facts].include?(key) }.merge(extra)
      command = Observed.new(@env)
      assert_equal 1, execute(command).first
      assert_nil command.analyses
      assert_nil command.model_calls
    end
  end

  def test_normal_reader_source_exclusions_are_preserved
    FileUtils.mkdir_p(File.join(@source, 'storage'))
    FileUtils.cp(File.join(@source, 'main.go'), File.join(@source, 'storage/main.go'))
    @project['files'] = ['storage/main.go']
    @project['units'] = { 'storage/main.go' => ['State.Started'] }
    command = Observed.new(@env)
    status, log = execute(command)
    assert_equal 1, status
    assert_includes log, 'excluded section evidence'
    assert_nil command.analyses
    assert_nil command.model_calls
  end
end
