// Owned syntax identity observer; selected source is never evaluated/imported.
const fs = require('fs'), crypto = require('crypto'), ts = require('typescript');
const raw = fs.readFileSync(0), source = raw.toString('utf8');
const sf = ts.createSourceFile('capsule.ts',source,ts.ScriptTarget.Latest,true,ts.ScriptKind.TS);
if(sf.parseDiagnostics.length) throw Error('unparseable source');
const selected = new Map();
for(const statement of sf.statements){
 if(ts.isVariableStatement(statement)) for(const d of statement.declarationList.declarations){
  if(d.name.getText(sf)==='_safeParse'){
   if(selected.has('_safeParse')) throw Error('duplicate selected owner');
   selected.set('_safeParse',d);
  }
 }
 if(ts.isFunctionDeclaration(statement)&&statement.name?.text==='failure'){
  if(selected.has('failure')) throw Error('duplicate selected owner');
  selected.set('failure',statement);
 }
}
if(selected.size!==2)throw Error('missing selected owner');
// Token kind/text identity ignores comments and whitespace, retains body tokens.
const owners={};
for(const [name,node] of selected){
 const slice=source.slice(node.getStart(sf),node.end);
 const scanner=ts.createScanner(ts.ScriptTarget.Latest,true,ts.LanguageVariant.Standard,slice);
 const tokens=[];
 for(let kind=scanner.scan();kind!==ts.SyntaxKind.EndOfFileToken;kind=scanner.scan())tokens.push([kind,scanner.getTokenText()]);
 const normalized=JSON.stringify(tokens);
 owners[name]={normalized_owner_sha256:crypto.createHash('sha256').update(normalized).digest('hex'),
  normalized_owner_tokens:tokens, first_line:sf.getLineAndCharacterOfPosition(node.getStart(sf)).line+1,
  last_line:sf.getLineAndCharacterOfPosition(node.end).line+1};
}
console.log(JSON.stringify({source_sha256:crypto.createHash('sha256').update(raw).digest('hex'),
 selected_owners:owners,typescript_version:ts.version,comments_in_identity:false,upstream_executed:false,
 typechecked:false,module_resolution:false,semantic_admission:false},null,2));
