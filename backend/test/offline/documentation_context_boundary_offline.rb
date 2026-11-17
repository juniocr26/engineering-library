require 'bundler/setup'
require 'minitest/autorun'
require 'tmpdir'
require 'fileutils'
require_relative '../../lib/documentation/command'
class DocumentationContextBoundaryTest < Minitest::Test
  class CapturingCommand < Documentation::Command
    attr_reader :request
    def call_model(body)
      @request = body
      { 'result' => { 'facts' => [] } }
    end
  end
  def setup
    @root=Dir.mktmpdir
    @command=CapturingCommand.new('DOCS_CONTEXT'=>'baseline')
    @project={'source'=>@root}
  end
  def teardown
    FileUtils.remove_entry(@root)
  end
  def write(path,bytes)
    dest=File.join(@root,path);FileUtils.mkdir_p(File.dirname(dest));File.write(dest,bytes)
  end
  def test_native_game_languages_reach_actual_model_context
    write('engine/World.cs', 'public class World { public int Tick() { return 17; } }')
    write('game/main.gd', "extends Node\nfunc _ready():\n    print(19)\n")
    snapshot=@command.evidence(@project)
    assert_equal %w[engine/World.cs game/main.gd],snapshot['files'].keys.sort
    @command.infer(snapshot['files'],'')
    context=JSON.generate(@command.request)
    assert_includes context,'class World'
    assert_includes context,'extends Node'
  end
  def test_reviewer_and_expected_answers_do_not_reach_captured_context
    write('main.py', 'LIMIT = 7')
    %w[docs_codex docs_backup-2026 reviewer-feedback reviewer_feedback expected-outputs expected_outputs comparison-summaries comparison_summary evaluation-answers codex-reference].each do |dir|
      write("#{dir}/answer.py", 'LEAKAGE_SENTINEL = 99')
    end
    %w[reviewer-feedback.py expected_outputs.py comparison-summary.rb evaluation_answers.cs codex-reference.gd].each { |file| write(file,'LEAKAGE_SENTINEL = 99') }
    snapshot=@command.evidence(@project)
    assert_equal ['main.py'],snapshot['files'].keys
    @command.infer(snapshot['files'],'')
    refute_includes JSON.generate(@command.request),'LEAKAGE_SENTINEL'
  end
  def test_explicit_file_list_cannot_bypass_exclusion
    write('expected-outputs/answer.cs','public class Expected { }')
    assert_raises(Documentation::Error) { @command.evidence(@project.merge('files'=>['expected-outputs/answer.cs'])) }
  end
  def test_ordinary_expected_value_logic_remains_eligible
    write('src/expected_value.cs','public class ExpectedValue { }')
    assert_equal ['src/expected_value.cs'],@command.evidence(@project)['files'].keys
  end
end
