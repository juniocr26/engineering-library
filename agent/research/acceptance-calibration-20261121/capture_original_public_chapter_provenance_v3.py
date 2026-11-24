"""Preserve exact original public baseline captures; never infer or rescore."""
from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
proto=json.loads((P/'original-public-chapter-provenance-capture-protocol-v1.json').read_text())
out=P/'original-public-chapter-provenance-captures-v1';receipts=[]
def sha(raw):return hashlib.sha256(raw).hexdigest()
for meta in proto['selected']:
 f=ROOT/'.local-backups/continuation-20261119'/meta['raw_artifact'];raw=f.read_bytes();rows=[json.loads(s) for s in raw.splitlines()] if f.suffix=='.jsonl' else [json.loads(raw)]
 if rows and all('event' in r and 'payload' in r for r in rows):events=rows;capture_form='event-jsonl'
 else:
  matches=[r for r in rows if any(e.get('event')=='model_response' and e.get('payload',{}).get('historical_original_body_sha256')==meta['response_sha256'] for e in r.get('trace',[]))];assert len(matches)==1;record=matches[0];events=record['trace'];capture_form='record-with-trace-selected-by-exact-response-digest'
 reqs=[(i,e) for i,e in enumerate(events) if e['event']=='model_request'];responses=[(i,e) for i,e in enumerate(events) if e['event']=='model_response'];assert len(reqs)==len(responses)==1
 ri,req=reqs[0];si,resp=responses[0];body=resp['payload']['body'].encode();assert sha(body)==meta['response_sha256']==resp['payload']['historical_original_body_sha256'];content=json.loads(body)['message']['content'];reqraw=(json.dumps(req['payload'],ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode();dest=out/meta['id']
 if dest.exists():
  assert (dest/'raw-response.json').read_bytes()==body and (dest/'recorded-request.json').read_bytes()==reqraw and (dest/'model-content.txt').read_text()==content
  receipt=json.loads((dest/'origin.json').read_text());assert receipt['original_response_sha256']==sha(body);receipt={**receipt,'existing_v1_copy_verified_not_overwritten':True,'capture_form':capture_form}
 else:
  dest.mkdir();(dest/'raw-response.json').write_bytes(body);(dest/'model-content.txt').write_text(content);(dest/'recorded-request.json').write_bytes(reqraw)
  receipt={'id':meta['id'],'capture':str(f.relative_to(ROOT)),'capture_sha256':sha(raw),'capture_form':capture_form,'request_event':ri,'response_event':si,'original_response_sha256':meta['response_sha256'],'original_raw_response_body_hash_matches':True,'recorded_request_canonical_withLF_sha256':sha(reqraw),'request_original_HTTP_encoding_not_claimed':True,'request_at':req['at'],'response_at':resp['at'],'source_executed_now':False,'model_calls_now':0,'original_semantic_scores_unchanged':True};(dest/'origin.json').write_text(json.dumps(receipt,indent=2)+'\n')
 receipts.append(receipt)
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'receipts':receipts,'count':len(receipts),'all_exact_original_body_hashes_match':True,'original_semantic_scores_unchanged':True,'new_model_calls':0,'no_gold':True,'v1_partial_failure':'Initial inline adapter stopped at event-jsonl rails-baseline after32 copies; v2 added event-jsonl and stopped after33 at matrix alias coverage-policy-live-gio-dimensions-helpers vs underlying gio-dimensions-helpers. v3 selects unique trace record by exact original response digest, not display alias. All partial copies verified without overwrite; no model calls or originals changed.'}
with (P/'original-public-chapter-provenance-capture-results-v3.json').open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({'count':len(receipts),'all_match':True,'new_model_calls':0}))
