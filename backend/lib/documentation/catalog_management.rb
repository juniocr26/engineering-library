# frozen_string_literal: true
require_relative 'catalog'
require 'fileutils'
require 'time'
require 'rbconfig'

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

    def lock(wait: false)
      File.open(@runtime.join('management.lock'), File::RDWR | File::CREAT | File::NOFOLLOW, 0o600) do |file|
        raise ArgumentError, 'Another catalog operation is running' unless file.flock(File::LOCK_EX | (wait ? 0 : File::LOCK_NB))
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
        path = @jobs.children.select { |p| p.basename.to_s.match?(/\A[0-9a-f]{32}\.json\z/) }.max_by(&:mtime)
        return nil unless path
        id = path.basename('.json').to_s
      end
      job = read_job(id)
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
      job.slice('id', 'action', 'projectId', 'state', 'phase', 'error', 'updatedAt')
    end

    def boot_identity
      File.read('/proc/sys/kernel/random/boot_id').strip
    rescue Errno::ENOENT
      'local'
    end

    def directory_candidates
      data = @catalog.read
      @catalog.source_roots(data).each_with_index.flat_map do |(prefix, root), index|
        begin
          next [] unless root.directory? && !root.symlink? && root.readable? && root.executable?
          root.children.sort.filter_map do |source|
            name = source.basename.to_s
            reference = prefix + '/' + name
            next unless @catalog.portable_source?(reference, data['sourceRoots']) && source.directory? && !source.symlink?
            next unless source.join('.git').exist? && !source.join('.git').symlink?
            candidate = { 'directory' => name, 'collection' => index + 1, 'status' => 'unavailable' }
            begin
              fingerprint = @catalog.identity(source)
              existing = data['projects'].find { |entry| entry['sourceIdentity'] == fingerprint || entry['sourcePath'] == reference }
              slug = existing ? existing['slug'] : name.unicode_normalize(:nfkd).gsub(/\p{Mn}/, '').downcase.gsub(/[^a-z0-9]+/, '-').gsub(/\A-|-(?=\z)/, '')[0, 100].to_s.sub(/-\z/, '')
              candidate.merge!('id' => Digest::SHA256.hexdigest(JSON.generate([reference, fingerprint])),
                'name' => existing ? existing['name'] : name, 'slug' => slug,
                'sourcePath' => reference, 'sourceIdentity' => fingerprint)
              if existing && existing['enabled']
                candidate['status'] = 'registered'
              else
                documentation_destination({ 'slug' => slug }, source)
                candidate['status'] = 'ready'
              end
            rescue ArgumentError, SystemCallError, IOError
              candidate['status'] = 'unavailable'
            end
            candidate
          end
        rescue SystemCallError, IOError
          []
        end
      end
    end

    def directories
      directory_candidates.map { |candidate| candidate.slice('id', 'directory', 'collection', 'name', 'slug', 'status') }
    end

    def resolve_directory(id, slug)
      raise ArgumentError, 'Invalid directory selection' unless id.is_a?(String) && id.match?(/\A[0-9a-f]{64}\z/)
      raise ArgumentError, 'Invalid slug' unless slug.is_a?(String) && slug.size <= 100 && Catalog::SLUG.match?(slug)
      candidate = directory_candidates.find { |item| item['id'] == id }
      raise ArgumentError, 'Source unavailable' unless candidate
      raise ArgumentError, 'Project already registered' if candidate['status'] == 'registered'
      raise ArgumentError, 'Source documentation mount unavailable' unless candidate['status'] == 'ready'
      source = @catalog.locate(candidate).first
      documentation_destination({ 'slug' => slug }, source)
      candidate.fetch('sourcePath')
    end

    def documentation_destination(entry, source)
      slug = entry.fetch('slug')
      raise ArgumentError, 'Invalid slug' unless slug.is_a?(String) && Catalog::SLUG.match?(slug)
      destination = Pathname.new('/project-docs').join(slug)
      destination = source.join('docs') unless destination.exist? || destination.symlink?
      library_source = @catalog.library_source?(source)
      destination = @catalog.root.join(slug) if library_source
      direct = destination == source.join('docs')
      ready = !destination.symlink? && if !destination.exist?
        direct && source.writable?
      else
        destination.directory? && destination.writable? && (library_source || direct || File.identical?(destination, source.join('docs')))
      end
      raise ArgumentError, 'Source documentation mount unavailable' unless ready
      destination
    end

    def enqueue(action, attributes)
      raise ArgumentError, 'Invalid operation' unless %w[add update remove].include?(action)
      lock do
        recover_removal
        latest = status
        raise ArgumentError, 'Another catalog operation needs completion' if latest && !TERMINAL.include?(latest['state'])
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
          raise ArgumentError, 'Unknown project' unless entry
        end
        job = { 'id' => SecureRandom.hex(16), 'action' => action, 'projectId' => entry['id'], 'entry' => entry, 'state' => 'queued', 'phase' => 'queued', 'boot' => boot_identity }
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
      env = { 'DOCS_LIBRARY' => @catalog.root.to_s }
      code = nil
      Open3.popen2e(env, RbConfig.ruby, File.join(__dir__, 'command.rb'), '--config', config.to_s, '--project', entry['slug']) do |input, output, child|
        input.close
        output.each_line do |line|
          $stdout.write(line)
          $stdout.flush
          begin
            event = JSON.parse(line)
            stage = event['status']
            phase(job, stage) if event['project'] == entry['slug'] && %w[validating-ownership evidence-collected generating publishing written no-op error].include?(stage)
          rescue JSON::ParserError
            nil
          end
        end
        code = child.value.exitstatus
      end
      raise ArgumentError, 'MakeDocs rejected the operation; inspect private operation log' unless code == 0
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

    def recover_removal
      pending = @state.join('removal.pending.json')
      return unless pending.exist? || pending.symlink?
      raise ArgumentError, 'Unsafe removal journal' if pending.symlink?
      journal = JSON.parse(pending.read)
      raise ArgumentError, 'Invalid removal journal' unless JOB_ID.match?(journal.fetch('job')) && Catalog::SLUG.match?(journal.fetch('slug')) && journal['archive'] == journal['job'] + '.removed'
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
        @catalog.atomic(@jobs.join(journal['job'] + '.removal.json'), pending.read)
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

    def remove(job, entry)
      File.open(@runtime.join('command.lock'), File::RDWR | File::CREAT | File::NOFOLLOW, 0o600) do |command_lock|
        raise ArgumentError, 'MakeDocs is running' unless command_lock.flock(File::LOCK_EX | File::LOCK_NB)
        raise ArgumentError, 'MakeDocs recovery pending' if @state.join(entry['slug'] + '.pending.json').exist?
        directory = @catalog.root.join(entry.fetch('slug'))
        raise ArgumentError, 'Unsafe documentation directory' unless directory.directory? && !directory.symlink? && directory.realpath.dirname == @catalog.root
        directory.find { |path| raise ArgumentError, 'Linked documentation cannot be removed automatically' if path.symlink? }
        # Preserve a complete rollback copy and the removal journal as private history.
        archive = @jobs.join(job['id'] + '.removed')
        pending = @state.join('removal.pending.json')
        before = @catalog.path.read
        @catalog.atomic(pending, JSON.generate('job' => job['id'], 'slug' => entry['slug'], 'catalogBefore' => before, 'archive' => archive.basename.to_s))
        phase(job, 'removing')
        expected = document_tree_hash(directory)
        FileUtils.copy_entry(directory, archive)
        raise ArgumentError, 'Documentation changed during removal backup' unless document_tree_hash(archive) == expected && document_tree_hash(directory) == expected
        journal = JSON.parse(pending.read).merge('archive_sha256' => expected)
        @catalog.atomic(pending, JSON.generate(journal))
        begin
          FileUtils.remove_entry(directory)
          @catalog.change { |data| data['projects'].reject! { |p| p['id'] == entry['id'] } }
        rescue StandardError
          if @catalog.read['projects'].any? { |p| p['id'] == entry['id'] }
            restore_removed_directory(archive, directory)
            File.unlink(pending)
          end
          raise
        end
        # The hidden recovery archive is outside the served library. Source and agent state stay intact.
        @catalog.atomic(@jobs.join(job['id'] + '.removal.json'), pending.read)
        File.unlink(pending)
      end
    end
  end
end

if $PROGRAM_NAME == __FILE__
  Documentation::CatalogManagement.new.perform(ARGV.fetch(0))
end
