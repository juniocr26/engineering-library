require "test_helper"

class BookmarksApiTest < ActionDispatch::IntegrationTest
  setup { Catalog::Sync.call }

  def location
    { project: "engineering-library", document: "architecture/current-state.md", language: "en", anchor: "purpose-and-evidence-boundary", excerpt: "Purpose" }
  end

  test "contents bookmarks use logical anchors and preserve document bookmarks" do
    get "/api/bookmarks", params: { language: "en", project_slug: "engineering-library" }
    csrf = response.parsed_body.fetch("csrf_token")
    headers = { "X-Annotation-CSRF" => csrf }
    assert_difference "Bookmark.count", 2 do
      post "/api/bookmarks", params: location, headers: headers, as: :json
      assert_response :created
      post "/api/bookmarks", params: location.merge(document: "@contents", anchor: "category:architecture"), headers: headers, as: :json
      assert_response :created
    end
    saved = response.parsed_body
    post "/api/bookmarks", params: location.merge(document: "@contents", anchor: "category:architecture"), headers: headers, as: :json
    assert_equal saved.fetch("id"), response.parsed_body.fetch("id")
    get "/api/bookmarks", params: { language: "en", project_slug: "engineering-library" }
    assert_equal ["@contents", location[:document]].sort, response.parsed_body.fetch("bookmarks").map { |item| item.fetch("document") }.sort
    delete "/api/bookmarks/#{saved.fetch('id')}", params: { language: "en" }, headers: headers
    assert_response :no_content
    get "/api/bookmarks", params: { language: "en", project_slug: "engineering-library" }
    assert_equal [location[:document]], response.parsed_body.fetch("bookmarks").map { |item| item.fetch("document") }
  end

  test "shared bookmarks need no cookies and mutations require CSRF" do
    first, second = open_session, open_session
    first.get "/api/bookmarks", params: { language: "en" }
    assert_equal 200, first.response.status
    assert_nil first.response.headers['set-cookie']
    csrf = first.response.parsed_body.fetch('csrf_token')
    first.post "/api/bookmarks", params: location, as: :json
    assert_equal 403, first.response.status
    first.post "/api/bookmarks", params: location, headers: { 'X-Annotation-CSRF' => csrf }, as: :json
    assert_equal 201, first.response.status
    saved = first.response.parsed_body
    first.post "/api/bookmarks", params: location, headers: { 'X-Annotation-CSRF' => csrf }, as: :json
    assert_equal saved['id'], first.response.parsed_body['id']
    second.get "/api/bookmarks", params: { language: "en" }
    assert_equal [saved['id']], second.response.parsed_body['bookmarks'].map { |b| b['id'] }
    assert_nil second.response.headers['set-cookie']
    second.delete "/api/bookmarks/#{saved['id']}", params: { language: 'en' }, headers: { 'X-Annotation-CSRF' => second.response.parsed_body.fetch('csrf_token') }
    assert_equal 204, second.response.status
    first.get '/api/bookmarks', params: { language: 'en' }
    assert_empty first.response.parsed_body['bookmarks']
  end

  test "shared project lists preserve other projects across reload and deletion" do
    reader = open_session
    reader.get "/api/bookmarks", params: { language: "en" }
    csrf = reader.response.parsed_body.fetch("csrf_token")
    saved = %w[engineering-library env-auditor go-image-optimizer].map do |project|
      reader.post "/api/bookmarks", params: location.merge(project: project, document: "README"), headers: { "X-Annotation-CSRF" => csrf }, as: :json
      assert_equal 201, reader.response.status
      reader.response.parsed_body
    end
    saved.each do |bookmark|
      2.times do
        reader.get "/api/bookmarks", params: { language: "en", project_slug: bookmark.fetch("project") }
        assert_equal 200, reader.response.status
        assert_equal [bookmark.fetch("id")], reader.response.parsed_body.fetch("bookmarks").map { |item| item.fetch("id") }
        assert_equal "no-store", reader.response.headers["Cache-Control"]
      end
    end
    other_browser = open_session
    other_browser.get '/api/bookmarks', params: { language: 'en', project_slug: 'engineering-library' }
    assert_equal [saved.first['id']], other_browser.response.parsed_body['bookmarks'].map { |b| b['id'] }
    assert_difference "Bookmark.count", -1 do
      reader.delete "/api/bookmarks/#{saved.first.fetch('id')}", params: { language: "en" }, headers: { "X-Annotation-CSRF" => csrf }
      assert_equal 204, reader.response.status
    end
    reader.get "/api/bookmarks", params: { language: "en", project_slug: "engineering-library" }
    assert_empty reader.response.parsed_body.fetch("bookmarks")
    reader.get "/api/bookmarks", params: { language: "en" }
    assert_equal saved.drop(1).map { |item| item.fetch("id") }.sort, reader.response.parsed_body.fetch("bookmarks").map { |item| item.fetch("id") }.sort
  end

  test "project filter rejects unknown inactive and malformed identifiers" do
    ["missing", "", "../env-auditor", ["env-auditor"]].each do |slug|
      get "/api/bookmarks", params: { language: "en", project_slug: slug }
      assert_response :unprocessable_entity
    end
    CatalogProject.find_by!(slug: "env-auditor").update!(active: false)
    get "/api/bookmarks", params: { language: "en", project_slug: "env-auditor" }
    assert_response :unprocessable_entity
  end

  test "language collections and deletes remain independent" do
    get "/api/bookmarks", params: { language: "en" }
    headers = { "X-Annotation-CSRF" => response.parsed_body.fetch("csrf_token") }
    ids = %w[en pt-BR].to_h do |language|
      post "/api/bookmarks", params: location.merge(document: "README", language: language), headers: headers, as: :json
      assert_response :created
      [language, response.parsed_body.fetch("id")]
    end
    %w[en pt-BR].each do |language|
      get "/api/bookmarks", params: { project_slug: "engineering-library", language: language }
      assert_equal [ids[language]], response.parsed_body.fetch("bookmarks").map { |item| item.fetch("id") }
    end
    delete "/api/bookmarks/#{ids['pt-BR']}", params: { language: "en" }, headers: headers
    assert_response :not_found
    delete "/api/bookmarks/#{ids['en']}", params: { language: "en" }, headers: headers
    assert_response :no_content
    assert Bookmark.exists?(ids['pt-BR'])
    get "/api/bookmarks", params: { language: "fr" }
    assert_response :unprocessable_entity
    get "/api/bookmarks"
    assert_response :unprocessable_entity
  end

  test "invalid documents and traversal cannot be bookmarked" do
    get "/api/bookmarks", params: { language: "en" }
    csrf = response.parsed_body["csrf_token"]
    [{ project: "missing" }, { document: "../../.env.md" }, { document: "missing.md" }, { language: "fr" }, { anchor: "" }].each do |invalid|
      assert_no_difference "Bookmark.count" do
        post "/api/bookmarks", params: location.merge(invalid), headers: { "X-Annotation-CSRF" => csrf }, as: :json
        assert_response :unprocessable_entity
      end
    end
  end
end
