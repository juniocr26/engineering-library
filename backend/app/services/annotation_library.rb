# Metadata is fetched in two scoped queries; only the current page loads note bodies.
# Shared scope indexes start with project/language.
class AnnotationLibrary
  PAGE_SIZE = 20

  def initialize(project:, language:)
    @scope = { project: project, language: language }
  end

  def list(filter:, page:)
    highlights = Highlight.where(@scope).select(:id, :document, :language, :project, :color, :segments, :created_at).to_a
    notes = Note.where(@scope).select(:id, :highlight_id, :document, :language, :project, :segments, :created_at).to_a
    by_anchor = highlights.group_by { |h| [h.document, Note.anchor_key(h.segments)] }
    paired = {}
    entries = notes.map do |note|
      matches = by_anchor[[note.document, Note.anchor_key(note.segments)]] || []
      highlight = matches.find { |h| h.id == note.highlight_id }
      paired[highlight.id] = true if highlight
      entry(note, highlight, note)
    end
    entries.concat(highlights.reject { |h| paired[h.id] }.map { |h| entry(h, h, nil) })
    counts = Highlight::COLORS.to_h { |color| [color, highlights.count { |h| h.color == color }] }
    counts['notes'] = notes.size
    counts['all'] = entries.size
    entries.select! { |item| filter == 'all' || (filter == 'notes' ? item[:note_id].present? : item[:color] == filter) }
    entries.sort_by! { |item| [-item[:created_at].to_f, -item[:record_id], item[:id]] }
    selected = entries.slice((page - 1) * PAGE_SIZE, PAGE_SIZE) || []
    bodies = Note.where(@scope).where(id: selected.filter_map { |item| item[:note_id] }).pluck(:id, :body).to_h
    { annotations: selected.map { |item| item.except(:record_id).merge(body: bodies[item[:note_id]]) }, counts: counts, next_page: page * PAGE_SIZE < entries.size ? page + 1 : nil }
  end

  private

  def entry(origin, highlight, note)
    { id: "#{note ? 'note' : 'highlight'}-#{origin.id}", record_id: origin.id, note_id: note&.id, highlight_id: highlight&.id,
      project: origin.project, document: origin.document, language: origin.language, segments: origin.segments,
      color: highlight&.color, created_at: origin.created_at }
  end
end
