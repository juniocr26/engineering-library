# Research-only direct invocation of the existing physical-source renderer.
require '/app/backend/lib/documentation/project_command'
require 'json'
require 'digest'
input=JSON.parse(STDIN.read)
rows=input.fetch('cases').map do |test|
  command=Documentation::SectionCommand.new({'DOCS_EVIDENCE_MODE'=>'structural'})
  project={'slug'=>'public-cache-renderer-probe','source'=>test.fetch('source_root',input['source_root']),
    'files'=>['jmespath/parser.py'],'units'=>{'jmespath/parser.py'=>['Parser._do_parse']},
    'require_selected_evidence_coverage'=>true}
  snapshot=command.evidence(project)
  files=snapshot.fetch('files')
  raise 'source identity changed' unless Digest::SHA256.hexdigest(files.fetch('jmespath/parser.py'))==test.fetch('source_sha256',input['source_sha256'])
  cards=command.evidence_cards(files)
  fact={'evidence_id'=>'S1','en'=>test.fetch('en'),'pt-br'=>test.fetch('pt-br')}
  begin
    output=command.validate_and_render({'facts'=>[fact]},files,input.fetch('source_sha256'),snapshot,project)
    {'id'=>test.fetch('id'),'status'=>'RENDERED','card'=>cards.fetch('S1'),'output'=>output}
  rescue Documentation::Error=>error
    {'id'=>test.fetch('id'),'status'=>'REFUSED','reason'=>error.message,'card'=>cards.fetch('S1')}
  end
end
puts JSON.generate({'caller_version'=>Documentation::Command::VERSION,'rows'=>rows,'model_calls'=>0,'published_files_written'=>false,'method'=>'Existing SectionCommand.evidence and Command.validate_and_render; no mocked cards or model output generation.'})
