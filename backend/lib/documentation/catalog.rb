# frozen_string_literal: true
require 'json'
require 'digest'
require 'pathname'
require 'open3'
require 'securerandom'
require_relative 'locations'

module Documentation
  class Catalog
    SLUG = /\A[a-z0-9]+(?:-[a-z0-9]+)*\z/
    DIRECTORY = /\A[\p{L}\p{N}][\p{L}\p{N} ._-]{0,199}\z/
    attr_reader :root

    def initialize(root = ENV.fetch('DOCS_LIBRARY', '/docs'))
      @root = Pathname.new(root).realpath
    end

    def path
      root.join('.catalog.json')
    end

    def locations
      @locations ||= Locations.new(root)
    end

    def read
      raise ArgumentError, 'Unsafe catalog' if path.symlink? || !path.file? || path.size > 1_048_576
      data = JSON.parse(path.read)
      validate(data)
    end

    def validate(data)
      raise ArgumentError, 'Invalid catalog' unless data.is_a?(Hash)
      entries = data['projects']
      roots = data['sourceRoots']
      valid = data['version'] == 1 && entries.is_a?(Array) && roots.is_a?(Array) && !roots.empty?
      raise ArgumentError, 'Invalid catalog' unless valid
      roots.each do |source|
        raise ArgumentError, 'Invalid source root' unless source.is_a?(Hash) && source['path'].is_a?(String) && !Pathname.new(source['path']).absolute? && source['containerPath'].to_s.match?(%r{\A/(?:sources|extra-sources-[1-9][0-9]*)\z})
      end
      entries.each do |entry|
        valid = entry.is_a?(Hash) && %w[id slug].all? { |key| entry[key].is_a?(String) && SLUG.match?(entry[key]) } &&
          entry['name'].is_a?(String) && (1..120).cover?(entry['name'].size) && !entry['name'].match?(/[\x00-\x1f]/) &&
          [true, false].include?(entry['enabled']) && entry['sourcePath'].is_a?(String) && portable_source?(entry['sourcePath'], roots)
        raise ArgumentError, 'Invalid catalog entry' unless valid
        raise ArgumentError, 'Invalid source identity' if entry['sourceIdentity'] && !(entry['sourceIdentity'].is_a?(String) && entry['sourceIdentity'].match?(/\A[0-9a-f]{64}\z/))
      end
      %w[id slug sourcePath sourceIdentity].each do |key|
        values = entries.filter_map { |entry| entry[key] }
        raise ArgumentError, "Duplicate catalog #{key}" unless values.uniq == values
      end
      data
    end

    def portable_source?(value, roots)
      roots.any? do |source|
        prefix = source['path'].delete_suffix('/') + '/'
        component = value.delete_prefix(prefix)
        value.start_with?(prefix) && DIRECTORY.match?(component) && !component.end_with?('.', ' ')
      end
    end

    def atomic(target, bytes)
      raise ArgumentError, 'Unsafe target' if target.symlink?
      target.dirname.ascend { |part| raise ArgumentError, 'Symlink target directory' if part.symlink? }
      parent = target.dirname.realpath
      permitted = [root, locations.base]
      raise ArgumentError, 'Target outside managed storage' unless permitted.any? { |base| parent == base || parent.to_s.start_with?(base.to_s + '/') }
      temporary = target.dirname.join(".#{target.basename}.#{SecureRandom.hex(8)}")
      File.open(temporary, File::WRONLY | File::CREAT | File::EXCL | File::NOFOLLOW, 0o600) do |file|
        file.write(bytes)
        file.flush
        file.fsync
      end
      File.rename(temporary, target)
      File.open(target.dirname, 'r') { |directory| directory.fsync }
    ensure
      File.unlink(temporary) if temporary && temporary.exist?
    end

    def change
      lock = Locations.ensure_directory(locations.runtime)
      File.open(lock.join('catalog.lock'), File::RDWR | File::CREAT | File::NOFOLLOW, 0o600) do |file|
        file.flock(File::LOCK_EX)
        data = read
        result = yield data
        validate(data)
        bytes = JSON.pretty_generate(data) + "\n"
        atomic(path, bytes) unless path.read == bytes
        result
      end
    end

    def source_roots(data = read)
      data.fetch('sourceRoots').map do |source|
        host = root.parent.join(source.fetch('path')).expand_path
        mounted = Pathname.new(source.fetch('containerPath') == '/sources' ? ENV.fetch('DOCS_SOURCES', '/sources') : source.fetch('containerPath'))
        [source.fetch('path').delete_suffix('/'), File.directory?('/app/backend') ? mounted : host]
      end
    end

    def safe_source(path)
      absolute = Pathname.new(path).expand_path
      absolute.ascend { |part| raise ArgumentError, 'Symlink source rejected' if part.symlink? }
      raise ArgumentError, 'Source unavailable' unless absolute.directory? && absolute.join('.git').exist?
      absolute
    end

    def identity(path)
      source = safe_source(path).to_s
      output, _, status = Open3.capture3('git', '-c', "safe.directory=#{source}", '-C', source, 'rev-list', '--max-parents=0', 'HEAD')
      raise ArgumentError, 'Source Git identity unavailable' unless status.success? && output.lines.all? { |line| line.strip.match?(/\A[0-9a-f]{40,64}\z/) } && !output.empty?
      Digest::SHA256.hexdigest(output.split.sort.join("\n"))
    end

    def locate(entry)
      data = read
      roots = source_roots(data)
      pair = roots.sort_by { |prefix, _| -prefix.size }.find { |prefix, _| entry.fetch('sourcePath').start_with?(prefix + '/') }
      raise ArgumentError, 'Source outside approved roots' unless pair
      expected = pair[1].join(entry['sourcePath'].delete_prefix(pair[0] + '/'))
      if expected.directory? && !expected.symlink?
        actual = identity(expected)
        raise ArgumentError, 'Source identity changed' if entry['sourceIdentity'] && actual != entry['sourceIdentity']
        return [expected, actual, entry['sourcePath']]
      end
      raise ArgumentError, 'Source unavailable; documentation preserved' unless entry['sourceIdentity']
      matches = roots.flat_map do |prefix, directory|
        next [] unless directory.directory? && !directory.symlink?
        directory.children.filter_map do |candidate|
          next unless candidate.directory? && !candidate.symlink? && DIRECTORY.match?(candidate.basename.to_s) && candidate.join('.git').exist?
          begin
            [candidate, entry['sourceIdentity'], prefix + '/' + candidate.basename.to_s] if identity(candidate) == entry['sourceIdentity']
          rescue ArgumentError
            nil
          end
        end
      end
      raise ArgumentError, 'Source unavailable or ambiguous; documentation preserved' unless matches.size == 1
      matches.first
    end

    def reconcile(entry)
      directory, fingerprint, reference = locate(entry)
      change do |data|
        current = data['projects'].find { |item| item['id'] == entry['id'] }
        raise ArgumentError, 'Project no longer registered' unless current
        if current['sourceDirectory'] && current['sourceDirectory'] != directory.basename.to_s
          current['name'] = directory.basename.to_s.split(/[-_ ]+/).map { |word| word.match?(/[A-Z]/) ? word : word.capitalize }.join(' ')
        end
        current.merge!('sourcePath' => reference, 'sourceIdentity' => fingerprint, 'sourceDirectory' => directory.basename.to_s)
      end
      directory
    end

    def library_source?(source)
      command = source.join('backend/lib/documentation/command.rb')
      source.join('docs').directory? && File.identical?(source.join('docs'), root) && command.file? &&
        File.identical?(command, File.join(__dir__, 'command.rb'))
    end

    def specifications(selected = [])
      entries = read.fetch('projects').select { |entry| entry['enabled'] }
      raise ArgumentError, 'Unknown selected project' unless (selected - entries.map { |entry| entry['slug'] }).empty?
      entries.select { |entry| selected.empty? || selected.include?(entry['slug']) }.map do |entry|
        begin
          source = reconcile(entry)
          mounted = Pathname.new(ENV.fetch('DOCS_DESTINATIONS', '/project-docs')).join(entry['slug'])
          destination = if library_source?(source)
            root.join(entry['slug'])
          else
            mounted.exist? || mounted.symlink? ? mounted : source.join('docs')
          end
          { 'slug' => entry['slug'], 'source' => source.to_s, 'destination' => destination.to_s }
        rescue ArgumentError => error
          { 'slug' => entry['slug'], 'source' => '/unavailable', 'destination' => "/project-docs/#{entry['slug']}", 'source_error' => error.message }
        end
      end
    end
  end
end
