require Rails.root.join('lib/documentation/catalog')

class RuntimeHealthController < ApplicationController
  def show
    if ENV['DOCS_HOST_REQUIRED'] == '1' && !Documentation::Catalog.new(Catalog::Files.root).host_filesystem.available?
      render json: { status: 'unavailable', component: 'host_filesystem' }, status: :service_unavailable
    else
      render json: { status: 'ok' }
    end
  rescue ArgumentError, IOError, SystemCallError
    render json: { status: 'unavailable', component: 'host_filesystem' }, status: :service_unavailable
  end
end
