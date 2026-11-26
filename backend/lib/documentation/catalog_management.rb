# frozen_string_literal: true
require_relative 'catalog'
require 'fileutils'
require 'time'
require 'rbconfig'
require 'yaml'

module Documentation
  class CatalogManagement
    JOB_ID = /\A[0-9a-f]{32}\z/
    TERMINAL = %w[completed error interrupted].freeze
    def initialize(root = ENV.fetch('CATALOG_ROOT', '/docs'))
      @catalog = Catalog.new(root)
      @state = Locations.ensure_directory(@catalog.locations.state)
      @runtime = Locations.ensure_directory(@catalog.locations.runtime)
      @jobs = @state.join('management')
      raise ArgumentError, 'Unsafe job directory' if @jobs.symlink?
      @jobs.mkpath
    end

    def lock(wait: false, timeout: nil)
      File.open(@runtime.join('management.lock'), File::RDWR | File::CREAT | File::NOFOLLOW, 0o600) do |file|
        acquired = file.flock(File::LOCK_EX | (wait ? 0 : File::LOCK_NB))
        deadline = Process.clock_gettime(Process::CLOCK_MONOTONIC) + timeout if timeout && !wait
        while !acquired && deadline && Process.clock_gettime(Process::CLOCK_MONOTONIC) < deadline
          sleep 0.02
          acquired = file.flock(File::LOCK_EX | File::LOCK_NB)
        end
        raise ArgumentError, 'Another catalog operation is running' unless acquired
        yield
      end
    end

    def job_path(id)
      raise ArgumentError, 'Invalid operation' unless id.is_a?(String) && JOB_ID.match?(id)
      @jobs.join(id + '.json')
    end

    def read_job(id)
      path = job_path(id)
      raise ArgumentError, 'Unsafe operation' if path.symlink? || !path.file?
      JSON.parse(path.read)
    end

    def save(job)
      job['updatedAt'] = Time.now.utc.iso8601
      @catalog.atomic(job_path(job.fetch('id')), JSON.pretty_generate(job))
    end

    def status(id = nil)
      if id.nil?
        paths = @jobs.children.select { |p| p.basename.to_s.match?(/\A[0-9a-f]{32}\.json\z/) && !p.symlink? }.sort_by(&:mtime).reverse
        path = paths.find { |p| data = JSON.parse(p.read); !TERMINAL.include?(data['state']) || data['delivery'] == 'pending' } ||
          paths.find { |p| data = JSON.parse(p.read); data['removalReason'] == 'source_missing' && !data['notificationAcknowledged'] } || paths.first
        return nil unless path
        id = path.basename('.json').to_s
      end
      job = read_job(id)
      receipt = @jobs.join(id + '.removal.json')
      if job['action'] == 'remove' && %w[queued running interrupted].include?(job['state']) && receipt.file? && !receipt.symlink?
        record = JSON.parse(receipt.read)
        archive = @jobs.join(id + '.removed')
        completed = record['job'] == id && record['slug'] == job.dig('entry', 'slug') && record['archive'] == id + '.removed' &&
          archive.directory? && !archive.symlink? && record['archive_sha256'] == document_tree_hash(archive) &&
          !@catalog.read['projects'].any? { |entry| entry['id'] == job['projectId'] } && !@catalog.root.join(record['slug']).exist?
        if completed
          job.merge!('state' => 'completed', 'phase' => 'completed')
          job.delete('error')
          save(job)
        end
      end
      unless TERMINAL.include?(job['state'])
        begin
          Process.kill(0, job.fetch('pid'))
          raise Errno::ESRCH if job['boot'] != boot_identity
          command = "/proc/#{job['pid']}/cmdline"
          raise Errno::ESRCH if File.exist?(command) && !File.binread(command).split("\x00").include?(id)
        rescue Errno::ESRCH, KeyError
          job.merge!('state' => 'interrupted', 'phase' => 'interrupted', 'error' => 'interrupted')
          # The worker may have stopped between filesystem steps. Its journal is retained.
          save(job)
        end
      end
      result = job.slice('id', 'action', 'projectId', 'state', 'phase', 'error', 'updatedAt', 'delivery', 'removalReason', 'notificationAcknowledged', 'coverage', 'review', 'outcome')
      result['projectName'] = job.dig('entry', 'name')
      result['projectSlug'] = job.dig('entry', 'slug')
      result['browserReference'] = job.dig('entry', 'browserReference') if job.dig('entry', 'sourceKind') == 'browser'
      result['directory'] = job.dig('entry', 'slug') if result['browserReference']
      result
    end

    def boot_identity
      File.read('/proc/sys/kernel/random/boot_id').strip
    rescue Errno::ENOENT
      'local'
    end

    def documentation_destination(entry, source)
      slug = entry.fetch('slug')
      raise ArgumentError, 'Invalid slug' unless slug.is_a?(String) && Catalog::PROJECT_DIRECTORY.match?(slug)
      destination = @catalog.host_filesystem.snapshot?(source) ? source.join('docs') : Pathname.new(ENV.fetch('DOCS_DESTINATIONS', '/project-docs')).join(slug)
      destination = source.join('docs') unless destination.exist? || destination.symlink?
      library_source = @catalog.library_source?(source)
      destination = @catalog.root.join(slug) if library_source
      direct = destination == source.join('docs')
      ready = !destination.symlink? && if !destination.exist?
        (direct && source.writable?) || (library_source && @catalog.root.writable?)
      else
        destination.directory? && destination.writable? && (library_source || direct || File.identical?(destination, source.join('docs')))
      end
      raise ArgumentError, 'Source documentation mount unavailable' unless ready
      destination
    end

    def acknowledge(id)
      lock(wait: true) do
        job = read_job(id)
        raise ArgumentError, 'Notification unavailable' unless TERMINAL.include?(job['state']) && job['removalReason'] == 'source_missing'
        job['notificationAcknowledged'] = true
        save(job)
        status(id)
      end
    end

    def enqueue(action, attributes)
      return acknowledge(attributes['id']) if action == 'acknowledge'
      raise ArgumentError, 'Invalid operation' unless %w[add update remove].include?(action)
      return register_project(attributes) if action == 'add'
      request_id = attributes['requestId']
      raise ArgumentError, 'Invalid request identifier' if request_id && !(request_id.is_a?(String) && JOB_ID.match?(request_id))
      lock do
        recover_removal
        if request_id && job_path(request_id).exist?
          previous = read_job(request_id)
          raise ArgumentError, 'Request identifier already used' unless previous['action'] == action && previous['projectId'] == attributes['id']
          return status(request_id)
        end
        latest = status
        if latest && latest['delivery'] == 'pending' && action == 'update' && latest['projectId'] == attributes['id']
          pending = read_job(latest.fetch('id'))
          config = JSON.parse(@jobs.join(pending['id'] + '.config.json').read)
          source = Pathname.new(config.fetch('projects').first.fetch('source'))
          @catalog.host_filesystem.publish(source)
          pending.merge!('delivery' => 'completed', 'state' => 'completed', 'phase' => 'completed')
          pending.delete('error')
          pending.delete('errorDetail')
          save(pending)
          return status(pending.fetch('id'))
        end
        raise ArgumentError, 'Another catalog operation needs completion' if latest && (!TERMINAL.include?(latest['state']) || latest['delivery'] == 'pending')
        # An interrupted removal must be reconciled before accepting another mutation.
        data = @catalog.read
        if action == 'add'
          raise ArgumentError, 'Invalid source reference' unless attributes['sourcePath'].is_a?(String) && @catalog.portable_source?(attributes['sourcePath'], data['sourceRoots'])
          raise ArgumentError, 'Invalid name' unless attributes['name'].is_a?(String) && (1..120).cover?(attributes['name'].strip.size) && !attributes['name'].match?(/[\x00-\x1f]/)
          slug = attributes['slug']
          raise ArgumentError, 'Invalid slug' unless slug.is_a?(String) && slug.size <= 100 && Catalog::SLUG.match?(slug)
          entry = { 'id' => "project-#{SecureRandom.hex(12)}", 'slug' => slug, 'name' => attributes['name'].strip, 'sourcePath' => attributes['sourcePath'], 'enabled' => false }
          source, fingerprint, = @catalog.locate(entry)
          entry.merge!('sourceIdentity' => fingerprint, 'sourceDirectory' => source.basename.to_s)
          previous = data['projects'].find { |p| p['slug'] == slug || p['sourcePath'] == entry['sourcePath'] || p['sourceIdentity'] == fingerprint }
          if previous
            raise ArgumentError, 'Project already registered' unless previous['enabled'] == false && previous['slug'] == slug && previous['sourceIdentity'] == fingerprint
            entry = previous.merge('name' => attributes['name'].strip)
          else
            raise ArgumentError, 'Documentation already exists' if @catalog.root.join(slug).exist? || @catalog.root.join(slug).symlink?
            restored = removed_entry(slug, fingerprint)
            entry['id'] = restored.fetch('id') if restored
          end
        else
          entry = data['projects'].find { |p| p['id'] == attributes['id'] }
          unless entry
            previous = @jobs.children.find do |path|
              next false unless path.basename.to_s.match?(/\A[0-9a-f]{32}\.removal\.json\z/) && !path.symlink?
              JSON.parse(JSON.parse(path.read).fetch('catalogBefore')).fetch('projects').any? { |item| item['id'] == attributes['id'] }
            end if action == 'remove'
            return { 'id' => previous.basename('.removal.json').to_s, 'state' => 'completed', 'phase' => 'completed' } if previous
            raise ArgumentError, 'Unknown project'
          end
        end
        job = { 'id' => request_id || SecureRandom.hex(16), 'action' => action, 'projectId' => entry['id'], 'entry' => entry, 'state' => 'queued', 'phase' => 'queued', 'boot' => boot_identity }
        save(job)
        log = @jobs.join(job['id'] + '.log')
        File.open(log, File::WRONLY | File::CREAT | File::EXCL | File::NOFOLLOW, 0o600) do |output|
          pid = Process.spawn({ 'CATALOG_ROOT' => @catalog.root.to_s }, RbConfig.ruby, File.expand_path(__FILE__), job['id'], out: output, err: output, pgroup: true)
          job['pid'] = pid
          save(job)
          Process.detach(pid)
        end
        job.slice('id', 'state', 'phase')
      end
    end

    def register_project(attributes)
      request_id = attributes['requestId']
      raise ArgumentError, 'Invalid request identifier' if request_id && !(request_id.is_a?(String) && JOB_ID.match?(request_id))
      reference = @catalog.relative_source_reference(attributes['sourcePath'])
      lock(timeout: 2) do
        if request_id && job_path(request_id).exist?
          previous = read_job(request_id)
          raise ArgumentError, 'Request identifier already used' unless previous['action'] == 'add' && previous['requestedSourcePath'] == reference
          return status(request_id)
        end
        recover_removal
        latest = status
        raise ArgumentError, 'Another catalog operation needs completion' if latest && (!TERMINAL.include?(latest['state']) || latest['delivery'] == 'pending')
        source, fingerprint, = @catalog.locate('sourcePath' => reference)
        data = @catalog.read
        existing = data['projects'].find { |item| item['sourceIdentity'] == fingerprint }
        if existing
          same = existing['sourcePath'] == reference
          unless same
            same = if @catalog.host_filesystem.snapshot?(source)
              @catalog.host_filesystem.same_source?(existing['sourcePath'], reference, fingerprint)
            else
              begin
                File.identical?(@catalog.locate(existing).first, source)
              rescue Errno::ENOENT
                false
              end
            end
          end
          if same
            documentation_destination(existing, source)
            ensure_registration_bios(existing)
            @catalog.change do |current|
              item = current['projects'].find { |entry| entry['id'] == existing['id'] }
              raise ArgumentError, 'Project changed during registration' unless item == existing
              item['enabled'] = true
            end unless existing['enabled']
            return complete_registration(existing.merge('enabled' => true), request_id, reference, 'already_registered')
          end
          relocate_project(existing, source, fingerprint, reference)
          current = @catalog.read['projects'].find { |entry| entry['id'] == existing['id'] }
          return complete_registration(current, request_id, reference, 'relocated')
        end
        slug = source.basename.to_s
        raise ArgumentError, 'Invalid project directory' unless Catalog::PROJECT_DIRECTORY.match?(slug) && slug.bytesize <= 255
        name = slug.split(/[-_ ]+/).map { |word| word.match?(/[A-Z]/) ? word : word.capitalize }.join(' ')[0, 120]
        entry = { 'id' => "project-#{SecureRandom.hex(12)}", 'slug' => slug, 'name' => name,
          'sourcePath' => reference, 'enabled' => true }
        entry.merge!('sourceIdentity' => fingerprint, 'sourceDirectory' => source.basename.to_s)
        documentation_destination(entry, source)
        data = @catalog.read
        raise ArgumentError, 'Project already registered' if data['projects'].any? { |p| p['slug'].downcase == slug.downcase || p['sourcePath'] == reference || p['sourceIdentity'] == fingerprint }
        target = @catalog.root.join(slug)
        raise ArgumentError, 'Documentation already exists' if target.exist? || target.symlink?
        restored = removed_entry(slug, fingerprint)
        entry['id'] = restored['id'] if restored
        begin
          if restored
            raise ArgumentError, 'Invalid recovery archive' unless restored['archive'].match?(/\A[0-9a-f]{32}\.removed\z/)
            archive = @jobs.join(restored['archive'])
            raise ArgumentError, 'Missing recovery archive' unless archive.directory? && !archive.symlink?
            document_tree(archive)
            FileUtils.copy_entry(archive, target)
          end
          ensure_registration_bios(entry)
          @catalog.change { |current| current['projects'] << entry }
        rescue StandardError
          FileUtils.remove_entry(target) if target.directory? && !@catalog.read['projects'].any? { |p| p['id'] == entry['id'] }
          raise
        end
        complete_registration(entry, request_id, reference, restored ? 'restored' : 'registered')
      end
    end

    def ensure_registration_bios(entry)
      target = @catalog.root.join(entry.fetch('slug'))
      raise ArgumentError, 'Catalog metadata directory is unsafe' if target.symlink? || (target.exist? && !target.directory?)
      existing = {}
      %w[en pt-br].each do |language|
        bio = target.join(language, 'bio.md')
        bio.parent.ascend { |part| raise ArgumentError, 'Catalog metadata directory is unsafe' if part.symlink? }
        raise ArgumentError, 'Catalog metadata is unsafe' if bio.symlink?
        next unless bio.exist?
        raise ArgumentError, 'Catalog metadata is invalid' unless bio.file? && bio.size <= 65536
        front = bio.read.match(/\A---\r?\n(.*?)\r?\n---\r?\n(.+)\z/m)
        metadata = front && YAML.safe_load(front[1], permitted_classes: [], aliases: false)
        raise ArgumentError, 'Catalog metadata identity differs' unless metadata.is_a?(Hash) && metadata['id'] == entry['id']
        existing[language] = metadata
      end
      name = existing.empty? ? entry['name'] : existing.values.first['name']
      %w[en pt-br].each do |language|
        next if existing.key?(language)
        directory = target.join(language)
        directory.mkpath
        description = language == 'en' ? 'Source documentation generated by MakeDocs.' : 'Documentação do código gerada pelo MakeDocs.'
        name_line = name.nil? ? '' : "name: #{JSON.generate(name)}\n"
        @catalog.atomic(directory.join('bio.md'), "---\nid: #{entry['id']}\n#{name_line}---\n#{description}\n")
      end
    end

    def complete_registration(entry, request_id, reference, outcome)
      synchronize_index
      job = { 'id' => request_id || SecureRandom.hex(16), 'action' => 'add', 'projectId' => entry.fetch('id'),
        'entry' => entry, 'requestedSourcePath' => reference, 'outcome' => outcome,
        'state' => 'completed', 'phase' => 'completed' }
      save(job)
      status(job.fetch('id'))
    end

    def relocate_project(entry, source, fingerprint, reference)
      File.open(@runtime.join('command.lock'), File::RDWR | File::CREAT | File::NOFOLLOW, 0o600) do |file|
        raise ArgumentError, 'MakeDocs is running; relocation deferred' unless file.flock(File::LOCK_EX | File::LOCK_NB)
        relocate_source_reference(entry, source, fingerprint, reference)
      end
    end

    def relocate_source_reference(entry, source, fingerprint, reference)
      raise ArgumentError, 'Project already registered' if entry['sourcePath'] == reference
      raise ArgumentError, 'Relocation changes the project directory; host preparation required' unless source.basename.to_s == entry['slug'] && (!entry['sourceDirectory'] || source.basename.to_s == entry['sourceDirectory'])
      raise ArgumentError, 'Previous source is accessible or unavailable; relocation is ambiguous' unless @catalog.confirmed_missing?(entry, relocating: true)
      unless @catalog.host_filesystem.snapshot?(source)
        matches = @catalog.identity_locations(fingerprint)
        raise ArgumentError, 'Multiple source copies or unresolved identity; relocation is ambiguous' unless matches.size == 1 && File.identical?(matches.first, source)
      end
      documentation_destination(entry, source)
      @catalog.change do |data|
        current = data['projects'].find { |item| item['id'] == entry['id'] }
        raise ArgumentError, 'Project changed during relocation' unless current == entry
        raise ArgumentError, 'Project already registered' if data['projects'].any? { |item| item['id'] != entry['id'] && (item['sourcePath'] == reference || item['sourceIdentity'] == fingerprint) }
        actual = @catalog.host_filesystem.snapshot?(source) ? @catalog.host_filesystem.inspect_source(reference, fingerprint).fetch('identity') : @catalog.identity(source)
        raise ArgumentError, 'Source changed during relocation' unless actual == fingerprint && @catalog.confirmed_missing?(entry, relocating: true)
        documentation_destination(entry, source)
        current['sourcePath'] = reference
      end
      { 'id' => SecureRandom.hex(16), 'state' => 'completed', 'phase' => 'completed', 'projectId' => entry['id'] }
    end

    def removed_entry(slug, fingerprint)
      @jobs.children.select { |p| p.basename.to_s.match?(/\A[0-9a-f]{32}\.removal\.json\z/) }.sort_by(&:mtime).reverse_each do |path|
        raise ArgumentError, 'Unsafe removal record' if path.symlink?
        record = JSON.parse(path.read)
        next unless record['slug'] == slug
        previous = JSON.parse(record.fetch('catalogBefore')).fetch('projects').find { |p| p['slug'] == slug && p['sourceIdentity'] == fingerprint }
        return previous.merge('archive' => record.fetch('archive')) if previous
      end
      nil
    end

    def phase(job, phase)
      job['phase'] = phase
      save(job)
    end

    def perform(id)
      lock(wait: true) do
        job = read_job(id)
        job['state'] = 'running'
        phase(job, 'validating')
        entry = job.fetch('entry')
        begin
          if job['action'] != 'add'
            entry = @catalog.read.fetch('projects').find { |item| item['id'] == job['projectId'] }
            raise ArgumentError, 'Project no longer registered' unless entry
          end
          job['action'] == 'remove' ? remove(job, entry) : generate(job, entry)
          job['state'] = 'completed'
          phase(job, 'completed')
        rescue StandardError => error
          job['state'] = 'error'
          job['error'] = error.message.match?(/Source .*unavailable|source mount|missing directory/) ? 'source_unavailable' : 'operation_failed'
          job['errorDetail'] = "#{error.class}: #{error.message}"
          phase(job, 'error')
        end
      end
    end

    def generate(job, entry)
      if job['action'] == 'update' && @catalog.confirmed_missing?(entry)
        remove(job, entry, removal_reason: 'source_missing')
        return
      end
      source = job['action'] == 'add' ? @catalog.locate(entry).first : @catalog.reconcile(entry)
      if job['action'] == 'add'
        @catalog.change do |data|
          data['projects'] << entry unless data['projects'].any? { |p| p['id'] == entry['id'] }
        end
      end
      # Keep the existing dual-output MakeDocs contract; never create a substitute mount.
      destination = documentation_destination(entry, source)
      if job['action'] == 'add'
        restored = removed_entry(entry['slug'], entry['sourceIdentity'])
        target = @catalog.root.join(entry['slug'])
        if restored && !target.exist?
          raise ArgumentError, 'Invalid recovery archive' unless restored['archive'].match?(/\A[0-9a-f]{32}\.removed\z/)
          archive = @jobs.join(restored['archive'])
          raise ArgumentError, 'Missing recovery archive' unless archive.directory? && !archive.symlink?
          archive.find { |path| raise ArgumentError, 'Unsafe recovery archive' if path.symlink? }
          FileUtils.copy_entry(archive, target)
        end
      end
      config = @jobs.join(job['id'] + '.config.json')
      @catalog.atomic(config, JSON.generate('projects' => [{ 'slug' => entry['slug'], 'source' => source.to_s, 'destination' => destination.to_s }]))
      phase(job, 'starting')
      env = { 'DOCS_LIBRARY' => @catalog.root.to_s, 'DOCS_HOST_DEFER_DELIVERY' => '1' }
      code = nil
      Open3.popen2e(env, RbConfig.ruby, File.join(__dir__, 'command.rb'), '--config', config.to_s, '--project', entry['slug']) do |input, output, child|
        input.close
        output.each_line do |line|
          $stdout.write(line)
          $stdout.flush
          begin
            event = JSON.parse(line)
            stage = event['status']
            if event['project'] == entry['slug'] && event['coverage']
              job['coverage'] = event['coverage']
              job['review'] = event['review']
            end
            phase(job, stage) if event['project'] == entry['slug'] && %w[validating-ownership evidence-collected generating publishing written no-op error].include?(stage)
          rescue JSON::ParserError
            nil
          end
        end
        code = child.value.exitstatus
      end
      raise ArgumentError, 'MakeDocs rejected the operation; inspect private operation log' unless code == 0
      manifest = @state.join(entry['slug'] + '.json')
      if manifest.file? && !manifest.symlink?
        ownership = JSON.parse(manifest.read)
        job['coverage'] = ownership['coverage']
        job['review'] = 'draft'
      end
      if @catalog.host_filesystem.snapshot?(source)
        job['delivery'] = 'pending'
        phase(job, 'publishing')
        @catalog.host_filesystem.publish(source)
        job['delivery'] = 'completed'
        save(job)
      end
      if job['action'] == 'add'
        # New bios are metadata, not an alternative document generator.
        %w[en pt-br].each do |language|
          bio = @catalog.root.join(entry['slug'], language, 'bio.md')
          description = language == 'en' ? 'Source documentation generated by MakeDocs.' : 'Documentação do código gerada pelo MakeDocs.'
          bytes = "---\nid: #{entry['id']}\nname: #{JSON.generate(entry['name'])}\n---\n#{description}\n"
          raise ArgumentError, 'Existing bio must be preserved' if bio.symlink? || (bio.exist? && !bio.read.match?(/\A---\r?\nid: #{Regexp.escape(entry['id'])}\r?\n/))
          @catalog.atomic(bio, bytes) unless bio.exist?
        end
        @catalog.change do |data|
          data['projects'].reject! { |p| p['id'] == entry['id'] }
          raise ArgumentError, 'Concurrent duplicate project' if data['projects'].any? { |p| p['slug'] == entry['slug'] || p['sourceIdentity'] == entry['sourceIdentity'] }
          data['projects'] << entry.merge('enabled' => true)
        end
      end
    end

    def recover_removal(command_locked: false)
      pending = @state.join('removal.pending.json')
      return unless pending.exist? || pending.symlink?
      File.open(@runtime.join('command.lock'), File::RDWR | File::CREAT | File::NOFOLLOW, 0o600) do |file|
        raise ArgumentError, 'MakeDocs is running' unless command_locked || file.flock(File::LOCK_EX | File::LOCK_NB)
        recover_removal_journal
      end
    end

    def recover_removal_journal
      pending = @state.join('removal.pending.json')
      return unless pending.exist? || pending.symlink?
      raise ArgumentError, 'Unsafe removal journal' if pending.symlink?
      journal = JSON.parse(pending.read)
      raise ArgumentError, 'Invalid removal journal' unless JOB_ID.match?(journal.fetch('job')) && Catalog::PROJECT_DIRECTORY.match?(journal.fetch('slug')) && journal['archive'] == journal['job'] + '.removed'
      archive = @jobs.join(journal['archive'])
      directory = @catalog.root.join(journal['slug'])
      raise ArgumentError, 'Unsafe removal recovery paths' if archive.symlink? || directory.symlink?
      registered = @catalog.read['projects'].any? { |p| p['slug'] == journal['slug'] }
      sealed = archive.directory? && journal['archive_sha256'] && document_tree_hash(archive) == journal['archive_sha256']
      if registered && sealed
        restore_removed_directory(archive, directory)
      elsif registered && directory.directory? && !journal['archive_sha256']
        # Copying was not sealed; the original directory was never removed.
      elsif !registered && sealed
        restore_removed_directory(archive, directory) if directory.exist?
        FileUtils.remove_entry(directory) if directory.exist?
        synchronize_index
        @catalog.atomic(@jobs.join(journal['job'] + '.removal.json'), pending.read)
        if job_path(journal['job']).file?
          recovered = read_job(journal['job'])
          raise ArgumentError, 'Removal journal differs from operation' unless recovered['action'] == 'remove' && recovered.dig('entry', 'slug') == journal['slug']
          recovered.merge!('state' => 'completed', 'phase' => 'completed')
          recovered.delete('error')
          recovered.delete('errorDetail')
          save(recovered)
        end
      else
        raise ArgumentError, 'Ambiguous removal recovery; preserve both paths'
      end
      File.unlink(pending)
    end

    def document_tree(directory)
      directory.find.each_with_object({}) do |path, entries|
        raise ArgumentError, 'Linked documentation rejected' if path.symlink?
        entries[path.relative_path_from(directory).to_s] = path.directory? ? nil : Digest::SHA256.file(path).hexdigest
      end
    end

    def document_tree_hash(directory)
      Digest::SHA256.hexdigest(JSON.generate(document_tree(directory).sort.to_h))
    end

    def restore_removed_directory(archive, directory)
      if directory.exist?
        expected = document_tree(archive)
        raise ArgumentError, 'Concurrent edit during removal recovery' unless document_tree(directory).all? { |path, hash| expected.key?(path) && expected[path] == hash }
      end
      FileUtils.copy_entry(archive, directory)
      raise ArgumentError, 'Removal recovery checksum mismatch' unless document_tree_hash(archive) == document_tree_hash(directory)
    end

    def synchronize_index
      return unless @catalog.locations.main
      require_relative '../../config/environment'
      ::Catalog::Sync.call(recover: false)
    end

    def remove_missing(entry)
      lock do
        recover_removal(command_locked: true)
        current = @catalog.read.fetch('projects').find { |item| item['id'] == entry['id'] }
        return unless current
        raise ArgumentError, 'Source absence no longer confirmed' unless @catalog.confirmed_missing?(current)
        job = { 'id' => SecureRandom.hex(16), 'action' => 'remove', 'projectId' => current['id'],
          'entry' => current, 'state' => 'running', 'phase' => 'validating', 'boot' => boot_identity }
        save(job)
        begin
          remove(job, current, command_locked: true, removal_reason: 'source_missing')
          job['state'] = 'completed'
          phase(job, 'completed')
        rescue StandardError => error
          job.merge!('state' => 'error', 'error' => 'operation_failed', 'errorDetail' => "#{error.class}: #{error.message}")
          phase(job, 'error')
          raise
        end
      end
    end

    def remove(job, entry, command_locked: false, removal_reason: nil)
      File.open(@runtime.join('command.lock'), File::RDWR | File::CREAT | File::NOFOLLOW, 0o600) do |command_lock|
        raise ArgumentError, 'MakeDocs is running' unless command_locked || command_lock.flock(File::LOCK_EX | File::LOCK_NB)
        raise ArgumentError, 'MakeDocs recovery pending' if @state.join(entry['slug'] + '.pending.json').exist? || @state.join(entry['slug'] + '.pending.json').symlink?
        slug = entry.fetch('slug')
        raise ArgumentError, 'Unsafe project directory' unless Catalog::PROJECT_DIRECTORY.match?(slug) && slug.downcase != 'img'
        directory = @catalog.root.join(slug)
        raise ArgumentError, 'Unsafe documentation directory' if directory.symlink? || directory.dirname != @catalog.root || (directory.exist? && (!directory.directory? || directory.realpath.dirname != @catalog.root))
        directory.find { |path| raise ArgumentError, 'Linked documentation cannot be removed automatically' if path.symlink? } if directory.exist?
        # Preserve a complete rollback copy and the removal journal as private history.
        archive = @jobs.join(job['id'] + '.removed')
        pending = @state.join('removal.pending.json')
        before = @catalog.path.read
        @catalog.atomic(pending, JSON.generate('job' => job['id'], 'slug' => entry['slug'], 'catalogBefore' => before, 'archive' => archive.basename.to_s))
        job['removalReason'] = removal_reason if removal_reason
        phase(job, 'removing')
        if directory.exist?
          expected = document_tree_hash(directory)
          FileUtils.copy_entry(directory, archive)
          raise ArgumentError, 'Documentation changed during removal backup' unless document_tree_hash(archive) == expected && document_tree_hash(directory) == expected
        else
          archive.mkpath
          expected = document_tree_hash(archive)
        end
        journal = JSON.parse(pending.read).merge('archive_sha256' => expected)
        @catalog.atomic(pending, JSON.generate(journal))
        begin
          FileUtils.remove_entry(directory) if directory.exist?
          @catalog.change { |data| data['projects'].reject! { |p| p['id'] == entry['id'] } }
        rescue StandardError
          if @catalog.read['projects'].any? { |p| p['id'] == entry['id'] }
            restore_removed_directory(archive, directory)
            File.unlink(pending)
          end
          raise
        end
        # The hidden recovery archive is outside the served library. Source and agent state stay intact.
        synchronize_index
        @catalog.atomic(@jobs.join(job['id'] + '.removal.json'), pending.read)
        File.unlink(pending)
      end
    end
  end
end



if $PROGRAM_NAME == __FILE__ && !Thread.current[:documentation_management_worker_running]
  Thread.current[:documentation_management_worker_running] = true
  begin
    Documentation::CatalogManagement.new.perform(ARGV.fetch(0))
  ensure
    Thread.current[:documentation_management_worker_running] = false
  end
end
