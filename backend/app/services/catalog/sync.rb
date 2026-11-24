require_relative '../../../lib/documentation/catalog'
require_relative '../../../lib/documentation/catalog_management'
module Catalog
  class Sync
    def self.call
      if Documentation::Locations.new(Files.root).state.join('removal.pending.json').exist?
        manager = Documentation::CatalogManagement.new(Files.root)
        manager.lock { manager.recover_removal }
      end
      entries = []
      errors = []
      catalog = Documentation::Catalog.new(Files.root)
      registered = catalog.read.fetch('projects').select { |entry| entry['enabled'] }.index_by { |entry| entry['slug'] }
      Files.root.children.sort.each do |directory|
        next unless directory.directory? && !directory.symlink? && Files::SLUG.match?(directory.basename.to_s)
        next unless directory.join("en/bio.md").file? || directory.join("pt-br/bio.md").file?
        slug = directory.basename.to_s
        next if registered && !registered.key?(slug)
        begin
          en = Files.bio(slug, "en")
          pt = Files.bio(slug, "pt-BR")
          raise ArgumentError, "Bios disagree" unless en.values_at(:id, :name) == pt.values_at(:id, :name)
          metadata = registered && registered.fetch(slug)
          raise ArgumentError, 'Catalog identity differs from bio' if metadata && metadata['id'] != en[:id]
          raise ArgumentError, "Duplicate stable identifier" if entries.any? { |entry| entry[:stable_id] == en[:id] }
          entries << { stable_id: en[:id], slug: slug, display_name: metadata ? metadata['name'] : en[:name] }
        rescue StandardError => error
          errors << "#{slug}: #{error.class} — invalid or missing bio metadata"
        end
      end
      errors << 'Registered documentation missing' if registered && (registered.keys - entries.map { |entry| entry[:slug] }).any?
      # Abort before writes on invalid input; retain the last valid index.
      raise ArgumentError, errors.join("; ") unless errors.empty?
      CatalogProject.transaction do
        CatalogProject.connection.execute("SELECT pg_advisory_xact_lock(68712401)")
        entries.each do |attributes|
          record = CatalogProject.find_or_initialize_by(stable_id: attributes[:stable_id])
          record.assign_attributes(attributes.merge(active: true))
          record.save! if record.new_record? || record.changed?
        end
        CatalogProject.where.not(stable_id: entries.map { |entry| entry[:stable_id] }).where(active: true).update_all(active: false, updated_at: Time.current)
      end
      { indexed: entries.size }
    end
  end
end
