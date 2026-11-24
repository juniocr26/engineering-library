'use strict'
// Syntax-only source facts. Only the selected installed TypeScript parser is loaded.
const fs = require('node:fs')
const crypto = require('node:crypto')
const VERSION = '1.1.0'
const sha256 = data => crypto.createHash('sha256').update(data).digest('hex')
const refuse = message => { throw new Error(message) }
function propertyName(node, ts) {
  if (ts.isIdentifier(node)) return node.text
  if (ts.isPropertyAccessExpression(node)) {
    const parent = propertyName(node.expression, ts)
    return parent && parent + '.' + node.name.text
  }
  return null
}
function declarations(file, ts) {
  const entries = []
  const functionValue = node => ts.isFunctionExpression(node) || ts.isArrowFunction(node)
  const memberName = node => node && (ts.isIdentifier(node) || ts.isStringLiteral(node)) &&
    /^[A-Za-z_$][\w$]*$/.test(node.text) ? node.text : null
  function objectMembers(object, owner) {
    for (const member of object.properties) {
      const name = memberName(member.name)
      if (!name) continue
      const selector = owner + '.' + name
      if (ts.isMethodDeclaration(member) && member.body) {
        entries.push({ selector, node: member, fn: member, kind: 'object-method' })
      } else if (ts.isPropertyAssignment(member)) {
        if (ts.isObjectLiteralExpression(member.initializer)) objectMembers(member.initializer, selector)
        else if (functionValue(member.initializer)) entries.push({ selector, node: member, fn: member.initializer, kind: 'object-function-property' })
      }
    }
  }
  for (const statement of file.statements) {
    if (ts.isFunctionDeclaration(statement) && statement.name) {
      entries.push({ selector: statement.name.text, node: statement, fn: statement, kind: 'function' })
    } else if (ts.isVariableStatement(statement) && statement.declarationList.declarations.length === 1) {
      const declaration = statement.declarationList.declarations[0]
      if (!ts.isIdentifier(declaration.name) || !declaration.initializer) continue
      if (ts.isObjectLiteralExpression(declaration.initializer)) objectMembers(declaration.initializer, declaration.name.text)
      else if (functionValue(declaration.initializer)) entries.push({ selector: declaration.name.text, node: statement, fn: declaration.initializer, kind: 'function-variable' })
    } else if (ts.isExpressionStatement(statement) && ts.isBinaryExpression(statement.expression)) {
      const assignment = statement.expression
      if (assignment.operatorToken.kind !== ts.SyntaxKind.EqualsToken || !functionValue(assignment.right)) continue
      const selector = propertyName(assignment.left, ts)
      if (selector) entries.push({ selector, node: statement, fn: assignment.right, kind: 'property-function' })
    }
  }
  return entries
}
function inline(value) {
  if (typeof value !== 'string' || !value || value.length > 400 || /[`\r\n\0]/.test(value)) refuse('expression outside bounded inline-code profile')
  return '`' + value + '`'
}
function orderedGuardChain(body, directiveCount, file, ts, selector, ir) {
  const statements = [...body.statements].slice(directiveCount)
  if (statements.length < 3 || statements.length > 4 || !ts.isReturnStatement(statements.at(-1))) return null
  const bounded = value => value === null || (typeof value === 'string' && value.length > 0 && value.length <= 400 && !/[`\r\n\0]/.test(value))
  const guards = []
  for (const statement of statements.slice(0, -1)) {
    if (!ts.isIfStatement(statement) || statement.elseStatement) return null
    let branch = statement.thenStatement
    if (ts.isBlock(branch)) {
      if (branch.statements.length !== 1) return null
      branch = branch.statements[0]
    }
    if (!ts.isReturnStatement(branch)) return null
    const condition = statement.expression.getText(file)
    const returned = branch.expression ? branch.expression.getText(file) : null
    if (!bounded(condition) || !bounded(returned)) return null
    guards.push({ condition, return_expression: returned,
      line: file.getLineAndCharacterOfPosition(statement.getStart(file)).line + 1 })
  }
  const final = statements.at(-1)
  const finalExpression = final.expression ? final.expression.getText(file) : null
  if (!bounded(finalExpression)) return null
  const returned = (expression, lang) => expression === null
    ? (lang === 'en' ? 'a return without an expression' : 'um retorno sem expressão')
    : (lang === 'en' ? 'a return with written expression ' : 'um retorno com a expressão escrita ') + inline(expression)
  const explanations = {}
  for (const lang of ['en', 'pt-br']) {
    let text = (lang === 'en' ? 'Lexical source selector ' : 'Seletor lexical da fonte ') + inline(selector) + ': '
    text += lang === 'en' ? 'after any string directives, the body contains ordered if-return guards and one final return. ' : 'após eventuais diretivas de string, o corpo contém guardas if-return ordenadas e um retorno final. '
    guards.forEach((guard, index) => {
      if (lang === 'en') text += (index === 0 ? 'First, ' : 'Only if preceding tests complete falsy, ') + 'the source tests ' + inline(guard.condition) + '; its truthy branch contains ' + returned(guard.return_expression, lang) + '. '
      else text += (index === 0 ? 'Primeiro, ' : 'Somente se os testes anteriores terminarem com valor lógico falso, ') + 'a fonte testa ' + inline(guard.condition) + '; seu ramo de valor lógico verdadeiro contém ' + returned(guard.return_expression, lang) + '. '
    })
    text += (lang === 'en' ? 'If all tests complete falsy, the final statement contains ' : 'Se todos os testes terminarem com valor lógico falso, a instrução final contém ') + returned(finalExpression, lang) + '. '
    text += lang === 'en' ? 'No guard has an else. This is written synchronous-body syntax only; parameter initialization, name bindings, helper/getter effects, runtime ownership and normal completion remain unverified.' : 'Nenhuma guarda tem else. Trata-se apenas da sintaxe escrita do corpo síncrono; inicialização de parâmetros, vínculos de nomes, efeitos de auxiliares/getters, vínculo em execução e conclusão normal permanecem sem verificação.'
    if (text.length > 1600) return null
    explanations[lang] = text
  }
  return { profile: 'ordered-synchronous-guard-chain-v1', lexical_selector: selector,
    scope: 'Ordered synchronous guard/return syntax; bindings, types, helpers, parameter effects and runtime completion unverified',
    source_path: file.fileName, source_sha256: ir.source_sha256, quote_sha256: ir.quote_sha256,
    start_line: ir.start_line, end_line: ir.end_line, guards,
    final_return_expression: finalExpression,
    source_statement_order: [...guards.map(() => 'if-return'), 'return'],
    parameter_initialization_analyzed: false, called_operations_analyzed: false,
    runtime_ownership_verified: false, source_executed: false, model_inference: false,
    explanations }
}
function prepare(packet, ts) {
  if (!packet || typeof packet !== 'object' || Array.isArray(packet) || Object.keys(packet).sort().join(',') !== 'path,selectors,source') refuse('invalid packet keys')
  const { source, path, selectors } = packet
  if (typeof source !== 'string' || Buffer.byteLength(source) > 2097152 || source.includes('\0') || Buffer.from(source).toString('utf8') !== source) refuse('invalid source bytes or size')
  if (source.replaceAll('\r\n', '').includes('\r')) refuse('bare CR line endings unsupported')
  if (/[\u2028\u2029]/.test(source)) refuse('Unicode line/paragraph separators outside LF/CRLF provenance profile')
  if (typeof path !== 'string' || path.length > 1024 || Buffer.from(path).toString('utf8') !== path ||
      /[\x00-\x1f:\\]/.test(path) || path.startsWith('/') || path.split('/').some(part => !part || part.startsWith('.'))) refuse('unsafe relative source path')
  const extension = path.slice(path.lastIndexOf('.'))
  const kinds = { '.js': ts.ScriptKind.JS, '.cjs': ts.ScriptKind.JS, '.mjs': ts.ScriptKind.JS,
    '.jsx': ts.ScriptKind.JSX, '.ts': ts.ScriptKind.TS, '.tsx': ts.ScriptKind.TSX }
  if (!Object.hasOwn(kinds, extension)) refuse('unsupported source extension')
  if (!Array.isArray(selectors) || selectors.length !== 1 || typeof selectors[0] !== 'string' ||
      !/^[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*$/.test(selectors[0])) refuse('one explicit lexical selector required')
  const file = ts.createSourceFile(path, source, ts.ScriptTarget.Latest, true, kinds[extension])
  if (file.parseDiagnostics.length) refuse('whole-module parse diagnostics')
  const selector = selectors[0]
  const matches = declarations(file, ts).filter(entry => entry.selector === selector)
  if (matches.length !== 1) refuse('selected declaration missing or ambiguous')
  const entry = matches[0]
  const fn = entry.fn
  if (!fn.body || !ts.isBlock(fn.body) || fn.asteriskToken ||
      (fn.modifiers || []).some(modifier => modifier.kind === ts.SyntaxKind.AsyncKeyword)) refuse('only synchronous nongenerator block bodies supported')
  let index = 0
  while (index < fn.body.statements.length && ts.isExpressionStatement(fn.body.statements[index]) &&
      ts.isStringLiteral(fn.body.statements[index].expression)) index++
  const guard = fn.body.statements[index]
  if (!guard || !ts.isIfStatement(guard) || guard.elseStatement) refuse('leading if without else required')
  let branch = guard.thenStatement
  if (ts.isBlock(branch)) {
    if (branch.statements.length !== 1) refuse('guard branch must contain only one return')
    branch = branch.statements[0]
  }
  if (!ts.isReturnStatement(branch)) refuse('leading guard must have sole return branch')
  const condition = guard.expression.getText(file)
  const returnExpression = branch.expression ? branch.expression.getText(file) : null
  inline(selector); inline(condition)
  if (returnExpression !== null) inline(returnExpression)
  const first = file.getLineAndCharacterOfPosition(entry.node.getStart(file))
  const last = file.getLineAndCharacterOfPosition(entry.node.end - 1)
  const lines = source.match(/[^\n]*\n|[^\n]+$/g) || []
  const prefix = lines[first.line].slice(0, first.character).trim()
  const suffix = lines[last.line].slice(last.character + 1).trim()
  if (prefix || !/^(?:[,;]\s*)?(?:\/\/[^\r\n]*)?$/.test(suffix)) refuse('adjacent source outside selected declaration')
  const quote = lines.slice(first.line, last.line + 1).join('')
  if (Buffer.byteLength(quote) > 6144) refuse('complete source declaration exceeds6144bytes')
  const ir = { kind: 'source-derived-leading-guard', lexical_selector: selector,
    declaration_kind: entry.kind, start_line: first.line + 1, end_line: last.line + 1,
    guard_line: file.getLineAndCharacterOfPosition(guard.getStart(file)).line + 1,
    condition, return_expression: returnExpression, directive_statements: index,
    remaining_body_statements_unanalyzed: fn.body.statements.length - index - 1,
    quote, quote_sha256: sha256(quote), source_sha256: sha256(source), source_executed: false }
  const en = 'Lexical source selector ' + inline(selector) + ': after any string directives, the first body statement tests ' + inline(condition) + '. ' +
    (returnExpression === null ? 'Its true branch contains a return without an expression. ' : 'Its true branch contains a return with expression ' + inline(returnExpression) + '. ') +
    'The guard has no else branch. This records written synchronous-body syntax only. Remaining statements, parameter initialization, helper/getter effects, runtime ownership and normal completion are unverified.'
  const pt = 'Seletor lexical da fonte ' + inline(selector) + ': após eventuais diretivas de string, a primeira instrução do corpo testa ' + inline(condition) + '. ' +
    (returnExpression === null ? 'Seu ramo verdadeiro contém um retorno sem expressão. ' : 'Seu ramo verdadeiro contém um retorno com a expressão ' + inline(returnExpression) + '. ') +
    'A guarda não tem ramo else. O registro se limita à sintaxe escrita do corpo síncrono. As instruções restantes, inicialização de parâmetros, efeitos de auxiliares/getters, vínculo em execução e conclusão normal não foram verificados.'
  if (en.length > 1600 || pt.length > 1600) refuse('source explanation exceeds paragraph limit')
  const result = { schema_version: 1, producer: 'javascript-leading-guard-' + VERSION,
    parser_version: ts.version, source_path: path, source_sha256: sha256(source), ir,
    explanations: { en, 'pt-br': pt }, model_inference: false,
    source_executed: false, scope: 'Leading guard syntax only; lexical owner is not generated/runtime binding; no type/helper/runtime verification' }
  const chain = orderedGuardChain(fn.body, index, file, ts, selector, ir)
  if (chain) result.ordered_guard_chain = chain
  return result
}
function parseWire(raw) {
  const packet = JSON.parse(raw)
  let depth = 0, arrays = 0
  const keys = new Set()
  for (let index = 0; index < raw.length; index++) {
    const char = raw[index]
    if (char === '"') {
      const start = index++
      while (index < raw.length) { if (raw[index] === '\\') index += 2; else if (raw[index++] === '"') break }
      let after = index
      while (/\s/.test(raw[after] || '') && after < raw.length) after++
      if (depth === 1 && arrays === 0 && raw[after] === ':') {
        const key = JSON.parse(raw.slice(start, index))
        if (keys.has(key)) refuse('duplicate JSON packet key')
        keys.add(key)
      }
      index--
    } else if (char === '{') depth++
    else if (char === '}') depth--
    else if (char === '[') arrays++
    else if (char === ']') arrays--
  }
  return packet
}
function readBounded() {
  const chunks = []; let total = 0
  while (true) {
    const chunk = Buffer.allocUnsafe(65536)
    const read = fs.readSync(0, chunk, 0, chunk.length, null)
    if (!read) break
    total += read
    if (total > 3145728) refuse('request exceeds byte limit')
    chunks.push(chunk.subarray(0, read))
  }
  return Buffer.concat(chunks)
}
if (require.main === module) {
  try {
    const parserPath = require.resolve(process.argv[2] || 'typescript')
    const ts = require(parserPath)
    const raw = new TextDecoder('utf-8', { fatal: true }).decode(readBounded())
    const result = prepare(parseWire(raw), ts)
    result.identity = { node: process.version, parser_sha256: sha256(fs.readFileSync(parserPath)),
      producer_sha256: sha256(fs.readFileSync(__filename)) }
    process.stdout.write(JSON.stringify(result) + '\n')
  } catch (error) {
    process.stdout.write(JSON.stringify({ status: 'unsupported', reason: String(error.message) }) + '\n')
    process.exitCode = 1
  }
}
module.exports = { prepare, parseWire, VERSION }
