require_relative "test_helper"

class FluxosAnotacoesTest < AnotacoesIsoladasTest
  def test_highlight_nota_e_listagem_usam_modelos_reais_e_criacao_repetida_preserva_markdown
    status, highlight, = requisicao(Api::HighlightsController, "create", atributos.merge(color: "yellow", segments: segmentos), method: "POST", token: token)
    assert_equal 201, status
    data = atributos.merge(highlight_id: highlight["id"], body: "Markdown original")
    status, note, = requisicao(Api::NotesController, "create", data, method: "POST", token: token)
    assert_equal 201, status
    assert_equal "Markdown original", note["body"]
    status, repeated, = requisicao(Api::NotesController, "create", data.merge(body: "Não deve sobrescrever"), method: "POST", token: token)
    assert_equal 200, status
    assert_equal note["id"], repeated["id"]
    assert_equal "Markdown original", Note.first.body
    result = AnnotationLibrary.new(project: "projeto", language: "en").list(filter: "all", page: 1)
    assert_equal 1, result[:annotations].size
    assert_equal highlight["id"], result[:annotations][0][:highlight_id]
    assert_equal "Markdown original", result[:annotations][0][:body]
    assert_equal 1, result[:counts]["all"]
    assert_equal [], AnnotationLibrary.new(project: "projeto", language: "pt-BR").list(filter: "all", page: 1)[:annotations]
  end

  def test_mutacoes_exigem_csrf_e_documento_aprovado
    status, _, = requisicao(Api::HighlightsController, "create", atributos.merge(color: "yellow", segments: segmentos), method: "POST")
    assert_equal 403, status
    ["../segredo.md", "@contents", "ausente.md"].each do |document|
      status, _, = requisicao(Api::HighlightsController, "create", atributos.merge(document: document, color: "yellow", segments: segmentos), method: "POST", token: token)
      assert_equal 422, status
    end
    assert_equal 0, Highlight.count
  end

  def test_bookmark_repetido_nao_duplica_e_outro_idioma_nao_remove
    data = atributos.merge(anchor: "b", excerpt: "Sintético")
    first = requisicao(Api::BookmarksController, "create", data, method: "POST", token: token)
    second = requisicao(Api::BookmarksController, "create", data, method: "POST", token: token)
    assert_equal 201, first[0]
    assert_equal first[1]["id"], second[1]["id"]
    assert_equal 1, Bookmark.count
    status, _, = requisicao(Api::BookmarksController, "destroy", { id: first[1]["id"], language: "pt-BR" }, method: "DELETE", token: token)
    assert_equal 404, status
    assert_equal 1, Bookmark.count
  end

  def test_modelos_rejeitam_ancoras_inseguras_cores_e_notas_incompativeis
    highlight = Highlight.create!(**atributos, color: "yellow", segments: segmentos)
    [segmentos.map { |s| s.merge("start" => -1) }, [], segmentos.map { |s| s.merge("extra" => "SENTINELA") }].each do |parts|
      refute Highlight.new(**atributos, color: "yellow", segments: parts).valid?
    end
    refute Highlight.new(**atributos, color: "unknown", segments: segmentos).valid?
    refute Bookmark.new(**atributos, anchor: "a\n", excerpt: "").valid?
    refute Note.new(**atributos.merge(language: "pt-BR"), highlight: highlight, segments: segmentos, anchor_digest: Note.anchor_key(segmentos), body: "Sintético").valid?
  end
  def test_biblioteca_filtra_pagina_e_preserva_corpos_apenas_no_idioma_consultado
    21.times do |index|
      Highlight.create!(**atributos, color: index.even? ? "yellow" : "blue", segments: segmentos,
        created_at: Time.utc(2026, 1, 1), updated_at: Time.utc(2026, 1, 1))
    end
    highlight = Highlight.order(:id).last
    Note.create!(**atributos, highlight: highlight, segments: segmentos, anchor_digest: Note.anchor_key(segmentos), body: "Corpo sintético")
    library = AnnotationLibrary.new(project: "projeto", language: "en")
    first = library.list(filter: "all", page: 1)
    assert_equal 21, first[:counts]["all"]
    assert_equal 20, first[:annotations].size
    assert_equal 2, first[:next_page]
    assert_equal 1, library.list(filter: "all", page: 2)[:annotations].size
    assert_nil library.list(filter: "all", page: 2)[:next_page]
    assert_equal ["Corpo sintético"], library.list(filter: "notes", page: 1)[:annotations].map { |entry| entry[:body] }
    assert library.list(filter: "blue", page: 1)[:annotations].all? { |entry| entry[:color] == "blue" }
  end

  def test_nota_rejeita_conteudo_invalido_e_acima_do_limite_em_bytes
    data = atributos.merge(segments: segmentos, anchor_digest: Note.anchor_key(segmentos))
    refute Note.new(**data, body: "x" * (Note::MAX_BYTES + 1)).valid?
    refute Note.new(**data, body: nil).valid?
    assert Note.new(**data, body: "").valid?
    refute Note.new(**data, body: "\xff".b.force_encoding("UTF-8")).valid?
  end

end
