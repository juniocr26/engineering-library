class CatalogProject < ApplicationRecord
  validates :stable_id, :slug, :display_name, presence: true
  validates :stable_id, :slug, uniqueness: true
end
