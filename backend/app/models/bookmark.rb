class Bookmark < ApplicationRecord
  validates :project, :document, :language, :anchor, :reader_digest, presence: true
  validates :project, length: { maximum: 100 }
  validates :document, length: { maximum: 240 }
  validates :anchor, length: { maximum: 200 }, format: { without: /[\x00-\x1f\x7f]/ }
  validates :excerpt, length: { maximum: 240 }
  validates :language, inclusion: { in: %w[en pt-BR] }
end
