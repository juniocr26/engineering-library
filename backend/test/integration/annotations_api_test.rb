require 'test_helper'

class AnnotationsApiTest < ActionDispatch::IntegrationTest
  setup do
    Catalog::Sync.call
    @scope = { project: 'engineering-library', document: 'README', language: 'en' }
    get '/api/highlights', params: @scope
    @headers = { 'X-Annotation-CSRF' => response.parsed_body.fetch('csrf_token') }
    @segments = [{ block: 'stable-test-block', start: 0, end: 5, exact: 'Hello', prefix: '', suffix: ' world' }]
    post '/api/highlights', params: @scope.merge(color: 'blue', segments: @segments), headers: @headers, as: :json
    @highlight = response.parsed_body.fetch('id')
    post '/api/notes', params: @scope.merge(highlight_id: @highlight, body: '**A saved note**'), headers: @headers, as: :json
    @note = response.parsed_body.fetch('id')
    @query = @scope.except(:document)
  end

  test 'combined entries counts filters independent notes and stable edit chronology' do
    get '/api/annotations', params: @query
    assert_response :success
    data = response.parsed_body
    assert_equal 1, data['annotations'].size
    assert_equal @note, data['annotations'][0]['note_id']
    assert_equal 'blue', data['annotations'][0]['color']
    assert_equal 1, data['counts']['blue']
    assert_equal 1, data['counts']['notes']
    original = data['annotations'][0]['created_at']
    patch "/api/notes/#{@note}", params: @scope.merge(body: 'Edited'), headers: @headers, as: :json
    get '/api/annotations', params: @query
    assert_equal original, response.parsed_body['annotations'][0]['created_at']
    delete "/api/highlights/#{@highlight}", params: @scope, headers: @headers
    get '/api/annotations', params: @query.merge(filter: 'notes')
    assert_equal [@note], response.parsed_body['annotations'].map { |item| item['note_id'] }
    assert_nil response.parsed_body['annotations'][0]['color']
    assert_equal 0, response.parsed_body['counts']['blue']
    get '/api/annotations', params: @query.merge(filter: 'blue')
    assert_empty response.parsed_body['annotations']
    post '/api/highlights', params: @scope.merge(color: 'pink', segments: @segments), headers: @headers, as: :json
    get '/api/annotations', params: @query.merge(filter: 'pink')
    assert_equal 1, response.parsed_body['annotations'].size
    assert_nil response.parsed_body['annotations'][0]['note_id']
    get '/api/annotations', params: @query.merge(filter: 'notes')
    assert_nil response.parsed_body['annotations'][0]['color']
  end

  test 'all documents newest first deterministic ties and pagination' do
    timestamp = Time.current
    25.times do |index|
      Highlight.create!(project: @scope[:project], document: 'architecture/current-state.md', language: 'en', color: Highlight::COLORS[index % 7], segments: @segments.map { |s| s.merge(block: "block-#{index}") }, created_at: timestamp)
    end
    get '/api/annotations', params: @query
    first = response.parsed_body
    assert_equal 20, first['annotations'].length
    assert_equal 2, first['next_page']
    assert_equal 26, first['counts']['all']
    ids = first['annotations'].map { |item| item['highlight_id'] }
    assert_equal ids.sort.reverse, ids
    get '/api/annotations', params: @query.merge(page: 2)
    second = response.parsed_body
    assert_equal 6, second['annotations'].length
    assert_nil second['next_page']
    assert_empty first['annotations'].map { |a| a['id'] } & second['annotations'].map { |a| a['id'] }
    Highlight::COLORS.each do |color|
      get '/api/annotations', params: @query.merge(filter: color)
      assert response.parsed_body['annotations'].all? { |item| item['color'] == color }
      assert_equal first['counts'][color], response.parsed_body['annotations'].size
    end
  end

  test 'shared project language invalid queries and bounded query count' do
    stranger = open_session
    stranger.get '/api/annotations', params: @query
    assert_equal [@note], stranger.response.parsed_body['annotations'].map { |n| n['note_id'] }
    get '/api/annotations', params: @query.merge(language: 'pt-BR')
    assert_empty response.parsed_body['annotations']
    other = CatalogProject.where(active: true).where.not(slug: @scope[:project]).first!
    get '/api/annotations', params: @query.merge(project: other.slug)
    assert_empty response.parsed_body['annotations']
    [{ filter: 'favorites' }, { language: 'xx' }, { project: '../private' }, { page: '0' }, { page: '-1' }, { page: '1junk' }, { filter: ['blue'] }].each do |invalid|
      get '/api/annotations', params: @query.merge(invalid)
      assert_response :unprocessable_entity
    end
    queries = []
    callback = ->(_name, _start, _finish, _id, payload) { queries << payload[:sql] unless payload[:name] == 'SCHEMA' }
    ActiveSupport::Notifications.subscribed(callback, 'sql.active_record') do
      AnnotationLibrary.new(project: @scope[:project], language: 'en').list(filter: 'all', page: 1)
    end
    assert_equal 3, queries.count { |sql| sql.match?(/\ASELECT/) }
  end
end
