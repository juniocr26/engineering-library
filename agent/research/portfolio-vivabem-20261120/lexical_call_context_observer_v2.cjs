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
  function lexicalScope(node) {
    for (let n=node;n;n=n.parent) {
      if (ts.isSourceFile(n) || ts.isFunctionLike(n) || ts.isCatchClause(n)) return n;
      if (ts.isBlock(n)) return ts.isFunctionLike(n.parent) ? n.parent : n;
      if (ts.isCaseBlock(n) || ts.isForStatement(n) || ts.isForInStatement(n) || ts.isForOfStatement(n)) return n;
    }
    return sf;
  }
  function hoistScope(node) {
    for (let n=node;n;n=n.parent) if(ts.isSourceFile(n)||ts.isFunctionLike(n)) return n;
    return sf;
  }
  const bindings=[], writes=[], dynamic=[];
  function scan(node) {
    if(ts.isFunctionDeclaration(node)&&node.name) bindings.push({node,name:node.name.text,scope:lexicalScope(node.parent)});
    if(ts.isVariableDeclaration(node)&&ts.isIdentifier(node.name)) {
      let scope;
      if(ts.isCatchClause(node.parent)) scope=node.parent;
      else scope=(node.parent.flags & ts.NodeFlags.BlockScoped) ? lexicalScope(node.parent.parent) : hoistScope(node.parent);
      bindings.push({node,name:node.name.text,scope});
    }
    if(ts.isParameter(node)&&ts.isIdentifier(node.name)) bindings.push({node,name:node.name.text,scope:hoistScope(node.parent)});
    if(ts.isBinaryExpression(node)&&node.operatorToken.kind>=ts.SyntaxKind.FirstAssignment&&node.operatorToken.kind<=ts.SyntaxKind.LastAssignment) writes.push(node.left);
    if((ts.isPrefixUnaryExpression(node)||ts.isPostfixUnaryExpression(node))&&[ts.SyntaxKind.PlusPlusToken,ts.SyntaxKind.MinusMinusToken].includes(node.operator)) writes.push(node.operand);
    if(ts.isWithStatement(node)||(ts.isCallExpression(node)&&ts.isIdentifier(node.expression)&&node.expression.text==='eval')) dynamic.push(loc(node));
    ts.forEachChild(node,scan);
  }
  scan(sf);
  const strict = sf.statements.some((n,i)=>i===0 && ts.isExpressionStatement(n)&&ts.isStringLiteral(n.expression)&&n.expression.text==='use strict');
  function hazardsFor(decl) {
    if(!decl) return [];
    const hazards=[];
    if(!strict) hazards.push({reason:'STRICT_SCOPE_NOT_ESTABLISHED'});
    if(dynamic.length) hazards.push({reason:'DYNAMIC_SCOPE_INDICATOR',locations:dynamic});
    const scope=lexicalScope(decl.parent);
    for(const b of bindings) if(b.node!==decl&&b.name===decl.name.text&&b.scope===scope) hazards.push({reason:'SAME_SCOPE_DECLARATION_COLLISION',kind:ts.SyntaxKind[b.node.kind],...loc(b.node)});
    const symbol=checker.getSymbolAtLocation(decl.name);
    for(const lhs of writes) {
      let base=lhs,property=false;
      if(ts.isPropertyAccessExpression(lhs)||ts.isElementAccessExpression(lhs)) {base=lhs.expression;property=true;}
      if(ts.isIdentifier(base)&&symbol&&checker.getSymbolAtLocation(base)===symbol) hazards.push({reason:property?'PROPERTY_WRITE_ON_BINDING':'DIRECT_BINDING_WRITE',...loc(lhs)});
    }
    return hazards;
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
      const hazards=hazardsFor(binding ? local[0] : null);
      calls.push({hazards,...loc(node),expression:expression.getText(sf),form,owner:ownerOf(node),local_function_declaration:binding,status:binding ? (hazards.length ? 'ABSTAIN_SOURCE_COLLISION_OR_WRITE' : 'LEXICAL_LOCAL_FUNCTION_REFERENCE') : 'UNRESOLVED_UNDER_NARROW_POLICY',symbol_declaration_kinds:declarations.map(d=>ts.SyntaxKind[d.kind]),runtime_target_proven:false});
    }
    ts.forEachChild(node,visit);
  }
  visit(sf);
  output.push({name:input.name,sha256:crypto.createHash('sha256').update(input.source).digest('hex'),parse_diagnostics:program.getSyntacticDiagnostics(sf).map(d=>({code:d.code,line:d.start===undefined?null:sf.getLineAndCharacterOfPosition(d.start).line+1,message:ts.flattenDiagnosticMessageText(d.messageText,' ')})),calls});
}
process.stdout.write(JSON.stringify({typescript_version:ts.version,source_execution:false,observer_version:2,typecheck_performed:false,external_resolution:false,runtime_call_graph:false,files:output},null,2)+'\n');
