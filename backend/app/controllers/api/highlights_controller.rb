module Api
  # Shares the signed anonymous cookie, CSRF verification and catalog validation.
  class HighlightsController < BookmarksController
    before_action :require_document_scope

    def index
      render json: { highlights: scope.order(:id).limit(500).map { |item| present(item) }, csrf_token: verifier.generate(@reader_digest, expires_in: 1.day, purpose: "bookmark-mutation") }
    end

    def create
      if scope.count >= 500
        render json: { error: "Highlight limit reached" }, status: :unprocessable_entity
        return
      end
      segments = params[:segments]
      segments = segments.map { |part| part.is_a?(ActionController::Parameters) ? part.permit(:block, :start, :end, :exact, :prefix, :suffix).to_h : part } if segments.is_a?(Array)
      item = scope.new(color: params[:color], segments: segments)
      if item.save
        render json: present(item), status: :created
      else
        render json: { error: "Invalid highlight" }, status: :unprocessable_entity
      end
    end

    def update
      item = scope.find_by(id: params[:id])
      return render json: { error: "Highlight not found" }, status: :not_found unless item
      if item.update(color: params[:color])
        render json: present(item)
      else
        render json: { error: "Invalid color" }, status: :unprocessable_entity
      end
    end

    def destroy
      item = scope.find_by(id: params[:id])
      return render json: { error: "Highlight not found" }, status: :not_found unless item
      item.destroy!
      head :no_content
    end

    private

    def scope
      Highlight.where(reader_digest: @reader_digest, project: params[:project], document: params[:document], language: params[:language])
    end

    def present(item) = item.as_json(only: %i[id project document language color segments created_at updated_at])

    def require_document_scope
      unless params[:document] != "@contents" && valid_document?(params.permit(:project, :document, :language).to_h)
        render json: { error: "Invalid document scope" }, status: :unprocessable_entity
      end
    end
  end
end
