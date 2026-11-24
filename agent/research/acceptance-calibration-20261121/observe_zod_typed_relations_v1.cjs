// Owned finite AST observer. TypeScript source is data, never evaluated/imported.
const fs = require('fs');
const crypto = require('crypto');
const ts = require('typescript');
const raw = fs.readFileSync(0);
const source = raw.toString('utf8');
const sf = ts.createSourceFile('pinned-parse.ts', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
if (sf.parseDiagnostics.length) throw Error('unparseable source');
const variables = new Map(), functions = new Map(), relations = [];
const one = (xs, message) => { if (xs.length !== 1) throw Error(message); return xs[0]; };
const text = n => n.getText(sf);
for (const statement of sf.statements) {
  if (ts.isVariableStatement(statement)) {
    for (const declaration of statement.declarationList.declarations) {
      const name = text(declaration.name);
      if (variables.has(name)) throw Error('duplicate variable owner');
      variables.set(name, declaration);
    }
  } else if (ts.isFunctionDeclaration(statement) && statement.name) {
    const name = text(statement.name);
    if (functions.has(name)) throw Error('duplicate function owner');
    functions.set(name, statement);
  }
}
function add(id, owner, value, node) {
  relations.push({id, owner, normalized_relation: value,
    first_line: sf.getLineAndCharacterOfPosition(node.getStart(sf)).line + 1,
    last_line: sf.getLineAndCharacterOfPosition(node.end).line + 1,
    exact_ast_source: text(node)});
}
function innerBody(owner) {
  const declaration = variables.get(owner);
  if (!declaration || !ts.isArrowFunction(declaration.initializer) ||
      !ts.isArrowFunction(declaration.initializer.body) ||
      !ts.isBlock(declaration.initializer.body.body)) throw Error('unadmitted curried-arrow owner');
  return declaration.initializer.body.body;
}
function localVariable(body, name) {
  return one(body.statements.filter(ts.isVariableStatement)
    .flatMap(s => [...s.declarationList.declarations])
    .filter(d => text(d.name) === name), 'missing/ambiguous local');
}
function unwrap(node) {
  while (ts.isParenthesizedExpression(node) || ts.isAsExpression(node)) node = node.expression;
  return node;
}
function property(object, name) {
  if (!ts.isObjectLiteralExpression(object)) throw Error('unadmitted literal');
  return one(object.properties.filter(p => p.name && text(p.name) === name), 'missing/ambiguous property');
}
const body = innerBody('_safeParse');
const context = localVariable(body, 'ctx').initializer;
if (!ts.isConditionalExpression(context)) throw Error('unadmitted context branches');
const yesAsync = property(context.whenTrue, 'async'), noAsync = property(context.whenFalse, 'async');
if (!ts.isPropertyAssignment(yesAsync) || !ts.isPropertyAssignment(noAsync) ||
    text(yesAsync.initializer) !== text(noAsync.initializer)) throw Error('unequal context flags');
add('Z01', '_safeParse', text(yesAsync.initializer), context);
const run = localVariable(body, 'result').initializer;
if (!ts.isCallExpression(run) || text(run.expression) !== 'schema._zod.run' || run.arguments.length !== 2) throw Error('unadmitted run call');
add('Z02', '_safeParse', [...run.arguments].map(text).join(', '), run);
const promiseIf = one(body.statements.filter(ts.isIfStatement).filter(s => text(s.expression) === 'result instanceof Promise'), 'missing/ambiguous promise branch');
if (!ts.isBlock(promiseIf.thenStatement) || promiseIf.thenStatement.statements.length !== 1 ||
    !ts.isThrowStatement(promiseIf.thenStatement.statements[0])) throw Error('unadmitted promise throw');
const thrown = promiseIf.thenStatement.statements[0];
if (!thrown.expression || !ts.isNewExpression(thrown.expression)) throw Error('not a constructed throw');
add('Z03', '_safeParse', 'throw ' + text(thrown.expression), thrown);
const returned = one(body.statements.filter(ts.isReturnStatement), 'missing/ambiguous sync return');
if (!returned.expression || !ts.isConditionalExpression(returned.expression)) throw Error('not conditional return');
const conditional = returned.expression;
add('Z04', '_safeParse', text(conditional.condition), conditional.condition);
const successObject = unwrap(conditional.whenFalse);
const success = property(successObject, 'success'), data = property(successObject, 'data');
if (!ts.isPropertyAssignment(success) || !ts.isPropertyAssignment(data)) throw Error('unadmitted success properties');
add('Z05', '_safeParse', text(success.initializer), success);
add('Z10', '_safeParse', text(data.initializer), data);
const failure = functions.get('failure');
if (!failure || !failure.body) throw Error('missing failure owner');
const failureReturn = one(failure.body.statements.filter(ts.isReturnStatement), 'missing failure return');
const failureObject = unwrap(failureReturn.expression);
if (!ts.isObjectLiteralExpression(failureObject)) throw Error('not failure object');
const getter = one(failureObject.properties.filter(p => ts.isGetAccessorDeclaration(p) && text(p.name) === 'error'), 'missing/ambiguous getter');
const setter = one(failureObject.properties.filter(p => ts.isSetAccessorDeclaration(p) && text(p.name) === 'error'), 'missing/ambiguous setter');
if (!getter.body || !ts.isIfStatement(getter.body.statements[0])) throw Error('unadmitted getter guard');
add('Z06', 'failure', text(getter.body.statements[0].expression), getter.body.statements[0].expression);
if (!setter.body || !ts.isExpressionStatement(setter.body.statements[0]) ||
    !ts.isBinaryExpression(setter.body.statements[0].expression) ||
    setter.body.statements[0].expression.operatorToken.kind !== ts.SyntaxKind.EqualsToken) throw Error('unadmitted setter assignment');
add('Z07', 'failure', text(setter.body.statements[0].expression), setter.body.statements[0].expression);
const asyncBody = innerBody('_safeParseAsync');
const asyncIf = one(asyncBody.statements.filter(ts.isIfStatement).filter(s => text(s.expression) === 'result instanceof Promise'), 'missing async branch');
if (!ts.isExpressionStatement(asyncIf.thenStatement) || !ts.isBinaryExpression(asyncIf.thenStatement.expression) ||
    asyncIf.thenStatement.expression.operatorToken.kind !== ts.SyntaxKind.EqualsToken ||
    !ts.isAwaitExpression(asyncIf.thenStatement.expression.right)) throw Error('unadmitted async assignment');
add('Z08', '_safeParseAsync', text(asyncIf.thenStatement.expression), asyncIf.thenStatement.expression);
const safeParse = variables.get('safeParse');
if (!safeParse || !ts.isCallExpression(safeParse.initializer) ||
    text(safeParse.initializer.expression) !== '_safeParse' || safeParse.initializer.arguments.length !== 1) throw Error('unadmitted factory binding');
add('Z09', 'safeParse', text(safeParse.initializer.arguments[0]), safeParse.initializer);
console.log(JSON.stringify({profile:'finite-zod-AST-role-v1', typescript_version:ts.version,
  source_sha256:crypto.createHash('sha256').update(raw).digest('hex'), relations,
  source_executed:false,typechecked:false,module_resolution:false,runtime_bindings_verified:false}, null, 2));
