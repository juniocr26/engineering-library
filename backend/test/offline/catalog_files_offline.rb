require_relative "test_helper"
class ArquivosCatalogoTest < CatalogoIsoladoTest
  def test_leitura_valida_e_rejeicao_de_traversal
    projeto
    assert_equal "# Conteúdo", Catalog::Files.read("projeto", "en/categoria/index.md")
    ["../segredo", "/segredo", "a/../../segredo"].each do |path|
      assert_raises(ArgumentError) { Catalog::Files.read("projeto", path) }
    end
    ["../projeto", "Projeto", "projeto/filho", ""].each do |slug|
      assert_raises(ArgumentError) { Catalog::Files.read(slug, "en/bio.md") }
    end
  end
  def test_symlink_de_arquivo_e_projeto_nao_escapa_do_catalogo
    projeto
    outside = Pathname.new(@temporary).join("segredo")
    outside.binwrite("SENTINELA")
    File.symlink(outside, @root.join("projeto/en/externo.md"))
    assert_raises(ArgumentError) { Catalog::Files.read("projeto", "en/externo.md") }
    File.symlink(Pathname.new(@temporary), @root.join("externo"))
    assert_raises(ArgumentError) { Catalog::Files.read("externo", "segredo") }
  end
  def test_arquivo_ausente_e_leitura_binaria
    projeto
    assert_raises(Errno::ENOENT) { Catalog::Files.read("projeto", "ausente.md") }
    bytes = "RIFF\x00\xff\x80\x00WEBP".b
    gravar("projeto/img/icon.webp", bytes)
    assert_equal bytes, Catalog::Files.read("projeto", "img/icon.webp", encoding: Encoding::BINARY)
  end
  def test_bio_exige_metadados_seguros_e_corpo
    projeto
    assert_equal "identidade", Catalog::Files.bio("projeto", "en")[:id]
    ["sem frontmatter", "---\nid: ../invalido\n---\nCorpo", "---\nid: valido\nname: []\n---\nCorpo", "---\nid: valido\n---\n   "].each do |content|
      gravar("projeto/en/bio.md", content)
      assert_raises(ArgumentError) { Catalog::Files.bio("projeto", "en") }
    end
    gravar("projeto/en/bio.md", "---\nid: valido\nname: !ruby/object:Object {}\n---\nCorpo")
    assert_raises(Psych::Exception) { Catalog::Files.bio("projeto", "en") }
  end
end
