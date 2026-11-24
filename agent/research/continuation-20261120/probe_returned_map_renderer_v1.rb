# Direct existing renderer; no mocked evidence cards or model generation.
require '/app/backend/lib/documentation/project_command'
require 'json'
require 'digest'
input = JSON.parse(STDIN.read)
rows = input.fetch('cases').map do |test|
  command = Documentation::SectionCommand.new({'DOCS_EVIDENCE_MODE'=>'structural'})
  path = test.fetch('file', input.fetch('file'))
  selector = test.fetch('selector', input.fetch('selector'))
  project = {'slug'=>'returned-map-reference-probe', 'source'=>test.fetch('source_root', input.fetch('source_root')),
    'files'=>[path], 'units'=>{path=>[selector]}, 'require_selected_evidence_coverage'=>true}
  snapshot = command.evidence(project)
  files = snapshot.fetch('files')
  expected = test.fetch('source_sha256', input.fetch('source_sha256'))
  raise 'source identity changed' unless Digest::SHA256.hexdigest(files.fetch(path)) == expected
  cards = command.evidence_cards(files)
  fact = {'evidence_id'=>'S1', 'en'=>test.fetch('en'), 'pt-br'=>test.fetch('pt-br')}
  begin
    output = command.validate_and_render({'facts'=>[fact]}, files, expected, snapshot, project)
    {'id'=>test.fetch('id'), 'status'=>'RENDERED', 'card'=>cards.fetch('S1'), 'output'=>output}
  rescue Documentation::Error => error
    {'id'=>test.fetch('id'), 'status'=>'REFUSED', 'reason'=>error.message, 'card'=>cards.fetch('S1')}
  end
end
puts JSON.generate({'caller_version'=>Documentation::Command::VERSION, 'rows'=>rows,
  'source_executed'=>false, 'model_calls'=>0, 'published_files_written'=>false,
  'method'=>'Unmodified current physical-source SectionCommand evidence and validate_and_render.'})
