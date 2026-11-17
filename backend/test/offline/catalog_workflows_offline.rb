require_relative "test_helper"
class FluxosCatalogoTest < CatalogoIsoladoTest
  def test_apresentacao_integra_bio_e_apenas_categorias_existentes
    project = projeto
    result = Catalog::Presenter.call(project, "pt-BR", details: true)
    assert_equal "projeto", result[:slug]
    assert_equal "Nome oficial", result[:name]
    assert_equal "Descrição sintética.", result[:description]
    assert_equal [{ name: "Categoria", url: "/projects/projeto/docs/categoria/index.md?lang=pt-BR" }], result[:categories]
    refute Catalog::Presenter.call(project, "en").key?(:categories)
  end
  def test_categoria_symlink_externa_nao_e_publicada
    projeto
    File.symlink(Pathname.new(@temporary), @root.join("projeto/en/externa"))
    gravar("projeto/en/index.md", "- [Externa](externa/index.md)\n")
    Pathname.new(@temporary).join("index.md").write("SENTINELA")
    assert_equal [], Catalog::Files.categories("projeto", "en")
  end
  def test_sincronizacao_aborta_antes_de_transacao_em_bios_divergentes
    projeto
    gravar("projeto/en/bio.md", "---\nid: outra-identidade\nname: Nome oficial\n---\nCorpo")
    CatalogProject.stub(:transaction, ->(*) { flunk "Não deve iniciar escrita" }) do
      assert_raises(ArgumentError) { Catalog::Sync.call }
    end
  end
  def test_sincronizacao_rejeita_identidade_duplicada_antes_de_escritas
    projeto("primeiro")
    projeto("segundo")
    CatalogProject.stub(:transaction, ->(*) { flunk "Não deve iniciar escrita" }) do
      assert_raises(ArgumentError) { Catalog::Sync.call }
    end
  end
  def test_politica_temporaria_valida_e_rejeita_dados_invalidos
    gravar('.catalog-policy.json', JSON.generate(schema: 1, temporary_projects: ['amostra']))
    assert_equal ['amostra'], Catalog::Files.temporary_projects
    gravar('.catalog-policy.json', JSON.generate(schema: 1, temporary_projects: ['../escape']))
    CatalogProject.stub(:transaction, ->(*) { flunk 'Não deve iniciar escrita' }) do
      assert_raises(ArgumentError) { Catalog::Sync.call }
    end
  end

  def test_bio_temporaria_nao_e_lida_nem_promovida_pelo_sync
    gravar('.catalog-policy.json', JSON.generate(schema: 1, temporary_projects: ['amostra']))
    gravar('amostra/en/bio.md', 'Malformed temporary metadata must not block the permanent catalog')
    entries = nil
    connection = Object.new
    connection.define_singleton_method(:execute) { |_| }
    scope = Object.new
    scope.define_singleton_method(:not) { |**conditions| entries = conditions; scope }
    scope.define_singleton_method(:where) { |**_| scope }
    scope.define_singleton_method(:update_all) { |**_| }
    CatalogProject.stub(:connection, connection) do
      CatalogProject.stub(:where, scope) do
        CatalogProject.stub(:transaction, ->(&block) { block.call }) do
          assert_equal({ indexed: 0 }, Catalog::Sync.call)
        end
      end
    end
    assert_equal({ stable_id: [] }, entries)
  end
end
