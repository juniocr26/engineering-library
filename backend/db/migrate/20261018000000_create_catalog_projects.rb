class CreateCatalogProjects < ActiveRecord::Migration[8.1]
  def change
    create_table :catalog_projects do |t|
      t.string :stable_id, null: false
      t.string :slug, null: false
      t.string :display_name, null: false
      t.boolean :active, null: false, default: true
      t.timestamps
    end
    add_index :catalog_projects, :stable_id, unique: true
    add_index :catalog_projects, :slug, unique: true
    execute 'CREATE INDEX catalog_projects_order ON catalog_projects ((lower(display_name) COLLATE "C"), stable_id) WHERE active'
  end
end
