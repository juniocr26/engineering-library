'use strict';
// Parse-only closed research profile. Never imports the input program.
const ts = require('typescript');
const crypto = require('node:crypto');
function tokens(text) {
  const scanner = ts.createScanner(ts.ScriptTarget.Latest, true, ts.LanguageVariant.Standard, text);
  const list = [];
  for (let kind = scanner.scan(); kind !== ts.SyntaxKind.EndOfFileToken; kind = scanner.scan()) {
    if (kind === ts.SyntaxKind.Unknown) throw Error('unknown token');
    list.push([kind, scanner.getTokenText()]);
  }
  return JSON.stringify(list);
}
function inspect(source, contract) {
  const contractDigest = crypto.createHash('sha256').update(JSON.stringify(contract)).digest('hex');
  if (contractDigest !== '04a155ff1f86bab03087f2133510c3d35d06b328fb7064198695273eb43176eb') throw Error('unregistered manual contract');
  const sf = ts.createSourceFile('parse.ts', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
  if (sf.parseDiagnostics.length) throw Error('syntax diagnostics');
  const imports = sf.statements.filter(ts.isImportDeclaration).map(n => n.getText(sf)).join('\n');
  if (tokens(imports) !== tokens(contract.imports)) throw Error('unsupported imports');
  const units = [];
  for (const [name, template] of Object.entries(contract.templates)) {
    const matches = [];
    for (const statement of sf.statements) {
      if (ts.isFunctionDeclaration(statement) && statement.name?.text === name) matches.push(statement);
      if (ts.isVariableStatement(statement)) {
        const declarations = statement.declarationList.declarations;
        if (declarations.some(d => ts.isIdentifier(d.name) && d.name.text === name)) {
          if (declarations.length !== 1) throw Error('multiple declaration statement');
          matches.push(statement);
        }
      }
    }
    if (matches.length !== 1) throw Error('non-unique top-level owner: ' + name);
    const node = matches[0];
    if (tokens(node.getText(sf)) !== tokens(template.text)) throw Error('unsupported selected shape: ' + name);
    if (name === 'failure') {
      if (!ts.isFunctionDeclaration(node)) throw Error('function owner required');
    } else {
      if (!ts.isVariableStatement(node)) throw Error('variable owner required');
      const init = node.declarationList.declarations[0].initializer;
      if (name.startsWith('_')) {
        if (!ts.isArrowFunction(init) || !ts.isArrowFunction(init.body)) throw Error('nested arrow owner required');
      } else if (!ts.isCallExpression(init)) throw Error('factory call required');
    }
    units.push({owner:name, start_line:sf.getLineAndCharacterOfPosition(node.getStart(sf)).line + 1,
      end_line:sf.getLineAndCharacterOfPosition(node.end).line + 1, quote:node.getText(sf),
      canonical_tokens_sha256:crypto.createHash('sha256').update(tokens(node.getText(sf))).digest('hex')});
  }
  return {source_sha256:crypto.createHash('sha256').update(source).digest('hex'), admitted:true,
    units, facts:contract.facts, source_executed:false,
    scope:'Closed token-exact selected declarations with AST owners; facts are registered manual interpretations.'};
}
let input = '';
process.stdin.on('data', b => input += b);
process.stdin.on('end', () => {
  const request = JSON.parse(input);
  const outcomes = request.cases.map(item => {
    try { return {id:item.id, expected_admitted:item.expected_admitted, observation:inspect(item.source, item.contract || request.contract)}; }
    catch (e) { return {id:item.id, expected_admitted:item.expected_admitted, observation:{admitted:false, reason:String(e.message), source_executed:false}}; }
  });
  process.stdout.write(JSON.stringify({node:process.version, typescript:ts.version, outcomes}));
});
