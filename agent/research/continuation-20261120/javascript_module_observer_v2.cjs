'use strict'
// Trusted research program only. Supplied source is parsed/checked, never loaded.
const fs = require('node:fs')
const crypto = require('node:crypto')
const childProcess = require('node:child_process')
const tsPath = require.resolve('typescript')
const ts = require('typescript')
const VERSION = '0.0.2-research'
const MAX_PACKET = 262144
const MAX_SOURCE = 65536
const MAX_QUOTE = 6144
const sha = raw => crypto.createHash('sha256').update(raw).digest('hex')
const namePattern = /^[A-Za-z_$][A-Za-z0-9_$]{0,127}$/
const refuse = message => { throw new Error(message) }

function strictJson(raw) {
  if (raw.length > MAX_PACKET || !Buffer.from(raw.toString('utf8')).equals(raw)) refuse('invalid bounded UTF-8 request')
  const text = raw.toString('utf8')
  const stack = []
  for (let i = 0; i < text.length; i++) {
    if (text[i] === '{') stack.push({ kind: 'object', keys: new Set() })
    else if (text[i] === '[') stack.push({ kind: 'array' })
    else if (text[i] === '}' || text[i] === ']') stack.pop()
    else if (text[i] === '"') {
      const start = i++
      for (; i < text.length; i++) {
        if (text[i] === '\\') i++
        else if (text[i] === '"') break
      }
      const value = JSON.parse(text.slice(start, i + 1))
      let next = i + 1
      while (/\s/.test(text[next] || '') && next < text.length) next++
      if (text[next] === ':' && stack.at(-1)?.kind === 'object') {
        if (stack.at(-1).keys.has(value)) refuse('duplicate JSON field')
        stack.at(-1).keys.add(value)
      }
    }
  }
  return JSON.parse(text)
}

function observe(packet) {
  if (!packet || typeof packet !== 'object' || Array.isArray(packet) ||
      Object.keys(packet).sort().join(',') !== 'path,selector,source,source_sha256') refuse('closed request required')
  const { source, selector, path, source_sha256: expected } = packet
  if (typeof source !== 'string' || Buffer.byteLength(source) > MAX_SOURCE || source.includes('\0') ||
      Buffer.from(source).toString() !== source || sha(Buffer.from(source)) !== expected) refuse('source identity or size differs')
  if (typeof path !== 'string' || path.length > 1024 || !/^[A-Za-z0-9_./-]+\.(?:js|mjs)$/.test(path) ||
      path.startsWith('/') || path.split('/').some(p => !p || p === '.' || p === '..')) refuse('canonical JS/ESM path required')
  if (typeof selector !== 'string' || !namePattern.test(selector)) refuse('bounded explicit selector required')
  if (source.replaceAll('\r\n', '').includes('\r') || /[\u2028\u2029]/.test(source)) refuse('source outside LF/CRLF physical-line profile')
  // --check parses module syntax without running imports, defaults or bodies.
  const checked = childProcess.spawnSync(process.execPath, ['--input-type=module', '--check'], {
    input: source, encoding: 'utf8', timeout: 5000, maxBuffer: 131072, shell: false
  })
  if (checked.status !== 0 || checked.error) refuse('Node static syntax check refused source')
  const file = ts.createSourceFile(path, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS)
  if (file.parseDiagnostics.length) refuse('TypeScript parser diagnostics')
  const bindings = new Map()
  const functions = new Map()
  const exports = new Map()
  const exportNodes = new Map()
  let moduleMarker = !source.trim()
  let unknownExports = false
  const bind = name => bindings.set(name, (bindings.get(name) || 0) + 1)
  const exported = statement => (statement.modifiers || []).some(m => m.kind === ts.SyntaxKind.ExportKeyword)
  const publish = (publicName, local, node) => {
    if (exports.has(publicName)) refuse('duplicate public export identity')
    exports.set(publicName, local)
    exportNodes.set(publicName, node)
  }
  for (const statement of file.statements) {
    if (ts.isImportDeclaration(statement)) {
      moduleMarker = true
      const clause = statement.importClause
      if (clause?.name) bind(clause.name.text)
      if (clause?.namedBindings) {
        if (ts.isNamespaceImport(clause.namedBindings)) bind(clause.namedBindings.name.text)
        else for (const element of clause.namedBindings.elements) bind(element.name.text)
      }
    } else if (ts.isFunctionDeclaration(statement) && statement.name) {
      const name = statement.name.text
      bind(name)
      functions.set(name, { node: statement, callable: statement })
      if (exported(statement)) {
        moduleMarker = true
        const isDefault = (statement.modifiers || []).some(m => m.kind === ts.SyntaxKind.DefaultKeyword)
        publish(isDefault ? 'default' : name, name, statement)
      }
    } else if (ts.isVariableStatement(statement)) {
      for (const declaration of statement.declarationList.declarations) {
        if (!ts.isIdentifier(declaration.name)) { unknownExports = true; continue }
        const name = declaration.name.text
        bind(name)
        if (declaration.initializer && (ts.isArrowFunction(declaration.initializer) || ts.isFunctionExpression(declaration.initializer)) && statement.declarationList.declarations.length === 1) {
          functions.set(name, { node: statement, callable: declaration.initializer })
        }
        if (exported(statement)) { moduleMarker = true; publish(name, name, statement) }
      }
    } else if (ts.isClassDeclaration(statement) && statement.name) {
      bind(statement.name.text)
      if (exported(statement)) { moduleMarker = true; unknownExports = true }
    } else if (ts.isExportDeclaration(statement)) {
      moduleMarker = true
      if (statement.moduleSpecifier || !statement.exportClause || !ts.isNamedExports(statement.exportClause)) {
        unknownExports = true
      } else for (const element of statement.exportClause.elements) publish(element.name.text, (element.propertyName || element.name).text, statement)
    } else if (ts.isExportAssignment(statement)) {
      moduleMarker = true
      unknownExports = true
    }
  }
  // Mixed CommonJS/global mutation is not silently treated as an empty export.
  let obstruction = false
  function bindWrittenTarget(node) {
    if (ts.isIdentifier(node)) bind(node.text)
    else if (ts.isParenthesizedExpression(node)) bindWrittenTarget(node.expression)
    else if (ts.isArrayLiteralExpression(node)) {
      for (const element of node.elements) bindWrittenTarget(ts.isSpreadElement(element) ? element.expression : element)
    } else if (ts.isObjectLiteralExpression(node)) {
      for (const property of node.properties) {
        if (ts.isShorthandPropertyAssignment(property)) bind(property.name.text)
        else if (ts.isPropertyAssignment(property)) bindWrittenTarget(property.initializer)
        else if (ts.isSpreadAssignment(property)) bindWrittenTarget(property.expression)
      }
    }
  }
  function moduleVisit(node) {
    if (ts.isFunctionLike(node) || ts.isClassDeclaration(node)) return
    if (ts.isIdentifier(node) && ['exports', 'module', 'eval', 'globalThis'].includes(node.text)) obstruction = true
    if (ts.isBinaryExpression(node) && node.operatorToken.kind >= ts.SyntaxKind.FirstAssignment && node.operatorToken.kind <= ts.SyntaxKind.LastAssignment) bindWrittenTarget(node.left)
    if ((ts.isPrefixUnaryExpression(node) || ts.isPostfixUnaryExpression(node)) &&
        [ts.SyntaxKind.PlusPlusToken, ts.SyntaxKind.MinusMinusToken].includes(node.operator)) bindWrittenTarget(node.operand)
    if ((ts.isForInStatement(node) || ts.isForOfStatement(node)) && ts.isIdentifier(node.initializer)) bindWrittenTarget(node.initializer)
    ts.forEachChild(node, moduleVisit)
  }
  for (const statement of file.statements) moduleVisit(statement)
  if (obstruction || !moduleMarker) refuse('module export mode or dynamic namespace unresolved')
  const producer = { version: VERSION, code_sha256: sha(fs.readFileSync(__filename)),
    parser_version: ts.version, parser_sha256: sha(fs.readFileSync(tsPath)), node_version: process.version }
  const result = { status: 'INCONCLUSIVE', selector, source_path: path, source_sha256: expected,
    source_bytes: Buffer.byteLength(source), source_executed: false, runtime_bindings_verified: false,
    owner_approved: false, publication_authorized: false, training_gold: false, producer,
    static_node_check: true, limitations: ['Written local ESM export/signature only; package type, build output, imports and actual calls are unverified.',
      'Missing local callable is never retirement evidence. Supplied source is not loaded or executed.'] }
  if (!exports.has(selector)) {
    if (unknownExports) refuse('wildcard or unresolved export prevents absence claim')
    result.status = 'NO_WRITTEN_EXPORTED_CALLABLE'
    return result
  }
  const local = exports.get(selector)
  if (!namePattern.test(local) || bindings.get(local) !== 1 || !functions.has(local)) refuse('unique local export/callable binding not established')
  const entry = functions.get(local)
  const start = entry.node.getStart(file)
  const end = entry.node.end
  const first = file.getLineAndCharacterOfPosition(start)
  const last = file.getLineAndCharacterOfPosition(end - 1)
  const lines = source.match(/[^\n]*\n|[^\n]+$/g) || []
  if (lines[first.line].slice(0, first.character).trim() || lines[last.line].slice(last.character + 1).trim()) refuse('adjacent same-line source outside selected declaration')
  const quote = lines.slice(first.line, last.line + 1).join('')
  if (!quote || Buffer.byteLength(quote) > MAX_QUOTE) refuse('complete callable quote exceeds bound')
  const parameters = entry.callable.parameters.map(parameter => {
    if (!ts.isIdentifier(parameter.name) || parameter.type || parameter.questionToken || parameter.modifiers?.length) refuse('parameter shape outside profile')
    return { name: parameter.name.text, rest: !!parameter.dotDotDotToken,
      default_expression: parameter.initializer ? parameter.initializer.getText(file) : null,
      default_expression_evaluated: false }
  })
  if (new Set(parameters.map(p => p.name)).size !== parameters.length) refuse('duplicate parameter identity')
  result.status = 'WRITTEN_EXPORTED_CALLABLE_FACTS'
  result.local_selector = local
  result.signature = { parameters, async: (entry.callable.modifiers || []).some(m => m.kind === ts.SyntaxKind.AsyncKeyword), generator: !!entry.callable.asteriskToken }
  result.evidence = { first_line: first.line + 1, last_line: last.line + 1, quote,
    quote_sha256: sha(Buffer.from(quote)), complete_unit: true,
    quote_byte_start: Buffer.byteLength(lines.slice(0, first.line).join('')),
    quote_byte_end: Buffer.byteLength(lines.slice(0, last.line + 1).join('')) }
  const wire = exportNodes.get(selector)
  if (wire === entry.node) {
    result.export_evidence = { kind: 'direct-export-in-callable-unit', source_sha256: expected, evidence_ref: 'evidence' }
  } else {
    const wireStart = wire.getStart(file)
    const wireEnd = wire.end
    const wf = file.getLineAndCharacterOfPosition(wireStart)
    const wl = file.getLineAndCharacterOfPosition(wireEnd - 1)
    if (lines[wf.line].slice(0, wf.character).trim() || lines[wl.line].slice(wl.character + 1).trim()) refuse('adjacent source outside export wire')
    const wireQuote = lines.slice(wf.line, wl.line + 1).join('')
    if (!wireQuote || Buffer.byteLength(wireQuote) > MAX_QUOTE) refuse('complete export wire exceeds quote bound')
    result.export_evidence = { kind: 'complete-written-export-alias', source_sha256: expected,
      first_line: wf.line + 1, last_line: wl.line + 1, quote: wireQuote, quote_sha256: sha(Buffer.from(wireQuote)),
      quote_byte_start: Buffer.byteLength(lines.slice(0, wf.line).join('')),
      quote_byte_end: Buffer.byteLength(lines.slice(0, wl.line + 1).join('')),
      complete_callable: false }
  }
  return result
}

if (require.main === module) {
  try {
    const raw = fs.readFileSync(0)
    const result = observe(strictJson(raw))
    const output = JSON.stringify(result)
    if (Buffer.byteLength(output) > 65536) refuse('response exceeds bound')
    process.stdout.write(output + '\n')
  } catch (error) {
    process.stdout.write(JSON.stringify({ status: 'INCONCLUSIVE', reason: String(error.message).slice(0, 1024),
      source_executed: false, runtime_bindings_verified: false, model_calls: 0, writes: 0, owner_approved: false }) + '\n')
  }
}
module.exports = { strictJson, observe }
