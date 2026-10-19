module Api
  # Explicit opt-in, current-cookie development data; never mounted in production.
  class NoteDemosController < NotesController
    def create
      return invalid_body unless params[:body].is_a?(String)
      key = params[:demo_key]
      return render json: { error: 'Invalid demonstration' }, status: :unprocessable_entity unless key.is_a?(String) && key.match?(/\Aphase2-\d{2}\z/)
      segments = params[:segments]
      return render json: { error: 'Invalid anchors' }, status: :unprocessable_entity unless segments.is_a?(Array) && segments.length.between?(1, 32) && segments.all? { |part| part.is_a?(ActionController::Parameters) }
      segments = segments.map { |part| part.permit(:block, :start, :end, :exact, :prefix, :suffix).to_h }
      item = Note.find_or_initialize_by(reader_digest: @reader_digest, demo_key: key)
      attributes = { project: params[:project], document: params[:document], language: params[:language], segments: segments }
      # Never take over a personal note occupying this passage.
      collision = scope.where(anchor_digest: Note.anchor_key(segments)).where.not(id: item.id).exists?
      return render json: { error: 'Passage already has a personal note' }, status: :conflict if collision
      Note.transaction do
        item.assign_attributes(attributes.merge(anchor_digest: Note.anchor_key(segments), body: params[:body]))
        if item.new_record?
          item.highlight = Highlight.create!(attributes.merge(reader_digest: @reader_digest, color: 'green'))
        end
        item.save!
        item.highlight&.destroy! if key == 'phase2-15'
      end
      render json: present(item.reload), status: :created
    rescue ActiveRecord::RecordInvalid, ActiveRecord::RecordNotUnique
      render json: { error: 'Invalid or occupied demonstration anchor' }, status: :unprocessable_entity
    end

    def destroy
      Note.where(reader_digest: @reader_digest).where.not(demo_key: nil).find_each do |note|
        Note.transaction do
          highlight = note.highlight
          note.destroy!
          highlight&.destroy!
        end
      end
      head :no_content
    end
  end
end
