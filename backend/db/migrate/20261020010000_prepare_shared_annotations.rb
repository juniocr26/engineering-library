# Expand first: preserve every row and foreign key before removing obsolete ownership.
class PrepareSharedAnnotations < ActiveRecord::Migration[8.1]
  def up
    add_column :bookmarks, :location_variant, :integer, default: 0, null: false
    execute <<~SQL
      WITH ranked AS (
        SELECT id, row_number() OVER (
          PARTITION BY project, document, language, anchor ORDER BY id
        ) - 1 AS variant FROM bookmarks
      )
      UPDATE bookmarks SET location_variant = ranked.variant FROM ranked WHERE bookmarks.id = ranked.id
    SQL
    add_index :bookmarks, [:project, :language, :document, :anchor, :location_variant], unique: true, name: 'bookmarks_shared_location'
    add_index :highlights, [:project, :language, :document], name: 'highlights_shared_scope'
    # Distinct notes at an identical range retain their own IDs and Markdown bodies.
    add_index :notes, [:project, :language, :document, :anchor_digest], name: 'notes_shared_scope'
    [:notes, :highlights, :bookmarks].each do |table|
      # Keep the earliest seed key canonical; retain conflicts under explicit legacy keys.
      # IDs, content and note/highlight relationships remain untouched.
      execute <<~SQL
        WITH ranked AS (
          SELECT id, row_number() OVER (PARTITION BY project, document, language, demo_key ORDER BY id) AS position
          FROM #{table} WHERE demo_key IS NOT NULL
        )
        UPDATE #{table} SET demo_key = '__legacy_demo__' || #{table}.id::text || ':' || #{table}.demo_key
        FROM ranked WHERE #{table}.id = ranked.id AND ranked.position > 1
      SQL
      add_index table, [:project, :document, :language, :demo_key], unique: true, where: 'demo_key IS NOT NULL', name: "#{table}_shared_demo_key"
      # Old identity is no longer needed for new writes during the expand/contract transition.
      change_column_null table, :reader_digest, true
    end
  end

  def down
    raise ActiveRecord::IrreversibleMigration, 'Shared writes have no former browser owner; restore a reviewed backup instead.'
  end
end
