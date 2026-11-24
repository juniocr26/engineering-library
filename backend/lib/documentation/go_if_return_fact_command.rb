# frozen_string_literal: true
require_relative 'go_deferred_fact_command'
module Documentation
  class GoIfReturnFactCommand < GoDeferredFactCommand
    PROFILE = 'go-if-return-fallthrough-syntax-v2'
    RENDERER = File.join(__dir__, 'go_if_return_facts.py')

    def analysis_identity
      super.merge('scope' => 'exact one-to-three initializer-free if-return guards and final return syntax; no binding/type/helper/runtime proof',
        'base_source_fact_consumer_sha256' => Digest::SHA256.file(File.join(__dir__, 'go_deferred_fact_command.rb')).hexdigest,
        'consumer_sha256' => Digest::SHA256.file(__FILE__).hexdigest)
    end

    def explanation_metadata(lang)
      super.merge(title: lang == 'en' ? 'Go if-return/fallthrough syntax (deterministic draft)' :
        'Sintaxe Go de guarda/retorno e continuação (rascunho determinístico)')
    end

    # The global model-owner guard remains unchanged. Permit only exact signature
    # references and direct callees in this immutable, verified syntax fact.
    def source_backed_callee_reference?(reference, prose, card)
      return true if super
      (@go_source_derivations || {}).values.any? do |proof|
        unit = proof.fetch('unit')
        next false unless proof['path'] == card['path'] && proof['quote'] == card['quote'] &&
          unit['start_line'] == card['line'] && unit['symbol'] == card['qualified_symbol'] &&
          proof.fetch('explanations').values.include?(prose)
        signature = unit['function_type']
        next true if signature.is_a?(String) && prose.include?("`#{signature}`") &&
          signature.scan(/\b[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+/).include?(reference)
        contract = unit['if_return_contract']
        chain = unit['if_return_chain_contract']
        if chain.is_a?(Hash) && chain['kind'] == 'if-return-chain-fallthrough-expressions'
          expressions = chain.fetch('guards').flat_map do |guard|
            [guard.fetch('condition'), *guard.fetch('true_return_contract').fetch('expressions')]
          end + chain.fetch('fallthrough_return_contract').fetch('expressions')
          next expressions.any? do |expression|
            expression.match?(/(?<![\w.])#{Regexp.escape(reference)}\(/) && prose.include?("`#{expression}`")
          end
        end
        next false unless contract.is_a?(Hash) && contract['kind'] == 'if-return-fallthrough-expressions'
        %w[true_return_contract fallthrough_return_contract].any? do |branch|
          contract.fetch(branch).fetch('expressions').any? do |expression|
            expression.match?(/\A#{Regexp.escape(reference)}\(/) && prose.include?("`#{expression}`")
          end
        end
      end
    end

  end
end

exit Documentation::GoIfReturnFactCommand.new.run(ARGV) if $PROGRAM_NAME == __FILE__
