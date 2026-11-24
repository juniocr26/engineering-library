class CreateNotes < ActiveRecord::Migration[8.1]
  def change
    create_table :notes do |t|
      t.string :reader_digest, limit: 64, null: false
      t.string :project, limit: 100, null: false
      t.string :document, limit: 240, null: false
      t.string :language, limit: 5, null: false
      t.jsonb :segments, null: false
      t.string :anchor_digest, limit: 64, null: false
      t.references :highlight, foreign_key: { on_delete: :nullify }, index: { unique: true }
      t.text :body, null: false
      t.string :demo_key
      t.timestamps
    end
    add_index :notes, [:reader_digest, :project, :document, :language, :anchor_digest], unique: true, name: :notes_logical_location
    add_index :notes, [:reader_digest, :demo_key], unique: true, where: 'demo_key IS NOT NULL'
    add_check_constraint :notes, "octet_length(body) <= 131072", name: :notes_body_size
    add_check_constraint :notes, "language IN ('en', 'pt-BR')", name: :notes_language
    add_check_constraint :notes, "reader_digest ~ '^[0-9a-f]{64}$'", name: :notes_reader_digest
  end
end
