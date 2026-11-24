require 'bundler/setup'
require 'minitest/autorun'
require 'tmpdir'
require 'fileutils'
require_relative '../../lib/documentation/command'
class DocumentationContextLimitsTest < Minitest::Test
  class FixtureCommand < Documentation::Command
    attr_reader :count
    def infer(files, skills)
      @count=(@count||0)+1
      result={'facts'=>[{'evidence_id'=>'S1','en'=>'LIMIT declares the constant value 7 in this source fixture.','pt-br'=>'LIMIT declara o valor constante 7 neste exemplo de código.'}]}
      {'result'=>result,'request'=>{},'response'=>result}
    end
  end
  def test_reduced_context_refuses_oversized_prompt_before_transport
    command=Documentation::Command.new('DOCS_CONTEXT_TOKENS'=>'4096')
    error=assert_raises(Documentation::Error) { command.call_model(messages:[{role:'user',content:'x'*4096}],options:{}) }
    assert_includes error.message,'reduced-context byte budget'
  end
  def test_invalid_context_refuses_work_before_creating_state
    Dir.mktmpdir do |root|
      command=Documentation::Command.new('DOCS_LIBRARY'=>root,'DOCS_CONTEXT_TOKENS'=>'0')
      capture_io { assert_equal 1,command.run([]) }
      refute File.exist?(root+'/.docs-state')
    end
  end
  def test_context_changes_invalidate_no_op_but_stable_profile_does_not
    Dir.mktmpdir do |root|
      library=root+'/library';source=root+'/project';FileUtils.mkdir_p(library);FileUtils.mkdir_p(source+'/docs')
      File.write(source+'/main.rb',"LIMIT = 7\n")
      config=root+'/config.json';File.write(config,JSON.generate('projects'=>[{'slug'=>'sample','source'=>source,'destination'=>source+'/docs','files'=>['main.rb']}]))
      env={'DOCS_LIBRARY'=>library,'DOCS_CONTEXT'=>'baseline','DOCS_CONTEXT_TOKENS'=>'4096'}
      command=FixtureCommand.new(env);capture_io { assert_equal 0,command.run(['--config',config]) };assert_equal 1,command.count
      command=FixtureCommand.new(env);capture_io { assert_equal 0,command.run(['--config',config]) };assert_nil command.count
      command=FixtureCommand.new(env.merge('DOCS_CONTEXT_TOKENS'=>'8192'));capture_io { assert_equal 0,command.run(['--config',config]) };assert_equal 1,command.count
    end
  end
  def test_csharp_complete_method_has_dot_qualified_identity
    command=Documentation::Command.new
    text="namespace Game {\npublic readonly struct WDist {\npublic static WDist FromCells(int cells) { return new WDist(1024 * cells); }\n}\n}\n"
    card=command.source_units('WDist.cs',text,['WDist.FromCells']).values.first
    assert_equal 'Game.WDist.FromCells',card['qualified_symbol']
    assert_equal 'WDist',card['enclosing_impl_hint']
    assert_equal true,card['complete_unit']
  end
end
