module Catalog
  class Page
    SIZE = 5
    def self.call(value)
      Sync.call if Files.root.join('.catalog.json').exist? || Files.root.join('.catalog.json').symlink?
      scope = CatalogProject.where(active: true)
      total = scope.count
      pages = [(total.to_f / SIZE).ceil, 1].max
      number = value.to_s.match?(/\A[0-9]{1,9}\z/) ? value.to_i : 1
      number = number.clamp(1, pages)
      records = scope.order(Arel.sql('lower(display_name) COLLATE "C" ASC, stable_id ASC')).offset((number - 1) * SIZE).limit(SIZE)
      { records: records, pagination: { page: number, total_pages: pages, total_projects: total, page_size: SIZE } }
    end
  end
end
