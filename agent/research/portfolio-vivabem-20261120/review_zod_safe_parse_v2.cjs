'use strict';
// Independent structural review: no profile template/observer imports, no source evaluation.
const ts = require('typescript');
let input = '';
process.stdin.on('data', b => input += b);
process.stdin.on('end', () => {
  const request = JSON.parse(input);
  const sf = ts.createSourceFile('parse.ts', request.source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
  if (sf.parseDiagnostics.length) throw Error('syntax errors');
  const text = node => node.getText(sf);
  const expectedImports = [['core','./core.js',false],['errors','./errors.js',false],['schemas','./schemas.js',true],['util','./util.js',false]];
  const actualImports = sf.statements.filter(ts.isImportDeclaration).map(n => {
    if (!n.importClause || !ts.isNamespaceImport(n.importClause.namedBindings)) throw Error('namespace import shape');
    return [n.importClause.namedBindings.name.text, n.moduleSpecifier.text, n.importClause.isTypeOnly];
  });
  if (JSON.stringify(actualImports) !== JSON.stringify(expectedImports)) throw Error('import targets');

  function requireCondition(value, reason) { if (!value) throw Error(reason); }
  function variable(name) {
    const list = sf.statements.filter(ts.isVariableStatement).flatMap(n => [...n.declarationList.declarations])
      .filter(n => ts.isIdentifier(n.name) && n.name.text === name);
    requireCondition(list.length === 1, 'unique ' + name);
    return list[0];
  }
  function arrow(name) {
    const outer = variable(name).initializer;
    requireCondition(ts.isArrowFunction(outer) && ts.isArrowFunction(outer.body), 'nested arrows');
    requireCondition(ts.isBlock(outer.body.body), 'block body');
    return outer.body;
  }
  function literalReturn(node) {
    const value = node.expression;
    requireCondition(ts.isObjectLiteralExpression(value), 'literal return');
    return value;
  }
  const safeTypes = sf.statements.filter(n => ts.isTypeAliasDeclaration(n) && n.name.text === '$SafeParse');
  requireCondition(safeTypes.length === 1 && ts.isFunctionTypeNode(safeTypes[0].type), 'safe parse declared type');
  const parameters = safeTypes[0].type.parameters;
  requireCondition(parameters.length === 3 && parameters.map(n => text(n.name)).join(',') === 'schema,value,_ctx' && !parameters[0].questionToken && !parameters[1].questionToken && !!parameters[2].questionToken, 'required and optional arguments');
  const sync = arrow('_safeParse');
  const ss = sync.body.statements;
  requireCondition(ss.length === 4, 'sync statement count');
  const promiseIf = ss[2];
  requireCondition(ts.isIfStatement(promiseIf) && text(promiseIf.expression) === 'result instanceof Promise', 'Promise condition');
  requireCondition(!promiseIf.elseStatement && ts.isBlock(promiseIf.thenStatement), 'guard shape');
  const throwNode = promiseIf.thenStatement.statements[0];
  requireCondition(promiseIf.thenStatement.statements.length === 1 && ts.isThrowStatement(throwNode), 'throw');
  requireCondition(text(throwNode.expression) === 'new core.$ZodAsyncError()', 'throw class identifier');
  requireCondition(ts.isVariableStatement(ss[0]) && text(ss[0].declarationList.declarations[0].initializer) === '_ctx ? { ..._ctx, async: false } : { async: false }' && text(ss[1]).includes('schema._zod.run({ value, issues: [] }, ctx)'), 'sync setup');
  requireCondition(ts.isReturnStatement(ss[3]) && ts.isConditionalExpression(ss[3].expression), 'sync conditional return');
  const choice = ss[3].expression;
  requireCondition(text(choice.condition) === 'result.issues.length' && text(choice.whenTrue) === 'failure(_Err, result.issues, ctx)', 'failure choice');
  requireCondition(text(choice.whenFalse) === '({ success: true, data: result.value } as any)', 'success choice');
  const failures = sf.statements.filter(n => ts.isFunctionDeclaration(n) && n.name?.text === 'failure');
  requireCondition(failures.length === 1 && failures[0].body.statements.length === 2, 'failure owner');
  const fbody = failures[0].body.statements;
  requireCondition(ts.isVariableStatement(fbody[0]) && fbody[0].declarationList.declarations.length === 1, 'local error declaration');
  const localError = fbody[0].declarationList.declarations[0];
  requireCondition(text(localError.name) === 'error' && localError.initializer === undefined, 'uninitialized error');
  const obj = literalReturn(fbody[1]);
  const getter = obj.properties.filter(n => ts.isGetAccessorDeclaration(n) && text(n.name) === 'error');
  const setter = obj.properties.filter(n => ts.isSetAccessorDeclaration(n) && text(n.name) === 'error');
  requireCondition(getter.length === 1 && setter.length === 1 && obj.properties.length === 3, 'accessor pair');
  requireCondition(text(obj.properties[0]) === 'success: false', 'failure flag');
  const g = getter[0].body.statements;
  requireCondition(g.length === 2 && ts.isIfStatement(g[0]) && text(g[0].expression) === '!error', 'lazy guard');
  const branch = g[0].thenStatement.statements;
  requireCondition(branch.length === 3 && !g[0].elseStatement, 'lazy branch length');
  requireCondition(text(branch[0]) === 'error = new Err(issues.map((iss) => util.finalizeIssue(iss, ctx, core.config())));', 'lazy construction');
  requireCondition(text(branch[1]) === 'issues = undefined as any;' && text(branch[2]) === 'ctx = undefined as any;', 'getter release order');
  requireCondition(ts.isReturnStatement(g[1]) && text(g[1].expression) === 'error', 'getter return');
  const set = setter[0].body.statements;
  requireCondition(set.length === 3 && text(set[0]) === 'error = e;' && text(set[1]) === 'issues = undefined as any;' && text(set[2]) === 'ctx = undefined as any;', 'setter assignments');
  const asyncArrow = arrow('_safeParseAsync');
  requireCondition(asyncArrow.modifiers?.some(n => n.kind === ts.SyntaxKind.AsyncKeyword), 'async arrow modifier');
  const ass = asyncArrow.body.statements;
  requireCondition(ass.length === 4 && ts.isVariableStatement(ass[0]) && text(ass[0].declarationList.declarations[0].initializer) === '_ctx ? { ..._ctx, async: true } : { async: true }' && text(ass[1]).includes('schema._zod.run({ value, issues: [] }, ctx)'), 'async setup');
  requireCondition(ts.isIfStatement(ass[2]) && text(ass[2].expression) === 'result instanceof Promise' && text(ass[2].thenStatement) === 'result = await result;', 'async await guard');
  requireCondition(text(ass[3].expression) === text(choice), 'shared return shape');
  requireCondition(text(variable('safeParse').initializer) === '_safeParse(errors.$ZodRealError)' && text(variable('safeParseAsync').initializer) === '_safeParseAsync(errors.$ZodRealError)', 'core factory bindings');
  process.stdout.write(JSON.stringify({verified_selected_groups:['ZF01','ZF02','ZF03','ZF04','ZF05','ZF06'],
    scope:'Separate AST queries over freshly acquired source, selected written structures only; not a general type/runtime proof.',
    source_executed:false, node:process.version, typescript:ts.version}));
});
