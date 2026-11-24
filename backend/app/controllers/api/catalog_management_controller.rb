require Rails.root.join('lib/documentation/catalog_management')

module Api
  class CatalogManagementController < ApplicationController
    before_action :authorize_local_management
    rescue_from ArgumentError, JSON::ParserError, Errno::ENOENT, with: :invalid_operation

    def show
      render json: { operation: manager.status(params[:id]) }
    end

    def directories
      render json: { directories: manager.directories }
    end

    def create
      return head :payload_too_large if request.raw_post.bytesize > 4096
      attributes = params.permit(:id, :name, :slug, :sourcePath).to_h
      if params[:action_name] == 'add' && params.key?(:sourceSelection)
        attributes['sourcePath'] = manager.resolve_directory(params[:sourceSelection], attributes['slug'])
      end
      render json: { operation: manager.enqueue(params[:action_name], attributes) }, status: :accepted
    end

    private

    def manager
      @manager ||= Documentation::CatalogManagement.new(Catalog::Files.root)
    end

    def authorize_local_management
      # The existing Compose deployment binds both HTTP services to loopback.
      # Public/production deployments cannot enable these filesystem operations.
      return head :forbidden unless Rails.env.development?
      state = Documentation::Locations.new(Catalog::Files.root).runtime
      key = state.join('management.key')
      return head :forbidden if state.symlink? || key.symlink? || !key.file?
      expected = key.read.strip
      supplied = request.headers['X-Catalog-Key'].to_s
      head :forbidden unless expected.match?(/\A[0-9a-f]{64}\z/) && ActiveSupport::SecurityUtils.secure_compare(expected, supplied)
    end

    def invalid_operation(error)
      Rails.logger.warn("Catalog management rejected: #{error.class}")
      code = if params[:action_name] == 'add' && params.key?(:sourceSelection)
        case error.message
        when /already registered|already exists/ then 'project_exists'
        when /Source|source/ then 'source_unavailable'
        else 'operation_rejected'
        end
      else
        'operation_rejected'
      end
      render json: { error: code }, status: :unprocessable_entity
    end
  end
end
