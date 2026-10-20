require 'test_helper'

class NoteDemosApiTest < ActionDispatch::IntegrationTest
  test 'shared fixture is idempotent and cleanup preserves manual annotations' do
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
      headers = { 'X-Annotation-CSRF' => response.parsed_body.fetch('csrf_token') }
      segment = { block: 'fixture-block', start: 0, end: 5, exact: 'Hello', prefix: '', suffix: '' }
      payload = location.merge(demo_key: 'visual-en-note', body: 'A note', segments: [segment], color: 'blue')
      2.times do
        post '/api/note_demos', params: payload, headers: headers, as: :json
        assert_response :created
      end
      assert_equal 1, Note.where(demo_key: 'visual-en-note').count
      assert_equal 1, Highlight.where(demo_key: 'visual-en-note').count
      moved = segment.merge(block: 'moved-fixture-block')
      post '/api/note_demos', params: payload.merge(segments: [moved], color: 'red'), headers: headers, as: :json
      assert_response :created
      assert_equal 'moved-fixture-block', Note.find_by!(demo_key: 'visual-en-note').segments.first['block']
      assert_equal 'moved-fixture-block', Highlight.find_by!(demo_key: 'visual-en-note').segments.first['block']
      assert_equal 'red', Highlight.find_by!(demo_key: 'visual-en-note').color
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
      assert_equal 1, stranger.response.parsed_body['notes'].size
      stranger.post '/api/note_demos', params: payload, headers: { 'X-Annotation-CSRF' => stranger.response.parsed_body.fetch('csrf_token') }, as: :json
      assert_equal 201, stranger.response.status
      demo_highlight = Highlight.create!(project: location[:project], document: location[:document], language: location[:language], color: 'red', segments: [segment.stringify_keys], demo_key: 'visual-en-manual-attachment')
      manual_note = Note.create!(project: location[:project], document: location[:document], language: location[:language], segments: demo_highlight.segments, anchor_digest: Note.anchor_key(demo_highlight.segments), highlight: demo_highlight, body: 'Manual independent content')
      delete '/api/note_demos', params: location, headers: headers
      assert_response :no_content
      assert_nil manual_note.reload.highlight_id
      assert_equal 'Manual independent content', manual_note.body
      assert Highlight.exists?(personal)
      assert Bookmark.exists?(bookmark)
      assert_equal 0, Note.where(demo_key: 'visual-en-note').count
      assert_equal 0, Bookmark.where(demo_key: 'visual-en-bookmark').count
    end
  end
end
