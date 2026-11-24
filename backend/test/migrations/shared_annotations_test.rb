require 'test_helper'
require Rails.root.join('db/migrate/20261018010000_create_bookmarks')
require Rails.root.join('db/migrate/20261019010000_create_highlights')
require Rails.root.join('db/migrate/20261019020000_create_notes')
require Rails.root.join('db/migrate/20261020000000_add_demonstration_ownership')
require Rails.root.join('db/migrate/20261020010000_prepare_shared_annotations')
require Rails.root.join('db/migrate/20261020020000_remove_annotation_reader_ownership')

class SharedAnnotationsMigrationTest < ActiveSupport::TestCase
  test 'conflicting legacy rows retain IDs bodies locations and foreign keys' do
    connection = ActiveRecord::Base.connection
    original_path = connection.schema_search_path
    schema = "migration_shared_#{SecureRandom.hex(6)}"
    connection.execute("CREATE SCHEMA #{schema}")
    connection.schema_search_path = schema
    ActiveRecord::Migration.suppress_messages do
      [CreateBookmarks, CreateHighlights, CreateNotes, AddDemonstrationOwnership].each { |migration| migration.new.migrate(:up) }
    end
    2.times do |index|
      digest = (index + 1).to_s * 64
      common = "'#{digest}', 'engineering-library', 'README', 'en'"
      connection.execute("INSERT INTO bookmarks(id,reader_digest,project,document,language,anchor,excerpt,demo_key,created_at,updated_at) VALUES (#{index+1},#{common},'same-block','distinct excerpt #{index}','same-seed',now(),now())")
      connection.execute("INSERT INTO highlights(id,reader_digest,project,document,language,color,segments,demo_key,created_at,updated_at) VALUES (#{index+1},#{common},'blue','[{\"block\":\"same-block\"}]','same-seed',now(),now())")
      connection.execute("INSERT INTO notes(id,reader_digest,project,document,language,segments,anchor_digest,highlight_id,body,demo_key,created_at,updated_at) VALUES (#{index+1},#{common},'[{\"block\":\"same-block\"}]','#{'a'*64}',#{index+1},'distinct body #{index}','same-seed',now(),now())")
    end
    before = connection.select_all('SELECT id, highlight_id, segments, body, anchor_digest FROM notes ORDER BY id').to_a
    ActiveRecord::Migration.suppress_messages do
      PrepareSharedAnnotations.new.migrate(:up)
      RemoveAnnotationReaderOwnership.new.migrate(:up)
    end
    assert_equal before, connection.select_all('SELECT id, highlight_id, segments, body, anchor_digest FROM notes ORDER BY id').to_a
    assert_equal [0, 1], connection.select_values('SELECT location_variant FROM bookmarks ORDER BY id').map(&:to_i)
    %w[bookmarks highlights notes].each do |table|
      assert_equal 2, connection.select_value("SELECT count(*) FROM #{table}").to_i
      assert_equal 2, connection.select_value("SELECT count(DISTINCT demo_key) FROM #{table}").to_i
      assert_not connection.columns(table).any? { |column| column.name == 'reader_digest' }
    end
    connection.execute('DELETE FROM highlights WHERE id = 1')
    assert_nil connection.select_value('SELECT highlight_id FROM notes WHERE id = 1')
    assert_equal 'distinct body 0', connection.select_value('SELECT body FROM notes WHERE id = 1')
  ensure
    connection.schema_search_path = original_path if original_path
    connection.execute("DROP SCHEMA IF EXISTS #{schema} CASCADE") if schema
  end
end
