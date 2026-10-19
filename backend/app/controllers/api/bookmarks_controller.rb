require "digest"
require "securerandom"

module Api
  class BookmarksController < ApplicationController
    include ActionController::Cookies
    before_action :identify_reader
    before_action :verify_reader_csrf, except: :index
    rescue_from ActiveRecord::ActiveRecordError, with: :database_unavailable

    def index
      bookmarks = scope
      if params.key?(:project_slug)
        slug = params[:project_slug]
        unless slug.is_a?(String) && CatalogProject.exists?(slug: slug, active: true)
          render json: { error: "Invalid project" }, status: :unprocessable_entity
          return
        end
        bookmarks = bookmarks.where(project: slug)
      end
      render json: { bookmarks: bookmarks.order(created_at: :desc).limit(200).map { |bookmark| present(bookmark) }, csrf_token: verifier.generate(@reader_digest, expires_in: 1.day, purpose: "bookmark-mutation") }
    end

    def create
      attributes = params.permit(:project, :document, :language, :anchor, :excerpt).to_h
      unless valid_document?(attributes)
        render json: { error: "Invalid document" }, status: :unprocessable_entity
        return
      end
      location = attributes.slice("project", "document", "language", "anchor")
      bookmark = scope.find_by(location)
      if !bookmark && scope.count >= 200
        render json: { error: "Bookmark limit reached" }, status: :unprocessable_entity
        return
      end
      bookmark ||= scope.create_or_find_by!(location) { |record| record.excerpt = attributes["excerpt"].to_s.first(240) }
      render json: present(bookmark), status: :created
    rescue ActiveRecord::RecordInvalid
      render json: { error: "Invalid bookmark" }, status: :unprocessable_entity
    end

    def destroy
      bookmark = scope.find_by(id: params[:id])
      if bookmark
        bookmark.destroy!
        head :no_content
      else
        render json: { error: "Bookmark not found" }, status: :not_found
      end
    end

    private

    def verifier = Rails.application.message_verifier("anonymous-bookmarks")
    def scope = Bookmark.where(reader_digest: @reader_digest)
    def present(bookmark) = bookmark.as_json(only: %i[id project document language anchor excerpt created_at])

    def identify_reader
      response.set_header("Cache-Control", "no-store")
      token = cookies.signed[:engineering_reader]
      unless token.is_a?(String) && token.match?(/\A[0-9a-f]{64}\z/)
        unless request.get?
          render json: { error: "Reader identity required" }, status: :forbidden
          return
        end
        token = SecureRandom.hex(32)
        cookies.signed[:engineering_reader] = { value: token, httponly: true, same_site: :lax, secure: Rails.env.production?, path: "/", expires: 1.year.from_now }
      end
      @reader_digest = Digest::SHA256.hexdigest(token)
    end

    def verify_reader_csrf
      digest = verifier.verified(request.headers["X-Reader-CSRF"], purpose: "bookmark-mutation")
      render json: { error: "Invalid CSRF token" }, status: :forbidden unless digest == @reader_digest
    end

    def valid_document?(attributes)
      slug, document, language = attributes.values_at("project", "document", "language")
      return false unless slug.is_a?(String) && CatalogProject.exists?(slug: slug, active: true) && %w[en pt-BR].include?(language)
      return false unless document.is_a?(String) && document.length <= 240 && !document.include?("\\") && !document.include?("\0")
      relative = if document == "README"
        language == "en" ? "README.md" : "README.pt-BR.md"
      else
        return false unless document.end_with?(".md") && document.split("/", -1).none? { |part| ["", ".", ".."].include?(part) }
        "docs/#{language}/#{document}"
      end
      Catalog::Files.read(slug, relative)
      true
    rescue ArgumentError, Errno::ENOENT, Errno::EACCES
      false
    end

    def database_unavailable
      render json: { error: "Bookmarks unavailable" }, status: :service_unavailable
    end
  end
end
