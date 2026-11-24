const ts = require('/app/frontend/node_modules/typescript');
const crypto = require('crypto');
const output = [];
for (const input of payload.files) {
  const fileName = '/' + input.name.replace(/^\/+/, '');
  const sf = ts.createSourceFile(fileName, input.source, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
  const host = {
    getSourceFile: name => name === fileName ? sf : undefined,
    getDefaultLibFileName: () => '/unavailable.d.ts',
    writeFile: () => { throw Error('emission forbidden'); },
    getCurrentDirectory: () => '/', getDirectories: () => [],
    fileExists: name => name === fileName, readFile: name => name === fileName ? input.source : undefined,
    getCanonicalFileName: name => name, useCaseSensitiveFileNames: () => true,
    getNewLine: () => '\n'
  };
  const program = ts.createProgram([fileName], {allowJs:true,noLib:true,noResolve:true,noEmit:true,target:ts.ScriptTarget.Latest}, host);
  const checker = program.getTypeChecker();
  const loc = node => ({line:sf.getLineAndCharacterOfPosition(node.getStart(sf)).line+1,end_line:sf.getLineAndCharacterOfPosition(node.end).line+1});
  function ownerOf(node) {
    let parent = node.parent;
    while (parent && !ts.isFunctionLike(parent)) parent = parent.parent;
    if (!parent) return {kind:'SourceFile',name:'<module>',line:1,end_line:sf.getLineAndCharacterOfPosition(sf.end).line+1};
    return {kind:ts.SyntaxKind[parent.kind],name:parent.name ? parent.name.getText(sf) : '<anonymous>',...loc(parent)};
  }
  const calls = [];
  function visit(node) {
    if (ts.isCallExpression(node)) {
      const expression = node.expression;
      let reference = null, form = 'OTHER_PROPERTY_OR_EXPRESSION';
      if (ts.isIdentifier(expression)) {reference=expression;form='DIRECT_IDENTIFIER';}
      else if (ts.isPropertyAccessExpression(expression) && ['call','apply'].includes(expression.name.text) && ts.isIdentifier(expression.expression)) {reference=expression.expression;form='IDENTIFIER_'+expression.name.text.toUpperCase()+'_PROPERTY';}
      const symbol = reference ? checker.getSymbolAtLocation(reference) : null;
      const declarations = symbol?.declarations || [];
      const local = declarations.filter(d=>ts.isFunctionDeclaration(d) && d.getSourceFile()===sf);
      const binding = local.length === 1 ? {name:local[0].name?.text,...loc(local[0])} : null;
      calls.push({...loc(node),expression:expression.getText(sf),form,owner:ownerOf(node),local_function_declaration:binding,status:binding ? 'LEXICAL_LOCAL_FUNCTION_REFERENCE' : 'UNRESOLVED_UNDER_NARROW_POLICY',symbol_declaration_kinds:declarations.map(d=>ts.SyntaxKind[d.kind]),runtime_target_proven:false});
    }
    ts.forEachChild(node,visit);
  }
  visit(sf);
  output.push({name:input.name,sha256:crypto.createHash('sha256').update(input.source).digest('hex'),parse_diagnostics:program.getSyntacticDiagnostics(sf).map(d=>({code:d.code,line:d.start===undefined?null:sf.getLineAndCharacterOfPosition(d.start).line+1,message:ts.flattenDiagnosticMessageText(d.messageText,' ')})),calls});
}
process.stdout.write(JSON.stringify({typescript_version:ts.version,source_execution:false,typecheck_performed:false,external_resolution:false,runtime_call_graph:false,files:output},null,2)+'\n');
