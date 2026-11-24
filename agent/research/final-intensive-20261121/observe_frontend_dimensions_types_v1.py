import argparse,ctypes as C,json,hashlib,datetime
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3]);ap.add_argument('--stdout-only',action='store_true');a=ap.parse_args();root=a.root.resolve();p=root/'agent/research/final-intensive-20261121';protocol_path=p/'frontend-dimensions-typecheck-protocol-v1.json';spec=json.loads(protocol_path.read_text());compiler=json.loads((p/'frontend-dimensions-jsc-protocol-v1.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();library=root/compiler['parser'];assert sha(library.read_bytes())==compiler['parser_sha256'];files={}
for edge in spec['standard_declarations']:
 raw=(root/edge['path']).read_bytes();assert sha(raw)==edge['sha256'];files[edge['name']]=raw.decode()
source=(root/spec['source_path']).read_bytes();assert sha(source)==spec['source_sha256'];cases=[{'name':'resize-options.ts','source':source.decode(),'expected_ok':True}, {'name':spec['negative_control']['name'],'source':spec['negative_control']['source'],'expected_ok':False}]
jsc = C.CDLL(compiler['runtime'])
V = C.c_void_p
definitions = {
    'JSGlobalContextCreate': ([V], V),
    'JSGlobalContextRelease': ([V], None),
    'JSStringCreateWithUTF8CString': ([C.c_char_p], V),
    'JSStringRelease': ([V], None),
    'JSEvaluateScript': ([V, V, V, V, C.c_int, C.POINTER(V)], V),
    'JSValueToStringCopy': ([V, V, C.POINTER(V)], V),
    'JSStringGetMaximumUTF8CStringSize': ([V], C.c_size_t),
    'JSStringGetUTF8CString': ([V, C.c_void_p, C.c_size_t], C.c_size_t),
}
for name, (arguments, returns) in definitions.items():
    function = getattr(jsc, name)
    function.argtypes, function.restype = arguments, returns
context = jsc.JSGlobalContextCreate(None)
assert context


def string_value(value):
    exception = V()
    string = jsc.JSValueToStringCopy(context, value, C.byref(exception))
    if not string or exception.value:
        raise RuntimeError('JSC value-to-string failed')
    try:
        capacity = jsc.JSStringGetMaximumUTF8CStringSize(string)
        buffer = C.create_string_buffer(capacity)
        written = jsc.JSStringGetUTF8CString(string, buffer, capacity)
        assert 0 < written <= capacity
        return buffer.raw[:written-1].decode()
    finally:
        jsc.JSStringRelease(string)


def evaluate(source):
    assert '\0' not in source
    script = jsc.JSStringCreateWithUTF8CString(source.encode())
    exception = V()
    try:
        result = jsc.JSEvaluateScript(context, script, None, None, 1, C.byref(exception))
        if exception.value:
            raise RuntimeError(string_value(exception))
        assert result
        return result
    finally:
        jsc.JSStringRelease(script)


program=r'''JSON.stringify({typescript:ts.version,cases:EL_INPUT.cases.map(c=>{
 const registered={...EL_INPUT.files,[c.name]:c.source};const cache={},unregistered=[];
 const key=f=>f.startsWith('/virtual/')?f.slice('/virtual/'.length):f;
 const options={strict:true,noEmit:true,noLib:true,skipLibCheck:false,target:ts.ScriptTarget.ESNext,module:ts.ModuleKind.ESNext};
 const host={
  getSourceFile:(f,v)=>{const k=key(f);if(!(k in registered)){unregistered.push(f);return undefined}return cache[k]||(cache[k]=ts.createSourceFile('/virtual/'+k,registered[k],v,true,ts.ScriptKind.TS))},
  getDefaultLibFileName:()=>'/virtual/lib.es5.d.ts',getDefaultLibLocation:()=>'/virtual',
  writeFile:()=>{throw new Error('NO_EMIT_PROFILE')},getCurrentDirectory:()=>'/virtual',
  getDirectories:()=>[],directoryExists:d=>d==='/virtual'||d==='/',
  fileExists:f=>key(f) in registered,readFile:f=>registered[key(f)],
  getCanonicalFileName:f=>f,useCaseSensitiveFileNames:()=>true,getNewLine:()=> '\n',
  resolveModuleNames:names=>names.map(n=>{unregistered.push('module:'+n);return undefined})
 };
 const roots=Object.keys(registered).map(n=>'/virtual/'+n);const p=ts.createProgram(roots,options,host);
 const sf=p.getSourceFile('/virtual/'+c.name);
 const diagnostics=ts.getPreEmitDiagnostics(p).map(d=>({code:d.code,file:d.file?d.file.fileName:null,line:d.file&&d.start!==undefined?d.file.getLineAndCharacterOfPosition(d.start).line+1:null,message:ts.flattenDiagnosticMessageText(d.messageText,' ')}));
 const declarations=[];if(diagnostics.length===0){const checker=p.getTypeChecker();for(const n of sf.statements){
  if(ts.isFunctionDeclaration(n)&&n.name){const sig=checker.getSignatureFromDeclaration(n);declarations.push({name:n.name.text,kind:'FunctionDeclaration',type:checker.typeToString(checker.getTypeAtLocation(n.name),undefined,ts.TypeFormatFlags.NoTruncation),return_type:checker.typeToString(checker.getReturnTypeOfSignature(sig),undefined,ts.TypeFormatFlags.NoTruncation),parameters:n.parameters.map(v=>({name:v.name.getText(sf),type:checker.typeToString(checker.getTypeAtLocation(v.name),undefined,ts.TypeFormatFlags.NoTruncation)}))})}
 }}
 return {name:c.name,expected_ok:c.expected_ok,parse_diagnostics:sf?sf.parseDiagnostics.length:null,diagnostics,unregistered_requests:unregistered,declarations,matched:(diagnostics.length===0)===c.expected_ok&&!!sf&&sf.parseDiagnostics.length===0};
})})'''
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha(protocol_path.read_bytes()),'parser_sha256':compiler['parser_sha256'],'runtime':compiler['runtime'],'target_source_executed':False,'UI_or_project_build':False,'new_installations':False,'new_model_calls':0,'scope':spec['limits']}
try:
 evaluate(library.read_text());evaluate('var EL_INPUT = '+json.dumps({'files':files,'cases':cases})+';');observations=json.loads(string_value(evaluate(program)));result['observations']=observations;result['status']='TYPECHECKED_CLOSED_VIRTUAL_PROFILE' if all(r['matched'] for r in observations['cases']) else 'INCONCLUSIVE_TYPE_DIAGNOSTICS'
except Exception as error:result.update(status='INCONCLUSIVE_OBSERVER_FAILURE',error_type=type(error).__name__,error=str(error))
finally:jsc.JSGlobalContextRelease(context)
if not a.stdout_only:
 with (p/'frontend-dimensions-typecheck-results-v1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result));assert result['status']=='TYPECHECKED_CLOSED_VIRTUAL_PROFILE'
