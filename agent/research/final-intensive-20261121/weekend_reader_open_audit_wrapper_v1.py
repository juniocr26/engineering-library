import sys,json,runpy,os,hashlib,datetime
from pathlib import Path
script=Path(sys.argv[1]).resolve();selected=Path(sys.argv[2]).resolve();original=Path(sys.argv[3]).resolve();output=Path(sys.argv[4]).resolve();assert script.is_relative_to(selected) and not output.exists();events=[];active=True
sys.path.insert(0,str(script.parent));sys.argv=[str(script),'--root',str(selected)]
def hook(event,args):
 if not active or event!='open':return
 value=args[0]
 if isinstance(value,int):events.append({'kind':'FILE_DESCRIPTOR_OPEN','descriptor':value});return
 try:
  raw=os.fsdecode(value);path=Path(raw);path=path if path.is_absolute() else Path.cwd()/path;resolved=path.resolve();mode=args[1] if len(args)>1 else None;flags=args[2] if len(args)>2 else 0;write=(isinstance(mode,str) and any(x in mode for x in ('w','a','+','x'))) or (isinstance(flags,int) and bool(flags&(os.O_WRONLY|os.O_RDWR)))
  events.append({'path':str(resolved),'under_selected_root':resolved.is_relative_to(selected),'under_original_workspace':resolved.is_relative_to(original),'mode':mode,'flags':flags,'write_intent':write})
 except Exception as e:events.append({'kind':'UNCLASSIFIED_OPEN','exception_type':type(e).__name__})
sys.addaudithook(hook);exception=None;status='EXIT_ZERO'
try:runpy.run_path(str(script),run_name='__main__')
except BaseException as e:exception={'type':type(e).__name__,'text':str(e)};status='TARGET_EXCEPTION'
finally:
 active=False;out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script':str(script),'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'selected_root':str(selected),'original_workspace':str(original),'status':status,'exception':exception,'events':events,'opens_under_original_workspace':sum(x.get('under_original_workspace',False) for x in events),'observed_write_intents':sum(x.get('write_intent',False) for x in events),'outside_selected_root_paths':sorted({x['path'] for x in events if 'path' in x and not x['under_selected_root']}),'limitations':'Pythonopen events onlyafterhook; nativefileaccess andstartupbeforehook nottraced. Instrumentedownedreaderexecution is not a fullOS/securityproof.'}
 with output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
if exception:raise SystemExit(1)
