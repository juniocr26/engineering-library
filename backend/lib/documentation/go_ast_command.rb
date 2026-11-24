# frozen_string_literal: true
require_relative 'project_command'

module Documentation
  # Explicit opt-in syntax preparation. Ordinary Command retains its prior selector.
  class GoAstCommand < SectionCommand
    PROFILE = 'go-standard-parser-declarations-v1'

    def validate_project(project)
      super
      unless project['units'].is_a?(Hash) && project.fetch('files').all? { |path| File.extname(path) == '.go' } &&
          project['units'].keys.sort == project['files'].sort && !project.key?('ranges')
        raise Error, 'Go AST mode requires explicit Go units for every file and no ranges'
      end
    end

    def source_units(path, text, selectors)
      raise Error, 'Go AST mode accepts Go source only' unless File.extname(path) == '.go'
      producer = File.join(@agent, 'tools/go_source_ast.py')
      raise Error, 'Go AST launcher unavailable or unsafe' if File.symlink?(producer) || !File.file?(producer)
      output, diagnostic, status = Open3.capture3('python3', producer,
        stdin_data: JSON.generate(source: text, path: path, selectors: selectors))
      raise Error, "Go AST producer refused: #{diagnostic.strip[0, 1500]}" unless status.success?
      parsed = JSON.parse(output)
      unless parsed['profile'] == PROFILE && parsed['path'] == path && parsed['source_sha256'] == digest(text) &&
          parsed['source_executed'] == false && parsed['syntax_only'] == true &&
          parsed['units'].is_a?(Array) && parsed['units'].map { |unit| unit['selector'] } == selectors
        raise Error, 'Go AST provenance differs from selected source'
      end
      producer_identity = parsed.fetch('producer')
      %w[source_sha256 binary_sha256 manifest_sha256 launcher_sha256].each do |key|
        raise Error, 'invalid Go producer identity' unless producer_identity[key].is_a?(String) && producer_identity[key].match?(/\A[0-9a-f]{64}\z/)
      end
      lines = text.lines
      parsed['units'].to_h do |unit|
        first, last = unit.values_at('start_line', 'end_line')
        unless first.is_a?(Integer) && last.is_a?(Integer) && first >= 1 && last >= first && last <= lines.size
          raise Error, 'Go AST span outside original source'
        end
        kind = unit['declaration_kind']
        raise Error, 'unsupported Go AST declaration kind' unless %w[function method type type-alias].include?(kind)
        quote = lines[(first - 1)...last].join
        # Producer returns line content without the final LF; cards retain every original byte.
        unless quote.delete_suffix("\n") == unit['quote'] && quote.bytesize <= UNIT_QUOTE_LIMIT &&
            unit['symbol'].is_a?(String) && unit['symbol'].match?(/\A[A-Za-z_]\w*(?:\.[A-Za-z_]\w*){1,2}\z/)
          raise Error, 'Go AST quote or symbol mismatch'
        end
        card = { 'path' => path, 'line' => first, 'quote' => quote, 'complete_unit' => true,
          'declaration_kind' => kind,
          'symbol' => unit['symbol'].split('.').last, 'qualified_symbol' => unit['symbol'],
          'enclosing_impl_hint' => unit['symbol'].split('.')[-2],
          'preparation' => 'explicit Go standard-parser declaration; syntax only, not type/import/runtime verification',
          'syntax_producer' => producer_identity, 'syntax_parser_version' => parsed.fetch('go_version') }
        card['required_symbol'] = unit['symbol'] if card['symbol'].size < 3
        @go_syntax_unit_proofs ||= {}
        @go_syntax_unit_proofs[[path, unit['symbol'], digest(text)]] = { 'unit' => unit, 'producer' => producer_identity,
          'quote' => quote, 'source_sha256' => digest(text) }
        [unit.fetch('selector'), card]
      end
    rescue Errno::ENOENT, JSON::ParserError, KeyError, TypeError => error
      raise Error, "Go AST producer unavailable or invalid (#{error.class})"
    end

    def go_syntax_unit_proof(card, source)
      proof = (@go_syntax_unit_proofs || {}).fetch([card['path'], card['qualified_symbol'], digest(source)]) do
        raise Error, 'missing exact Go syntax derivation'
      end
      unless proof['quote'] == card['quote'] && proof['unit']['start_line'] == card['line'] &&
          proof['unit']['symbol'] == card['qualified_symbol'] && proof['source_sha256'] == digest(source)
        raise Error, 'Go syntax derivation differs from selected card'
      end
      proof
    end

    # Refuse the observed positive EN/PT error only with an exact same-body proof.
    # This does not validate arbitrary prose, helper behavior or unsupported scopes.
    def deferred_execution_order_contradiction?(prose, card, source)
      contract = go_syntax_unit_proof(card, source).fetch('unit')['handler_defer_contract']
      return false unless contract.is_a?(Hash) &&
        contract['kind'] == 'handler-literal-defer-then-direct-call-v1' &&
        contract['source_statement_order'] == %w[defer-registration direct-call] &&
        contract['direct_call_expression'] == 'next.ServeHTTP(w, r)'
      # A faithful quotation of a misleading source comment is not an assertion
      # that its described behavior occurs. Keep that existing citation behavior.
      plain = prose.gsub(/`[^`]*`|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/, ' ')
      # Conservative exclusions preserve negated statements and explicit corrections.
      return false if plain.match?(/\b(?:not|never|incorrect|wrong|false|rejects?|rejected|não|nunca|incorreta?|incorreto|errada?|errado|falsa?|falso|rejeita)\b/i)
      return false unless plain.match?(/\bdefer\b/i)
      plain.match?(/\bpanic\s+is\s+handled\s+before\s+the\s+next\s+function\s+in\s+the\s+pipeline\s+is\s+called\b/i) ||
        plain.match?(/\bpanic\s+seja\s+lidado\s+antes\s+que\s+a\s+próxima\s+função\s+no\s+pipeline\s+seja\s+chamada\b/i)
    end
  end
end

exit Documentation::GoAstCommand.new.run(ARGV) if $PROGRAM_NAME == __FILE__
