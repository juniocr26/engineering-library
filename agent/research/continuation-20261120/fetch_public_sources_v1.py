import pathlib,json,hashlib,urllib.request,datetime,concurrent.futures
ROOT=pathlib.Path(__file__).resolve().parent
TARGET=ROOT/'new-public-sources-v1'
SPECS=[('jmespath/jmespath.py','e600d11e5d4e90b0d7f67882756fffc90a52eb36',['jmespath/__init__.py','jmespath/parser.py','jmespath/visitor.py','LICENSE.txt']),('jmespath/jmespath.py','6ff419a8b171d055a9bfc6904605bceb8b7a80ef',['jmespath/__init__.py','jmespath/parser.py','jmespath/visitor.py','LICENSE.txt']),('lukeed/totalist','193f6476c04804dba24f02a6e1fa0f509b205be9',['src/index.js','src/sync.js','license','package.json']),('lukeed/totalist','4b071d3e54d466a4059de89006c752da782c8b02',['src/index.js','src/sync.js','license','package.json']),('twpayne/go-geom','35c4f489de5a7c7ff43af07e02c07a121fbd6a70',['geom.go','flat.go','point.go','LICENSE','go.mod']),('twpayne/go-geom','ccb5701a505df08114edca6b19efaf9d3f01fc8d',['geom.go','flat.go','point.go','LICENSE','go.mod'])]
def fetch(item):
 repo,rev,name=item; url=f'https://raw.githubusercontent.com/{repo}/{rev}/{name}'
 row={'repository':repo,'revision':rev,'source_path':name,'url':url,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=40) as response:
   raw=response.read(262145);row['http_status']=response.status
  if len(raw)>262144:raise ValueError('source receipt byte cap exceeded')
  dest=TARGET/repo.replace('/','--')/rev/name;dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb') as stream:stream.write(raw)
  row.update(local_path=str(dest.relative_to(ROOT)),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),status='preserved')
 except Exception as error:row.update(status='failed',error=str(error))
 return row
if __name__=='__main__':
 TARGET.mkdir(exist_ok=False)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,[(r,v,n) for r,v,ns in SPECS for n in ns]))
 (ROOT/'new-public-source-provenance-v1.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'freeze':'new-family-evaluation-freeze-v3.json','read_only_external_repositories':True,'sources_executed':False,'rows':rows},indent=2)+'\n')
 print(json.dumps({'preserved':sum(x['status']=='preserved' for x in rows),'failed':[x for x in rows if x['status']=='failed']}))
