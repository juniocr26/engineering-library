module Api
  # Explicit shared development data; never mounted in production.
  class NoteDemosController < NotesController
    before_action :require_demo_project

    def index
      records = [Note, Highlight, Bookmark].to_h do |model|
        [model.table_name, model.where(project: params[:project], document: params[:document], language: params[:language]).where.not(demo_key: nil).order(:id).as_json(only: [:id, :project, :document, :language, :demo_key, :segments, :anchor, :highlight_id, :color])]
      end
      render json: records.merge(csrf_token: csrf_token)
    end

    def create
      return invalid_body unless params[:body].is_a?(String)
      key = params[:demo_key]
      return render json: { error: 'Invalid demonstration' }, status: :unprocessable_entity unless key.is_a?(String) && key.match?(/\A(?:phase2-\d{2}|visual-(?:en|pt-BR)-[a-z0-9-]+)\z/)
      segments = params[:segments]
      return render json: { error: 'Invalid anchors' }, status: :unprocessable_entity unless segments.is_a?(Array) && segments.length.between?(1, 32) && segments.all? { |part| part.is_a?(ActionController::Parameters) }
      segments = segments.map { |part| part.permit(:block, :start, :end, :exact, :prefix, :suffix).to_h }
      return render json: { error: 'Invalid color' }, status: :unprocessable_entity unless Highlight::COLORS.include?(params[:color] || 'green')
      attributes = { project: params[:project], document: params[:document], language: params[:language], segments: segments }
      probe = Highlight.new(attributes.merge(color: params[:color] || 'green'))
      return render json: { error: 'Invalid anchors' }, status: :unprocessable_entity unless probe.valid?
      if params[:kind] == 'bookmark'
        location = attributes.except(:segments).merge(anchor: segments.first['block'])
        existing = Bookmark.order(:id).find_by(location)
        return render json: { error: 'Personal bookmark exists' }, status: :conflict if existing && existing.demo_key != key
        item = Bookmark.find_or_initialize_by(project: params[:project], document: params[:document], language: params[:language], demo_key: key)
        item.update!(location.merge(excerpt: segments.first['exact']))
        return render json: { id: item.id }, status: :created
      end
      if params[:kind] == 'highlight'
        item = Highlight.find_or_initialize_by(project: params[:project], document: params[:document], language: params[:language], demo_key: key)
        item.update!(attributes.merge(color: params[:color] || 'yellow'))
        return render json: { id: item.id }, status: :created
      end
      item = Note.find_or_initialize_by(project: params[:project], document: params[:document], language: params[:language], demo_key: key)
      # Never take over a personal note occupying this passage.
      collision = scope.where(anchor_digest: Note.anchor_key(segments), demo_key: nil).where.not(id: item.id).exists?
      return render json: { error: 'Passage already has a personal note' }, status: :conflict if collision
      Note.transaction do
        item.assign_attributes(attributes.merge(anchor_digest: Note.anchor_key(segments), body: params[:body]))
        if item.highlight || !(key == 'phase2-15' || params[:remove_color] == true)
          highlight = item.highlight || Highlight.find_or_initialize_by(project: params[:project], document: params[:document], language: params[:language], demo_key: key)
          # Reconcile deterministic anchors after document edits, only for demo-owned colors.
          if highlight.demo_key == key
            highlight.update!(attributes.merge(color: params[:color] || 'green'))
            item.highlight = highlight
          end
        end
        item.save!
        item.highlight&.destroy! if item.highlight&.demo_key == key && (key == 'phase2-15' || params[:remove_color] == true)
      end
      render json: present(item.reload), status: :created
    rescue ActiveRecord::RecordInvalid, ActiveRecord::RecordNotUnique
      render json: { error: 'Invalid or occupied demonstration anchor' }, status: :unprocessable_entity
    end

    def destroy
      Note.where(project: params[:project]).where.not(demo_key: nil).find_each do |note|
        note.destroy!
      end
      [Highlight, Bookmark].each do |model|
        model.where(project: params[:project]).where.not(demo_key: nil).destroy_all
      end
      head :no_content
    end

    private

    def require_demo_project
      render json: { error: 'Demonstrations belong to Engineering Library' }, status: :unprocessable_entity unless params[:project] == 'engineering-library'
    end
  end
end
