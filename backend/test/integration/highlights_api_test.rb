require "test_helper"

class HighlightsApiTest < ActionDispatch::IntegrationTest
  setup { Catalog::Sync.call }

  def context(language = "en")
    { project: "engineering-library", document: "README", language: language }
  end

  def passage
    { color: "yellow", segments: [{ block: "stable-block", start: 0, end: 5, exact: "Hello", prefix: "", suffix: " world" }] }
  end

  test "CRUD remains scoped to language document and anonymous reader" do
    get "/api/highlights", params: context
    assert_response :success
    headers = { "X-Reader-CSRF" => response.parsed_body.fetch("csrf_token") }
    post "/api/highlights", params: context.merge(passage), headers: headers, as: :json
    assert_response :created
    saved = response.parsed_body
    assert_nil saved["reader_digest"]
    assert_equal "stable-block", saved.fetch("segments").first.fetch("block")
    get "/api/highlights", params: context("pt-BR")
    assert_empty response.parsed_body.fetch("highlights")
    patch "/api/highlights/#{saved['id']}", params: context("pt-BR").merge(color: "red"), headers: headers, as: :json
    assert_response :not_found
    stranger = open_session
    stranger.get "/api/highlights", params: context
    assert_empty stranger.response.parsed_body.fetch("highlights")
    stranger.delete "/api/highlights/#{saved['id']}", params: context, headers: { "X-Reader-CSRF" => stranger.response.parsed_body.fetch("csrf_token") }
    assert_equal 404, stranger.response.status
    Highlight::COLORS.each do |color|
      patch "/api/highlights/#{saved['id']}", params: context.merge(color: color), headers: headers, as: :json
      assert_response :success
      assert_equal color, response.parsed_body.fetch("color")
    end
    get "/api/highlights", params: context
    assert_equal [saved['id']], response.parsed_body.fetch("highlights").map { |item| item['id'] }
    delete "/api/highlights/#{saved['id']}", params: context, headers: headers
    assert_response :no_content
  end

  test "rejects invalid scopes colors anchors and missing CSRF" do
    get "/api/highlights", params: context
    headers = { "X-Reader-CSRF" => response.parsed_body.fetch("csrf_token") }
    post "/api/highlights", params: context.merge(passage), as: :json
    assert_response :forbidden
    [{ color: "black" }, { segments: nil }, { segments: "invalid" }, { segments: [{}] }, { segments: passage[:segments].map { |part| part.merge(start: -1) } }, { language: "fr" }, { document: "../secret.md" }].each do |invalid|
      assert_no_difference "Highlight.count" do
        post "/api/highlights", params: context.merge(passage).merge(invalid), headers: headers, as: :json
        assert_response :unprocessable_entity
      end
    end
  end
end
