# frozen_string_literal: true
require 'json'
require 'digest'
require 'pathname'
require 'open3'
require 'securerandom'
require_relative 'locations'
require_relative 'host_filesystem'

module Documentation
  class Catalog
    SLUG = /\A[a-z0-9]+(?:-[a-z0-9]+)*\z/
    PROJECT_DIRECTORY = /\A(?!.*[ .]\z)(?!CON(?:[ .]|\z)|PRN(?:[ .]|\z)|AUX(?:[ .]|\z)|NUL(?:[ .]|\z)|(?:COM|LPT)[1-9](?:[ .]|\z))[^\x00-\x1f\x7f\\\/:*?"<>|]{1,255}\z/i
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
        raise ArgumentError, 'Invalid source root' unless source.is_a?(Hash) && source['path'].is_a?(String) && source_root_path?(source['path']) && valid_container_root?(source)
        aliases = source['hostAliases']
        raise ArgumentError, 'Invalid source aliases' if aliases && !(aliases.is_a?(Array) && aliases.size <= 32 && aliases.all? { |value| absolute_source?(value) })
      end
      entries.each do |entry|
        valid = entry.is_a?(Hash) && entry['id'].is_a?(String) && SLUG.match?(entry['id']) && entry['slug'].is_a?(String) && PROJECT_DIRECTORY.match?(entry['slug']) &&
          entry['name'].is_a?(String) && (1..120).cover?(entry['name'].size) && !entry['name'].match?(/[\x00-\x1f]/) &&
          [true, false].include?(entry['enabled']) && ((entry['sourceKind'] == 'browser' && entry['browserReference'].is_a?(String) && entry['browserReference'].match?(/\A[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\z/) && entry['sourceDirectory'] == entry['slug'] && !entry.key?('sourcePath')) || (entry['sourceKind'].nil? && entry['sourcePath'].is_a?(String) && (absolute_source?(entry['sourcePath']) || relative_reference?(entry['sourcePath']))))
        raise ArgumentError, 'Invalid catalog entry' unless valid
        raise ArgumentError, 'Invalid source identity' if entry['sourceIdentity'] && !(entry['sourceIdentity'].is_a?(String) && entry['sourceIdentity'].match?(/\A[0-9a-f]{64}\z/))
      end
      %w[id slug sourcePath sourceIdentity browserReference].each do |key|
        values = entries.filter_map { |entry| entry[key] }
        raise ArgumentError, "Duplicate catalog #{key}" unless values.uniq == values
      end
      data
    end

    def source_root_path?(value)
      !value.empty? && !value.match?(/[\x00-\x1f\x7f]/) && (absolute_source?(value) || !Pathname.new(value).absolute?)
    end

    def valid_container_root?(source)
      target = source['containerPath'].to_s
      return target.match?(%r{\A/(?:sources|extra-sources-[1-9][0-9]*)\z}) unless source['projectRoot']
      base, name = target.rpartition('/').values_at(0, 2)
      source['projectRoot'] == true && base.match?(%r{\A/extra-sources-[1-9][0-9]*\z}) && PROJECT_DIRECTORY.match?(name)
    end

    def portable_source?(value, roots)
      roots.any? do |source|
        base = source['path'].delete_suffix('/')
        next value == base if source['projectRoot']
        prefix = base + '/'
        components = value.delete_prefix(prefix).split('/', -1)
        value.start_with?(prefix) && !components.empty? && components.all? { |part| PROJECT_DIRECTORY.match?(part) && part.bytesize <= 255 }
      end
    end

    def host_filesystem
      @host_filesystem ||= HostFilesystem.new(self)
    end

    def relative_reference?(value)
      value.is_a?(String) && !value.empty? && value.bytesize <= 4096 &&
        !value.match?(/[\x00-\x1f\x7f]/) && !value.tr('\\', '/').start_with?('/') &&
        !value.match?(/\A[A-Za-z]:/) && value.tr('\\', '/').split('/').all? { |part| %w[. ..].include?(part) || PROJECT_DIRECTORY.match?(part) }
    end

    def relative_source_reference(value)
      raise ArgumentError, 'Invalid relative source path' unless value.is_a?(String) && !value.empty? && value.bytesize <= 4096 && !value.match?(/[\x00-\x1f\x7f]/)
      normalized = value.tr('\\', '/')
      raise ArgumentError, 'Expected relative source path' if normalized.start_with?('/') || normalized.match?(/\A[A-Za-z]:/)
      reference = Pathname.new(normalized).cleanpath.to_s
      raise ArgumentError, 'Invalid relative source path' unless relative_reference?(reference)
      reference
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

    def verify_source_mount(collection)
      return unless File.directory?('/app/backend')
      mounted = File.readlines('/proc/self/mountinfo').find do |line|
        line.split[4].to_s.gsub(/\\([0-7]{3})/) { [$1.to_i(8)].pack('C') } == collection.to_s
      end
      raise ArgumentError, 'Source mount unavailable; host preparation required' unless mounted
      origin = mounted.split[3].gsub(/\\([0-7]{3})/) { [$1.to_i(8)].pack('C') }
      raise ArgumentError, 'Stale source mount; host preparation required' if origin.end_with?('//deleted', ' (deleted)')
    end

    def identity_locations(fingerprint)
      found = []
      seen = {}
      count = 0
      source_roots.each do |_, collection|
        begin
          verify_source_mount(collection)
        rescue ArgumentError
          next
        end
        next unless collection.directory? && collection.readable? && collection.executable?
        pending = [collection]
        until pending.empty?
          candidate = pending.pop
          raise ArgumentError, 'Source search is ambiguous; host preparation required' if (count += 1) > 10_000
          next if candidate.symlink?
          stat = candidate.stat
          key = [stat.dev, stat.ino]
          next if seen[key]
          seen[key] = true
          if candidate.join('.git').exist?
            found << candidate if identity(candidate) == fingerprint
          else
            pending.concat(candidate.children.select { |child| child.directory? && !child.symlink? })
          end
        end
      end
      found
    rescue SystemCallError, IOError
      raise ArgumentError, 'Source search unavailable; host preparation required'
    end

    def absolute_source?(value)
      return false unless value.is_a?(String) && value.bytesize <= 4096 && !value.match?(/[\x00-\x1f\x7f]/)
      normalized = value.tr('\\', '/')
      (normalized.start_with?('/') || normalized.match?(%r{\A[A-Za-z]:/})) &&
        !normalized.split('/').any? { |part| part == '.' || part == '..' }
    end

    def host_source_roots(data = read)
      mounts = if File.directory?('/app/backend') && File.file?('/proc/self/mountinfo')
        File.readlines('/proc/self/mountinfo').filter_map do |line|
          fields = line.split
          separator = fields.index('-')
          next unless separator
          decode = ->(text) { text.gsub(/\\([0-7]{3})/) { [$1.to_i(8)].pack('C') } }
          target = decode.call(fields[4])
          origin = decode.call(fields[3])
          device = decode.call(fields[separator + 2])
          # Docker Desktop exposes the host share separately from the bind root.
          origin = File.join(device.delete_prefix('/run/host_mark'), origin) if device.start_with?('/run/host_mark/')
          [target, origin]
        end.to_h
      else
        {}
      end
      data['sourceRoots'].map do |source|
        host = File.directory?('/app/backend') ? mounts[source['containerPath']] : @root.parent.join(source['path']).expand_path.to_s
        [source['path'].delete_suffix('/'), host]
      end
    end

    def host_source_reference(reference, data = read)
      pair = host_source_roots(data).sort_by { |prefix, _| -prefix.size }.find { |prefix, host| host && (reference == prefix || reference.start_with?(prefix + '/')) }
      raise ArgumentError, 'Host source mount unavailable' unless pair && portable_source?(reference, data['sourceRoots'])
      reference == pair[0] ? pair[1] : pair[1].delete_suffix('/') + '/' + reference.delete_prefix(pair[0] + '/')
    end

    def absolute_source_reference(value)
      raise ArgumentError, 'Invalid absolute source path' unless absolute_source?(value)
      windows = value.match?(/\A[A-Za-z]:[\\\/]/) || (value.start_with?('\\\\') || value.start_with?('//'))
      normalized = (windows ? value.tr('\\', '/') : value).sub(%r{/+\z}, '')
      data = read
      components = normalized.split('/', -1)
      matches = host_source_roots(data).flat_map do |prefix, host|
        next [] unless host
        host = host.sub(%r{\A/(?:run/desktop/mnt/host|host_mnt|mnt)/([A-Za-z])(?=/)}) { "#{$1}:" } if windows
        host = host.delete_suffix('/')
        record = data['sourceRoots'].find { |source| source['path'].delete_suffix('/') == prefix }
        aliases = (record['hostAliases'] || []).map { |value| windows ? value.tr('\\', '/') : value }
        bound = aliases.any? { |value| windows ? value.downcase == host.downcase : value == host }
        candidates = [host]
        if bound
          canonical = host.unicode_normalize(:nfc)
          candidates += aliases.select { |value| value.unicode_normalize(:nfc).casecmp?(canonical) }
        end
        candidates.uniq.filter_map do |candidate|
          parts = candidate.delete_suffix('/').split('/', -1)
          next unless components.size >= parts.size && parts.each_with_index.all? { |part, index| windows ? part.downcase == components[index].downcase : part == components[index] }
          relative = components.drop(parts.size)
          if record['projectRoot']
            next [parts.size, prefix] if relative.empty?
            next
          end
          reference = prefix + '/' + relative.join('/')
          [parts.size, reference] if !relative.empty? && portable_source?(reference, [record])
        end
      end
      longest = matches.map(&:first).max
      references = matches.select { |size, _| size == longest }.map(&:last).uniq
      raise ArgumentError, 'Source outside accessible approved mounts' unless references.size == 1
      references.first
    end

    def safe_source(path)
      absolute = Pathname.new(path).expand_path
      absolute.ascend { |part| raise ArgumentError, 'Symlink source rejected' if part.symlink? }
      raise ArgumentError, 'Source unavailable' unless absolute.directory? && absolute.readable? && absolute.executable? && absolute.join('.git').exist?
      absolute
    end

    def identity(path)
      source = safe_source(path).to_s
      output, _, status = Open3.capture3('git', '-c', "safe.directory=#{source}", '-C', source, 'rev-list', '--max-parents=0', 'HEAD')
      raise ArgumentError, 'Source Git identity unavailable' unless status.success? && output.lines.all? { |line| line.strip.match?(/\A[0-9a-f]{40,64}\z/) } && !output.empty?
      Digest::SHA256.hexdigest(output.split.sort.join("\n"))
    end

    def source_child(parent, name)
      requested = parent.join(name)
      raise ArgumentError, 'Symlink source rejected' if requested.symlink?
      return requested unless requested.exist?
      raise ArgumentError, 'Source parent unavailable' unless parent.directory? && parent.readable? && parent.executable?
      children = parent.children
      exact = children.find { |child| child.basename.to_s == name }
      return exact if exact
      matches = children.reject(&:symlink?).select { |child| File.identical?(child, requested) }
      raise ArgumentError, 'Source spelling is ambiguous' unless matches.size == 1
      matches.first
    end

    def source_location(entry)
      raise ArgumentError, 'Browser source requires native authorization' if entry['sourceKind'] == 'browser'
      data = read
      stored = entry.fetch('sourcePath')
      reference = absolute_source?(stored) ? absolute_source_reference(stored) : stored
      pair = source_roots(data).sort_by { |prefix, _| -prefix.size }.find { |prefix, _| reference == prefix || reference.start_with?(prefix + '/') }
      raise ArgumentError, 'Source outside approved roots' unless pair && portable_source?(reference, data['sourceRoots'])
      verify_source_mount(pair[1])
      expected = pair[1]
      unless reference == pair[0]
        reference.delete_prefix(pair[0] + '/').split('/').each { |name| expected = source_child(expected, name) }
      end
      [expected, pair[1], reference]
    end

    def confirmed_missing?(entry, relocating: false)
      if host_filesystem.configured? && relative_reference?(entry['sourcePath'])
        # A missing host path may be a relocation outside all currently known paths.
        # Preserve registration until the owner supplies the replacement reference.
        return relocating ? host_filesystem.missing?(entry) : false
      end
      expected, collection, = source_location(entry)
      # Only an accessible, positively identified collection can establish absence.
      collection.ascend do |part|
        raise ArgumentError, 'Source symlink status unresolved' if part.symlink?
        raise ArgumentError, 'Source collection unavailable' unless part.directory? && part.readable? && part.executable?
      end
      if File.directory?('/app/backend')
        mounted = File.readlines('/proc/self/mountinfo').any? do |line|
          line.split[4].to_s.gsub(/\\([0-7]{3})/) { [$1.to_i(8)].pack('C') } == collection.to_s
        end
        raise ArgumentError, 'Source mount unavailable' unless mounted
      end
      record = read['sourceRoots'].find { |item| Pathname.new(item['containerPath']) == collection }
      if record && record['mountIdentity'] && record['mountIdentity'] != [collection.stat.dev, collection.stat.ino]
        raise ArgumentError, 'Source root identity changed; host reconciliation required'
      end
      # A project-only mount cannot establish absence on its inaccessible host parent.
      return false if expected == collection
      parent = expected.dirname
      parent.ascend do |part|
        break if part == collection
        raise ArgumentError, 'Source parent status unresolved' if part.symlink? || !part.directory? || !part.readable? || !part.executable?
      end
      before = parent.stat
      names = parent.children.map { |child| child.basename.to_s }
      raise ArgumentError, 'Source symlink status unresolved' if expected.symlink?
      return false if names.include?(expected.basename.to_s)
      spelling = expected.basename.to_s.unicode_normalize(:nfc)
      if names.any? { |name| name.unicode_normalize(:nfc).casecmp?(spelling) }
        raise ArgumentError, 'Source spelling changed; absence is uncertain'
      end
      begin
        expected.lstat
        return false
      rescue Errno::ENOENT
        after = parent.stat
        raise ArgumentError, 'Source collection changed during inspection' unless [before.dev, before.ino, before.mtime, before.ctime] == [after.dev, after.ino, after.mtime, after.ctime]
        unless relocating
          verify_source_mount(Pathname.new(ENV.fetch('DOCS_DESTINATIONS', '/project-docs')).join(entry.fetch('slug')))
          if entry['sourceIdentity'] && !identity_locations(entry['sourceIdentity']).empty?
            raise ArgumentError, 'Source relocation requires confirmation; registration preserved'
          end
        end
        true
      end
    end

    def existing_library_source?(entry)
      expected, = source_location(entry)
      library_source?(expected)
    rescue ArgumentError, SystemCallError
      false
    end

    def locate(entry)
      if host_filesystem.configured? && relative_reference?(entry['sourcePath']) && !existing_library_source?(entry)
        return host_filesystem.prepare(entry)
      end
      expected, _, reference = source_location(entry)
      actual = identity(expected)
      raise ArgumentError, 'Source identity changed' if entry['sourceIdentity'] && actual != entry['sourceIdentity']
      raise ArgumentError, 'Source directory differs from library entry' if entry['slug'] && expected.basename.to_s != entry['slug']
      stored = entry.fetch('sourcePath')
      [expected, actual, absolute_source?(stored) ? stored : host_source_reference(reference)]
    end

    def reconcile(entry)
      directory, fingerprint, reference = locate(entry)
      reference = absolute_source_reference(reference) if absolute_source?(reference)
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
          if confirmed_missing?(entry)
            next({ 'slug' => entry['slug'], 'missing_entry' => entry })
          end
          source = reconcile(entry)
          mounted = host_filesystem.snapshot?(source) ? source.join('docs') : Pathname.new(ENV.fetch('DOCS_DESTINATIONS', '/project-docs')).join(entry['slug'])
          destination = if library_source?(source)
            root.join(entry['slug'])
          else
            mounted.exist? || mounted.symlink? ? mounted : source.join('docs')
          end
          { 'slug' => entry['slug'], 'source' => source.to_s, 'destination' => destination.to_s }
        rescue ArgumentError, SystemCallError, IOError => error
          { 'slug' => entry['slug'], 'source' => '/unavailable', 'destination' => "/project-docs/#{entry['slug']}", 'source_error' => error.message }
        end
      end
    end
  end
end
