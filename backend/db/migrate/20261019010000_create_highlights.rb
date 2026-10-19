class CreateHighlights < ActiveRecord::Migration[8.1]
  def change
    create_table :highlights do |t|
      t.string :reader_digest, limit: 64, null: false
      t.string :project, limit: 100, null: false
      t.string :document, limit: 240, null: false
      t.string :language, limit: 5, null: false
      t.string :color, null: false
      t.jsonb :segments, null: false
      t.timestamps
    end
    add_index :highlights, [:reader_digest, :project, :document, :language], name: "highlights_document_scope"
    add_check_constraint :highlights, "language IN ('en', 'pt-BR')", name: "highlights_language"
    add_check_constraint :highlights, "color IN ('yellow', 'blue', 'pink', 'orange', 'purple', 'red', 'green')", name: "highlights_color"
    add_check_constraint :highlights, "reader_digest ~ '^[0-9a-f]{64}$'", name: "highlights_reader_digest"
    add_check_constraint :highlights, "jsonb_typeof(segments) = 'array' AND jsonb_array_length(segments) BETWEEN 1 AND 32", name: "highlights_segments"
  end
end
