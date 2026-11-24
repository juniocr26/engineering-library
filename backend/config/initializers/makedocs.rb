require Rails.root.join('lib/documentation/locations')

if Rails.env.development? && ENV['CATALOG_ROOT'] == '/docs'
  Documentation::Locations.new('/docs').ensure_key
end
