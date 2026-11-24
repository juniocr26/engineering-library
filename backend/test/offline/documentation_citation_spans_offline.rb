require 'bundler/setup'
require 'minitest/autorun'
require_relative '../../lib/documentation/command'

class DocumentationCitationSpansTest < Minitest::Test
  def source
    "# Acentuação preservada: ação\nclass First:\n    def value(self):\n        return 7\n\nclass Second:\n    def value(self):\n        return 7\n"
  end

  def command_and_card
    command = Documentation::Command.new
    card = command.source_units('sample.py', source, ['Second.value']).values.first
    [command, card]
  end

  def render(command, card)
    command.define_singleton_method(:evidence_cards) { |_| { 'S1' => card } }
    facts = { 'facts' => [{ 'evidence_id' => 'S1',
      'en' => '`Second.value` returns the literal value `7` in the selected source method.',
      'pt-br' => '`Second.value` retorna o valor literal `7` no método selecionado da fonte.' }] }
    command.validate_and_render(facts, { 'sample.py' => source }, 'frozen-source',
      { 'candidate_count' => 1, 'selection' => 'explicit', 'omitted_count' => 0 },
      { 'slug' => 'citation-sample' })
  end

  def test_identical_method_quotes_keep_the_selected_owner_source_location
    command, card = command_and_card
    assert_equal 7, card.fetch('line')
    documents = render(command, card)
    documents.each_value do |text|
      assert_includes text, '`sample.py:7`'
      refute_includes text, '`sample.py:3`'
      assert_includes text, 'def value(self):'
      assert_includes text, 'return 7'
    end
  end

  def test_quote_at_a_different_source_line_is_refused
    command, card = command_and_card
    card['line'] = 6
    assert_raises(Documentation::Error) { render(command, card) }
  end

  def test_missing_source_line_is_refused
    command, card = command_and_card
    card.delete('line')
    assert_raises(Documentation::Error) { render(command, card) }
  end

  def test_noninteger_and_out_of_range_lines_are_refused
    [0, -1, 99, '7', nil, true].each do |line|
      command, card = command_and_card
      card['line'] = line
      assert_raises(Documentation::Error, "line #{line.inspect}") { render(command, card) }
    end
  end

  def test_unique_source_quote_and_multibyte_prefix_keep_valid_citation
    command = Documentation::Command.new
    text = "# ação e revisão\nLIMIT = 7\n"
    card = { 'path' => 'limit.py', 'line' => 2, 'quote' => "LIMIT = 7\n" }
    command.define_singleton_method(:evidence_cards) { |_| { 'S1' => card } }
    result = { 'facts' => [{ 'evidence_id' => 'S1',
      'en' => 'The source declares LIMIT with the literal value 7.',
      'pt-br' => 'O código declara LIMIT com o valor literal 7.' }] }
    documents = command.validate_and_render(result, { 'limit.py' => text }, 'frozen',
      { 'candidate_count' => 1, 'selection' => 'explicit', 'omitted_count' => 0 },
      { 'slug' => 'citation-sample' })
    documents.each_value { |document| assert_includes document, '`limit.py:2`' }
  end
end
