module Catalog
  class Sync
    def self.call
      entries = []
      errors = []
      Files.root.children.sort.each do |directory|
        next unless directory.directory? && !directory.symlink? && Files::SLUG.match?(directory.basename.to_s)
        next unless directory.join("README.md").file? || directory.join("bio").directory?
        slug = directory.basename.to_s
        begin
          en = Files.bio(slug, "en")
          pt = Files.bio(slug, "pt-BR")
          raise ArgumentError, "Bios disagree" unless en.values_at(:id, :name) == pt.values_at(:id, :name)
          raise ArgumentError, "Duplicate stable identifier" if entries.any? { |entry| entry[:stable_id] == en[:id] }
          entries << { stable_id: en[:id], slug: slug, display_name: en[:name] }
        rescue StandardError => error
          errors << "#{slug}: #{error.class} — invalid or missing bio metadata"
        end
      end
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
