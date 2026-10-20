require 'test_helper'

class NoteDemosApiTest < ActionDispatch::IntegrationTest
  test 'development fixture is idempotent and cleanup preserves personal and other reader records' do
    Catalog::Sync.call
    with_routing do |routes|
      routes.draw do
        namespace :api do
          resource :note_demos, only: [:create, :destroy]
          resources :notes, only: [:index]
          resources :highlights, only: [:create]
          resources :bookmarks, only: [:create]
        end
      end
      location = { project: 'engineering-library', document: 'README', language: 'en' }
      get '/api/notes', params: location
      headers = { 'X-Reader-CSRF' => response.parsed_body.fetch('csrf_token') }
      segment = { block: 'fixture-block', start: 0, end: 5, exact: 'Hello', prefix: '', suffix: '' }
      payload = location.merge(demo_key: 'visual-en-note', body: 'A note', segments: [segment], color: 'blue')
      2.times do
        post '/api/note_demos', params: payload, headers: headers, as: :json
        assert_response :created
      end
      assert_equal 1, Note.where(demo_key: 'visual-en-note').count
      assert_equal 1, Highlight.where(demo_key: 'visual-en-note').count
      post '/api/note_demos', params: payload.merge(remove_color: true), headers: headers, as: :json
      assert_response :created
      assert_nil Note.find_by!(demo_key: 'visual-en-note').highlight_id
      post '/api/highlights', params: location.merge(color: 'green', segments: [segment.merge(block: 'personal')]), headers: headers, as: :json
      assert_response :created
      personal = response.parsed_body.fetch('id')
      post '/api/bookmarks', params: location.merge(anchor: 'personal', excerpt: 'Manual bookmark'), headers: headers, as: :json
      assert_response :created
      bookmark = response.parsed_body.fetch('id')
      post '/api/note_demos', params: payload.merge(kind: 'bookmark', demo_key: 'visual-en-bookmark'), headers: headers, as: :json
      assert_response :created
      stranger = open_session
      stranger.get '/api/notes', params: location
      assert_empty stranger.response.parsed_body['notes']
      stranger.post '/api/note_demos', params: payload, headers: { 'X-Reader-CSRF' => stranger.response.parsed_body.fetch('csrf_token') }, as: :json
      assert_equal 201, stranger.response.status
      delete '/api/note_demos', params: location, headers: headers
      assert_response :no_content
      assert Highlight.exists?(personal)
      assert Bookmark.exists?(bookmark)
      assert_equal 1, Note.where(demo_key: 'visual-en-note').count
      assert_equal 0, Bookmark.where(demo_key: 'visual-en-bookmark').count
    end
  end
end
