class CreateBookmarks < ActiveRecord::Migration[8.1]
  def change
    create_table :bookmarks do |t|
      t.string :reader_digest, limit: 64, null: false
      t.string :project, limit: 100, null: false
      t.string :document, limit: 240, null: false
      t.string :language, limit: 5, null: false
      t.string :anchor, limit: 200, null: false
      t.string :excerpt, limit: 240, null: false, default: ""
      t.timestamps
    end
    add_index :bookmarks, [:reader_digest, :project, :document, :language, :anchor], unique: true, name: "bookmarks_logical_location"
    add_check_constraint :bookmarks, "language IN ('en', 'pt-BR')", name: "bookmarks_language"
    add_check_constraint :bookmarks, "reader_digest ~ '^[0-9a-f]{64}$'", name: "bookmarks_reader_digest"
  end
end
