"""Isolated exact-hash paired link correction; published documents stay read-only."""
import datetime,hashlib,json,posixpath,re,sys,unicodedata,urllib.parse
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT/'agent/tools'))
from documentation_workspace import directory,read,same_root
protocol_path=P/'go-catalog-link-repair-protocol-v1.json';protocol=json.loads(protocol_path.read_text());baseline=json.loads((P/'baseline.json').read_text());sha=lambda raw:hashlib.sha256(raw).hexdigest();snapshots={};pairs={}
with directory(str(ROOT))as fd:
 inputs={name:read(fd,name,262144)[0]for name in protocol['input_hashes']}
 for name,raw in inputs.items():assert sha(raw)==protocol['input_hashes'][name]==baseline['tracked_identity'][name]['sha256']
 catalog=json.loads(inputs['docs/go-image-optimizer/en/links/catalog.json']);assert catalog['project']=='go-image-optimizer'
 for language in ['en','pt-br']:
  name='docs/go-image-optimizer/'+language+'/operations/source-review.md';before=inputs[name].decode();lines=before.splitlines(keepends=True);changes=[];result=[];fence=None;offset=0
  for number,line in enumerate(lines,1):
   marker=re.match(r'^\s*(`{3,}|~{3,})',line)
   if marker:
    token=marker.group(1)
    if fence is None:fence=token
    elif token[0]==fence[0]and len(token)>=len(fence):fence=None
    result.append(line);offset+=len(line.encode());continue
   replacement=line
   if fence is None and re.match(r'^\s*[-*]\s+\[',line):
    matches=list(re.finditer(r'(?<!!)\[[^\]\n]+\]\(([^\s)]+)\)',line))
    for match in reversed(matches):
     href=match.group(1);url=urllib.parse.urlsplit(href)
     if url.scheme or url.netloc or url.query:continue
     decoded=unicodedata.normalize('NFC',urllib.parse.unquote(url.path));parts=decoded.split('/')
     if 'Portifólio'not in parts:continue
     index=parts.index('Portifólio');assert all(part=='..'for part in parts[:index])and parts[index+1]=='go-image-optimizer';source_path='/'.join(parts[index+2:]);record=catalog['files'].get(source_path)
     assert record and record['status']=='available'and re.fullmatch(r'snapshots/[a-f0-9]{64}\.txt',record['snapshot'])
     snapshot_name='docs/go-image-optimizer/en/links/'+record['snapshot'];snapshot=read(fd,snapshot_name,512000)[0];assert sha(snapshot)==record['sha256'];snapshots[snapshot_name]={'sha256':sha(snapshot),'bytes':len(snapshot)}
     assert not url.fragment or re.fullmatch(r'L[1-9][0-9]*(?:-L?[1-9][0-9]*)?',url.fragment)
     parent=posixpath.dirname('/workspace/engineering-library/'+name);target='/workspace/go-image-optimizer/'+source_path;destination=posixpath.relpath(target,parent)+('#'+url.fragment if url.fragment else'')
     start,end=match.span(1);replacement=replacement[:start]+destination+replacement[end:]
     changes.append({'line':number,'before_href':href,'after_href':destination,'source_path':source_path,'source_fingerprint':record['sha256'],'snapshot':snapshot_name,'original_href_byte_start':offset+len(line[:start].encode()),'original_href_byte_end':offset+len(line[:end].encode())})
   result.append(replacement);offset+=len(line.encode())
  after=''.join(result);assert len(changes)==3 and after!=before
  # Replay only the registered byte edits to prove every other byte is preserved.
  replay=inputs[name]
  for change in sorted(changes,key=lambda c:c['original_href_byte_start'],reverse=True):
   start,end=change['original_href_byte_start'],change['original_href_byte_end'];assert replay[start:end].decode()==change['before_href'];replay=replay[:start]+change['after_href'].encode()+replay[end:]
  assert replay.decode()==after
  pairs[language]={'path':name,'document_id':'operations/source-review.md','before_source':before,'before_sha256':sha(inputs[name]),'candidate_source':after,'candidate_sha256':sha(after.encode()),'changes':changes,'all_non_href_bytes_preserved':True}
 assert {c['source_path']for c in pairs['en']['changes']}=={c['source_path']for c in pairs['pt-br']['changes']}
 for name,raw in inputs.items():assert read(fd,name,262144)[0]==raw
 for name,identity in snapshots.items():assert sha(read(fd,name,512000)[0])==identity['sha256']
 assert same_root(str(ROOT),fd)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'ISOLATED_SOURCE_BOUND_PAIRED_CANDIDATE_AWAITING_CONSUMER_REVIEW','project':'go-image-optimizer','proposed_action':'MODIFY','label_category':'DOCUMENT_REPAIR_NOT_SOURCE_EVOLUTION','protocol_sha256':sha(protocol_path.read_bytes()),'pairs':pairs,'source_snapshot_identities':snapshots,'input_identity_hashes':protocol['input_hashes'],'catalog_has_upstream_git_revision':False,'source_binding':'Existing content-addressed approvedcatalogsnapshot identities; no invented Gitrevision or externalrepo mutation.','all_live_inputs_rechecked':True,'active_catalog_or_documents_written':False,'ui_components_changed':False,'owner_approved':False,'training_gold':False,'training_excluded':True,'publication_authorized':False,'model_calls':0,'source_code_executed':False}
with(P/'go-catalog-link-paired-candidate-v1.json').open('x')as f:f.write(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
print({'languages':2,'exact_href_edits':6,'snapshots':len(snapshots),'non_href_bytes_preserved':True,'published':False})
