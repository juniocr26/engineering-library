require "test_helper"
class CatalogApiTest < ActionDispatch::IntegrationTest
  setup { Catalog::Sync.call }
  test "official names and localized descriptions retain original slugs" do
    names = { "engineering-library" => "Engineering Library", "go-image-optimizer" => "Go Image Optimizer", "payment-reconciliation-lab" => "Payment Reconciliation Lab", "rust-event-relay" => "Reliable Event Relay", "url-shortener" => "URL Shortener" }
    names.each do |slug, name|
      %w[en pt-BR].each do |language|
        get "/api/projects/#{slug}", params: { lang: language }
        assert_response :success
        assert_equal slug, response.parsed_body["slug"]
        assert_equal name, response.parsed_body["name"]
        assert_equal Catalog::Files.bio(slug, language)[:description], response.parsed_body["description"]
      end
    end
  end
  test "removed duplicate is absent while the existing ecosystem tool remains cataloged" do
    get "/api/projects/env-auditor", params: { lang: "en" }
    assert_response :not_found
    assert_not CatalogProject.exists?(slug: "env-auditor", active: true)
    get "/api/projects/script-auditoria-envs", params: { lang: "en" }
    assert_response :success
    slugs = (1..Catalog::Page.call(1)[:pagination][:total_pages]).flat_map do |page|
      get "/api/projects", params: { page: page, lang: "en" }
      response.parsed_body.fetch("projects").map { |project| project.fetch("slug") }
    end
    assert_not_includes slugs, "env-auditor"
    assert_includes slugs, "script-auditoria-envs"
  end
  test "fixed page size, language and real categories" do
    get "/api/projects", params: { page: 1, per_page: 500, lang: "en" }
    assert_response :success
    assert_equal 5, response.parsed_body["projects"].size
    assert_equal CatalogProject.where(active: true).count, response.parsed_body.dig("pagination", "total_projects")
    get "/api/projects", params: { page: 2, lang: "pt-BR" }
    assert_equal [5, CatalogProject.where(active: true).count - 5].min, response.parsed_body["projects"].size
    get "/api/projects/engineering-library", params: { lang: "en" }
    assert_response :success
    assert response.parsed_body["categories"].any?
    assert_not_includes response.body, "/docs/engineering-library/en/bio"
    get "/api/projects/absent"
    assert_response :not_found
  end
end
