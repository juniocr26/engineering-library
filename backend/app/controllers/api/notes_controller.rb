module Api
  class NotesController < HighlightsController
    def index
      render json: { notes: scope.order(:id).limit(500).map { |item| present(item) }, csrf_token: verifier.generate(@reader_digest, expires_in: 1.day, purpose: "bookmark-mutation") }
    end

    def create
      return invalid_body unless params[:body].is_a?(String)
      highlight = Highlight.where(reader_digest: @reader_digest, project: params[:project], document: params[:document], language: params[:language]).find_by(id: params[:highlight_id])
      return render json: { error: "Highlight not found" }, status: :not_found unless highlight
      highlight.with_lock do
        key = Note.anchor_key(highlight.segments)
        item = scope.find_by(anchor_digest: key)
        # Repeated creation opens the original; it never overwrites its Markdown.
        return render json: present(item) if item
        return render json: { error: "Note limit reached" }, status: :unprocessable_entity if scope.count >= 500
        item = scope.new(highlight: highlight, segments: highlight.segments, anchor_digest: key, body: params[:body])
        if item.save
          render json: present(item), status: :created
        else
          render json: { error: "Invalid note. Maximum size is 5 MiB of UTF-8 text." }, status: :unprocessable_entity
        end
      end
    end

    def update
      return invalid_body unless params[:body].is_a?(String)
      item = scope.find_by(id: params[:id])
      return render json: { error: "Note not found" }, status: :not_found unless item
      if item.update(body: params[:body])
        render json: present(item)
      else
        render json: { error: "Invalid note. Maximum size is 5 MiB of UTF-8 text." }, status: :unprocessable_entity
      end
    end

    def destroy
      item = scope.find_by(id: params[:id])
      return render json: { error: "Note not found" }, status: :not_found unless item
      item.destroy!
      head :no_content
    end

    private

    def invalid_body
      render json: { error: "Markdown body must be a string" }, status: :unprocessable_entity
    end

    def scope
      Note.where(reader_digest: @reader_digest, project: params[:project], document: params[:document], language: params[:language])
    end

    def present(item) = item.as_json(only: %i[id highlight_id project document language segments body created_at updated_at])
  end
end
