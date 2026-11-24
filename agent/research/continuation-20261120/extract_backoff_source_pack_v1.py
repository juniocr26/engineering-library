"""Use existing verified Go parser; preserve full selected source declarations."""
import datetime,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT/'agent/tools'));import go_source_ast
fetch=json.loads((P/'backoff-source-fetch-v1.json').read_text());units={};sources={}
common={'backoff.go':['BackOff','StopBackOff.NextBackOff','ZeroBackOff.NextBackOff','ConstantBackOff.NextBackOff'],'context.go':['BackOffContext','WithContext','getContext','backOffContext.Context','backOffContext.NextBackOff'],'exponential.go':['ExponentialBackOff','Clock','NewExponentialBackOff','ExponentialBackOff.Reset','ExponentialBackOff.NextBackOff','ExponentialBackOff.GetElapsedTime','ExponentialBackOff.incrementCurrentInterval','getRandomValueFromInterval'],'retry.go':['Operation','Notify','Retry','RetryNotify','RetryNotifyWithTimer','PermanentError','PermanentError.Error','PermanentError.Unwrap','PermanentError.Is','Permanent'],'timer.go':['Timer','defaultTimer.Start','defaultTimer.Stop'],'tries.go':['WithMaxRetries','backOffTries.NextBackOff','backOffTries.Reset']}
current={'exponential.go':['ExponentialBackOffOpts','WithInitialInterval','WithRandomizationFactor','WithMultiplier','WithMaxInterval','WithMaxElapsedTime','WithRetryStopDuration','WithClockProvider'],'retry.go':['OperationWithData','Operation.withEmptyData','RetryWithData','RetryNotifyWithData','RetryNotifyWithTimerAndData','doRetryNotify']}
for entry in fetch['files']:
 file=P/entry['path'];raw=file.read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256'];name=file.name;tag=entry['tag'];sources[tag+':'+name]=entry
 if name not in common:continue
 selectors=common[name]+(current.get(name,[])if tag=='v4.3.0'else[])
 for start in range(0,len(selectors),4):
  result=go_source_ast.run(json.dumps({'source':raw.decode(),'path':name,'selectors':selectors[start:start+4]}).encode());assert result['source_executed']is False
  for unit in result['units']:
   quote='\n'.join(raw.decode().splitlines()[unit['start_line']-1:unit['end_line']]);assert quote==unit['quote'];units[tag+':'+unit['selector']]={'revision':entry['revision'],'source_path':name,'source_snapshot':entry['path'],'source_sha256':entry['sha256'],'first_line':unit['start_line'],'last_line':unit['end_line'],'quote':quote,'quote_sha256':hashlib.sha256(quote.encode()).hexdigest(),'unit':unit,'producer':result['producer'],'complete_callable_or_type':True,'physical_quote_verified':True,'runtime_guarantee_from_syntax':False}
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':'cenkalti/backoff','units':units,'sources':sources,'runtime_results':'backoff-confined-runtime-results-v1.json','runtime_results_sha256':hashlib.sha256((P/'backoff-confined-runtime-results-v1.json').read_bytes()).hexdigest(),'subject_source_executed_by_parser':False,'prior_confined_runtime_observations_exist':True,'training_excluded':True,'owner_approved':False,'model_calls':0}
with(P/'backoff-source-pack-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'units':len(units),'sources':len(sources)})
