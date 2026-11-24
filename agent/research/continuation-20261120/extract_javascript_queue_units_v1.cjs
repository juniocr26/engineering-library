'use strict';
const fs=require('node:fs'),crypto=require('node:crypto'),ts=require('typescript');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const packet=JSON.parse(fs.readFileSync(0,'utf8'));const units={},facts={};
function add(key,card,node){
 const lines=card.source.match(/[^\n]*\n|[^\n]+$/g)||[];let first=0,last=lines.length-1;
 if(node){const file=node.getSourceFile();first=file.getLineAndCharacterOfPosition(node.getStart(file)).line;last=file.getLineAndCharacterOfPosition(node.end-1).line}
 const quote=lines.slice(first,last+1).join('');if(Buffer.byteLength(quote)>6144||!quote)throw Error('quote bound');
 units[key]={path:card.path,repository:card.repository,revision:card.revision,source_sha256:card.sha256,first_line:first+1,last_line:last+1,quote,quote_sha256:sha(quote),source_executed_during_extraction:false};
}
for(const card of packet.cards){
 if(sha(card.source)!==card.sha256||Buffer.byteLength(card.source)>32768)throw Error('sourcecard identity/bound');
 const family=card.repository.endsWith('/p-limit')?'limit':'queue';
 if(card.path==='package.json'){add(family+':manifest',card);facts[family+':manifest']=JSON.parse(card.source);continue}
 if(card.path==='license'){add(family+':license',card);continue}
 const file=ts.createSourceFile(card.path,card.source,ts.ScriptTarget.Latest,true,card.path.endsWith('.ts')?ts.ScriptKind.TS:ts.ScriptKind.JS);
 if(file.parseDiagnostics.length)throw Error('parse diagnostics');
 if(card.path==='index.d.ts'){
  for(const node of file.statements){
   if(ts.isInterfaceDeclaration(node)||ts.isClassDeclaration(node)||ts.isFunctionDeclaration(node)){
    const name=node.name.text;add(family+':types:'+name,card,node);
    if(node.members)for(const member of node.members){
     const key=member.name?member.name.getText(file):ts.isCallSignatureDeclaration(member)?'call':ts.isConstructSignatureDeclaration(member)?'constructor':'unnamed';
     add(family+':types:'+name+'.'+key,card,member);
    }
   }
  }
  continue;
 }
 if(family==='limit'){
  const imports=file.statements.filter(ts.isImportDeclaration);if(imports.length!==1||imports[0].moduleSpecifier.text!=='yocto-queue'||imports[0].importClause.name.text!=='Queue')throw Error('fixed import differs');add('limit:queue-import',card,imports[0]);
  const factory=file.statements.find(ts.isFunctionDeclaration);if(factory.name.text!=='pLimit'||factory.parameters.length!==1||factory.parameters[0].name.text!=='concurrency')throw Error('factory differs');
  add('limit:factory',card,factory);
  for(const statement of factory.body.statements){
   if(ts.isVariableStatement(statement))for(const declaration of statement.declarationList.declarations)add('limit:'+declaration.name.getText(file),card,statement);
   if(ts.isIfStatement(statement))add('limit:validation',card,statement);
   if(ts.isExpressionStatement(statement)&&ts.isCallExpression(statement.expression)&&statement.expression.expression.getText(file)==='Object.defineProperties')add('limit:defined-properties',card,statement);
   if(ts.isReturnStatement(statement))add('limit:return',card,statement);
  }
  facts.limiter={factory:'pLimit',parameter:'concurrency',imported_default_binding:'Queue',imported_specifier:'yocto-queue',export_mode:'default function declaration',source_only:true};
 }else{
  const classes=file.statements.filter(ts.isClassDeclaration);if(classes.length!==2||classes[0].name.text!=='Node'||classes[1].name.text!=='Queue')throw Error('class declarations differ');
  for(const cls of classes){add('queue:'+cls.name.text,card,cls);for(const member of cls.members)if(member.body)add('queue:'+cls.name.text+'.'+(member.name?member.name.getText(file):'constructor'),card,member)}
  facts.queue={helper_class:'Node',default_class:'Queue',source_only:true};
 }
}
process.stdout.write(JSON.stringify({typescript_version:ts.version,node:process.version,units,facts,source_executed_during_extraction:false,runtime_bindings_certified:false}));
