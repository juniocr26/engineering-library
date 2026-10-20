require "digest"

class Note < ApplicationRecord
  MAX_BYTES = 5 * 1024 * 1024
  belongs_to :highlight, optional: true
  validates :project, :document, :language, :anchor_digest, presence: true
  validates :language, inclusion: { in: %w[en pt-BR] }
  validates :body, exclusion: { in: [nil] }
  validate :safe_content

  # Context is retained for relocation; identity is the original logical block/range.
  def self.anchor_key(segments)
    Digest::SHA256.hexdigest(JSON.generate(segments.map { |s| s.slice("block", "start", "end", "exact").sort.to_h }))
  end

  private

  def safe_content
    errors.add(:body, "must be UTF-8 text of at most 5 MiB") unless body.is_a?(String) && body.valid_encoding? && body.bytesize <= MAX_BYTES
    probe = Highlight.new(project: project, document: document, language: language, color: "yellow", segments: segments)
    errors.add(:segments, "invalid text anchor") unless probe.valid?
    if highlight && highlight.attributes.slice("project", "document", "language", "segments") != attributes.slice("project", "document", "language", "segments")
      errors.add(:highlight, "must match note content location")
    end
  end
end
