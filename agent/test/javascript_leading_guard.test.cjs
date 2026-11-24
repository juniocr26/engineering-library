'use strict'
const test=require('node:test'),assert=require('node:assert/strict'),ts=require(process.argv[2] || 'typescript')
const {prepare,parseWire}=require('../tools/javascript_leading_guard.cjs')
const packet=(source,selector='f',path='sample.js')=>({source,path,selectors:[selector]})
rejects('Unicode line separator cannot cite adjacent function', 'const x=1;\u2028function f(v) { if(v) return 1 }\nfunction g(v) { if(v) return 2 }\n', 'f', /Unicode line\/paragraph separators/)
rejects('Unicode paragraph separator cannot cite adjacent function', 'const x=1;\u2029function f(v) { if(v) return 1 }\nfunction g(v) { if(v) return 2 }\n', 'f', /Unicode line\/paragraph separators/)
rejects('literal Unicode separator inside string outside profile', 'function f(v) {\n if(v) return "x\u2028y"\n}\n', 'f', /Unicode line\/paragraph separators/)
function accepts(name,source,selector,condition,returned,path='sample.js') {
 test(name,()=>{const result=prepare(packet(source,selector,path),ts);assert.equal(result.ir.condition,condition);assert.equal(result.ir.return_expression,returned);assert.equal(result.source_executed,false);assert.equal(result.model_inference,false);assert.deepEqual([...result.explanations.en.matchAll(/`([^`]+)`/g)].map(m=>m[1]),[...result.explanations['pt-br'].matchAll(/`([^`]+)`/g)].map(m=>m[1]));assert.equal(result.ir.quote,source.split(/(?<=\n)/).slice(result.ir.start_line-1,result.ir.end_line).join(''))})
}
function rejects(name,source,selector='f',pattern){test(name,()=>assert.throws(()=>prepare(packet(source,selector),ts),pattern))}
accepts('sync nullish false guard','function f(x) {\n if (x == null) return false\n work(x)\n}\n','f','x == null','false')
accepts('sole block return','function f(x) {\n if (!x) { return 0 }\n next()\n}\n','f','!x','0')
accepts('bare return','function f(x) {\n if (x) return\n next()\n}\n','f','x',null)
accepts('string directives','function f(x) {\n "use strict"\n if (x) return true\n}\n','f','x','true')
accepts('lexical variable function','const f = function named(x) {\n if (x) return null\n}\n','f','x','null')
accepts('block arrow','const f = x => {\n if (x) return x\n}\n','f','x','x')
accepts('qualified assigned function','Obj.f = function (x) {\n if (x) return this\n}\n','Obj.f','x','this')
accepts('object shorthand method','const Obj = {\n f(x) {\n  if (x) return 1\n },\n}\n','Obj.f','x','1')
accepts('nested object function property and dollar','const Obj = {\n $Nested: {\n  f: function(x) {\n   if (x) return -1\n  },\n },\n}\n','Obj.$Nested.f','x','-1')
accepts('unicode and CRLF preserved','function f(x) {\r\n if (x === "ação") return "ação"\r\n}\r\n','f','x === "ação"','"ação"')
accepts('written helper expression not executed','throw new Error("must not run")\nfunction f(x) {\n if (x) return helper(x)\n}\n','f','x','helper(x)')
accepts('TypeScript syntax does not imply typechecking','function f<T>(x: T): T | null {\n if (x == null) return null\n return x\n}\n','f','x == null','null','sample.ts')
rejects('async result boundary refused','async function f(x) { if(x) return false }\n')
rejects('generator result boundary refused','function* f(x) { if(x) return false }\n')
rejects('concise arrow refused','const f=x=>x?false:true\n')
rejects('else guard refused','function f(x) { if(x) return false; else return true }\n')
rejects('multiple branch statements refused','function f(x) { if(x) {work();return false} }\n')
rejects('prefix computation refused','function f(x) { const y=work();if(x)return false }\n')
rejects('throw guard refused','function f(x) {if(x)throw new Error("bad")}\n')
rejects('syntax diagnostics anywhere refused','function f(x) {if(x)return false}\nfunction broken( {\n')
rejects('duplicate function selector refused','function f(x){if(x)return false}\nfunction f(x){if(x)return true}\n')
rejects('class method outside lexical profile','class Obj {f(x){if(x)return false}}\n','Obj.f')
rejects('same line adjacent declaration refused','function f(x){if(x)return false}; function other(){}\n')
rejects('computed object member refused','const Obj={\n [key](x){if(x)return false}\n}\n','Obj.f')
rejects('duplicate object member refused','const Obj={\n f(x){if(x)return false},\n f(x){if(x)return true},\n}\n','Obj.f')
rejects('inline template/backtick refused','function f(x) {if(x)return `value`}\n')
rejects('oversized complete unit not truncated','function f(x) {\n if(x)return false\n //'+('x'.repeat(6200))+'\n}\n')
test('physical line directive stays physical',()=>{const r=prepare(packet('//line fake.js:900\nfunction f(x){if(x)return false}\n'),ts);assert.equal(r.ir.start_line,2)})
test('invalid source/path/selector/keys fail closed',()=>{const base=packet('function f(x){if(x)return false}\n');for(const item of [{...base,path:'../sample.js'},{...base,path:'a\\b.js'},{...base,selectors:['f','f']},{...base,selectors:['f;run']},{...base,extra:true},{...base,source:base.source+'\0'},{...base,source:base.source+'\ud800'}])assert.throws(()=>prepare(item,ts))})
test('wire duplicate and escaped duplicate fields refused',()=>{assert.throws(()=>parseWire('{"source":"a","source":"b","path":"x.js","selectors":["f"]}'),/duplicate/);assert.throws(()=>parseWire('{"source":"a","\\u0073ource":"b","path":"x.js","selectors":["f"]}'),/duplicate/);assert.equal(parseWire('{"source":"quote: \\\"source\\\": inside value","path":"x.js","selectors":["f"]}').path,'x.js')})

test('ordered three-guard packet preserves first-guard facts and exact source provenance',()=>{
 const source='function f(x) {\n if (x === 0) return "fallback"\n if (x < 1) return 1\n if (x > 100) return 100\n return x\n}\n'
 const r=prepare(packet(source),ts),chain=r.ordered_guard_chain
 assert.equal(r.ir.condition,'x === 0');assert.equal(r.ir.return_expression,'"fallback"')
 assert.equal(r.ir.remaining_body_statements_unanalyzed,3)
 assert.match(r.explanations.en,/Remaining statements/)
 assert.deepEqual(chain.guards.map(g=>g.condition),['x === 0','x < 1','x > 100'])
 assert.deepEqual(chain.guards.map(g=>g.return_expression),['"fallback"','1','100'])
 assert.deepEqual(chain.guards.map(g=>g.line),[2,3,4])
 assert.deepEqual(chain.source_statement_order,['if-return','if-return','if-return','return'])
 assert.equal(chain.final_return_expression,'x');assert.equal(chain.source_sha256,r.ir.source_sha256)
 assert.equal(chain.quote_sha256,r.ir.quote_sha256);assert.equal(chain.source_executed,false)
 assert.deepEqual([...chain.explanations.en.matchAll(/`([^`]+)`/g)].map(m=>m[1]),[...chain.explanations['pt-br'].matchAll(/`([^`]+)`/g)].map(m=>m[1]))
 assert.match(chain.explanations.en,/Only if preceding tests complete falsy/)
})
test('unsupported chains retain leading-guard behavior without a whole-chain packet',()=>{
 for(const rest of [
  'work();if(b)return 2;return 3',
  'if(b)return 2;if(c)return 3;if(d)return 4;return 5',
  'if(b)return 2;else return 3;return 4',
  'if(b){work();return 2};return 3',
  'if(b){if(c)return 2};return 3',
  'if(b)throw failure;return 3',
  'if(b)return 2;work()',
  'if(b)return `template`;return 3',
  'if(b)return "'+'x'.repeat(401)+'";return 3',
 ]){
  const r=prepare(packet('function f(x){\n if(a)return 1\n '+rest+'\n}\n'),ts)
  assert.equal(r.ir.condition,'a');assert.equal(r.ir.return_expression,'1')
  assert.equal(r.ordered_guard_chain,undefined)
  assert.match(r.explanations.en,/Remaining statements/)
 }
})
test('ordered packet keeps bare returns and does not execute source or parameter defaults',()=>{
 const source='throw new Error("source must not run")\nfunction f(x=absentFactory()){\n if(a)return\n if(b)return helper(x)\n return\n}\n'
 const chain=prepare(packet(source),ts).ordered_guard_chain
 assert.equal(chain.guards.length,2);assert.equal(chain.guards[0].return_expression,null)
 assert.equal(chain.final_return_expression,null);assert.equal(chain.parameter_initialization_analyzed,false)
 assert.equal(chain.called_operations_analyzed,false);assert.equal(chain.runtime_ownership_verified,false)
 assert.equal(chain.model_inference,false);assert.match(chain.explanations.en,/return without an expression/)
})
test('ordered packet uses physical CRLF lines and lexical object ownership',()=>{
 const source='//line logical.js:900\nconst Obj={\n f(x){\n  if(this.a)return "ação"\n  if(this.b)return null\n  return x\n },\n}\n'
 for(const text of [source,source.replaceAll('\n','\r\n')]){
  const r=prepare(packet(text,'Obj.f'),ts),chain=r.ordered_guard_chain
  assert.equal(chain.lexical_selector,'Obj.f');assert.deepEqual(chain.guards.map(g=>g.line),[4,5])
  assert.equal(chain.start_line,3);assert.equal(chain.end_line,7)
  assert.match(chain.explanations.en,/runtime ownership and normal completion remain unverified/)
 }
})
