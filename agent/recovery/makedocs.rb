require 'openssl'
require 'securerandom'
require 'json'
require 'base64'
require 'digest'
require 'zlib'
require 'stringio'
require 'pathname'
require 'fileutils'

module MakeDocsRecovery
  MAGIC = "ELMD001\n".freeze
  def self.safe(path)
    path = Pathname.new(path).expand_path
    path.ascend { |part| raise 'Symlink rejected' if part.symlink? }
    path
  end

  def self.inventory(root)
    root = safe(root)
    entries = []
    root.find do |path|
      next if path == root
      safe(path)
      raise 'Special file rejected' unless path.file? || path.directory?
      entry = { 'path' => path.relative_path_from(root).to_s, 'mode' => path.stat.mode & 0o777, 'directory' => path.directory? }
      if path.file?
        bytes = path.binread
        entry.merge!('size' => bytes.bytesize, 'sha256' => Digest::SHA256.hexdigest(bytes), 'data' => Base64.strict_encode64(bytes))
      end
      entries << entry
    end
    entries.sort_by { |entry| entry['path'] }
  end

  def self.fingerprint(entries)
    Digest::SHA256.hexdigest(JSON.generate(entries.map { |entry| entry.reject { |key, _| key == 'data' } }))
  end

  def self.read(archive, key)
    bytes = safe(archive).binread
    raise 'Invalid recovery archive' unless bytes.start_with?(MAGIC) && bytes.bytesize > MAGIC.bytesize + 28
    cipher = OpenSSL::Cipher.new('aes-256-gcm')
    cipher.decrypt
    cipher.key = safe(key).binread
    cipher.iv = bytes.byteslice(8, 12)
    cipher.auth_tag = bytes.byteslice(20, 16)
    cipher.auth_data = MAGIC
    compressed = cipher.update(bytes.byteslice(36..-1)) + cipher.final
    payload = JSON.parse(Zlib::GzipReader.new(StringIO.new(compressed)).read)
    raise 'Invalid recovery schema' unless payload['version'] == 1 && payload['entries'].is_a?(Array)
    names = []
    payload['entries'].each do |entry|
      name = entry.fetch('path')
      raise 'Unsafe recovery path' unless name.is_a?(String) && !name.start_with?('/') && !name.include?("\x00") && !name.include?('\\') && name.split('/').none? { |part| part.empty? || part == '.' || part == '..' }
      raise 'Duplicate recovery path' if names.include?(name)
      names << name
      next if entry['directory']
      content = Base64.strict_decode64(entry.fetch('data'))
      raise 'Recovery checksum mismatch' unless content.bytesize == entry['size'] && Digest::SHA256.hexdigest(content) == entry['sha256']
    end
    raise 'Recovery inventory mismatch' unless fingerprint(payload['entries']) == payload['inventory_sha256']
    payload
  end

  def self.pack(source, key, archive)
    key = safe(key)
    unless key.exist?
      key.dirname.mkpath
      File.open(key, File::WRONLY | File::CREAT | File::EXCL, 0o600) { |file| file.write(SecureRandom.random_bytes(32)); file.flush; file.fsync }
    end
    raise 'Invalid key' unless key.size == 32
    entries = inventory(source)
    payload = { 'version' => 1, 'inventory_sha256' => fingerprint(entries), 'entries' => entries }
    buffer = StringIO.new
    gzip = Zlib::GzipWriter.new(buffer)
    gzip.write(JSON.generate(payload))
    gzip.close
    cipher = OpenSSL::Cipher.new('aes-256-gcm')
    cipher.encrypt
    cipher.key = key.binread
    iv = cipher.random_iv
    cipher.auth_data = MAGIC
    encrypted = cipher.update(buffer.string) + cipher.final
    archive = safe(archive)
    archive.dirname.mkpath
    File.open(archive, File::WRONLY | File::CREAT | File::EXCL, 0o600) { |file| file.write(MAGIC + iv + cipher.auth_tag + encrypted); file.flush; file.fsync }
    verified = read(archive, key)
    raise 'Source changed while packing' unless fingerprint(inventory(source)) == verified['inventory_sha256']
    { 'version' => 1, 'cipher' => 'AES-256-GCM', 'key_sha256' => Digest::SHA256.hexdigest(key.binread), 'archive_sha256' => Digest::SHA256.file(archive).hexdigest,
      'archive_bytes' => archive.size, 'inventory_sha256' => verified['inventory_sha256'], 'files' => entries.count { |entry| !entry['directory'] } }
  end

  def self.restore(archive, key, target)
    payload = read(archive, key)
    target = safe(target)
    raise 'Recovery target must be new' if target.exist?
    target.mkpath
    payload['entries'].select { |entry| entry['directory'] }.sort_by { |entry| entry['path'].split('/').size }.each { |entry| safe(target.join(entry['path'])).mkpath }
    payload['entries'].reject { |entry| entry['directory'] }.each do |entry|
      path = safe(target.join(entry['path']))
      path.dirname.mkpath
      File.open(path, File::WRONLY | File::CREAT | File::EXCL, entry.fetch('mode')) { |file| file.write(Base64.strict_decode64(entry.fetch('data'))); file.flush; file.fsync }
      File.chmod(entry['mode'], path)
    end
    payload['entries'].select { |entry| entry['directory'] }.reverse_each { |entry| File.chmod(entry['mode'], target.join(entry['path'])) }
    raise 'Restored inventory mismatch' unless fingerprint(inventory(target)) == payload['inventory_sha256']
    { 'verified_files' => payload['entries'].count { |entry| !entry['directory'] }, 'inventory_sha256' => payload['inventory_sha256'] }
  end

  def self.history(archive, key, target)
    payload = read(archive, key)
    entries = payload.fetch('entries').each_with_object({}) { |entry, map| map[entry['path']] = entry }
    index = JSON.parse(Base64.strict_decode64(entries.fetch('index.json').fetch('data')))
    target = safe(target)
    raise 'Recovery target must be new' if target.exist?
    index.fetch('files').each do |entry|
      name = entry.fetch('path')
      raise 'Unsafe historical path' if name.start_with?('/') || name.include?('\\') || name.include?("\x00") || name.split('/').any? { |part| part.empty? || part == '.' || part == '..' }
      blob = entries.fetch('blobs/' + entry.fetch('sha256'))
      raise 'Historical checksum mismatch' unless blob['sha256'] == entry['sha256'] && blob['size'] == entry['size']
    end
    target.mkpath
    index['files'].each do |entry|
      path = safe(target.join(entry['path']))
      path.dirname.mkpath
      bytes = Base64.strict_decode64(entries.fetch('blobs/' + entry['sha256']).fetch('data'))
      File.open(path, File::WRONLY | File::CREAT | File::EXCL, 0o600) { |file| file.write(bytes); file.flush; file.fsync }
      raise 'Restored historical checksum mismatch' unless Digest::SHA256.file(path).hexdigest == entry['sha256']
    end
    { 'restored_historical_files' => index['files'].size, 'unique_contents' => entries.keys.count { |name| name.start_with?('blobs/') } }
  end
end

if $PROGRAM_NAME == __FILE__
  action, source, key, target = ARGV
  result = case action
  when 'pack' then MakeDocsRecovery.pack(source, key, target)
  when 'verify'
    data = MakeDocsRecovery.read(source, key)
    { 'verified_files' => data['entries'].count { |entry| !entry['directory'] }, 'inventory_sha256' => data['inventory_sha256'] }
  when 'restore' then MakeDocsRecovery.restore(source, key, target)
  when 'history' then MakeDocsRecovery.history(source, key, target)
  else raise 'Usage: makedocs.rb pack SOURCE KEY ARCHIVE | verify ARCHIVE KEY | restore ARCHIVE KEY NEW_DIRECTORY | history ARCHIVE KEY NEW_DIRECTORY'
  end
  puts JSON.pretty_generate(result)
end
