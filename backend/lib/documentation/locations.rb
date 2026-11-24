require 'pathname'
require 'digest'
require 'securerandom'

module Documentation
  class Locations
    attr_reader :base, :state, :runtime, :evaluations, :main

    def initialize(library, env = ENV)
      library = Pathname.new(library).expand_path
      backend = Pathname.new(__dir__).join('../..').expand_path
      main = library == Pathname.new('/docs') || library == backend.dirname.join('docs')
      @main = main
      @base = main ? backend.join('storage/makedocs') : library.dirname.join('backend-storage/makedocs', Digest::SHA256.hexdigest(library.to_s))
      @state = base.join('state')
      @runtime = base.join('runtime')
      @evaluations = base.join('evaluations')
    end

    def self.ensure_directory(path)
      path = Pathname.new(path)
      path.ascend { |part| raise ArgumentError, 'Symlink operational directory rejected' if part.symlink? }
      path.mkpath unless path.directory?
      path
    end

    def ensure_key
      self.class.ensure_directory(runtime)
      key = runtime.join('management.key')
      raise ArgumentError, 'Symlink key rejected' if key.symlink?
      begin
        File.open(key, File::WRONLY | File::CREAT | File::EXCL | File::NOFOLLOW, 0o600) { |file| file.write(SecureRandom.hex(32)); file.flush; file.fsync }
      rescue Errno::EEXIST
        raise ArgumentError, 'Invalid management key' unless key.file? && key.read.strip.match?(/\A[0-9a-f]{64}\z/)
      end
      key
    end
  end
end
