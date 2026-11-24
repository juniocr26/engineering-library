"""Read current model identity/container state and native package discoverability only."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,platform,subprocess,sys
P=Path(__file__).resolve().parent
code="""import json,urllib.request
tags=json.load(urllib.request.urlopen('http://ollama:11434/api/tags',timeout=15))
print(json.dumps([{'name':m.get('name'),'digest':m.get('digest'),'size':m.get('size'),'details':m.get('details')}for m in tags.get('models',[])if m.get('name')=='llama3.2:3b']))
"""
commands=[['/usr/local/bin/docker','exec','engineering-library-backend-1','python3','-c',code],
          ['/usr/local/bin/docker','inspect','--format','{{json .State}}','engineering-library-ollama-1']]
observations=[]
for command in commands:
 out=subprocess.run(command,capture_output=True,text=True,timeout=30)
 observations.append({'command':command,'exit_code':out.returncode,'stdout':out.stdout,'stderr':out.stderr})
 assert out.returncode==0,out.stderr
models=json.loads(observations[0]['stdout']);state=json.loads(observations[1]['stdout'])
expected='a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72'
packages={name:importlib.util.find_spec(name)is not None for name in ['mlx','mlx_lm','torch','transformers','peft','tokenizers']}
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observations':observations,
 'target_model':models,'expected_digest':expected,'digest_matches':len(models)==1 and models[0]['digest']==expected,
 'container_state':state,'framework_discoverability_no_imports':packages,'python':sys.version,
 'host_platform':platform.platform(),'new_inference_calls':0,'native_imports':0,'installations':0,
 'limitations':'Dockerstate/tagidentityandpackagefindspecarenotnativeMLXcompatibility,tokenization,trainablebaseidentity,hardwaretrainingfeasibilityorweightfilefull-byteverification.',
 'optimizer_updates':0,'gold':0}
with(P/'runtime-identity-closure-v1.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({k:v for k,v in result.items()if k!='observations'},indent=2))
