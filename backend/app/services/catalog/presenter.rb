module Catalog
  class Presenter
    def self.call(project, language, details: false)
      bio = Files.bio(project.slug, language)
      result = { id: bio[:id], slug: project.slug, name: project.display_name, description: bio[:description] }
      metadata = if Files.root.join('.catalog.json').file?
        Documentation::Catalog.new(Files.root).read['projects'].find { |entry| entry['id'] == bio[:id] }
      end
      result[:browserReference] = metadata['browserReference'] if metadata && metadata['sourceKind'] == 'browser'
      result[:categories] = Files.categories(project.slug, language) if details
      result
    end
  end
end
