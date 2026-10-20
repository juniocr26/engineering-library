class RemoveAnnotationReaderOwnership < ActiveRecord::Migration[8.1]
  def up
    remove_index :bookmarks, name: 'bookmarks_logical_location'
    remove_index :highlights, name: 'highlights_document_scope'
    remove_index :notes, name: 'notes_logical_location'
    [:bookmarks, :highlights, :notes].each do |table|
      remove_index table, name: "index_#{table}_on_reader_digest_and_demo_key"
      remove_check_constraint table, name: "#{table}_reader_digest"
      remove_column table, :reader_digest
    end
  end

  def down
    raise ActiveRecord::IrreversibleMigration, 'Removed ownership cannot be reconstructed from a shared dataset.'
  end
end
