require "test_helper"
class CatalogApiTest < ActionDispatch::IntegrationTest
  setup { Catalog::Sync.call }
  test "official names and localized descriptions retain original slugs" do
    names = { "engineering-library" => "Engineering Library", "env-auditor" => "Env Auditor", "go-image-optimizer" => "Go Image Optimizer", "payment-reconciliation-lab" => "Payment Reconciliation Lab", "rust-event-relay" => "Reliable Event Relay", "url-shortener" => "URL Shortener" }
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
  test "fixed page size, language and real categories" do
    get "/api/projects", params: { page: 1, per_page: 500, lang: "en" }
    assert_response :success
    assert_equal 5, response.parsed_body["projects"].size
    assert_equal 6, response.parsed_body.dig("pagination", "total_projects")
    get "/api/projects", params: { page: 2, lang: "pt-BR" }
    assert_equal 1, response.parsed_body["projects"].size
    get "/api/projects/engineering-library", params: { lang: "en" }
    assert_response :success
    assert response.parsed_body["categories"].any?
    assert_not_includes response.body, "/docs/projects/engineering-library/bio"
    get "/api/projects/absent"
    assert_response :not_found
  end
end
