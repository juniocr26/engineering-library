require "test_helper"

class NotesApiTest < ActionDispatch::IntegrationTest
  setup do
    Catalog::Sync.call
    @scope = { project: 'engineering-library', document: 'README', language: 'en' }
    get '/api/highlights', params: @scope
    @headers = { 'X-Annotation-CSRF' => response.parsed_body.fetch('csrf_token') }
    @segments = [{ block: 'a-real-logical-block', start: 0, end: 5, exact: 'Hello', prefix: '', suffix: ' world' }]
    post '/api/highlights', params: @scope.merge(color: 'green', segments: @segments), headers: @headers, as: :json
    @highlight = response.parsed_body.fetch('id')
    @body = "# Revisão 📚\n\nAção e persistência.\n\n```ruby\nputs :example\n```\n\n|A|B|\n|-|-|\n|1|2|"
  end

  def create_note
    post '/api/notes', params: @scope.merge(highlight_id: @highlight, body: @body), headers: @headers, as: :json
    assert_response :created
    response.parsed_body.fetch('id')
  end

  test 'notes preserve exact Unicode and independent lifecycle across recolor removal and rehighlight' do
    id = create_note
    assert_equal @body, Note.find(id).body
    post '/api/notes', params: @scope.merge(highlight_id: @highlight, body: 'must not overwrite'), headers: @headers, as: :json
    assert_response :success
    assert_equal id, response.parsed_body['id']
    assert_equal @body, response.parsed_body['body']
    patch "/api/highlights/#{@highlight}", params: @scope.merge(color: 'blue'), headers: @headers, as: :json
    assert_response :success
    delete "/api/highlights/#{@highlight}", params: @scope, headers: @headers
    assert_response :no_content
    assert_nil Note.find(id).highlight_id
    assert_equal @segments.map(&:stringify_keys), Note.find(id).segments
    get '/api/notes', params: @scope
    assert_equal [id], response.parsed_body['notes'].map { |item| item['id'] }
    post '/api/highlights', params: @scope.merge(color: 'pink', segments: @segments), headers: @headers, as: :json
    replacement = response.parsed_body.fetch('id')
    post '/api/notes', params: @scope.merge(highlight_id: replacement, body: 'duplicate'), headers: @headers, as: :json
    assert_response :success
    assert_equal id, response.parsed_body['id']
    patch "/api/notes/#{id}", params: @scope.merge(body: "updated\n📚"), headers: @headers, as: :json
    assert_response :success
    assert_equal "updated\n📚", Note.find(id).body
    delete "/api/notes/#{id}", params: @scope, headers: @headers
    assert_response :no_content
    assert Highlight.exists?(replacement)
  end

  test 'rich source larger than the previous limit roundtrips without rewriting' do
    @body = "<div style=\"color:navy\"><svg><text>ação 📚</text></svg></div>\n" + ("Mixed **Markdown** and HTML\n" * 6000)
    id = create_note
    assert_equal @body, Note.find(id).body
    get '/api/notes', params: @scope
    assert_equal @body, response.parsed_body['notes'].find { |note| note['id'] == id }['body']
  end

  test 'shared access CSRF language document and invalid payloads' do
    id = create_note
    other_browser = open_session
    other_browser.get '/api/notes', params: @scope
    assert_equal [id], other_browser.response.parsed_body['notes'].map { |n| n['id'] }
    token = other_browser.response.parsed_body['csrf_token']
    other_browser.patch "/api/notes/#{id}", params: @scope.merge(body: @body), headers: { 'X-Annotation-CSRF' => token }, as: :json
    assert_equal 200, other_browser.response.status
    [@scope.merge(language: 'pt-BR'), @scope.merge(document: 'architecture/current-state.md')].each do |scope|
      get '/api/notes', params: scope
      assert_empty response.parsed_body['notes']
      patch "/api/notes/#{id}", params: scope.merge(body: 'wrong scope'), headers: @headers, as: :json
      assert_response :not_found
    end
    patch "/api/notes/#{id}", params: @scope.merge(body: 'no csrf'), as: :json
    assert_response :forbidden
    [nil, {}, 'a' * (Note::MAX_BYTES + 1), '📚' * (Note::MAX_BYTES / 4 + 1)].each do |body|
      patch "/api/notes/#{id}", params: @scope.merge(body: body), headers: @headers, as: :json
      assert_response :unprocessable_entity
      assert_equal @body, Note.find(id).body
    end
    post '/api/notes', params: @scope.merge(highlight_id: 0, body: ''), headers: @headers, as: :json
    assert_response :not_found
  end
end
