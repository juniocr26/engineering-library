'use strict';
const fs=require('node:fs');const crypto=require('node:crypto');const vm=require('node:vm');
const sha=raw=>crypto.createHash('sha256').update(raw).digest('hex');
async function main(){
 const raw=fs.readFileSync(0);if(raw.length>131072)throw Error('packet bound');const packet=JSON.parse(raw);
 const {protocol,sources}=packet;for(const [name,text]of Object.entries(sources))if(sha(Buffer.from(text))!==protocol.source_files[name])throw Error('source hash differs');
 const limitName=Object.keys(sources).find(n=>n.includes('sindresorhus--p-limit')&&n.endsWith('/index.js'));
 const queueName=Object.keys(sources).find(n=>n.includes('sindresorhus--yocto-queue')&&n.endsWith('/index.js'));
 if(!limitName||!queueName)throw Error('exact source pair required');
 const context=vm.createContext(Object.create(null),{codeGeneration:{strings:false,wasm:false}});
 const queue=new vm.SourceTextModule(sources[queueName],{context,identifier:queueName});
 const limiter=new vm.SourceTextModule(sources[limitName],{context,identifier:limitName});
 if(queue.dependencySpecifiers.length!==0||JSON.stringify(limiter.dependencySpecifiers)!=='["yocto-queue"]')throw Error('import graph differs');
 await queue.link(()=>{throw Error('queue import forbidden')});
 await limiter.link((specifier,referencing)=>{if(referencing!==limiter||specifier!=='yocto-queue')throw Error('link outside fixed graph');return queue});
 await limiter.evaluate({timeout:1000});
 context.pLimit=limiter.namespace.default;context.Queue=queue.namespace.default;context.ownedCases=protocol.cases;
 const owned=`(async()=>{
 const rows=[];const gate=()=>{let release;const promise=new Promise(resolve=>{release=resolve});return {promise,release}};
 const drain=async()=>{for(let i=0;i<12;i++)await Promise.resolve()};
 for(const c of ownedCases){
  const checks={};const trace={};
  if(c.kind==='invalid-concurrency'){
   const value=c.input==='OWNED_NAN_SENTINEL'?NaN:c.input;
   try{pLimit(value);checks.typeerror=false}catch(e){checks.typeerror=e instanceof TypeError;trace.error=e.message}
  }else if(c.kind==='infinity'){
   const limit=pLimit(Infinity);checks.callable=typeof limit==='function';checks.value=await limit(()=>7)===7;await drain();checks.empty=limit.activeCount===0&&limit.pendingCount===0;
  }else if(c.kind==='deferred-start'){
   const limit=pLimit(1),a=gate(),starts=[];
   const pa=limit(async()=>{starts.push('A');await a.promise;return 'A-value'});
   const pb=limit(()=>{starts.push('B');return 'B-value'});
   trace.immediate=[limit.activeCount,limit.pendingCount,starts.slice()];checks.immediate=limit.activeCount===0&&limit.pendingCount===2&&starts.length===0;
   await Promise.resolve();trace.firstMicrotask=[limit.activeCount,limit.pendingCount,starts.slice()];checks.first=limit.activeCount===1&&limit.pendingCount===1&&starts.join(',')==='A';
   a.release();const values=await Promise.all([pa,pb]);await drain();checks.fifo=starts.join(',')==='A,B';checks.values=values.join(',')==='A-value,B-value';checks.final=limit.activeCount===0&&limit.pendingCount===0;
  }else if(c.kind==='width-two'){
   const limit=pLimit(2),gates=[gate(),gate(),gate()],starts=[];let running=0,maximum=0;
   const promises=gates.map((g,index)=>limit(async()=>{starts.push(index);running++;maximum=Math.max(maximum,running);await g.promise;running--;return index}));
   await Promise.resolve();trace.initial=[limit.activeCount,limit.pendingCount,starts.slice()];checks.initial=limit.activeCount===2&&limit.pendingCount===1&&starts.join(',')==='0,1';
   gates[0].release();await promises[0];await Promise.resolve();checks.thirdStarted=starts.join(',')==='0,1,2';checks.width=maximum===2;
   gates[1].release();gates[2].release();checks.values=(await Promise.all(promises)).join(',')==='0,1,2';await drain();checks.final=limit.activeCount===0&&limit.pendingCount===0;
  }else if(c.kind==='throw-preserves-identity'){
   const limit=pLimit(1),marker={owned:'failure'};let nextRan=false;
   const pa=limit(()=>{throw marker}),pb=limit(()=>{nextRan=true;return 9});const results=await Promise.allSettled([pa,pb]);await drain();
   checks.originalIdentity=results[0].status==='rejected'&&results[0].reason===marker;checks.queueContinues=nextRan&&results[1].status==='fulfilled'&&results[1].value===9;checks.final=limit.activeCount===0&&limit.pendingCount===0;
  }else if(c.kind==='clear-before-start'){
   const limit=pLimit(1);let called=0,settled=0;
   const pa=limit(()=>{called++;return 1}),pb=limit(()=>{called++;return 2});pa.then(()=>settled++,()=>settled++);pb.then(()=>settled++,()=>settled++);
   limit.clearQueue();checks.immediate=limit.activeCount===0&&limit.pendingCount===0;await drain();checks.notCalled=called===0;checks.unsettledAfter12=settled===0;
   checks.laterNewTask=await limit(()=>3)===3;trace.discardedPromisesSettledAfter12=settled;
  }else if(c.kind==='clear-while-active'){
   const limit=pLimit(1),a=gate();let pendingCalled=false,pendingSettled=false;
   const pa=limit(async()=>{await a.promise;return 'active-completed'}),pb=limit(()=>{pendingCalled=true;return 'discarded'});pb.then(()=>pendingSettled=true,()=>pendingSettled=true);
   await Promise.resolve();checks.beforeClear=limit.activeCount===1&&limit.pendingCount===1;limit.clearQueue();checks.afterClear=limit.activeCount===1&&limit.pendingCount===0;
   a.release();checks.activeCompletes=await pa==='active-completed';await drain();checks.pendingNotCalled=!pendingCalled;checks.pendingUnsettledAfter12=!pendingSettled;checks.final=limit.activeCount===0&&limit.pendingCount===0;
  }else if(c.kind==='arguments-forwarded'){
   const limit=pLimit(1),sentinel={owned:'identity'};let seen;const value=await limit((a,b)=>{seen=[a,b];return 11},sentinel,7);checks.argsIdentity=seen[0]===sentinel&&seen[1]===7;checks.returnedValue=value===11;
  }else if(c.kind==='invalid-task'){
   const limit=pLimit(1);let promise;try{promise=limit(42);checks.noSynchronousThrow=true}catch(e){checks.noSynchronousThrow=false}
   try{await promise;checks.rejectsTypeError=false}catch(e){checks.rejectsTypeError=e instanceof TypeError}await drain();checks.final=limit.activeCount===0&&limit.pendingCount===0;
  }else if(c.kind==='queue-fifo-iteration'){
   const q=new Queue();q.enqueue('A');q.enqueue('B');q.enqueue(undefined);const snapshot=[...q];checks.iterator=snapshot.length===3&&snapshot[0]==='A'&&snapshot[1]==='B'&&snapshot[2]===undefined;checks.nonDestructive=q.size===3;
   checks.fifo=q.dequeue()==='A'&&q.dequeue()==='B'&&q.size===1;checks.undefinedValue=q.dequeue()===undefined&&q.size===0;checks.emptyUndefined=q.dequeue()===undefined&&q.size===0;
  }else if(c.kind==='queue-clear'){
   const q=new Queue();q.enqueue(1);q.enqueue(2);q.clear();checks.empty=q.size===0&&q.dequeue()===undefined&&[...q].length===0;q.enqueue(3);checks.reusable=q.size===1&&q.dequeue()===3&&q.size===0;
  }else throw Error('unregistered case');
  rows.push({id:c.id,checks,trace,allPass:Object.values(checks).every(v=>v===true)});
 }
 return {rows,allPass:rows.every(r=>r.allPass),noTimersUsed:true,noApplicationIo:true};
})()`;
 const result=await new vm.Script(owned,{filename:'owned-frozen-queue-observations.js'}).runInContext(context,{timeout:1000});
 process.stdout.write(JSON.stringify({node:process.version,platform:process.platform,arch:process.arch,protocolSha256:sha(Buffer.from(JSON.stringify(protocol))),...result,exactSourceModulesEvaluated:2,sourceRewritten:false,installedPackagesImported:false,applicationHttpRequests:0,modelCalls:0,optimizerSteps:0}));
}
main().catch(e=>{process.stderr.write(String(e.stack)+'\n');process.exitCode=1});
