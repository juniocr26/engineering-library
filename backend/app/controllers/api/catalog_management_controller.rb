require Rails.root.join('lib/documentation/catalog_management')

module Api
  class CatalogManagementController < ApplicationController
    before_action :authorize_local_management
    rescue_from ArgumentError, JSON::ParserError, Psych::Exception, Errno::ENOENT, Errno::EACCES, Errno::EPERM, with: :invalid_operation

    def show
      render json: { operation: manager.status(params[:id]) }
    end

    def create
      return head :payload_too_large if request.raw_post.bytesize > 65536
      attributes = params.permit(:id, :slug, :sourcePath, :requestId).to_h
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
      code = if params[:action_name] == 'add'
        case error.message
        when /Request identifier already used/ then 'request_conflict'
        when /Another catalog operation|needs completion|MakeDocs is running/ then 'operation_busy'
        when /relocation is ambiguous|Multiple source copies/ then 'source_conflict'
        when /Catalog metadata|Bios disagree|Catalog identity/ then 'catalog_metadata_conflict'
        when /already registered|already exists/ then 'project_exists'
        when /Source|source|Host filesystem|snapshot|Git|Permission/ then 'source_unavailable'
        else 'operation_rejected'
        end
      else
        'operation_rejected'
      end
      code = 'source_unavailable' if error.is_a?(Errno::EACCES) || error.is_a?(Errno::EPERM)
      code = 'catalog_metadata_conflict' if error.is_a?(Psych::Exception)
      render json: { error: code }, status: :unprocessable_entity
    end
  end
end
