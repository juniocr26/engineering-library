require 'bundler/setup'
require 'minitest/autorun'
require 'minitest/mock'
require 'tmpdir'
require_relative '../../lib/documentation/project_command'

class DocumentationProjectTest < Minitest::Test
  def fixture
    Dir.mktmpdir do |root|
      origin=root+'/origin';FileUtils.mkdir_p(origin);File.write(origin+'/main.rb',"LIMIT = 7\n")
      sections=%w[architecture configuration].map { |id| {'id'=>id,'titles'=>{'en'=>id,'pt-br'=>id},'files'=>['main.rb'],'ranges'=>{'main.rb'=>[[1,1]]},'question'=>'Explain the actual LIMIT declaration.'} }
      project={'slug'=>'sample','name'=>'Sample','source'=>origin,'source_revision'=>'a'*40,'sections'=>sections}
      path=root+'/plan.json';File.write(path,JSON.generate('schema'=>1,'projects'=>[project]))
      env={'DOCS_LIBRARY'=>root+'/library','DOCS_WORKSPACE'=>root+'/workspace','DOCS_CONTEXT'=>'baseline','DOCS_CONTEXT_TOKENS'=>'4096','DOCS_REQUEST_TIMEOUT'=>'60','DOCS_OLLAMA'=>'http://127.0.0.1:1'}
      yield root,project,path,env
    end
  end
  def stub_revision(revision='a'*40)
    success=Object.new;success.define_singleton_method(:success?) { true }
    Open3.stub(:capture3,[revision+"\n",'',success]) { yield }
  end
  def test_demonstratives_are_not_invented_type_names
    command=Documentation::Command.new
    card={'quote'=>"class OpenShotApp(QApplication):\n    pass\n"}
    refute command.invented_named_type?('OpenShotApp is declared here. This class initializes state.',card)
    refute command.invented_named_type?('OpenShotApp está declarada aqui. Essa classe inicializa o estado.',card)
    assert command.invented_named_type?('The class ForeignType initializes state.',card)
    assert command.invented_named_type?('The class This initializes state.',card)
  end
  def test_connection_failure_stops_before_another_section
    fixture do |root,project,path,env|
      code=nil;capture_io { stub_revision { code=Documentation::ProjectCommand.new(env).run(['--config',path]) } }
      assert_equal 3,code
      rows=JSON.parse(File.read(root+'/library/sample-progress.json'))
      assert_equal 1,rows.size
      assert_equal root+'/library/audits/sample/architecture.ndjson',rows.first['audit_log']
      assert File.file?(rows.first['audit_log'])
      assert_match(/ECONNREFUSED/,rows.first['transport_error'])
      refute File.exist?(root+'/workspace/sample/configuration')
      refute File.exist?(root+'/library/projects/sample/en.md')
    end
  end
  def test_changed_source_revision_stops_before_inference
    fixture do |root,project,path,env|
      code=nil;capture_io { stub_revision('b'*40) { code=Documentation::ProjectCommand.new(env).run(['--config',path]) } }
      assert_equal 1,code
      refute File.exist?(root+'/workspace/sample')
    end
  end
  def test_range_must_fit_the_original_source
    fixture do |_root,project,_path,env|
      command=Documentation::SectionCommand.new(env)
      specification=project.merge('files'=>['main.rb'],'ranges'=>{'main.rb'=>[[1,2]]})
      error=assert_raises(Documentation::Error) { command.evidence(specification) }
      assert_match(/range outside original source/,error.message)
    end
  end
  def test_reference_directory_cannot_be_used_as_explicit_source
    fixture do |root,project,_path,env|
      FileUtils.mkdir_p(project['source']+'/docs_codex');File.write(project['source']+'/docs_codex/reference.rb',"ANSWER = 7\n")
      specification=project.merge('files'=>['docs_codex/reference.rb'],'ranges'=>{'docs_codex/reference.rb'=>[[1,1]]})
      assert_raises(Documentation::Error) { Documentation::SectionCommand.new(env).evidence(specification) }
    end
  end
  def test_human_edited_staged_source_is_preserved
    fixture do |root,_project,path,env|
      capture_io { stub_revision { Documentation::ProjectCommand.new(env).run(['--config',path]) } }
      staged=root+'/workspace/sample/architecture/source/main.rb';File.write(staged,'human change')
      code=nil;capture_io { stub_revision { code=Documentation::ProjectCommand.new(env).run(['--config',path]) } }
      assert_equal 1,code
      assert_equal 'human change',File.read(staged)
    end
  end
  def test_assembly_keeps_facts_and_quotes_without_repeating_child_provenance
    fixture do |root,project,_path,env|
      FileUtils.mkdir_p(env['DOCS_LIBRARY'])
      child=root+'/child.md'
      File.write(child,"# Child draft\n\nCoverage: staging only\n\n## 1\n\nLIMIT is 7.\n\nSource: `main.rb:1`; SHA-256: `abc`.\n\n    LIMIT = 7\n")
      records=[{'id'=>'architecture','titles'=>{'en'=>'Architecture','pt-br'=>'Arquitetura'},'exit'=>0,'outputs'=>{'en'=>child,'pt-br'=>child}}]
      capture_io { Documentation::ProjectCommand.new(env).assemble(project,records,env['DOCS_LIBRARY']) }
      english=File.read(env['DOCS_LIBRARY']+'/projects/sample/en.md')
      portuguese=File.read(env['DOCS_LIBRARY']+'/projects/sample/pt-br.md')
      assert_includes english,"### 1\n\nLIMIT is 7."
      assert_includes english,'    LIMIT = 7'
      assert_includes english,'Source: `main.rb:1`; SHA-256: `abc`.'
      refute_includes english,'Coverage: staging only'
      assert_includes portuguese,'Revisão:'
    end
  end
  def test_both_languages_are_checked_before_first_assembly_write
    fixture do |root,project,_path,env|
      FileUtils.mkdir_p(env['DOCS_LIBRARY']);command=Documentation::ProjectCommand.new(env);records=[]
      command.assemble(project,records,env['DOCS_LIBRARY'])
      directory=env['DOCS_LIBRARY']+'/projects/sample';english=File.binread(directory+'/en.md');File.write(directory+'/pt-br.md','human Portuguese revision')
      assert_raises(Documentation::Error) { command.assemble(project,records,env['DOCS_LIBRARY']) }
      assert_equal english,File.binread(directory+'/en.md')
      assert_equal 'human Portuguese revision',File.read(directory+'/pt-br.md')
    end
  end
  def test_rejected_revision_does_not_replace_previous_assembly
    fixture do |_root,project,_path,env|
      FileUtils.mkdir_p(env['DOCS_LIBRARY']);command=Documentation::ProjectCommand.new(env);command.assemble(project,[],env['DOCS_LIBRARY'])
      path=env['DOCS_LIBRARY']+'/projects/sample/en.md';before=File.binread(path)
      capture_io { command.assemble(project,[{'exit'=>1}],env['DOCS_LIBRARY']) }
      assert_equal before,File.binread(path)
    end
  end

  def test_identical_assembly_preserves_output_and_manifest_mtimes
    fixture do |_root,project,_path,env|
      FileUtils.mkdir_p(env['DOCS_LIBRARY'])
      command=Documentation::ProjectCommand.new(env)
      capture_io { command.assemble(project,[],env['DOCS_LIBRARY']) }
      directory=env['DOCS_LIBRARY']+'/projects/sample'
      paths=%w[en.md pt-br.md assembly.json].map { |name| directory+'/'+name }
      paths.each { |path| File.utime(Time.at(100),Time.at(100),path) }
      before=paths.to_h { |path| [path,[File.binread(path),File.stat(path).mtime,File.stat(path).ino]] }
      output,_=capture_io { command.assemble(project,[],env['DOCS_LIBRARY']) }
      paths.each { |path| assert_equal before[path],[File.binread(path),File.stat(path).mtime,File.stat(path).ino] }
      assert_includes output,'project-draft-noop'
      refute File.exist?(directory+'/assembly.pending.json')
    end
  end

  def test_changed_language_preserves_unchanged_language_file
    fixture do |root,project,_path,env|
      FileUtils.mkdir_p(env['DOCS_LIBRARY'])
      english=root+'/english.md';portuguese=root+'/portuguese.md'
      File.write(english,"# Draft\n\n## 1\n\nLIMIT is 7.\n")
      File.write(portuguese,"# Rascunho\n\n## 1\n\nLIMIT vale 7.\n")
      records=[{'id'=>'configuration','titles'=>{'en'=>'Configuration','pt-br'=>'Configuração'},'exit'=>0,'outputs'=>{'en'=>english,'pt-br'=>portuguese}}]
      command=Documentation::ProjectCommand.new(env)
      capture_io { command.assemble(project,records,env['DOCS_LIBRARY']) }
      path=env['DOCS_LIBRARY']+'/projects/sample/en.md'
      File.utime(Time.at(100),Time.at(100),path)
      before=[File.binread(path),File.stat(path).mtime,File.stat(path).ino]
      File.write(portuguese,"# Rascunho\n\n## 1\n\nO valor de LIMIT é 7.\n")
      capture_io { command.assemble(project,records,env['DOCS_LIBRARY']) }
      assert_equal before,[File.binread(path),File.stat(path).mtime,File.stat(path).ino]
      assert_includes File.read(env['DOCS_LIBRARY']+'/projects/sample/pt-br.md'),'O valor de LIMIT é 7.'
    end
  end

  def test_interrupted_bilingual_reassembly_restores_unicode_bytes
    fixture do |root,project,_path,env|
      FileUtils.mkdir_p(env['DOCS_LIBRARY'])
      child=root+'/child.md';File.write(child,"# Draft\n\n## 1\n\nLIMIT is 7.\n")
      records=[{'id'=>'configuration','titles'=>{'en'=>'Configuration','pt-br'=>'Configuração'},'exit'=>0,'outputs'=>{'en'=>child,'pt-br'=>child}}]
      command=Documentation::ProjectCommand.new(env)
      capture_io { command.assemble(project,records,env['DOCS_LIBRARY']) }
      directory=env['DOCS_LIBRARY']+'/projects/sample'
      paths=%w[en.md pt-br.md].map { |name| directory+'/'+name }
      before=paths.to_h { |path| [path,File.binread(path)] }
      File.write(child,"# Draft\n\n## 1\n\nLIMIT is now 8.\n")
      guard=command.instance_variable_get(:@guard);atomic=guard.method(:atomic)
      replacement=lambda do |path,bytes|
        raise IOError,'simulated second-language write failure' if path==paths.last && bytes.include?('now 8')
        atomic.call(path,bytes)
      end
      guard.stub(:atomic,replacement) do
        assert_raises(IOError) { capture_io { command.assemble(project,records,env['DOCS_LIBRARY']) } }
      end
      paths.each { |path| assert_equal before[path],File.binread(path) }
      journal=JSON.parse(File.read(directory+'/assembly.pending.json'))
      assert_equal before[paths.last].force_encoding('UTF-8'),journal['before'][paths.last]
      assert_raises(Documentation::Error) { command.assemble(project,records,env['DOCS_LIBRARY']) }
    end
  end
  def pending_assembly_fixture(only_portuguese: false)
    fixture do |root,project,plan,env|
      FileUtils.mkdir_p(env['DOCS_LIBRARY'])
      english=root+'/english.md';portuguese=root+'/portuguese.md'
      File.write(english,"# Draft\n\n## 1\n\nLIMIT is 7.\n")
      File.write(portuguese,"# Rascunho\n\n## 1\n\nLIMIT é 7.\n")
      records=[{'id'=>'configuration','titles'=>{'en'=>'Configuration','pt-br'=>'Configuração'},'exit'=>0,'outputs'=>{'en'=>english,'pt-br'=>portuguese}}]
      command=Documentation::ProjectCommand.new(env)
      capture_io { command.assemble(project,records,env['DOCS_LIBRARY']) }
      directory=env['DOCS_LIBRARY']+'/projects/sample';paths=%w[en.md pt-br.md assembly.json].map { |name| directory+'/'+name }
      originals=paths.to_h { |path| [path,File.binread(path)] }
      File.write(english,"# Draft\n\n## 1\n\nLIMIT is 8.\n") unless only_portuguese
      File.write(portuguese,"# Rascunho\n\n## 1\n\nLIMIT é 8.\n")
      guard=command.instance_variable_get(:@guard);atomic=guard.method(:atomic)
      fail_manifest=lambda { |path,bytes| raise IOError,'manifest write interrupted' if path==paths.last;atomic.call(path,bytes) }
      guard.stub(:atomic,fail_manifest) { assert_raises(IOError) { capture_io { command.assemble(project,records,env['DOCS_LIBRARY']) } } }
      assert File.file?(directory+'/assembly.pending.json')
      assert_includes File.read(paths[1]),'LIMIT é 8.'
      yield root,project,plan,env,command,directory,paths,originals
    end
  end

  def recover_project(command,plan,strategy)
    code=nil;out,err=capture_io { code=command.run(['--config',plan,'--project','sample','--recover',strategy]) };[code,out,err]
  end

  def test_explicit_project_rollback_restores_both_languages_and_manifest_without_source
    pending_assembly_fixture do |_root,project,plan,_env,command,directory,paths,originals|
      FileUtils.remove_entry(project['source'])
      code,out,_=recover_project(command,plan,'rollback')
      assert_equal 0,code;assert_includes out,'project-assembly-recovered'
      paths.each { |path| assert_equal originals[path],File.binread(path) }
      refute File.exist?(directory+'/assembly.pending.json')
    end
  end

  def test_explicit_project_completion_commits_owned_candidate_and_matching_manifest
    pending_assembly_fixture do |_root,_project,plan,_env,command,directory,paths,_originals|
      assert_equal 0,recover_project(command,plan,'complete').first
      manifest=JSON.parse(File.read(paths.last))
      paths.first(2).each { |path| assert_equal Digest::SHA256.file(path).hexdigest,manifest['outputs'][path] }
      assert_includes File.read(paths[0]),'LIMIT is 8.'
      assert_includes File.read(paths[1]),'LIMIT é 8.'
      refute File.exist?(directory+'/assembly.pending.json')
    end
  end

  def test_project_recovery_preflights_human_edits_before_any_write
    pending_assembly_fixture do |_root,_project,plan,_env,command,directory,paths,_originals|
      File.write(paths[1],'Human Portuguese edit')
      before=(paths+[directory+'/assembly.pending.json']).to_h { |path| [path,[File.binread(path),File.stat(path).mtime,File.stat(path).ino]] }
      code,_,err=recover_project(command,plan,'rollback')
      assert_equal 1,code;assert_includes err,'human edit conflicts'
      before.each { |path,state| assert_equal state,[File.binread(path),File.stat(path).mtime,File.stat(path).ino] }
    end
  end

  def test_project_completion_rejects_human_edit_to_language_that_was_not_changed
    pending_assembly_fixture(only_portuguese:true) do |_root,_project,plan,_env,command,directory,paths,_originals|
      File.write(paths[0],'Human English edit')
      before=paths.to_h { |path| [path,File.binread(path)] }
      code,_,err=recover_project(command,plan,'complete')
      assert_equal 1,code;assert_includes err,'human edit to unchanged'
      before.each { |path,bytes| assert_equal bytes,File.binread(path) }
      assert File.file?(directory+'/assembly.pending.json')
    end
  end

  def test_interrupted_project_rollback_can_resume_from_mixed_owned_states
    pending_assembly_fixture do |_root,_project,plan,_env,command,directory,paths,originals|
      guard=command.instance_variable_get(:@guard);atomic=guard.method(:atomic)
      interrupt=lambda { |path,bytes| raise IOError,'recovery interrupted' if path==paths[1];atomic.call(path,bytes) }
      guard.stub(:atomic,interrupt) { assert_equal 1,recover_project(command,plan,'rollback').first }
      assert_equal originals[paths[0]],File.binread(paths[0])
      assert_includes File.read(paths[1]),'LIMIT é 8.'
      assert File.file?(directory+'/assembly.pending.json')
      assert_equal 0,recover_project(command,plan,'rollback').first
      paths.each { |path| assert_equal originals[path],File.binread(path) }
    end
  end

  def test_project_recovery_rejects_journal_paths_outside_its_owned_outputs
    pending_assembly_fixture do |root,_project,plan,_env,command,directory,paths,_originals|
      other=root+'/human.md';File.write(other,'Human content')
      pending=directory+'/assembly.pending.json';journal=JSON.parse(File.read(pending));journal['before'][other]='Human content';journal['candidate'][other]='Overwritten';File.write(pending,JSON.generate(journal))
      before=paths.to_h { |path| [path,File.binread(path)] }
      assert_equal 1,recover_project(command,plan,'complete').first
      assert_equal 'Human content',File.read(other)
      before.each { |path,bytes| assert_equal bytes,File.binread(path) }
      assert File.file?(pending)
    end
  end

  def test_project_recovery_rejects_legacy_journal_and_invalid_strategy
    pending_assembly_fixture do |_root,_project,plan,_env,command,directory,paths,_originals|
      pending=directory+'/assembly.pending.json';journal=JSON.parse(File.read(pending));journal.delete('schema');File.write(pending,JSON.generate(journal))
      before=paths.to_h { |path| [path,File.binread(path)] }
      code,_,err=recover_project(command,plan,'rollback');assert_equal 1,code;assert_includes err,'legacy project journal'
      assert_equal 1,recover_project(command,plan,'discard').first
      before.each { |path,bytes| assert_equal bytes,File.binread(path) }
    end
  end

  def test_project_recovery_preserves_unchanged_english_mtime_and_inode
    pending_assembly_fixture(only_portuguese:true) do |_root,_project,plan,_env,command,_directory,paths,_originals|
      File.utime(Time.at(100),Time.at(100),paths[0]);before=[File.binread(paths[0]),File.stat(paths[0]).mtime,File.stat(paths[0]).ino]
      assert_equal 0,recover_project(command,plan,'complete').first
      assert_equal before,[File.binread(paths[0]),File.stat(paths[0]).mtime,File.stat(paths[0]).ino]
    end
  end

  def test_project_recovery_detects_human_edit_arriving_after_preflight
    pending_assembly_fixture(only_portuguese:true) do |_root,_project,plan,_env,command,directory,paths,_originals|
      guard=command.instance_variable_get(:@guard);atomic=guard.method(:atomic)
      edit=lambda do |path,bytes|
        atomic.call(path,bytes)
        File.write(paths[0],'Concurrent human English edit') if path==paths[1]
      end
      guard.stub(:atomic,edit) { assert_equal 1,recover_project(command,plan,'rollback').first }
      assert_equal 'Concurrent human English edit',File.read(paths[0])
      assert File.file?(directory+'/assembly.pending.json')
    end
  end

  def test_initial_project_rollback_removes_only_its_new_owned_files
    fixture do |root,project,plan,env|
      FileUtils.mkdir_p(env['DOCS_LIBRARY']);child=root+'/child.md';File.write(child,"# Draft\n\n## 1\n\nLIMIT is 7.\n")
      records=[{'id'=>'configuration','titles'=>{'en'=>'Configuration','pt-br'=>'Configuração'},'exit'=>0,'outputs'=>{'en'=>child,'pt-br'=>child}}]
      command=Documentation::ProjectCommand.new(env);directory=env['DOCS_LIBRARY']+'/projects/sample';guard=command.instance_variable_get(:@guard);atomic=guard.method(:atomic)
      fail_manifest=lambda { |path,bytes| raise IOError,'initial manifest interrupted' if path==directory+'/assembly.json';atomic.call(path,bytes) }
      guard.stub(:atomic,fail_manifest) { assert_raises(IOError) { capture_io { command.assemble(project,records,env['DOCS_LIBRARY']) } } }
      File.write(directory+'/human.md','Preserve human note')
      assert_equal 0,recover_project(command,plan,'rollback').first
      %w[en.md pt-br.md assembly.json assembly.pending.json].each { |name| refute File.exist?(directory+'/'+name) }
      assert_equal 'Preserve human note',File.read(directory+'/human.md')
    end
  end

  def test_project_native_heading_targets_preserve_accents_and_duplicate_slug_collisions
    command=Documentation::ProjectCommand.new
    text="# Sample\n\n## Contents\n\n<!-- reading-section: project-section-a -->\n## Configuração & opções\n\n### 1\n\n<!-- reading-section: project-section-b -->\n## Configuração & opções\n\n<!-- reading-section: project-section-c -->\n## Configuração  opções-1\n"
    assert_equal({'project-section-a'=>'configuração--opções','project-section-b'=>'configuração--opções-1','project-section-c'=>'configuração--opções-1-1'},command.project_heading_targets(text))
  end

  def test_project_index_uses_native_headings_and_existing_canonical_reading_sections
    fixture do |root,project,_path,env|
      FileUtils.mkdir_p(env['DOCS_LIBRARY']);child=root+'/child.md';File.write(child,"# Draft\n\n## 1\n\nLIMIT is 7.\n\n    ## Not a heading\n")
      records=[{'id'=>'configuration','titles'=>{'en'=>'Configuration and options','pt-br'=>'Configuração e opções'},'exit'=>0,'outputs'=>{'en'=>child,'pt-br'=>child}}]
      capture_io { Documentation::ProjectCommand.new(env).assemble(project,records,env['DOCS_LIBRARY']) }
      %w[en pt-br].each do |lang|
        text=File.read(env['DOCS_LIBRARY']+'/projects/sample/'+lang+'.md')
        target=lang=='en' ? 'configuration-and-options' : 'configuração-e-opções'
        assert_includes text,"](##{target})"
        assert_includes text,'<!-- reading-section: project-section-configuration -->'
        refute_includes text,'<a id='
        assert_includes text,'    ## Not a heading'
      end
    end
  end

  def test_formatted_owner_titles_preserve_legacy_assembly_without_an_invented_target
    fixture do |root,project,_path,env|
      FileUtils.mkdir_p(env['DOCS_LIBRARY']);child=root+'/child.md';File.write(child,"# Draft\n\n## 1\n\nLIMIT is 7.\n")
      records=[{'id'=>'configuration','titles'=>{'en'=>'Configuration [options]','pt-br'=>'Configuração [opções]'},'exit'=>0,'outputs'=>{'en'=>child,'pt-br'=>child}}]
      capture_io { Documentation::ProjectCommand.new(env).assemble(project,records,env['DOCS_LIBRARY']) }
      text=File.read(env['DOCS_LIBRARY']+'/projects/sample/en.md')
      refute_includes text,'project-contents-placeholder'
      refute_includes text,'## Contents'
      assert_includes text,'## Configuration [options]'
    end
  end

end
