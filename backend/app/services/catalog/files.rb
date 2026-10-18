require "yaml"
module Catalog
  class Files
    LANGUAGES = %w[pt-BR en].freeze
    SLUG = /\A[a-z0-9]+(?:-[a-z0-9]+)*\z/
    def self.root
      Pathname.new(ENV.fetch("CATALOG_ROOT", Rails.root.join("../docs/projects").to_s)).realpath
    end
    def self.read(slug, relative)
      raise ArgumentError, "Invalid project identifier" unless SLUG.match?(slug)
      raise ArgumentError, "Invalid relative path" if Pathname.new(relative).absolute? || relative.split("/").include?("..")
      path = root.join(slug, relative).realpath
      raise ArgumentError, "Outside catalog" unless path.to_s.start_with?(root.join(slug).to_s + "/") && path.to_s.start_with?(root.to_s + "/")
      path.read(encoding: "UTF-8")
    end
    def self.bio(slug, language)
      source = read(slug, "bio/#{language}.md")
      match = source.match(/\A---\r?\n(.*?)\r?\n---\r?\n(.+)\z/m)
      raise ArgumentError, "Invalid bio" unless match
      data = YAML.safe_load(match[1], permitted_classes: [], aliases: false)
      raise ArgumentError, "Invalid metadata" unless data.is_a?(Hash) && SLUG.match?(data["id"].to_s) && data["name"].is_a?(String) && !data["name"].strip.empty? && !match[2].strip.empty?
      { id: data["id"], name: data["name"].strip, description: match[2].strip }
    end
    def self.categories(slug, language)
      source = read(slug, "docs/#{language}/index.md")
      source.scan(/^[-*] \[([^\]]+)\]\(([a-zA-Z0-9_-]+)\/index\.md\)/).filter_map do |label, category|
        begin
          read(slug, "docs/#{language}/#{category}/index.md")
          { name: label, url: "https://github.com/juniocr26/engineering-library/blob/main/docs/projects/#{slug}/docs/#{language}/#{category}/index.md" }
        rescue Errno::ENOENT, ArgumentError
          nil
        end
      end
    rescue Errno::ENOENT
      []
    end
  end
end
