require "bundler/setup"
require "minitest/autorun"
require "minitest/mock"
require "rails"
require "rails/application"
Rails.application = Class.new(Rails::Application).new
Rails.application.config.secret_key_base = "segredo-sintetico-" * 8
Rails.application.config.root = Pathname.new(File.expand_path("../..", __dir__))
require "pathname"
require "tmpdir"
require "fileutils"
require "json"
require "active_support"
require "active_support/core_ext"
require "active_record"
require "action_controller"
require "rack/mock"
require_relative "../../app/models/application_record"
require_relative "../../app/models/catalog_project"
require_relative "../../app/models/highlight"
require_relative "../../app/models/note"
require_relative "../../app/services/catalog/files"
require_relative "../../app/services/catalog/presenter"
require_relative "../../app/services/catalog/page"
require_relative "../../app/services/catalog/sync"
require_relative "../../app/controllers/application_controller"
require_relative "../../app/controllers/api/projects_controller"

class CatalogoIsoladoTest < Minitest::Test
  def setup
    @previous_root = ENV["CATALOG_ROOT"]
    @temporary = Dir.mktmpdir("catalogo-test-")
    @root = Pathname.new(@temporary).join("catalogo")
    @root.mkpath
    ENV["CATALOG_ROOT"] = @root.to_s
  end
  def teardown
    ENV["CATALOG_ROOT"] = @previous_root
    FileUtils.remove_entry(@temporary)
  end
  def gravar(relative, content)
    path = @root.join(relative)
    path.dirname.mkpath
    path.binwrite(content)
    path
  end
  def projeto(slug = "projeto", id = "identidade")
    %w[en pt-br].each do |language|
      gravar("#{slug}/#{language}/bio.md", "---\nid: #{id}\nname: Nome oficial\n---\n\nDescrição sintética.\n")
      gravar("#{slug}/#{language}/index.md", "- [Categoria](categoria/index.md)\n- [Ausente](ausente/index.md)\n")
      gravar("#{slug}/#{language}/categoria/index.md", "# Conteúdo")
    end
    Struct.new(:slug, :display_name).new(slug, "Nome oficial")
  end
end

require_relative "../../app/models/bookmark"
require_relative "../../app/services/annotation_library"
require_relative "../../app/controllers/api/bookmarks_controller"
require_relative "../../app/controllers/api/highlights_controller"
require_relative "../../app/controllers/api/notes_controller"
require_relative "../../app/controllers/api/annotations_controller"

class AnotacoesIsoladasTest < CatalogoIsoladoTest
  def setup
    super
    ActiveRecord::Base.establish_connection(adapter: "sqlite3", database: ":memory:")
    ActiveRecord::Schema.verbose = false
    ActiveRecord::Schema.define do
      create_table(:catalog_projects) { |t| t.string :stable_id; t.string :slug; t.string :display_name; t.boolean :active, default: true; t.timestamps }
      create_table(:highlights) { |t| t.string :project; t.string :document; t.string :language; t.string :color; t.json :segments; t.timestamps }
      create_table(:notes) { |t| t.integer :highlight_id; t.string :project; t.string :document; t.string :language; t.json :segments; t.string :anchor_digest; t.text :body; t.timestamps }
      create_table(:bookmarks) { |t| t.string :project; t.string :document; t.string :language; t.string :anchor; t.string :excerpt; t.integer :location_variant, default: 0; t.timestamps }
      add_index :bookmarks, [:project, :document, :language, :anchor, :location_variant], unique: true
      add_index :notes, :highlight_id, unique: true
    end
    [CatalogProject, Highlight, Note, Bookmark].each(&:reset_column_information)
    projeto
    CatalogProject.create!(stable_id: "identidade", slug: "projeto", display_name: "Nome oficial")
  end

  def teardown
    ActiveRecord::Base.connection_pool.disconnect!
    super
  end

  def segmentos
    [{ "block" => "b", "start" => 0, "end" => 4, "exact" => "text", "prefix" => "", "suffix" => "" }]
  end

  def atributos
    { project: "projeto", document: "categoria/index.md", language: "en" }
  end

  def requisicao(controller, action, data, method: "GET", token: nil)
    env = Rack::MockRequest.env_for("/api/anotacoes", method: method, input: JSON.generate(data),
      "CONTENT_TYPE" => "application/json", "HTTP_X_ANNOTATION_CSRF" => token,
      "action_dispatch.request.path_parameters" => { action: action })
    status, headers, body = controller.action(action).call(env)
    text = +""
    body.each { |part| text << part }
    body.close if body.respond_to?(:close)
    [status, text.empty? ? nil : JSON.parse(text), headers]
  end

  def token
    Rails.application.message_verifier("shared-annotations").generate("shared-annotations", expires_in: 1.day, purpose: "annotation-mutation")
  end
end
