# frozen_string_literal: true
require_relative 'project_command'

module Documentation
  # Explicit source-only profile; the ordinary model command remains separate.
  class SourceFactCommand < SectionCommand
    PROFILE = 'python-async-dispatch-return-and-iteration-v4'
    PRODUCER = File.join(__dir__, 'python_async_facts.py')

    def validate_project(project)
      super
      raise Error, 'source facts require offline research' unless @env.fetch('DOCS_RESEARCH', 'offline') == 'offline'
      raise Error, 'source facts do not accept authoring questions or feedback' if project.key?('question') || project.key?('feedback')
      unless project['units'] && project.fetch('files').all? { |path| File.extname(path) == '.py' } && project['units'].keys.sort == project['files'].sort
        raise Error, 'source facts require explicit Python units for every selected file'
      end
    end

    def analysis_identity
      { 'profile' => PROFILE, 'producer_sha256' => Digest::SHA256.file(PRODUCER).hexdigest,
        'consumer_sha256' => Digest::SHA256.file(__FILE__).hexdigest, 'model_inference' => false,
        'scope' => 'bounded source syntax; helper/type/runtime behavior unverified' }
    end

    def evidence(project)
      super.merge('source_analysis' => analysis_identity)
    end

    def infer(files, _skills)
      raise Error, 'source facts cannot mix public-reference generation' unless (@research_packet || {}).fetch('references', []).empty?
      @source_derivations = {}
      facts = evidence_cards(files).map do |id, card|
        raise Error, 'source facts require a complete selected unit' unless card['complete_unit'] && card['symbol']
        selector = card['qualified_symbol'] || card['symbol']
        packet = JSON.generate(source: files.fetch(card.fetch('path')), selector: selector)
        output, _, status = Open3.capture3('python3', PRODUCER, stdin_data: packet)
        analysis = JSON.parse(output)
        raise Error, "source facts refused: #{analysis.fetch('reason', 'producer unavailable')}" unless status.success?
        ir = analysis.fetch('ir')
        unless ir['kind'] == 'source-derived' && ir['qualified_symbol'] == selector && ir['line'] == card['line'] &&
            ir['quote'] == card['quote'] && ir['quote_sha256'] == digest(card['quote']) &&
            ir['source_sha256'] == digest(files.fetch(card['path'])) && ir['source_executed'] == false
          raise Error, 'source-fact provenance differs from selected source'
        end
        @source_derivations[id] = analysis.merge('path' => card['path'])
        { 'evidence_id' => id, 'en' => analysis.fetch('explanations').fetch('en'),
          'pt-br' => analysis.fetch('explanations').fetch('pt-br') }
      end
      audit('source_analysis', analysis_identity.merge('derivations' => @source_derivations))
      { 'result' => { 'facts' => facts }, 'request' => { 'source_analysis' => analysis_identity },
        'response' => { 'origin' => 'source-derived', 'model_inference' => false } }
    rescue JSON::ParserError, KeyError, SystemCallError => error
      raise Error, "source-fact producer unavailable or invalid (#{error.class})"
    end

    def model_inference?
      false
    end

    def supports_model_fact_reuse?
      false
    end

    def source_backed_callee_reference?(reference, prose, card)
      return true if super
      (@source_derivations || {}).values.any? do |proof|
        ir = proof.fetch('ir')
        next false unless proof['path'] == card['path'] && ir['quote_sha256'] == digest(card['quote']) &&
          ir['qualified_symbol'] == (card['qualified_symbol'] || card['symbol']) && proof.fetch('explanations').value?(prose)
        spans = prose.scan(/`([^`\r\n]+)`/).flatten
        if ir['shape'] == 'local-call-awaited-return'
          [[ir.fetch('binding_callee'), ir.fetch('binding_call')],
           [ir.fetch('returned_callee'), "return await #{ir.fetch('returned_call')}"]].any? do |callee, expression|
            callee == reference && spans.include?(expression)
          end
        elsif ir['shape'] == 'local-call-guarded-yield-await'
          [[ir.fetch('initial_callee'), ir.fetch('initial_call')],
           [ir.fetch('yielded_callee'), "yield await #{ir.fetch('yielded_call')}"]].any? do |callee, expression|
            callee == reference && spans.include?(expression)
          end
        else
          %w[truthy falsy].any? do |branch|
            ir.fetch("#{branch}_callee") == reference && spans.include?(ir.fetch("#{branch}_await"))
          end
        end
      end
    rescue KeyError, TypeError
      false
    end

    def explanation_metadata(lang)
      if lang == 'en'
        { title: 'Source facts (deterministic draft)', actor_label: 'analyzer', actor_value: PROFILE,
          caveat: 'These facts come from bounded Python AST analysis, not model inference. Exact source lines were checked. Helper behavior, dynamic dispatch and runtime success are unverified. Human factual and bilingual review is required.' }
      else
        { title: 'Fatos da fonte (rascunho determinístico)', actor_label: 'analisador', actor_value: PROFILE,
          caveat: 'Estes fatos vêm de análise AST Python limitada, não de inferência de modelo. Linhas exatas da fonte foram conferidas. Comportamento de auxiliares, despacho dinâmico e sucesso em execução não foram verificados. É necessária revisão humana factual e bilíngue.' }
      end
    end

    def fact_origin_note(fact, lang)
      proof = (@source_derivations || {}).fetch(fact['evidence_id']) { raise Error, 'missing source-fact derivation' }
      unless fact[lang] == proof.fetch('explanations').fetch(lang) && fact['path'] == proof['path'] &&
          fact['line'] == proof.fetch('ir').fetch('line') && digest(fact['quote']) == proof['ir']['quote_sha256']
        raise Error, 'source-derived explanation or citation was changed'
      end
      checksum = analysis_identity.fetch('producer_sha256')
      lang == 'en' ? "Origin: deterministic source-derived fact; producer SHA-256: `#{checksum}`; model inference: not invoked; human review: pending." :
        "Origem: fato determinístico derivado da fonte; SHA-256 do produtor: `#{checksum}`; inferência de modelo: não invocada; revisão humana: pendente."
    end
  end
end

exit Documentation::SourceFactCommand.new.run(ARGV) if $PROGRAM_NAME == __FILE__
