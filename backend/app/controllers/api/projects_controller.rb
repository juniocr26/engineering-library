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
      svg = Catalog::Files.read(project.slug, "bio/icon.svg")
      # Only locally maintained SVGs with no active or external content.
      return head :not_found if svg.match?(/<script|<foreignObject|\bon\w+\s*=|href\s*=|<!DOCTYPE|<!ENTITY/i)
      response.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'none'; sandbox"
      send_data svg, type: "image/svg+xml", disposition: "inline"
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
