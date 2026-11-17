module Api
  class ProjectsController < ApplicationController
    rescue_from ArgumentError, Errno::ENOENT, Psych::Exception, with: :catalog_unavailable
    def index
      result = Catalog::Page.call(params[:page])
      render json: { projects: result[:records].map { |project| Catalog::Presenter.call(project, language) }, pagination: result[:pagination] }
    end
    def show
      project = CatalogProject.find_by!(slug: params[:id], active: true)
      render json: Catalog::Presenter.call(project, language, details: true)
    end
    def icon
      project = CatalogProject.find_by!(slug: params[:id], active: true)
      image = Catalog::Files.read(project.slug, "img/icon.webp", encoding: Encoding::BINARY)
      return head :not_found unless image.start_with?("RIFF") && image.byteslice(8, 4) == "WEBP"
      response.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'none'; sandbox"
      send_data image, type: "image/webp", disposition: "inline"
    rescue Errno::ENOENT
      head :not_found
    end
    private
    def language
      Catalog::Files::LANGUAGES.include?(params[:lang]) ? params[:lang] : "pt-BR"
    end
    def catalog_unavailable
      render json: { error: "catalog_unavailable" }, status: :service_unavailable
    end
  end
end
