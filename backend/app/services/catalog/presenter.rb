module Catalog
  class Presenter
    def self.call(project, language, details: false)
      bio = Files.bio(project.slug, language)
      result = { slug: project.slug, name: project.display_name, description: bio[:description] }
      result[:categories] = Files.categories(project.slug, language) if details
      result
    end
  end
end
