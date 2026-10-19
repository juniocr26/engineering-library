module Api
  class AnnotationsController < BookmarksController
    def index
      filter = params.fetch(:filter, 'all')
      page = params.fetch(:page, '1')
      unless params[:project].is_a?(String) && CatalogProject.exists?(slug: params[:project], active: true) &&
          (['all', 'notes'] + Highlight::COLORS).include?(filter) && page.is_a?(String) && page.match?(/\A[1-9]\d{0,5}\z/)
        return render json: { error: 'Invalid annotation query' }, status: :unprocessable_entity
      end
      render json: AnnotationLibrary.new(reader: @reader_digest, project: params[:project], language: params[:language]).list(filter: filter, page: page.to_i)
    end
  end
end
