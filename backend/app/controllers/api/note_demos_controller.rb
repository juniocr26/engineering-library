module Api
  # Explicit opt-in, current-cookie development data; never mounted in production.
  class NoteDemosController < NotesController
    before_action :require_demo_project

    def create
      return invalid_body unless params[:body].is_a?(String)
      key = params[:demo_key]
      return render json: { error: 'Invalid demonstration' }, status: :unprocessable_entity unless key.is_a?(String) && key.match?(/\A(?:phase2-\d{2}|visual-(?:en|pt-BR)-[a-z0-9-]+)\z/)
      segments = params[:segments]
      return render json: { error: 'Invalid anchors' }, status: :unprocessable_entity unless segments.is_a?(Array) && segments.length.between?(1, 32) && segments.all? { |part| part.is_a?(ActionController::Parameters) }
      segments = segments.map { |part| part.permit(:block, :start, :end, :exact, :prefix, :suffix).to_h }
      return render json: { error: 'Invalid color' }, status: :unprocessable_entity unless Highlight::COLORS.include?(params[:color] || 'green')
      attributes = { project: params[:project], document: params[:document], language: params[:language], segments: segments }
      probe = Highlight.new(attributes.merge(reader_digest: @reader_digest, color: params[:color] || 'green'))
      return render json: { error: 'Invalid anchors' }, status: :unprocessable_entity unless probe.valid?
      if params[:kind] == 'bookmark'
        location = attributes.except(:segments).merge(anchor: segments.first['block'])
        existing = Bookmark.find_by(location.merge(reader_digest: @reader_digest))
        return render json: { error: 'Personal bookmark exists' }, status: :conflict if existing && existing.demo_key != key
        item = Bookmark.find_or_initialize_by(reader_digest: @reader_digest, demo_key: key)
        item.update!(location.merge(excerpt: segments.first['exact']))
        return render json: { id: item.id }, status: :created
      end
      if params[:kind] == 'highlight'
        item = Highlight.find_or_initialize_by(reader_digest: @reader_digest, demo_key: key)
        item.update!(attributes.merge(color: params[:color] || 'yellow'))
        return render json: { id: item.id }, status: :created
      end
      item = Note.find_or_initialize_by(reader_digest: @reader_digest, demo_key: key)
      # Never take over a personal note occupying this passage.
      collision = scope.where(anchor_digest: Note.anchor_key(segments)).where.not(id: item.id).exists?
      return render json: { error: 'Passage already has a personal note' }, status: :conflict if collision
      Note.transaction do
        item.assign_attributes(attributes.merge(anchor_digest: Note.anchor_key(segments), body: params[:body]))
        if item.new_record?
          item.highlight = Highlight.create!(attributes.merge(reader_digest: @reader_digest, color: params[:color] || 'green', demo_key: key))
        end
        item.save!
        item.highlight&.destroy! if key == 'phase2-15' || params[:remove_color] == true
      end
      render json: present(item.reload), status: :created
    rescue ActiveRecord::RecordInvalid, ActiveRecord::RecordNotUnique
      render json: { error: 'Invalid or occupied demonstration anchor' }, status: :unprocessable_entity
    end

    def destroy
      Note.where(reader_digest: @reader_digest, project: params[:project]).where.not(demo_key: nil).find_each do |note|
        Note.transaction do
          highlight = note.highlight
          note.destroy!
          highlight&.destroy! if highlight&.demo_key == note.demo_key
        end
      end
      [Highlight, Bookmark].each do |model|
        model.where(reader_digest: @reader_digest, project: params[:project]).where.not(demo_key: nil).destroy_all
      end
      head :no_content
    end

    private

    def require_demo_project
      render json: { error: 'Demonstrations belong to Engineering Library' }, status: :unprocessable_entity unless params[:project] == 'engineering-library'
    end
  end
end
