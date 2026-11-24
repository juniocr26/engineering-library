# frozen_string_literal: true
require_relative 'go_ast_command'
module Documentation
  class GoSourceFactCommand < GoAstCommand
    PROFILE = 'go-sole-return-syntax-v1'
    RENDERER = File.join(__dir__, 'go_return_facts.py')

    def validate_project(project)
      super
      raise Error, 'Go source facts require offline research' unless @env.fetch('DOCS_RESEARCH', 'offline') == 'offline'
      raise Error, 'Go source facts reject questions and feedback' if project.key?('question') || project.key?('feedback')
    end

    def analysis_identity
      { 'profile' => PROFILE, 'producer_sha256' => Digest::SHA256.file(RENDERER).hexdigest,
        'consumer_sha256' => Digest::SHA256.file(__FILE__).hexdigest,
        'Go_ast_consumer_sha256' => Digest::SHA256.file(File.join(__dir__, 'go_ast_command.rb')).hexdigest,
        'Go_manifest_sha256' => Digest::SHA256.file(File.join(@agent, 'tools/go-source-ast/manifest.json')).hexdigest,
        'model_inference' => false, 'scope' => 'sole-return syntax; imports, types, helper meanings and runtime unverified' }
    end

    def evidence(project)
      super.merge('source_analysis' => analysis_identity)
    end

    def infer(files, _skills)
      raise Error, 'Go source facts reject public references' unless (@research_packet || {}).fetch('references', []).empty?
      @go_source_derivations = {}
      facts = evidence_cards(files).map do |id, card|
        proof = go_syntax_unit_proof(card, files.fetch(card.fetch('path')))
        unless %w[function method].include?(proof.fetch('unit').fetch('declaration_kind'))
          raise Error, 'Go source facts require function or method declarations'
        end
        output, _, status = Open3.capture3('python3', RENDERER, stdin_data: JSON.generate(proof.fetch('unit')))
        result = JSON.parse(output)
        raise Error, "Go source facts refused: #{result.fetch('reason', 'renderer unavailable')}" unless status.success?
        unless result['profile'] == PROFILE && result['model_inference'] == false
          raise Error, 'invalid Go source-fact profile'
        end
        @go_source_derivations[id] = proof.merge('path' => card['path'], 'explanations' => result.fetch('explanations'))
        { 'evidence_id' => id, 'en' => result.fetch('explanations').fetch('en'), 'pt-br' => result.fetch('explanations').fetch('pt-br') }
      end
      audit('source_analysis', analysis_identity.merge('derivations' => @go_source_derivations))
      { 'result' => { 'facts' => facts }, 'request' => { 'source_analysis' => analysis_identity },
        'response' => { 'origin' => 'source-derived', 'model_inference' => false } }
    rescue JSON::ParserError, KeyError, TypeError, SystemCallError => error
      raise Error, "Go source-fact producer unavailable or invalid (#{error.class})"
    end

    def model_inference?; false; end
    def supports_model_fact_reuse?; false; end

    def explanation_metadata(lang)
      if lang == 'en'
        { title: 'Go return syntax facts (deterministic draft)', actor_label: 'analyzer', actor_value: PROFILE,
          caveat: 'Bounded Go AST syntax facts, without model inference. Exact source lines were checked. This profile does not provide complete behavioral documentation, type checking or runtime verification. Human factual and bilingual review is required.' }
      else
        { title: 'Fatos sintáticos de retorno Go (rascunho determinístico)', actor_label: 'analisador', actor_value: PROFILE,
          caveat: 'Fatos sintáticos limitados de AST Go, sem inferência de modelo. Linhas exatas da fonte foram conferidas. O perfil não fornece documentação comportamental completa, verificação de tipos ou de execução. É necessária revisão humana factual e bilíngue.' }
      end
    end

    def fact_origin_note(fact, lang)
      proof = (@go_source_derivations || {}).fetch(fact['evidence_id']) { raise Error, 'missing Go source-fact derivation' }
      unless fact[lang] == proof.fetch('explanations').fetch(lang) && fact['path'] == proof['path'] &&
          fact['line'] == proof.fetch('unit').fetch('start_line') && fact['quote'] == proof['quote']
        raise Error, 'Go source-derived explanation or citation was changed'
      end
      checksum = analysis_identity.fetch('producer_sha256')
      lang == 'en' ? "Origin: deterministic Go syntax fact; renderer SHA-256: `#{checksum}`; model inference: not invoked; human review: pending." :
        "Origem: fato sintático Go determinístico; SHA-256 do renderizador: `#{checksum}`; inferência de modelo: não invocada; revisão humana: pendente."
    end
  end
end
exit Documentation::GoSourceFactCommand.new.run(ARGV) if $PROGRAM_NAME == __FILE__
