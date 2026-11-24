class ExpandNoteBodySize < ActiveRecord::Migration[8.1]
  def up
    remove_check_constraint :notes, name: :notes_body_size
    add_check_constraint :notes, "octet_length(body) <= 5242880", name: :notes_body_size
  end

  def down
    remove_check_constraint :notes, name: :notes_body_size
    add_check_constraint :notes, "octet_length(body) <= 131072", name: :notes_body_size
  end
end
