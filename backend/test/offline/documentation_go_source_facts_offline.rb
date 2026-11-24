require 'bundler/setup'
require 'minitest/autorun'
require 'tmpdir'
require 'fileutils'
require_relative '../../lib/documentation/go_source_fact_command'

class DocumentationGoSourceFactsTest < Minitest::Test
  class Observed < Documentation::GoSourceFactCommand
    attr_reader :analyses, :model_requests
    attr_accessor :mutate_fact, :mutate_source
    def infer(files, skills)
      @analyses = (@analyses || 0) + 1
      result = super
      result['result']['facts'].first['en'] += ' Changed.' if mutate_fact
      if mutate_source
        source = File.join(@env.fetch('DOCS_SOURCES'), 'project/main.go')
        File.write(source, File.read(source).sub('helper(x)', 'helper(8)'))
      end
      result
    end
    def call_model(_body)
      @model_requests = (@model_requests || 0) + 1
      raise 'unexpected actual model transport'
    end
  end

  def setup
    @root = Dir.mktmpdir('documentation-go-source-facts-')
    @source = File.join(@root, 'project')
    @library = File.join(@root, 'library')
    FileUtils.mkdir_p([File.join(@source, 'docs'), @library])
    @text = "package p\nfunc F() func(x int) error { return func(x int) error { return helper(x) } }\n"
    File.write(File.join(@source, 'main.go'), @text)
    agent = File.expand_path('../../../agent', __dir__)
    agent = '/agent' unless File.directory?(agent)
    @env = { 'DOCS_LIBRARY' => @library, 'DOCS_SOURCES' => @root, 'DOCS_AGENT' => agent, 'DOCS_CONTEXT' => 'baseline' }
    @project = { 'slug' => 'go-facts', 'source' => @source, 'destination' => File.join(@source, 'docs'),
      'lifecycle' => 'temporary', 'files' => ['main.go'], 'units' => { 'main.go' => ['F'] } }
    @config = File.join(@root, 'config.json')
  end

  def teardown
    FileUtils.remove_entry(@root)
  end

  def execute(command = Observed.new(@env))
    File.write(@config, JSON.generate('projects' => [@project]))
    status = nil
    out, err = capture_io { status = command.run(['--config', @config]) }
    [status, out, err]
  end

  def documents
    [File.join(@library, '.evaluations/go-facts'), File.join(@source, 'docs')].flat_map do |root|
      %w[en pt-br].map { |lang| File.join(root, lang, Documentation::Command::DOCUMENT) }
    end
  end

  def test_actual_parser_and_renderer_preserve_callback_timing_and_return_expression_without_model
    command = Observed.new(@env)
    status, log, = execute(command)
    assert_equal 0, status, log
    assert_nil command.model_requests
    assert_equal 1, command.analyses
    assert_includes log, '"inference":false'
    en, pt = documents.first(2).map { |path| File.read(path) }
    assert_includes en, '`p.F`'
    assert_includes en, '`func(x int) error`'
    assert_includes en, '`helper(x)`'
    assert_includes en, 'Returning this literal does not execute its body'
    assert_includes pt, 'Retornar esse literal não executa seu corpo'
    assert_includes en, 'model inference: not invoked'
    assert_equal en.scan(/`([^`\r\n]+)`/).flatten, pt.scan(/`([^`\r\n]+)`/).flatten
    manifest = JSON.parse(File.read(File.join(@library, '.docs-state/evaluations/go-facts.json')))
    assert_equal false, manifest['coverage']['source_analysis']['model_inference']
    assert_equal 'go-sole-return-syntax-v1', manifest['coverage']['source_analysis']['profile']
    refute_includes en, 'model: llama3.2'
  end

  def test_noop_preserves_bytes_and_mtimes_without_new_analysis
    command = Observed.new(@env)
    assert_equal 0, execute(command).first
    before = documents.to_h { |path| [path, [File.binread(path), File.stat(path).mtime]] }
    status, log, = execute(command)
    assert_equal 0, status
    assert_includes log, '"status":"no-op"'
    assert_equal 1, command.analyses
    assert_nil command.model_requests
    documents.each { |path| assert_equal before[path], [File.binread(path), File.stat(path).mtime] }
  end

  def test_body_with_work_before_return_refuses_without_fallback_or_outputs
    File.write(File.join(@source, 'main.go'), "package p\nfunc F() int { log(); return 7 }\n")
    command = Observed.new(@env)
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'Go source facts refused'
    assert_nil command.model_requests
    assert documents.none? { |path| File.exist?(path) }
  end

  def test_unanalyzed_callback_body_is_explicitly_limited
    File.write(File.join(@source, 'main.go'), "package p\nfunc F() func() { return func() { log(); write() } }\n")
    status, log, = execute
    assert_equal 0, status, log
    assert_includes File.read(documents.first), 'callback body is outside this profile and remains unanalyzed'
  end

  def test_questions_feedback_and_online_research_refuse_before_analysis
    variants = [@project.merge('question' => 'explain'), @project.merge('feedback' => { 'kind' => 'notes', 'text' => 'read source' })]
    variants.each do |project|
      @project = project
      command = Observed.new(@env)
      assert_equal 1, execute(command).first
      assert_nil command.analyses
      assert_nil command.model_requests
    end
    @project.delete('feedback')
    command = Observed.new(@env.merge('DOCS_RESEARCH' => 'public'))
    assert_equal 1, execute(command).first
    assert_nil command.analyses
    assert_nil command.model_requests
  end

  def test_human_edit_blocks_before_another_analysis
    command = Observed.new(@env)
    assert_equal 0, execute(command).first
    File.write(documents.first, 'human revision')
    File.write(File.join(@source, 'main.go'), @text.sub('helper(x)', 'other(x)'))
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'human edit'
    assert_equal 1, command.analyses
    assert_equal 'human revision', File.read(documents.first)
  end

  def test_changed_fact_is_not_relabelled_as_source_derived
    command = Observed.new(@env)
    command.mutate_fact = true
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'Go source-derived explanation or citation was changed'
    assert documents.none? { |path| File.exist?(path) }
    assert_nil command.model_requests
  end

  def test_source_change_after_analysis_prevents_writing_old_facts
    command = Observed.new(@env)
    command.mutate_source = true
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'source changed'
    assert documents.none? { |path| File.exist?(path) }
    assert_nil command.model_requests
  end

  def test_direct_return_tuple_preserves_expression_order
    File.write(File.join(@source, 'main.go'), "package p\nfunc F() (int,error) { return value, err }\n")
    status, log, = execute
    assert_equal 0, status, log
    en = File.read(documents.first)
    assert_includes en, 'source order: `value`, `err`'
  end

  def test_unsupported_markdown_or_oversized_signature_refuses_without_truncation
    sources = ["package p\nfunc F() string { return `raw` }\n",
      "package p\nfunc F(x #{'X' * 710}) int { return 7 }\n"]
    sources.each do |source|
      File.write(File.join(@source, 'main.go'), source)
      command = Observed.new(@env)
      status, log, = execute(command)
      assert_equal 1, status
      assert_includes log, 'Go source facts refused'
      assert_nil command.model_requests
      assert documents.none? { |path| File.exist?(path) }
    end
  end

  def test_type_context_is_not_silently_relabelled_as_return_facts
    File.write(File.join(@source, 'main.go'), "package p\ntype Record struct { Value int }\n")
    @project['units'] = { 'main.go' => ['Record'] }
    command = Observed.new(@env)
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'require function or method declarations'
    assert_nil command.model_requests
    assert documents.none? { |path| File.exist?(path) }
  end

  def test_model_request_reuse_is_rejected_in_source_only_profile
    @project['reuse_selected_unit_facts'] = true
    command = Observed.new(@env)
    assert_equal 1, execute(command).first
    assert_nil command.analyses
    assert_nil command.model_requests
  end
end
