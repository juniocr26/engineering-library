# frozen_string_literal: true
require 'json'
require 'pathname'
require 'securerandom'

module Documentation
  class HostFilesystem
    def initialize(catalog)
      @catalog = catalog
      @root = Pathname.new(ENV.fetch('DOCS_HOST_EXCHANGE', catalog.locations.base.join('filesystem/host').to_s))
    end

    def configured?
      ENV['DOCS_HOST_REQUIRED'] == '1' || @root.join('managed.json').exist? || @root.join('ready.json').exist?
    end

    def available?
      @root.ascend { |part| return false if part.symlink? }
      ready = @root.join('ready.json')
      return false unless ready.file? && !ready.symlink?
      age = Time.now.to_f - JSON.parse(ready.read).fetch('at')
      age >= -5 && age < 30
    rescue JSON::ParserError, KeyError, TypeError, SystemCallError
      false
    end

    def request(operation, attributes)
      @root.ascend { |part| raise ArgumentError, 'Linked host adapter rejected' if part.symlink? }
      # Host-side atomic heartbeat replacement can briefly appear absent through
      # a Docker bind mount. Recheck readiness without replaying any operation.
      available = available?
      5.times do
        break if available
        sleep 0.1
        available = available?
      end
      raise ArgumentError, 'Host filesystem adapter unavailable; launch with python3 tools/init_dev_env.py up' unless available
      id = SecureRandom.hex(16)
      path = @root.join('requests', id + '.json')
      response = @root.join('responses', id + '.json')
      @catalog.atomic(path, JSON.generate(attributes.merge('operation' => operation)))
      deadline = Process.clock_gettime(Process::CLOCK_MONOTONIC) + 120
      until response.file?
        raise ArgumentError, 'Host filesystem adapter timed out; inspect local worker' if Process.clock_gettime(Process::CLOCK_MONOTONIC) >= deadline
        sleep 0.05
      end
      raise ArgumentError, 'Linked host response rejected' if response.symlink? || response.size > 65536
      result = JSON.parse(response.read)
      File.unlink(response)
      raise ArgumentError, "Host filesystem: #{result['error']}" if result['error']
      result.fetch('result')
    end

    def inspect_source(reference, identity = nil)
      request('inspect', 'reference' => reference, 'identity' => identity)
    end

    def prepare(entry)
      reference = entry.fetch('sourcePath')
      result = request('prepare', 'reference' => reference, 'identity' => entry['sourceIdentity'])
      key, name = result.values_at('key', 'name')
      raise ArgumentError, 'Invalid host workspace' unless key.is_a?(String) && key.match?(/\A[0-9a-f]{64}\z/) && name.is_a?(String) && Catalog::PROJECT_DIRECTORY.match?(name)
      source = @root.join('workspaces', key, name)
      source.ascend { |part| raise ArgumentError, 'Linked host workspace rejected' if part.symlink? }
      raise ArgumentError, 'Host snapshot unavailable' unless source.directory?
      raise ArgumentError, 'Source directory differs from library entry' if entry['slug'] && name != entry['slug']
      [source, result.fetch('identity'), reference]
    end

    def same_source?(reference, other_reference, identity)
      request('same_source', 'reference' => reference, 'otherReference' => other_reference, 'identity' => identity).fetch('same')
    end

    def snapshot?(source)
      source = Pathname.new(source)
      source.dirname.dirname == @root.join('workspaces') && source.dirname.basename.to_s.match?(/\A[0-9a-f]{64}\z/)
    end

    def publish(source)
      raise ArgumentError, 'Invalid host publication workspace' unless snapshot?(source)
      request('publish', 'key' => Pathname.new(source).dirname.basename.to_s)
    end

    def missing?(entry)
      request('missing', 'reference' => entry.fetch('sourcePath')).fetch('missing')
    end
  end
end
