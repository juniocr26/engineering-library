require "test_helper"
require "tmpdir"
class CatalogTest < ActiveSupport::TestCase
  setup { CatalogProject.delete_all }
  test "database pagination boundaries and alphabetical stable ordering" do
    [0, 1, 5, 6, 10, 11, 506].each do |count|
      CatalogProject.delete_all
      count.times { |i| CatalogProject.create!(stable_id: "p-#{i.to_s.rjust(4, '0')}", slug: "p-#{i}", display_name: i.even? ? "Beta" : "alpha") }
      pages = [(count.to_f / 5).ceil, 1].max
      first = Catalog::Page.call("1")
      assert_equal count, first[:pagination][:total_projects]
      assert_equal pages, first[:pagination][:total_pages]
      assert_equal [5, count].min, first[:records].size
      expected = CatalogProject.order(Arel.sql('lower(display_name) COLLATE "C", stable_id')).pluck(:stable_id)
      actual = (1..pages).flat_map { |page| Catalog::Page.call(page)[:records].map(&:stable_id) }
      assert_equal expected, actual
      assert_equal pages, Catalog::Page.call("999999")[:pagination][:page]
      [nil, "", "0", "-1", "foo", "1.5", "99999999999999999999"].each { |value| assert_equal 1, Catalog::Page.call(value)[:pagination][:page] }
    end
  end
  test "sync is idempotent, preserves identities on rename and deactivates missing entries" do
    with_catalog do |root|
      bio(root, "one", "identity", "One")
      Catalog::Sync.call
      original = CatalogProject.first
      Catalog::Sync.call
      assert_equal 1, CatalogProject.count
      assert_equal original.updated_at, original.reload.updated_at
      File.rename(root.join("one"), root.join("renamed"))
      Catalog::Sync.call
      assert_equal original.id, CatalogProject.find_by!(slug: "renamed").id
      FileUtils.rm_rf(root.join("renamed"))
      Catalog::Sync.call
      assert_not original.reload.active
      assert_equal 1, CatalogProject.count
    end
  end
  test "missing invalid and duplicate bios abort without partial writes" do
    with_catalog do |root|
      bio(root, "one", "identity", "One")
      Catalog::Sync.call
      bio(root, "two", "identity", "Two")
      assert_raises(ArgumentError) { Catalog::Sync.call }
      assert_equal 1, CatalogProject.count
      File.write(root.join("two/bio/en.md"), "invalid")
      assert_raises(ArgumentError) { Catalog::Sync.call }
      File.delete(root.join("two/bio/en.md"))
      assert_raises(ArgumentError) { Catalog::Sync.call }
      assert CatalogProject.first.active
    end
  end
  test "catalog prevents path traversal" do
    assert_raises(ArgumentError) { Catalog::Files.read("../secret", "README.md") }
    assert_raises(ArgumentError) { Catalog::Files.read("engineering-library", "../../index.md") }
  end
  private
  def with_catalog
    previous = ENV["CATALOG_ROOT"]
    Dir.mktmpdir do |directory|
      ENV["CATALOG_ROOT"] = directory
      yield Pathname.new(directory)
    end
  ensure
    ENV["CATALOG_ROOT"] = previous
  end
  def bio(root, slug, id, name)
    FileUtils.mkdir_p(root.join(slug, "bio"))
    %w[en pt-BR].each { |language| File.write(root.join(slug, "bio", "#{language}.md"), "---\nid: #{id}\nname: #{name}\n---\n\nA concise purpose.\n") }
  end
end
