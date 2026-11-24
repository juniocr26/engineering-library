require 'bundler/setup'
require 'minitest/autorun'
require 'minitest/mock'
require 'tmpdir'
require 'fileutils'
require 'socket'
require_relative '../../lib/documentation/command'

class DocumentationAttemptPreservationTest < Minitest::Test
  class FixtureCommand < Documentation::Command
    attr_reader :infer_calls
    attr_accessor :invalid, :change_source, :fail_input

    def infer(files, _skills)
      @infer_calls = (@infer_calls || 0) + 1
      audit('fixture_provider', { 'source_sha256' => files.transform_values { |value| digest(value) }, 'real_model_calls' => 0 })
      result = if invalid
        { 'unexpected' => 'original invalid provider value' }
      else
        { 'facts' => [{ 'evidence_id' => 'S1',
          'en' => '`Widget.answer` returns the literal `7` in the selected source body.',
          'pt-br' => '`Widget.answer` retorna o literal `7` no corpo selecionado da fonte.' }] }
      end
      File.write(change_source, File.read(change_source).sub('return 7', 'return 8')) if change_source
      { 'result' => result, 'request' => { 'fixture' => true }, 'response' => { 'fixture' => true } }
    end

    def preserve_attempt_artifact(name, payload)
      raise IOError, 'synthetic input persistence failure' if fail_input && name == 'generation-input.json'
      super
    end
  end

  class TransportFixtureCommand < FixtureCommand
    def infer(files, skills)
      Documentation::Command.instance_method(:infer).bind_call(self, files, skills)
    end

    def verify_model_identity(_body)
      { 'fixture' => 'isolated loopback HTTP response; not Ollama/model inference' }
    end
  end

  def setup
    @root = Dir.mktmpdir('documentation-attempt-preservation-')
    @library = File.join(@root, 'library')
    @source = File.join(@root, 'source')
    FileUtils.mkdir_p([@library, File.join(@source, 'docs')])
    @text = "class Widget:\n    def answer(self):\n        return 7\n"
    File.write(File.join(@source, 'main.py'), @text)
    @project = { 'slug' => 'sample', 'source' => @source, 'destination' => File.join(@source, 'docs'),
      'lifecycle' => 'temporary', 'files' => ['main.py'], 'units' => { 'main.py' => ['Widget.answer'] } }
    @config = File.join(@root, 'plan.json')
    @env = { 'DOCS_LIBRARY' => @library, 'DOCS_SOURCES' => @root,
      'DOCS_AGENT' => File.join(@root, 'absent-agent'), 'DOCS_CONTEXT' => 'baseline' }
  end

  def teardown
    FileUtils.remove_entry(@root)
  end

  def execute(command, projects = [@project])
    File.write(@config, JSON.generate('projects' => projects))
    status = nil
    out, err = capture_io { status = command.run(['--config', @config]) }
    [status, out, err]
  end

  def runs
    Dir[File.join(@library, '.docs-state/evaluations/runs/*')].sort
  end

  def read_artifact(name, run = runs.fetch(0))
    file = File.join(run, name)
    assert File.file?(file), "missing retained artifact #{name}"
    JSON.parse(File.read(file))
  end

  def events(run = runs.fetch(0))
    file = File.join(run, 'generation-events.ndjson')
    assert File.file?(file), 'missing private generation event stream'
    File.readlines(file).map { |line| JSON.parse(line) }
  end

  def document
    File.join(@library, '.evaluations/sample/en', Documentation::Command::DOCUMENT)
  end

  def test_disabled_console_audit_still_retains_private_exact_inputs_and_result
    command = FixtureCommand.new(@env)
    status, log, = execute(command)
    assert_equal 0, status
    assert_equal 1, command.infer_calls
    input = read_artifact('generation-input.json')
    assert_equal @text, input.fetch('source_snapshot').fetch('files').fetch('main.py')
    assert_equal 'baseline', input.fetch('context')
    assert_equal Documentation::Command::VERSION, input.fetch('caller_version')
    result = read_artifact('generation-result.json')
    assert_equal true, result.fetch('request').fetch('fixture')
    assert_equal 'S1', result.fetch('result').fetch('facts').first.fetch('evidence_id')
    assert events.any? { |event| event['event'] == 'evidence_snapshot' }
    assert events.any? { |event| event['event'] == 'fixture_provider' }
    refute_includes log, '"event":"evidence_snapshot"'
    refute_includes log, 'return 7'
    %w[generation-input.json generation-result.json generation-events.ndjson].each do |name|
      assert_equal 0o600, File.stat(File.join(runs.first, name)).mode & 0o777
    end
    assert_equal 0o700, File.stat(runs.first).mode & 0o777
    assert_nil command.instance_variable_get(:@attempt_directory)
  end

  def test_rejected_result_is_retained_before_validation_without_replacing_documents
    command = FixtureCommand.new(@env)
    command.invalid = true
    assert_equal 1, execute(command).first
    assert_equal({ 'unexpected' => 'original invalid provider value' }, read_artifact('generation-result.json')['result'])
    assert_equal @text, read_artifact('generation-input.json')['source_snapshot']['files']['main.py']
    assert events.any? { |event| event['event'] == 'generation_rejected' }
    refute File.exist?(document)
    assert_nil command.instance_variable_get(:@attempt_directory)
  end

  def test_noop_does_not_create_or_touch_attempt_artifacts
    command = FixtureCommand.new(@env)
    assert_equal 0, execute(command).first
    before = Dir[File.join(runs.first, '*')].to_h { |file| [file, [File.binread(file), File.stat(file).mtime]] }
    assert_equal 1, runs.size
    status, log, = execute(command)
    assert_equal 0, status
    assert_includes log, '"status":"no-op"'
    assert_equal 1, command.infer_calls
    assert_equal 1, runs.size
    assert_equal before, before.keys.to_h { |file| [file, [File.binread(file), File.stat(file).mtime]] }
    assert_nil command.instance_variable_get(:@attempt_directory)
  end

  def test_human_edit_blocks_before_new_attempt_or_inference
    command = FixtureCommand.new(@env)
    assert_equal 0, execute(command).first
    File.write(document, 'owner annotation')
    File.write(File.join(@source, 'main.py'), @text.sub('return 7', 'return 8'))
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'human edit'
    assert_equal 1, command.infer_calls
    assert_equal 1, runs.size
    assert_equal 'owner annotation', File.read(document)
    assert_nil command.instance_variable_get(:@attempt_directory)
  end

  def test_input_persistence_failure_stops_before_inference
    command = FixtureCommand.new(@env)
    command.fail_input = true
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'synthetic input persistence failure'
    assert_nil command.infer_calls
    refute File.exist?(document)
    assert_nil command.instance_variable_get(:@attempt_directory)
  end

  def test_source_change_after_inference_preserves_original_inputs_and_result
    command = FixtureCommand.new(@env)
    command.change_source = File.join(@source, 'main.py')
    status, log, = execute(command)
    assert_equal 1, status
    assert_includes log, 'source changed during inference'
    assert_equal @text, read_artifact('generation-input.json')['source_snapshot']['files']['main.py']
    assert_equal true, read_artifact('generation-result.json')['response']['fixture']
    refute File.exist?(document)
    assert_nil command.instance_variable_get(:@attempt_directory)
  end

  def test_multi_project_attempt_context_does_not_leak_to_the_next_project
    second_source = File.join(@root, 'second')
    FileUtils.mkdir_p(File.join(second_source, 'docs'))
    File.write(File.join(second_source, 'main.py'), @text)
    second = @project.merge('slug' => 'second', 'source' => second_source, 'destination' => File.join(second_source, 'docs'))
    command = FixtureCommand.new(@env)
    assert_equal 0, execute(command, [@project, second]).first
    assert_equal 2, runs.size
    assert_equal %w[sample second], runs.map { |run| read_artifact('generation-input.json', run)['project_slug'] }.sort
    runs.each { |run| assert_equal 1, events(run).count { |event| event['event'] == 'fixture_provider' } }
    assert_nil command.instance_variable_get(:@attempt_directory)
  end

  def test_existing_attempt_directory_is_not_overwritten_on_name_collision
    old = File.join(@library, '.docs-state/evaluations/runs/sample-collision')
    FileUtils.mkdir_p(old)
    marker = File.join(old, 'generation-input.json')
    File.write(marker, 'valuable prior attempt')
    command = FixtureCommand.new(@env)
    status = nil
    SecureRandom.stub(:hex, 'collision') { status = execute(command).first }
    assert_equal 1, status
    assert_nil command.infer_calls
    assert_equal 'valuable prior attempt', File.read(marker)
    refute File.exist?(File.join(old, 'generation-events.ndjson'))
    refute File.exist?(document)
    assert_nil command.instance_variable_get(:@attempt_directory)
  end

  def with_http_response(body)
    server = TCPServer.new('127.0.0.1', 0)
    port = server.addr[1]
    worker = Thread.new do
      connection = server.accept
      headers = +''
      headers << connection.read(1) until headers.end_with?("\r\n\r\n")
      size = headers[/Content-Length: (\d+)/i, 1].to_i
      connection.read(size) if size > 0
      connection.write("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: #{body.bytesize}\r\nConnection: close\r\n\r\n".b + body.b)
      connection.close
    end
    yield port
    assert worker.join(3), 'loopback fixture did not finish'
  ensure
    server.close if server
    worker.kill if worker&.alive?
  end

  def test_invalid_utf8_transport_body_survives_with_audit_disabled
    raw = "\xFF{invalid".b
    with_http_response(raw) do |port|
      command = TransportFixtureCommand.new(@env.merge('DOCS_OLLAMA' => "http://127.0.0.1:#{port}"))
      status, log, = execute(command)
      assert_equal 1, status
      assert_includes log, 'invalid UTF-8'
      response = events.find { |event| event['event'] == 'model_response' }.fetch('payload')
      assert_equal raw, response.fetch('body_base64').unpack1('m0')
      assert_equal Digest::SHA256.hexdigest(raw), response.fetch('historical_original_body_sha256')
      assert_nil response['body']
      assert_equal @text, read_artifact('generation-input.json')['source_snapshot']['files']['main.py']
      refute File.exist?(document)
      refute File.exist?(File.join(runs.first, 'generation-result.json'))
      assert_nil command.instance_variable_get(:@attempt_directory)
    end
  end
end
