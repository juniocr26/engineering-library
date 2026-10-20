class Highlight < ApplicationRecord
  COLORS = %w[yellow blue pink orange purple red green].freeze
  validates :project, :document, :language, presence: true
  validates :project, length: { maximum: 100 }
  validates :document, length: { maximum: 240 }
  validates :language, inclusion: { in: %w[en pt-BR] }
  validates :color, inclusion: { in: COLORS }
  validate :safe_segments

  private

  def safe_segments
    valid = segments.is_a?(Array) && segments.length.between?(1, 32) && segments.all? do |part|
      part.is_a?(Hash) && %w[block start end exact prefix suffix].all? { |key| part.key?(key) } &&
        part["block"].is_a?(String) && part["block"].length.between?(1, 200) &&
        part["start"].is_a?(Integer) && part["end"].is_a?(Integer) && part["start"] >= 0 && part["end"] > part["start"] && part["end"] <= 1_000_000 &&
        part["exact"].is_a?(String) && part["exact"].length.between?(1, 8000) &&
        %w[prefix suffix].all? { |key| part[key].is_a?(String) && part[key].length <= 48 } &&
        (part.keys - %w[block start end exact prefix suffix]).empty?
    end
    errors.add(:segments, "invalid text anchor") unless valid
  end
end
