'use strict';
// Copied pure Boolean expressions only; never imports/evaluates the Fastify module.
const ts = require('/app/frontend/node_modules/typescript');
const vm = require('node:vm');
const crypto = require('node:crypto');
let input = '';
process.stdin.on('data', b => input += b);
process.stdin.on('end', () => {
  const request = JSON.parse(input);
  const knownNames = new Set(['path','prefix','opts','length','method','isGeneratedHeadRoute']);
  const knownProperties = new Set(['prefix.length','opts.method','opts.isGeneratedHeadRoute']);
  const knownOperators = new Set([ts.SyntaxKind.AmpersandAmpersandToken,
    ts.SyntaxKind.EqualsEqualsEqualsToken, ts.SyntaxKind.ExclamationEqualsEqualsToken,
    ts.SyntaxKind.GreaterThanToken]);
  const knownKinds = new Set([ts.SyntaxKind.ParenthesizedExpression, ts.SyntaxKind.BinaryExpression,
    ts.SyntaxKind.Identifier, ts.SyntaxKind.PropertyAccessExpression, ts.SyntaxKind.StringLiteral,
    ts.SyntaxKind.NumericLiteral, ts.SyntaxKind.PrefixUnaryExpression, ...knownOperators]);
  function requireCondition(value, message) { if (!value) throw Error(message); }
  const prepared = request.sources.map(source => {
    requireCondition(crypto.createHash('sha256').update(source.source).digest('hex') === source.sha256, 'source bytes');
    const sf = ts.createSourceFile('route.js', source.source, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
    requireCondition(sf.parseDiagnostics.length === 0, 'module syntax');
    const found = [];
    function visit(node, owners) {
      const next = ts.isFunctionDeclaration(node) ? [...owners, node.name?.text || '<anonymous>'] : owners;
      if (ts.isIfStatement(node) && node.expression.getText(sf).startsWith("path === '/' && prefix.length > 0")) {
        found.push({owners:next, expression:node.expression.getText(sf), line:sf.getLineAndCharacterOfPosition(node.getStart(sf)).line + 1});
      }
      ts.forEachChild(node, child => visit(child, next));
    }
    visit(sf, []);
    requireCondition(found.length === 1 && found[0].owners.join('.') === 'buildRouting.route', 'unique lexical owner');
    const expression = found[0].expression;
    requireCondition(expression === source.registered_expression, 'registered exact expression');
    const exprFile = ts.createSourceFile('owned-guard.js', 'const guard = (' + expression + ');', ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
    requireCondition(exprFile.parseDiagnostics.length === 0, 'expression syntax');
    const root = exprFile.statements[0].declarationList.declarations[0].initializer;
    function inspect(node) {
      requireCondition(knownKinds.has(node.kind), 'unreviewed expression node');
      if (ts.isIdentifier(node)) requireCondition(knownNames.has(node.text), 'unreviewed identifier');
      if (ts.isPropertyAccessExpression(node)) requireCondition(knownProperties.has(node.getText(exprFile)), 'unreviewed property');
      if (ts.isBinaryExpression(node)) requireCondition(knownOperators.has(node.operatorToken.kind), 'unreviewed operator');
      if (ts.isPrefixUnaryExpression(node)) requireCondition(node.operator === ts.SyntaxKind.ExclamationToken, 'unreviewed unary operator');
      if (ts.isStringLiteral(node)) requireCondition(['/', 'HEAD'].includes(node.text), 'unreviewed string');
      if (ts.isNumericLiteral(node)) requireCondition(node.text === '0', 'unreviewed number');
      ts.forEachChild(node, inspect);
    }
    inspect(root);
    return {...source, ...found[0], safety_ast_admitted:true};
  });
  requireCondition(prepared.length === 2 && request.cases.length === 8, 'bounded invocation count');
  for (const row of request.cases) {
    requireCondition(typeof row.path === 'string' && typeof row.prefix === 'string', 'owned strings only');
    requireCondition(typeof row.opts.isGeneratedHeadRoute === 'boolean', 'owned Boolean marker');
    requireCondition(typeof row.opts.method === 'string' || (Array.isArray(row.opts.method) && row.opts.method.every(x => typeof x === 'string')), 'owned method strings/arrays');
  }
  const results = prepared.map(source => {
    const script = new vm.Script('(' + source.expression + ')', {filename:'owned-public-fastify-guard.js'});
    const observations = request.cases.map(row => {
      const actual = script.runInNewContext({path:row.path, prefix:row.prefix, opts:row.opts}, {timeout:50});
      const expected = row[source.phase];
      return {id:row.id, expected, actual, matched:typeof actual === 'boolean' && actual === expected};
    });
    return {phase:source.phase, revision:source.revision, expression:source.expression,
      source_sha256:source.sha256, owner:source.owners, line:source.line, safety_ast_admitted:true, observations};
  });
  process.stdout.write(JSON.stringify({node:process.version, typescript:ts.version, results,
    all_expected_matched:results.every(r => r.observations.every(o => o.matched)), guard_evaluations:16,
    copied_public_guard_expressions_executed:true, original_fastify_module_executed:false,
    Fastify_constructed:false, upstream_tests_executed:false, private_inputs:false,
    scope:'Owned strings/arrays/Booleans in two reviewed pure expressions; no route registration/reachability/application guarantee.'}));
});
