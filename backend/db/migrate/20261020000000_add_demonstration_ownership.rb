class AddDemonstrationOwnership < ActiveRecord::Migration[8.1]
  def change
    [:highlights, :bookmarks].each do |table|
      add_column table, :demo_key, :string
      add_index table, [:reader_digest, :demo_key], unique: true, where: 'demo_key IS NOT NULL'
    end
  end
end
