'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),ts=require('typescript');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');const packet=JSON.parse(fs.readFileSync(0,'utf8'));if(ts.version!=='5.9.3')throw Error('frozen compiler version differs');
const oracle=packet.oracle,allowed=new Map();for(const item of packet.files){const raw=fs.readFileSync(item.path);if(sha(raw)!==item.sha256)throw Error('pinned declaration/manifest drift');allowed.set(item.path,raw.toString('utf8'))}
const limitType=packet.files.find(e=>e.path.includes('sindresorhus--p-limit')&&e.path.endsWith('/index.d.ts')).path;
const queueType=packet.files.find(e=>e.path.includes('sindresorhus--yocto-queue')&&e.path.endsWith('/index.d.ts')).path;
const options={strict:true,noEmit:true,target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext,moduleResolution:ts.ModuleResolutionKind.Bundler,types:[],lib:['lib.es2022.d.ts'],paths:{'p-limit':[limitType],'yocto-queue':[queueType]}};
const libDirectory=path.dirname(ts.getDefaultLibFilePath(options));const knownLibraries=new Map(),deniedReads=new Set(),rows=[];
for(const c of oracle.cases){
 const virtual='/tmp/el-owned-queue-type-consumers-v1/'+c.id+'.mts';const host=ts.createCompilerHost(options);const originalRead=host.readFile.bind(host),originalExists=host.fileExists.bind(host);
 host.readFile=name=>{if(name===virtual)return c.source;if(allowed.has(name))return allowed.get(name);if(path.dirname(name)===libDirectory&&/^lib\..*\.d\.ts$/.test(path.basename(name))){const text=originalRead(name);if(text!==undefined)knownLibraries.set(name,{sha256:sha(text),bytes:Buffer.byteLength(text)});return text}deniedReads.add(name);return undefined};
 host.fileExists=name=>name===virtual||allowed.has(name)||(path.dirname(name)===libDirectory&&/^lib\..*\.d\.ts$/.test(path.basename(name))&&originalExists(name));
 host.getSourceFile=(name,languageVersion,onError)=>{const text=host.readFile(name);return text===undefined?undefined:ts.createSourceFile(name,text,languageVersion,true)};
 const program=ts.createProgram([virtual],options,host);for(const file of program.getSourceFiles())if(file.fileName!==virtual&&!allowed.has(file.fileName)&&path.dirname(file.fileName)!==libDirectory)throw Error('unexpected program source');
 const diagnostics=ts.getPreEmitDiagnostics(program);const codes=[...new Set(diagnostics.map(d=>d.code))].sort((a,b)=>a-b);const expected=[...c.expected_diagnostic_codes].sort((a,b)=>a-b);
 rows.push({id:c.id,expected_diagnostic_codes:expected,observed_diagnostic_codes:codes,matches:JSON.stringify(codes)===JSON.stringify(expected),diagnostics:diagnostics.map(d=>({code:d.code,file:d.file?.fileName,message:ts.flattenDiagnosticMessageText(d.messageText,' ')})),consumer_source_sha256:sha(c.source),virtual_consumer_file_not_written:true});
}
process.stdout.write(JSON.stringify({typescript_version:ts.version,node:process.version,rows,correct:rows.filter(r=>r.matches).length,n:rows.length,pinned_declaration_paths:[limitType,queueType],standard_library_files:Object.fromEntries([...knownLibraries].sort()),denied_metadata_reads:[...deniedReads].sort(),source_execution:false,emit:false,packages_installed:false,scope:'Declaration-level checking against exact Git-source d.ts copies, not installed-package identity, whole JS application compilation or runtime safety.'}));
