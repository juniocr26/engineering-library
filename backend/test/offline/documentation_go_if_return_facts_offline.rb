require 'bundler/setup'
require 'minitest/autorun'
require 'tmpdir'
require 'fileutils'
require_relative '../../lib/documentation/go_if_return_fact_command'

class DocumentationGoIfReturnFactsTest < Minitest::Test
  class Observed < Documentation::GoIfReturnFactCommand
    attr_accessor :change_fact, :change_source, :foreign_call, :foreign_type
    attr_reader :analyses, :model_calls
    def infer(files, skills)
      @analyses = (@analyses || 0) + 1
      result = super
      fact = result['result']['facts'].first
      fact['en'] += ' Changed.' if change_fact
      fact['en'].sub!('s.Parent.Value(x)', 'Other.Value(x)') if foreign_call
      fact['en'].sub!('driver.Value', 'other.Value') if foreign_type
      if change_source
        path = File.join(@env.fetch('DOCS_SOURCES'), 'project/main.go')
        File.write(path, File.read(path).sub('!s.Valid', 's.Valid'))
      end
      result
    end
    def call_model(_body)
      @model_calls = (@model_calls || 0) + 1
      raise 'unexpected model transport'
    end
  end

  def setup
    @root = Dir.mktmpdir('documentation-go-if-return-')
    @source = File.join(@root, 'project')
    @library = File.join(@root, 'library')
    FileUtils.mkdir_p([File.join(@source, 'docs'), @library])
    @body = 'if !s.Valid { return nil, nil }; return s.Parent.Value(x)'
    write_source
    @project = { 'slug' => 'if-return-facts', 'source' => @source, 'destination' => File.join(@source, 'docs'),
      'lifecycle' => 'temporary', 'files' => ['main.go'], 'units' => { 'main.go' => ['State.Value'] } }
    agent = File.expand_path('../../../agent', __dir__)
    agent = '/agent' unless File.directory?(agent)
    @env = { 'DOCS_LIBRARY' => @library, 'DOCS_SOURCES' => @root,
      'DOCS_AGENT' => agent, 'DOCS_CONTEXT' => 'baseline' }
  end

  def teardown
    FileUtils.remove_entry(@root)
  end

  def write_source(body = @body)
    # Deliberately lacks type/import definitions: this is syntax, not compilation.
    File.write(File.join(@source, 'main.go'), "package p\nfunc (s *State) Value(x any) (driver.Value, error) {\n#{body}\n}\n")
  end

  def execute(command = Observed.new(@env))
    config = File.join(@root, 'config.json')
    File.write(config, JSON.generate('projects' => [@project]))
    status = nil
    out, = capture_io { status = command.run(['--config', config]) }
    [status, out]
  end

  def documents
    %w[en pt-br].map { |lang| File.join(@library, '.evaluations/if-return-facts', lang, Documentation::Command::DOCUMENT) }
  end

  def test_exact_guard_signature_same_named_callee_and_bilingual_origin_without_model
    command = Observed.new(@env)
    status, log = execute(command)
    assert_equal 0, status, log
    assert_nil command.model_calls
    en, pt = documents.map { |file| File.read(file) }
    assert_includes en, '`!s.Valid`'
    assert_includes en, '`func(x any) (driver.Value, error)`'
    assert_includes en, '`s.Parent.Value(x)`'
    assert_includes en, 'If the test completes false'
    assert_includes en, 'do not establish the number of values returned by a helper call'
    assert_includes en, 'model inference: not invoked'
    assert_equal en.scan(/`([^`\r\n]+)`/), pt.scan(/`([^`\r\n]+)`/)
    state = JSON.parse(File.read(File.join(@library, '.docs-state/evaluations/if-return-facts.json')))
    assert_equal 'go-if-return-fallthrough-syntax-v2', state['coverage']['source_analysis']['profile']
    assert_equal false, state['coverage']['source_analysis']['model_inference']
    before = documents.to_h { |path| [path, [File.binread(path), File.stat(path).mtime]] }
    assert_equal 0, execute(command).first
    assert_equal 1, command.analyses
    assert_equal before, documents.to_h { |path| [path, [File.binread(path), File.stat(path).mtime]] }
  end

  def test_changed_source_while_deriving_is_refused_before_write
    command = Observed.new(@env); command.change_source = true
    status, log = execute(command)
    assert_equal 1, status
    assert_includes log, 'source changed'
    documents.each { |path| refute File.exist?(path) }
    assert_nil command.model_calls
  end

  def test_changed_immutable_prose_is_refused
    # Use a declaration name distinct from Value, so the independent immutable
    # origin check is reached without the earlier same-name owner rejection.
    path = File.join(@source, 'main.go')
    File.write(path, File.read(path).sub(') Value(', ') Read('))
    @project['units']['main.go'] = ['State.Read']
    command = Observed.new(@env); command.change_fact = true
    status, log = execute(command)
    assert_equal 1, status
    assert_includes log, 'source-derived explanation or citation was changed'
    documents.each { |path| refute File.exist?(path) }
  end

  def test_wrong_same_named_helper_owner_is_not_exempted
    command = Observed.new(@env); command.foreign_call = true
    status, log = execute(command)
    assert_equal 1, status
    assert_includes log, 'different owner'
    documents.each { |path| refute File.exist?(path) }
  end

  def test_invented_type_in_signature_is_not_exempted
    command = Observed.new(@env); command.foreign_type = true
    status, log = execute(command)
    assert_equal 1, status
    assert_includes log, 'different owner'
    documents.each { |path| refute File.exist?(path) }
  end

  def test_initializer_else_and_extra_statement_are_safely_refused
    [
      'if v := s.Valid; v { return nil, nil }; return s.Parent.Value(x)',
      'if s.Valid { return nil, nil } else { return s.Parent.Value(x) }; return nil, nil',
      's.prepare(); if s.Valid { return nil, nil }; return s.Parent.Value(x)'
    ].each do |body|
      write_source(body)
      command = Observed.new(@env)
      status, log = execute(command)
      assert_equal 1, status
      assert_includes log, 'outside bounded if-return/fallthrough profile'
      assert_nil command.model_calls
      documents.each { |path| refute File.exist?(path) }
    end
  end

  def test_question_and_model_cache_remain_outside_source_fact_profile
    @project['question'] = 'Explain the source condition.'
    command = Observed.new(@env)
    status, log = execute(command)
    assert_equal 1, status
    assert_includes log, 'reject questions and feedback'
    assert_nil command.analyses
    @project.delete('question'); @project['reuse_selected_unit_facts'] = true
    status, log = execute(Observed.new(@env))
    assert_equal 1, status
    assert_includes log, 'model-fact reuse'
  end

  def test_three_guard_chain_records_order_and_fallthrough_without_model_and_then_noops
    write_source('if x == 0 { return s.Fallback }; if x < 1 { return 1 }; if x > 100 { return 100 }; return x')
    command = Observed.new(@env)
    status, log = execute(command)
    assert_equal 0, status, log
    assert_nil command.model_calls
    en, pt = documents.map { |file| File.read(file) }
    assert_includes en, 'Only if preceding tests complete false'
    assert_includes en, 'If all tests complete false'
    assert_includes pt, 'Somente se os testes anteriores terminarem falsos'
    assert_includes en, 'do not prove name bindings'
    assert_operator en.index('`x == 0`'), :<, en.index('`x < 1`')
    assert_operator en.index('`x < 1`'), :<, en.index('`x > 100`')
    assert_equal en.scan(/`([^`\r\n]+)`/), pt.scan(/`([^`\r\n]+)`/)
    before = documents.to_h { |path| [path, [File.binread(path), File.stat(path).mtime]] }
    assert_equal 0, execute(command).first
    assert_equal 1, command.analyses
    assert_equal before, documents.to_h { |path| [path, [File.binread(path), File.stat(path).mtime]] }
  end

  def test_two_guard_chain_permits_only_exact_same_named_callees_in_verified_prose
    write_source('if s.Parent.Value(x) { return s.Parent.Value(x) }; if !s.Valid { return nil, nil }; return s.Other.Value(x)')
    command = Observed.new(@env)
    status, log = execute(command)
    assert_equal 0, status, log
    assert_includes File.read(documents.first), '`s.Parent.Value(x)`'
    assert_includes File.read(documents.first), '`s.Other.Value(x)`'
    assert_nil command.model_calls
    before = documents.to_h { |path| [path, [File.binread(path), File.stat(path).mtime]] }
    write_source('if s.Parent.Value(x) { return s.Parent.Value(x) }; if s.Valid { return nil, nil }; return s.Other.Value(x)')
    command.foreign_call = true
    assert_equal 1, execute(command).first
    assert_equal before, documents.to_h { |path| [path, [File.binread(path), File.stat(path).mtime]] }
    assert_nil command.model_calls
  end

  def test_unsupported_changed_chains_preserve_owned_outputs_and_guard_reorder_invalidates
    write_source('if x == 0 { return 7 }; if x < 1 { return 1 }; return x')
    command = Observed.new(@env)
    status, log = execute(command)
    assert_equal 0, status, log
    write_source('if x < 1 { return 1 }; if x == 0 { return 7 }; return x')
    assert_equal 0, execute(command).first
    assert_equal 2, command.analyses
    en = File.read(documents.first)
    assert_operator en.index('`x < 1`'), :<, en.index('`x == 0`')
    owned = [File.join(@library, '.evaluations/if-return-facts'), File.join(@source, 'docs')].flat_map do |root|
      Dir[File.join(root, '**', '*.md')]
    end
    assert_equal 8, owned.size
    before = owned.to_h { |path| [path, [File.binread(path), File.stat(path).mtime]] }
    [
      'if a { return 0 }; if b { return 1 }; if c { return 2 }; if d { return 3 }; return x',
      'if a { return 0 }; if b := x; b > 1 { return 1 }; return x',
      'if a { return 0 }; if b { return 1 } else { return 2 }; return x',
      'if a { return 0 }; prepare(); if b { return 1 }; return x'
    ].each do |body|
      write_source(body)
      assert_equal 1, execute(command).first
      assert_equal before, owned.to_h { |path| [path, [File.binread(path), File.stat(path).mtime]] }
      assert_nil command.model_calls
    end
  end

  def test_guard_chain_with_line_directive_keeps_original_physical_citation
    write_source('if x == 0 { return 7 }; if x < 1 { return 1 }; return x')
    path = File.join(@source, 'main.go')
    File.write(path, File.read(path).sub("package p\n", "package p\n//line logical.go:700\n"))
    command = Observed.new(@env)
    status, log = execute(command)
    assert_equal 0, status, log
    en = File.read(documents.first)
    assert_includes en, 'main.go:3'
    refute_includes en, 'logical.go:700'
    assert_nil command.model_calls
  end
end
