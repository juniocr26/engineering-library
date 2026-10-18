require "test_helper"

class BookmarksApiTest < ActionDispatch::IntegrationTest
  setup { Catalog::Sync.call }

  def location
    { project: "engineering-library", document: "architecture/current-state.md", language: "en", anchor: "purpose-and-evidence-boundary", excerpt: "Purpose" }
  end

  test "anonymous cookie, stable location, duplicate prevention and isolation" do
    first = open_session
    second = open_session
    first.get "/api/bookmarks"
    assert_equal 200, first.response.status
    cookie = first.response.headers["set-cookie"].to_s
    assert_match(/httponly/i, cookie)
    assert_match(/samesite=lax/i, cookie)
    csrf = first.response.parsed_body["csrf_token"]
    assert_no_difference "Bookmark.count" do
      first.post "/api/bookmarks", params: location, as: :json
      assert_equal 403, first.response.status
    end
    assert_difference "Bookmark.count", 1 do
      first.post "/api/bookmarks", params: location, headers: { "X-Reader-CSRF" => csrf }, as: :json
      assert_equal 201, first.response.status
    end
    saved = first.response.parsed_body
    assert_equal "purpose-and-evidence-boundary", saved["anchor"]
    assert_nil saved["reader_digest"]
    assert_nil saved["page"]
    first.post "/api/bookmarks", params: location, headers: { "X-Reader-CSRF" => csrf }, as: :json
    assert_equal saved["id"], first.response.parsed_body["id"]
    second.get "/api/bookmarks"
    assert_empty second.response.parsed_body["bookmarks"]
    other_csrf = second.response.parsed_body["csrf_token"]
    second.delete "/api/bookmarks/#{saved['id']}", headers: { "X-Reader-CSRF" => other_csrf }
    assert_equal 404, second.response.status
    second.post "/api/bookmarks", params: location, headers: { "X-Reader-CSRF" => csrf }, as: :json
    assert_equal 403, second.response.status
    first.get "/api/bookmarks"
    assert_equal 1, first.response.parsed_body["bookmarks"].length
    assert_difference "Bookmark.count", -1 do
      first.delete "/api/bookmarks/#{saved['id']}", headers: { "X-Reader-CSRF" => csrf }
      assert_equal 204, first.response.status
    end
  end

  test "invalid documents and traversal cannot be bookmarked" do
    get "/api/bookmarks"
    csrf = response.parsed_body["csrf_token"]
    [{ project: "missing" }, { document: "../../.env.md" }, { document: "missing.md" }, { language: "fr" }, { anchor: "" }].each do |invalid|
      assert_no_difference "Bookmark.count" do
        post "/api/bookmarks", params: location.merge(invalid), headers: { "X-Reader-CSRF" => csrf }, as: :json
        assert_response :unprocessable_entity
      end
    end
  end
end
