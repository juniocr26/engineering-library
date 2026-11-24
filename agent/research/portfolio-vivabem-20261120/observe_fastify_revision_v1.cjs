'use strict';
// Research-only syntax observation. Public input source is parsed, never evaluated.
const ts = require('typescript');
let input = '';
process.stdin.on('data', b => input += b);
process.stdin.on('end', () => {
  const rows = JSON.parse(input).map(item => {
    const sf = ts.createSourceFile(item.path, item.source, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
    if (sf.parseDiagnostics.length) throw Error('source syntax diagnostics');
    const found = [];
    function visit(node, owners) {
      let next = owners;
      if (ts.isFunctionDeclaration(node)) next = [...owners, node.name?.text || '<anonymous>'];
      if (ts.isIfStatement(node) && node.expression.getText(sf).startsWith("path === '/' && prefix.length > 0")) {
        found.push({owners: next, start_line: sf.getLineAndCharacterOfPosition(node.getStart(sf)).line + 1,
          end_line: sf.getLineAndCharacterOfPosition(node.end).line + 1,
          condition: node.expression.getText(sf), branch: node.thenStatement.getText(sf),
          else_branch: node.elseStatement?.getText(sf)});
      }
      ts.forEachChild(node, child => visit(child, next));
    }
    visit(sf, []);
    if (found.length !== 1 || found[0].owners.join('.') !== 'buildRouting.route') throw Error('unique lexical owner required');
    return {revision:item.revision, observations:found, source_executed:false, syntax_only:true};
  });
  process.stdout.write(JSON.stringify({node:process.version, typescript:ts.version, rows}));
});
