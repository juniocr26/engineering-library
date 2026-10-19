require "test_helper"

class BookmarksApiTest < ActionDispatch::IntegrationTest
  setup { Catalog::Sync.call }

  def location
    { project: "engineering-library", document: "architecture/current-state.md", language: "en", anchor: "purpose-and-evidence-boundary", excerpt: "Purpose" }
  end

  test "contents bookmarks use logical anchors and preserve document bookmarks" do
    get "/api/bookmarks", params: { project_slug: "engineering-library" }
    csrf = response.parsed_body.fetch("csrf_token")
    headers = { "X-Reader-CSRF" => csrf }
    assert_difference "Bookmark.count", 2 do
      post "/api/bookmarks", params: location, headers: headers, as: :json
      assert_response :created
      post "/api/bookmarks", params: location.merge(document: "@contents", anchor: "category:architecture"), headers: headers, as: :json
      assert_response :created
    end
    saved = response.parsed_body
    post "/api/bookmarks", params: location.merge(document: "@contents", anchor: "category:architecture"), headers: headers, as: :json
    assert_equal saved.fetch("id"), response.parsed_body.fetch("id")
    get "/api/bookmarks", params: { project_slug: "engineering-library" }
    assert_equal ["@contents", location[:document]].sort, response.parsed_body.fetch("bookmarks").map { |item| item.fetch("document") }.sort
    delete "/api/bookmarks/#{saved.fetch('id')}", headers: headers
    assert_response :no_content
    get "/api/bookmarks", params: { project_slug: "engineering-library" }
    assert_equal [location[:document]], response.parsed_body.fetch("bookmarks").map { |item| item.fetch("document") }
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

  test "project lists preserve reader isolation and other projects across reload and deletion" do
    reader = open_session
    reader.get "/api/bookmarks"
    csrf = reader.response.parsed_body.fetch("csrf_token")
    saved = %w[engineering-library env-auditor go-image-optimizer].map do |project|
      reader.post "/api/bookmarks", params: location.merge(project: project, document: "README"), headers: { "X-Reader-CSRF" => csrf }, as: :json
      assert_equal 201, reader.response.status
      reader.response.parsed_body
    end
    saved.each do |bookmark|
      2.times do
        reader.get "/api/bookmarks", params: { project_slug: bookmark.fetch("project") }
        assert_equal 200, reader.response.status
        assert_equal [bookmark.fetch("id")], reader.response.parsed_body.fetch("bookmarks").map { |item| item.fetch("id") }
        assert_equal "no-store", reader.response.headers["Cache-Control"]
      end
    end
    stranger = open_session
    stranger.get "/api/bookmarks", params: { project_slug: "engineering-library" }
    assert_empty stranger.response.parsed_body.fetch("bookmarks")
    stranger.delete "/api/bookmarks/#{saved.first.fetch('id')}", headers: { "X-Reader-CSRF" => stranger.response.parsed_body.fetch("csrf_token") }
    assert_equal 404, stranger.response.status
    assert_difference "Bookmark.count", -1 do
      reader.delete "/api/bookmarks/#{saved.first.fetch('id')}", headers: { "X-Reader-CSRF" => csrf }
      assert_equal 204, reader.response.status
    end
    reader.get "/api/bookmarks", params: { project_slug: "engineering-library" }
    assert_empty reader.response.parsed_body.fetch("bookmarks")
    reader.get "/api/bookmarks"
    assert_equal saved.drop(1).map { |item| item.fetch("id") }.sort, reader.response.parsed_body.fetch("bookmarks").map { |item| item.fetch("id") }.sort
  end

  test "project filter rejects unknown inactive and malformed identifiers" do
    ["missing", "", "../env-auditor", ["env-auditor"]].each do |slug|
      get "/api/bookmarks", params: { project_slug: slug }
      assert_response :unprocessable_entity
    end
    CatalogProject.find_by!(slug: "env-auditor").update!(active: false)
    get "/api/bookmarks", params: { project_slug: "env-auditor" }
    assert_response :unprocessable_entity
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
