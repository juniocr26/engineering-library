# Owned research driver; loads the library without Rails or Command#run/process.
require 'json'
require 'digest'
require '/app/backend/lib/documentation/command'

packet = JSON.parse(STDIN.read(131_073))
implementation = Documentation::Command.instance_method(:validate_and_render).source_location.fetch(0)
identity = {
  'version' => Documentation::Command::VERSION,
  'ruby_version' => RUBY_VERSION,
  'ruby_platform' => RUBY_PLATFORM,
  'loaded_method_source_location' => Documentation::Command.instance_method(:validate_and_render).source_location,
  'on_disk_source_sha256' => Digest::SHA256.file(implementation).hexdigest,
  'scope' => 'Fresh Ruby library process, not existing Rails worker identity or in-memory bytecode hash'
}
if identity['on_disk_source_sha256'] != packet.fetch('caller_expected_sha256')
  puts JSON.generate('status' => 'INCONCLUSIVE_CALLER_SOURCE_IDENTITY_MISMATCH', 'identity' => identity)
  exit 0
end
files = packet.fetch('files')
raise 'unexpected owned source packet' unless files.keys == ['args.go'] && Digest::SHA256.hexdigest(files.fetch('args.go')) == packet.fetch('source_full_file_sha256')
command = Documentation::Command.new({
  'DOCS_LIBRARY' => '/tmp/owned-renderer-unused-library',
  'DOCS_AGENT' => '/app/agent',
  'DOCS_SOURCES' => '/tmp/owned-renderer-unused-sources',
  'DOCS_DESTINATIONS' => '/tmp/owned-renderer-unused-destinations',
  'DOCS_CONTEXT' => 'baseline',
  'DOCS_EVIDENCE_MODE' => 'declarations',
  'DOCS_FACT_LIMIT' => '1',
  'DOCS_MODEL' => 'owned-synthetic-prose-no-model-call'
})
# The same explicit unit-selection input is normally populated from project config.
# Neither evidence_cards nor validate_and_render is overridden.
selection = { 'args.go' => ['OnlyValidArgs'] }
command.instance_variable_set(:@unit_selection, selection)
command.instance_variable_set(:@research_packet, { 'mode' => 'offline', 'references' => [] })
begin
  cards = command.send(:evidence_cards, files)
  raise 'one complete selected declaration required' unless cards.keys == ['S1'] && cards.fetch('S1')['complete_unit']
rescue StandardError => error
  puts JSON.generate('status' => 'INCONCLUSIVE_SOURCE_ADMISSION', 'identity' => identity, 'error_class' => error.class.name, 'reason' => error.message)
  exit 0
end
snapshot = { 'candidate_count' => 1, 'selection' => 'owned explicit frozen public source', 'omitted_count' => 0, 'unit_selection' => selection }
project = { 'slug' => 'owned-cobra-renderer-controls', 'require_selected_evidence_coverage' => true }
revision = packet.fetch('source_full_file_sha256')
rows = packet.fetch('cases').map do |item|
  begin
    rendered = command.send(:validate_and_render, { 'facts' => [item.fetch('fact')] }, files, revision, snapshot, project)
    { 'id' => item.fetch('id'), 'oracle_source_supported' => item.fetch('oracle_source_supported'),
      'renderer_accepted' => true, 'rendered_documents' => rendered,
      'authorship' => 'Owned manually written canary prose; no model call. Renderer metadata does not establish model authorship.' }
  rescue StandardError => error
    { 'id' => item.fetch('id'), 'oracle_source_supported' => item.fetch('oracle_source_supported'),
      'renderer_accepted' => false, 'error_class' => error.class.name, 'reason' => error.message }
  end
end
raise 'implementation changed during observation' unless identity.fetch('on_disk_source_sha256') == Digest::SHA256.file(implementation).hexdigest
puts JSON.generate('status' => 'OBSERVED_RENDERER_BOUNDARY_ONLY', 'identity' => identity, 'cards' => cards, 'rows' => rows,
                   'source_or_application_program_executed' => false, 'model_calls' => 0, 'catalog_writes' => 0,
                   'bypassed_not_measured' => ['Collector/privacy filtering', 'Command#run/process ownership and persistence', 'Model inference', 'Existing Rails-loaded process', 'Full chapter semantic approval'],
                   'production_modified' => false, 'owner_approved' => false, 'training_gold' => false)
