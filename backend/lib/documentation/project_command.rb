# frozen_string_literal: true
require_relative 'command'
require 'stringio'

module Documentation
  # Explicit source ranges retain original bytes/lines; they are not complete AST units.
  class SectionCommand < Command
    EVIDENCE_VERSION = '1.0.1'
    attr_reader :transport_error
    EXTRA_MANIFESTS = %w[CMakeLists.txt CMakeOptions.txt SConstruct Makefile Directory.Build.props Directory.Build.targets Directory.Packages.props global.json].freeze
    def evidence(project)
      @unit_selection = project.fetch('units', {})
      @ranges = project.fetch('ranges', {})
      files = {}
      project.fetch('files').each do |relative|
        raise Error, 'excluded section evidence' if relative.split('/').any? { |part| excluded_source_name?(part) }
        allowed = EXTENSIONS.include?(File.extname(relative)) || EXTRA_MANIFESTS.include?(File.basename(relative)) || %w[.csproj .props .cmake].include?(File.extname(relative))
        raise Error, 'unsupported section source extension' unless allowed
        path = File.join(project.fetch('source'), relative)
        safe_directory(File.dirname(path), create: false)
        raise Error, 'unsafe section source' if File.symlink?(path) || !File.file?(path) || File.size(path) > 2_097_152
        text = File.binread(path).force_encoding('UTF-8')
        raise Error, 'unsafe section source content' unless text.valid_encoding? && !text.include?("\x00") && !credential_literal?(text, File.extname(relative))
        files[relative] = text
      end
      cards = evidence_cards(files)
      raise Error, 'empty section source selection' if cards.empty?
      { 'files' => files, 'candidate_count' => files.size, 'omitted_count' => 0,
        'selection' => 'explicit project section; counts apply only to staged files, not whole repository coverage',
        'range_selection' => @ranges, 'unit_selection' => @unit_selection,
        'selected_context_bytes' => cards.values.sum { |card| card.fetch('quote').bytesize },
        'section_workflow_version' => EVIDENCE_VERSION }
    end
    def evidence_cards(files)
      cards = {}
      files.each do |path,text|
        selected = if @unit_selection && @unit_selection[path]
          source_units(path,text,@unit_selection[path]).values
        else
          ranges = @ranges.fetch(path) { raise Error, 'section source needs explicit ranges or units' }
          raise Error, 'invalid bounded range list' unless ranges.is_a?(Array) && (1..4).cover?(ranges.size)
          lines = text.lines
          ranges.map do |pair|
            valid = pair.is_a?(Array) && pair.size == 2 && pair.all? { |n| n.is_a?(Integer) } && pair[0] >= 1 && pair[1] >= pair[0] && pair[1] <= lines.size
            raise Error, 'range outside original source' unless valid
            quote = lines[(pair[0]-1)...pair[1]].join
            raise Error, 'source range exceeds bounded quotation' if quote.strip.empty? || quote.bytesize > 1900
            { 'path' => path, 'line' => pair[0], 'quote' => quote, 'complete_unit' => false,
              'preparation' => 'explicit original line range; surrounding dependencies and complete syntax are not implied' }
          end
        end
        selected.each { |card| cards["S#{cards.size+1}"] = card }
      end
      raise Error, 'too many section evidence cards' if cards.size > 4
      cards
    end
    def call_model(body)
      super
    rescue Net::OpenTimeout, Net::ReadTimeout, EOFError, SocketError, Errno::ECONNREFUSED, Errno::ECONNRESET, Errno::EHOSTUNREACH => error
      @transport_error = "#{error.class}: #{error.message}"
      raise
    rescue Error => error
      @transport_error = error.message if error.message.match?(/Ollama HTTP (?:4|5)\d\d|inference incomplete or truncated|model integrity:/)
      raise
    end
  end

  class ProjectCommand
    VERSION = '1.0.8'
    SLUG = /\A[a-z0-9]+(?:-[a-z0-9]+)*\z/
    def initialize(env = ENV)
      @env = env.to_h
      @guard = Command.new(env)
    end
    def run(args)
      config = nil; selected = []; recovery = nil
      OptionParser.new do |o|
        o.banner = 'make docs DOCS_WORKFLOW=project DOCS_ARGS="--config PLAN [--project SLUG] [--recover rollback|complete]"'
        o.on('--config PATH') { |v| config=v }
        o.on('--project SLUG') { |v| selected << v }
        o.on('--recover STRATEGY', %w[rollback complete]) { |v| recovery=v }
      end.parse!(args)
      raise Error, 'project workflow requires an explicit plan' unless config
      plan = JSON.parse(File.read(config));projects = plan.fetch('projects')
      raise Error, 'invalid project plan' unless plan['schema']==1 && projects.is_a?(Array) && !projects.empty?
      slugs = projects.map { |p| p.fetch('slug') }
      raise Error, 'invalid/duplicate project slugs' unless slugs.uniq==slugs && slugs.all? { |s| s.is_a?(String) && SLUG.match?(s) }
      raise Error, 'unknown selected project' unless (selected-slugs).empty?
      raise Error, 'project recovery requires exactly one --project' if recovery && selected.size!=1
      root = @guard.safe_directory(File.expand_path(@env.fetch('DOCS_LIBRARY')))
      workspace = @guard.safe_directory(File.expand_path(@env.fetch('DOCS_WORKSPACE')))
      raise Error, 'workspace/library overlap' if root==workspace || root.start_with?(workspace+'/') || workspace.start_with?(root+'/')
      lock=File.open(File.join(root,'.project-command.lock'),File::RDWR|File::CREAT|File::NOFOLLOW,0600)
      raise Error,'another project command holds the lock' unless lock.flock(File::LOCK_EX|File::LOCK_NB)
      failures=0
      projects.each do |project|
        next unless selected.empty? || selected.include?(project['slug'])
        result=recovery ? recover_assembly(project,root,recovery) : process(project,root,workspace)
        failures+=1 unless result
      end
      failures.zero? ? 0 : 1
    rescue StandardError => error
      warn "project docs: #{error.class}: #{error.message}"
      error.is_a?(TransportUnavailable) ? 3 : 1
    ensure
      lock.close if lock
    end
    class TransportUnavailable < Error; end
    def process(project,root,workspace)
      slug=project.fetch('slug');name=project.fetch('name');origin=@guard.safe_directory(File.expand_path(project.fetch('source')),create:false)
      head,_,status=Open3.capture3('git','-C',origin,'rev-parse','HEAD')
      raise Error, 'source revision changed from frozen project plan' unless status.success? && head.strip==project.fetch('source_revision')
      sections=project.fetch('sections');ids=sections.map { |s| s.fetch('id') }
      raise Error, 'invalid section identities' unless (1..12).cover?(sections.size) && ids.uniq==ids && ids.all? { |s| SLUG.match?(s) }
      records=[];collected_source_hashes={}
      sections.each do |section|
        id=section.fetch('id');stage=@guard.safe_directory(File.join(workspace,slug,id));source=@guard.safe_directory(File.join(stage,'source'));@guard.safe_directory(File.join(source,'docs'))
        raise Error, 'staging overlaps original source' if source==origin || source.start_with?(origin+'/') || origin.start_with?(source+'/')
        files=section.fetch('files');raise Error,'invalid source file plan' unless files.is_a?(Array) && (1..12).cover?(files.size) && files.uniq==files
        hashes={}
        ownership_path=File.join(stage,'source-ownership.json')
        owned=File.exist?(ownership_path) ? JSON.parse(File.read(ownership_path)) : {}
        files.each do |relative|
          raise Error,'unsafe project evidence path' unless relative.is_a?(String) && !relative.start_with?('/') && relative.split('/').none? { |part| part.empty? || part=='..' || @guard.excluded_source_name?(part) }
          original=File.join(origin,relative);@guard.safe_directory(File.dirname(original),create:false)
          raise Error,'unsafe original source file' if File.symlink?(original) || !File.file?(original) || File.size(original)>2_097_152
          bytes=File.binread(original);hashes[relative]=Digest::SHA256.hexdigest(bytes)
          if collected_source_hashes.key?(relative) && collected_source_hashes[relative]!=hashes[relative]
            raise Error,"original source changed between project sections: #{relative}"
          end
          collected_source_hashes[relative]=hashes[relative]
          dest=File.join(source,relative);@guard.safe_directory(File.dirname(dest))
          raise Error,'human edit or unowned staged source' unless @guard.file_hash(dest)==owned[relative]
          @guard.atomic(dest,bytes)
        end
        @guard.atomic(ownership_path,JSON.pretty_generate(hashes))
        library=@guard.safe_directory(File.join(root,'passes',id))
        audit_directory=@guard.safe_directory(File.join(root,'audits',slug));log=File.join(audit_directory,id+'.ndjson')
        specification={'slug'=>slug,'source'=>source,'destination'=>source+'/docs','lifecycle'=>'temporary','files'=>files,'ranges'=>section.fetch('ranges',{}),'units'=>section.fetch('units',{}),'question'=>section.fetch('question')}
        specification['reuse_selected_unit_facts'] = section['reuse_selected_unit_facts'] if section.key?('reuse_selected_unit_facts')
        specification['require_selected_evidence_coverage'] = section['require_selected_evidence_coverage'] if section.key?('require_selected_evidence_coverage')
        specification.delete('units') if specification['units'].empty?
        specification.delete('ranges') if specification['ranges'].empty?
        cfg=File.join(stage,'section.json');@guard.atomic(cfg,JSON.pretty_generate('projects'=>[specification]))
        env=@env.merge('DOCS_LIBRARY'=>library)
        command=SectionCommand.new(env);puts JSON.generate(project:slug,section:id,status:'generation-started',source_hashes:hashes);$stdout.flush
        original_stdout=$stdout
        begin
          File.open(log,'a',0600) do |output|
            output.sync=true;$stdout=output
            code=command.run(['--config',cfg,'--project',slug])
            outputs=%w[en pt-br].to_h { |lang| [lang,File.join(Locations.new(library,env).evaluations,slug,lang,Command::DOCUMENT)] }
            record={'id'=>id,'titles'=>section.fetch('titles'),'exit'=>code,'source_hashes'=>hashes,'outputs'=>outputs,'status'=>code.zero? ? 'generated-unreviewed' : 'rejected','transport_error'=>command.transport_error,'audit_log'=>log}
            records << record
          end
        ensure
          $stdout=original_stdout
        end
        @guard.atomic(File.join(root,slug+'-progress.json'),JSON.pretty_generate(records))
        puts JSON.generate(project:slug,section:id,status:records.last['status'],exit:records.last['exit'],outputs:records.last['outputs']);$stdout.flush
        raise TransportUnavailable,command.transport_error if command.transport_error
        files.each { |relative| raise Error,'original source changed during project generation' unless Digest::SHA256.file(File.join(origin,relative)).hexdigest==hashes[relative] }
      end
      collected_source_hashes.each do |relative,expected|
        original=File.join(origin,relative);@guard.safe_directory(File.dirname(original),create:false)
        raise Error,"original source changed before project assembly: #{relative}" unless @guard.file_hash(original)==expected
      end
      assemble(project,records,root)
      records.all? { |record| record['exit'].zero? }
    end
    def recover_assembly(project,root,strategy)
      raise Error,'invalid project recovery strategy' unless %w[rollback complete].include?(strategy)
      slug=project.fetch('slug');raise Error,'invalid recovery project' unless SLUG.match?(slug)
      directory=@guard.safe_directory(File.join(root,'projects',slug),create:false)
      pending_path=File.join(directory,'assembly.pending.json');manifest_path=File.join(directory,'assembly.json')
      raise Error,'missing or unsafe project recovery journal' if File.symlink?(pending_path) || !File.file?(pending_path)
      journal_hash=@guard.file_hash(pending_path);journal=JSON.parse(File.read(pending_path))
      raise Error,'legacy project journal requires manual recovery' unless journal['schema']==1
      paths=%w[en pt-br].map { |language| File.join(directory,language+'.md') }
      before=journal.fetch('before');candidate=journal.fetch('candidate');hashes=journal.fetch('candidate_hashes');manifest=journal.fetch('manifest')
      valid=before.is_a?(Hash) && candidate.is_a?(Hash) && hashes.is_a?(Hash) && manifest.is_a?(Hash) &&
        !before.empty? && before.keys.sort==candidate.keys.sort && (before.keys-paths).empty? && hashes.keys.sort==paths.sort &&
        manifest.keys.sort==%w[before candidate] && (manifest['before'].nil? || manifest['before'].is_a?(String)) && manifest['candidate'].is_a?(String)
      raise Error,'invalid project recovery journal' unless valid
      expected={}
      paths.each do |path|
        raise Error,'unsafe recovery output' if File.symlink?(path)
        hash=hashes.fetch(path);raise Error,'invalid recovery output hash' unless hash.is_a?(String) && hash.match?(/\A[0-9a-f]{64}\z/)
        if candidate.key?(path)
          raise Error,'invalid recovery text' unless candidate[path].is_a?(String) && (before[path].nil? || before[path].is_a?(String))
          raise Error,'recovery candidate hash mismatch' unless Digest::SHA256.hexdigest(candidate[path])==hash
          expected[path]=[before[path],candidate[path]]
        else
          raise Error,'human edit to unchanged recovery output' unless @guard.file_hash(path)==hash
        end
      end
      parsed=JSON.parse(manifest.fetch('candidate'));raise Error,'recovery manifest outputs differ' unless parsed['outputs']==hashes
      expected[manifest_path]=[manifest['before'],manifest['candidate']]
      observed={}
      expected.each do |path,versions|
        raise Error,'unsafe recovery output' if File.symlink?(path)
        observed[path]=@guard.file_hash(path)
        allowed=versions.map { |text| text && Digest::SHA256.hexdigest(text) }
        raise Error,'human edit conflicts with project recovery' unless allowed.include?(observed[path])
      end
      expected.each do |path,versions|
        if path==manifest_path
          paths.each do |output|
            target_hash=strategy=='rollback' && before.key?(output) ? (before[output] && Digest::SHA256.hexdigest(before[output])) : hashes[output]
            raise Error,'concurrent edit before recovery manifest' if File.symlink?(output) || @guard.file_hash(output)!=target_hash
          end
        end
        raise Error,'concurrent edit during project recovery' unless @guard.file_hash(path)==observed[path]
        desired=versions[strategy=='rollback' ? 0 : 1]
        next if observed[path]==(desired && Digest::SHA256.hexdigest(desired))
        desired ? @guard.atomic(path,desired) : File.unlink(path)
      end
      raise Error,'project recovery journal changed' unless @guard.file_hash(pending_path)==journal_hash
      File.unlink(pending_path)
      puts JSON.generate(project:slug,status:'project-assembly-recovered',strategy:strategy);$stdout.flush
      true
    end
    def plain_project_heading?(text)
      text.is_a?(String) && !text.strip.empty? && !text.match?(/[\r\n\t\[\]<>#*~`_\\]/) && !text.match?(/&(?:\#\w+|[A-Za-z]\w*);/)
    end
    def project_heading_targets(text)
      seen={};counts=Hash.new(0);targets={};pending=nil;fence=nil
      text.each_line do |line|
        next if line.start_with?('    ')
        if (marker=line.match(/\A {0,3}(`{3,}|~{3,})/))
          token=marker[1]
          if fence.nil?
            fence=token
          elsif token[0]==fence[0] && token.size>=fence.size
            fence=nil
          end
          next
        end
        next if fence
        if (marker=line.match(/\A<!-- reading-section: (project-[a-z0-9-]+) -->\s*\z/))
          pending=marker[1];next
        end
        heading=line.match(/\A\#{1,6}[ \t]+(.+?)[ \t]*\r?\n?\z/)
        next unless heading
        title=heading[1].strip
        raise Error,'project index needs plain generated headings' unless plain_project_heading?(title)
        base=title.downcase.gsub(/[^\p{L}\p{M}\p{N} -]/,'').tr(' ','-')
        raise Error,'empty project heading target' if base.empty?
        target=base
        while seen[target]
          counts[base]+=1;target=base+'-'+counts[base].to_s
        end
        seen[target]=true
        if pending
          raise Error,'duplicate canonical project section' if targets.key?(pending)
          targets[pending]=target;pending=nil
        end
      end
      targets
    end
    def assemble(project,records,root)
      directory=@guard.safe_directory(File.join(root,'projects',project.fetch('slug')))
      manifest_path=File.join(directory,'assembly.json');previous=File.exist?(manifest_path) ? JSON.parse(File.read(manifest_path)) : {}
      if records.any? { |record| !record['exit'].zero? } && !previous.fetch('outputs',{}).empty?
        puts JSON.generate(project:project['slug'],status:'rejected-project-revision-preserved-previous-assembly')
        return
      end
      pending_path=File.join(directory,'assembly.pending.json')
      raise Error,'pending project assembly requires recovery before another write' if File.exist?(pending_path)
      %w[en pt-br].each do |language|
        path=File.join(directory,language+'.md')
        raise Error,'human edit or unowned project output' unless @guard.file_hash(path)==previous.fetch('outputs',{})[path]
      end
      outputs={};staged={}
      %w[en pt-br].each do |language|
        path=File.join(directory,language+'.md');expected=previous.fetch('outputs',{})[path]
        raise Error,'human edit or unowned project output' unless @guard.file_hash(path)==expected
        text="# #{project.fetch('name')}\n\n"
        text << (language=='en' ? 'Evaluation draft assembled from separate bounded local-model passes over supplied source. Explanations require factual and bilingual review. Selected files do not establish complete project documentation.' : 'Rascunho de avaliação montado com passes locais separados e limitados à fonte fornecida. As explicações exigem revisão factual e bilíngue. Os arquivos selecionados não comprovam documentação completa do projeto.')+"\n\n"
        text << "#{language=='en' ? 'Git HEAD observed' : 'HEAD Git observado'}: `#{project.fetch('source_revision')}`.\n\n"
        text << (language=='en' ? 'The excerpts describe collected working-file bytes; section metadata records per-file SHA-256. Committed-tree equivalence was not checked.' : 'Os trechos descrevem bytes dos arquivos de trabalho coletados; os metadados das seções registram SHA-256 por arquivo. A equivalência com a árvore do commit não foi verificada.')+"\n\n"
        indexed=plain_project_heading?(project.fetch('name')) && records.all? { |record| plain_project_heading?(record.fetch('titles').fetch(language)) }
        contents_title=language=='en' ? 'Contents' : 'Sumário'
        index_marker="<!-- project-contents-placeholder -->"
        text << "## #{contents_title}\n\n#{index_marker}\n\n" if indexed
        records.each do |record|
          text << "<!-- reading-section: project-section-#{record.fetch('id')} -->\n\n" if indexed
          text << "## #{record.fetch('titles').fetch(language)}\n\n"
          source=record['outputs'][language]
          if record['exit'].zero? && File.file?(source)
            body=File.read(source)
            # The project header already states provenance and scope. Retain every fact and citation verbatim.
            first_fact=body.match(/^## \d+\s*$/)
            body=first_fact ? body[first_fact.begin(0)..] : body.sub(/^# [^\n]+\n/,'')
            text << body.gsub(/^## (\d+)/,'### \\1')+"\n\n"
          else
            text << (language=='en' ? 'Generation rejected. No rejected prose was applied to this section; inspect the audit log.' : 'Geração rejeitada. Nenhum texto rejeitado foi aplicado nesta seção; consultar o log de auditoria.')+"\n\n"
          end
        end
        text << "<!-- reading-section: project-verification -->\n\n" if indexed
        text << (language=='en' ? "## Verification and technical limitations\n\nRuntime/build evidence is recorded separately in the campaign report. This generation command executes no discovered source code and does not certify GUI/GPU/device behavior.\n" : "## Verificação e limitações técnicas\n\nAs evidências de runtime/build estão registradas separadamente no relatório da campanha. Este comando não executa o código descoberto nem certifica comportamento de GUI/GPU/dispositivos.\n")
        if indexed
          targets=project_heading_targets(text)
          entries=records.map { |record| "- [#{record.fetch('titles').fetch(language)}](##{targets.fetch('project-section-'+record.fetch('id'))})" }
          label=language=='en' ? 'Verification and technical limitations' : 'Verificação e limitações técnicas'
          entries << "- [#{label}](##{targets.fetch('project-verification')})"
          text.sub!(index_marker,entries.join("\n"))
        end
        staged[path]=text;outputs[path]=Digest::SHA256.hexdigest(text)
      end
      staged.each_key { |path| raise Error,'concurrent project edit before assembly' unless @guard.file_hash(path)==previous.fetch('outputs',{})[path] }
      manifest=JSON.pretty_generate('workflow_version'=>VERSION,'source_revision'=>project['source_revision'],
        'source_revision_role'=>'observed-git-head','source_content_origin'=>'working-tree-files','committed_tree_equivalence'=>'not-checked',
        'sections'=>records,'outputs'=>outputs,'factual_acceptance'=>'pending independent source review')
      changed=staged.reject { |path,_| @guard.file_hash(path)==outputs[path] }
      if changed.empty?
        @guard.atomic(manifest_path,manifest) unless @guard.file_hash(manifest_path)==Digest::SHA256.hexdigest(manifest)
        puts JSON.generate(project:project['slug'],status:'project-draft-noop',outputs:outputs.keys);$stdout.flush
        return
      end
      # Owned Markdown is UTF-8; binread's binary encoding cannot serialize
      # existing Portuguese text into the JSON recovery journal on a rerun.
      before=changed.keys.to_h { |path| [path,File.exist?(path) ? File.binread(path).force_encoding('UTF-8') : nil] }
      @guard.atomic(pending_path,JSON.pretty_generate('schema'=>1,'before'=>before,'candidate_hashes'=>outputs,'candidate'=>changed,
        'manifest'=>{'before'=>File.exist?(manifest_path) ? File.read(manifest_path) : nil,'candidate'=>manifest}))
      begin
        changed.each do |path,text|
          raise Error,'concurrent project edit during assembly' unless @guard.file_hash(path)==previous.fetch('outputs',{})[path]
          @guard.atomic(path,text)
        end
      rescue Exception
        before.each do |path,bytes|
          next unless @guard.file_hash(path)==outputs[path]
          bytes ? @guard.atomic(path,bytes) : File.unlink(path)
        end
        raise
      end
      @guard.atomic(manifest_path,manifest)
      File.unlink(pending_path)
      puts JSON.generate(project:project['slug'],status:'project-draft-assembled',outputs:outputs.keys);$stdout.flush
    end
  end
end
if $PROGRAM_NAME==__FILE__
  $stdout.sync=true
  Signal.trap('TERM') { raise Interrupt }
  begin
    exit Documentation::ProjectCommand.new.run(ARGV)
  rescue Interrupt
    warn 'project docs: interrupted; no further sections scheduled'
    exit 130
  end
end
