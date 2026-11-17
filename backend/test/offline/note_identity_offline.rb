require_relative "test_helper"
class IdentidadeNotaTest < Minitest::Test
  def test_identidade_preserva_ancora_e_ignora_contexto_de_relocalizacao
    segment = { "block" => "b", "start" => 0, "end" => 4, "exact" => "text", "prefix" => "antes", "suffix" => "depois" }
    original = Note.anchor_key([segment])
    assert_equal original, Note.anchor_key([segment.merge("prefix" => "outro", "suffix" => "contexto")])
    assert_equal original, Note.anchor_key([segment.to_a.reverse.to_h])
    %w[block start end exact].each do |field|
      changed = segment.merge(field => (field == "start" || field == "end" ? 9 : "outro"))
      refute_equal original, Note.anchor_key([changed])
    end
  end
end
