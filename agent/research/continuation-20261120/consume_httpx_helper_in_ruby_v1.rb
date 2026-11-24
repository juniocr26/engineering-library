# Isolated actual renderer consumer; public source is parsed, never imported.
require '/app/backend/lib/documentation/project_command'
require 'json'
require 'digest'
input=JSON.parse(STDIN.read)
command=Documentation::SectionCommand.new({'DOCS_EVIDENCE_MODE'=>'structural'})
project={'slug'=>'helper-httpx-renderer-research','source'=>input.fetch('source_root'),'files'=>[input.fetch('source_path')],'units'=>{input.fetch('source_path')=>[input.fetch('selector')]},'require_selected_evidence_coverage'=>true}
snapshot=command.evidence(project);files=snapshot.fetch('files');raw=files.fetch(input.fetch('source_path'));raise 'source hash drift' unless Digest::SHA256.hexdigest(raw)==input.fetch('source_sha256')
helper=input.fetch('helper_evidence');raise 'helper physical quote mismatch' unless raw.b.byteslice(helper.fetch('quote_byte_start')...helper.fetch('quote_byte_end'))==helper.fetch('quote').b
cards=command.evidence_cards(files);card=cards.fetch('S1')
rows=input.fetch('cases').map do |test|
 fact={'evidence_id'=>test.fetch('evidence_id'),'en'=>test.fetch('en'),'pt-br'=>test.fetch('pt-br')}
 begin
  output=command.validate_and_render({'facts'=>[fact]},files,input.fetch('source_sha256'),snapshot,project)
  {'id'=>test.fetch('id'),'status'=>'RENDERED','output'=>output}
 rescue Documentation::Error=>error
  {'id'=>test.fetch('id'),'status'=>'REFUSED','reason'=>error.message}
 end
end
puts JSON.generate({'caller_version'=>Documentation::Command::VERSION,'helper_version'=>input.fetch('helper_version'),'card'=>card,'helper_evidence'=>helper,'independent_source_hash_equal'=>true,'helper_quote_byte_slice_verified'=>true,'rows'=>rows,'source_executed'=>false,'model_calls'=>0,'published_files_written'=>false})
