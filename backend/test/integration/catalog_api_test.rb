require "test_helper"
class CatalogApiTest < ActionDispatch::IntegrationTest
  setup { Catalog::Sync.call }
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
