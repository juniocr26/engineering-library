"""One actual public quote under current helper; prepare explicitly mapped consumer input."""
import datetime,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT/'agent/tools'));from documentation_retrieval import HelperRetrieval,VERSION
assert VERSION=='0.1.4';protocol=json.loads((P/'helper-ruby-httpx-consumption-protocol-v2.json').read_text());out=P/'helper-ruby-httpx-consumption-v1';out.mkdir(exist_ok=False);journal=out/'journal';journal.mkdir();tool=HelperRetrieval(protocol['registry'],str(journal),max_steps=1,max_quote_bytes=6144);result=tool.request(protocol['request'])
with(out/'helper-result.json').open('x')as f:f.write(json.dumps(result,indent=2)+'\n')
assert result['status']=='FOUND',result
unit=result['evidence'];source=protocol['registry']['httpx-current'];raw=(Path(source['root'])/protocol['request']['path']).read_bytes();assert raw[unit['quote_byte_start']:unit['quote_byte_end']]==unit['quote'].encode()
container_root='/sources/engineering-library/'+str(Path(source['root']).relative_to(ROOT));input={'source_root':container_root,'source_path':protocol['request']['path'],'selector':protocol['request']['qualified_symbol'],'source_sha256':protocol['request']['expected_sha256'],'helper_evidence':unit,'helper_version':VERSION,'cases':protocol['cases'],'mapping':'Explicitly verify the helper physical quote is contained at the identical selected unit physical lines in S1 before renderer invocation; H1 is intentionally not mapped.'}
with(out/'ruby-input.json').open('x')as f:f.write(json.dumps(input,indent=2,ensure_ascii=False)+'\n')
print({'status':result['status'],'helper_version':VERSION,'quote_bytes':len(unit['quote'].encode()),'source_executed':False,'consumer_not_yet_invoked':True})
