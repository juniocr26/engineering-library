"""Run an existing text parser in the existing host JSC; never evaluate target modules."""
from pathlib import Path
import argparse
import ctypes as C
import datetime
import hashlib
import json
import re

parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
parser.add_argument('--stdout-only', action='store_true')
args = parser.parse_args()
P = args.root/'agent/research/final-intensive-20261121'
sha = lambda b: hashlib.sha256(b).hexdigest()
protocol = json.loads((P/'frontend-dimensions-jsc-protocol-v1.json').read_text())
library = args.root/protocol['parser']
assert sha(library.read_bytes()) == protocol['parser_sha256']
cases = []
for item in protocol['cases']:
    raw=(args.root/item['snapshot']).read_bytes();assert sha(raw)==item['sha256']
    cases.append({'id':item['id'],'source':raw.decode(),'source_sha256':sha(raw),'script_kind':item['script_kind'],'expected_zero_diagnostics':item['expected_zero_diagnostics']})
cases.append(protocol['negative_control'])
jsc = C.CDLL(protocol['runtime'])
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


try:
    evaluate(library.read_text())
    program = "JSON.stringify({typescript:ts.version,cases:CASES.map(c=>{\n const kind=ts.ScriptKind[c.script_kind];\n const sf=ts.createSourceFile(c.id,c.source,ts.ScriptTarget.Latest,true,kind);\n const diagnostics=sf.parseDiagnostics.map(d=>({code:d.code,message:ts.flattenDiagnosticMessageText(d.messageText,' ')}));\n const declarations=[];\n if(c.id.endsWith('resize-options.ts') && diagnostics.length===0){\n  for(const node of sf.statements){\n   if(ts.isTypeAliasDeclaration(node))declarations.push({name:node.name.text,kind:'TypeAliasDeclaration',start_line:sf.getLineAndCharacterOfPosition(node.getStart(sf)).line+1,end_line:sf.getLineAndCharacterOfPosition(node.end-1).line+1,type_text:node.type.getText(sf)});\n   if(ts.isFunctionDeclaration(node)&&node.name&&node.body){\n    const guards=node.body.statements.filter(ts.isIfStatement).map(n=>{\n      const branch=ts.isBlock(n.thenStatement)?n.thenStatement.statements:[n.thenStatement];\n      return {line:sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1,condition:n.expression.getText(sf),direct_branch_returns:branch.filter(ts.isReturnStatement).map(r=>r.expression?r.expression.getText(sf):null),has_else:!!n.elseStatement};\n    });\n    let calls=[],throws=0;function visit(n){if(ts.isCallExpression(n))calls.push(n.expression.getText(sf));if(ts.isThrowStatement(n))throws++;ts.forEachChild(n,visit)};visit(node.body);\n    const last=node.body.statements[node.body.statements.length-1];\n    declarations.push({name:node.name.text,kind:'FunctionDeclaration',start_line:sf.getLineAndCharacterOfPosition(node.getStart(sf)).line+1,end_line:sf.getLineAndCharacterOfPosition(node.end-1).line+1,parameters:node.parameters.map(n=>({name:n.name.getText(sf),type:n.type?n.type.getText(sf):null})),guards,called_expression_text: calls,explicit_throw_statements:throws,last_return:ts.isReturnStatement(last)?(last.expression?last.expression.getText(sf):null):'NOT_RETURN'});\n   }\n  }\n }\n return {...c,diagnostics,declarations,matched:(diagnostics.length===0)===c.expected_zero_diagnostics};\n})})".replace('CASES', json.dumps(cases))
    observations = json.loads(string_value(evaluate(program)))
finally:
    jsc.JSGlobalContextRelease(context)
assert all(row['matched'] for row in observations['cases'])
result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'protocol_sha256': sha((P/'frontend-dimensions-jsc-protocol-v1.json').read_bytes()),
          'parser_sha256': protocol['parser_sha256'], 'runtime': protocol['runtime'],
          'observations': observations, 'node_used': False, 'target_source_executed': False,
          'typechecked': False, 'module_resolution': False, 'new_installations': False,
          'scope': protocol['scope']}
if not args.stdout_only:
    with (P/'frontend-dimensions-jsc-results-v1.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
print(json.dumps(result))
