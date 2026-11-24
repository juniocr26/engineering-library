'use strict'
// Optional syntax-only context preparer. Inspected source is never loaded as code.
const crypto = require('node:crypto')
const fs = require('node:fs')
const pathModule = require('node:path')
const VERSION = '1.0.1'
const MAX_SOURCE_BYTES = 2097152
const MAX_QUOTE_BYTES = 1900
const MAX_CARDS = 4
const sha256 = value => crypto.createHash('sha256').update(value).digest('hex')

function refuse(message) { throw new Error(message) }
function propertyName(node, ts) {
  if (ts.isIdentifier(node)) return node.text
  if (ts.isPropertyAccessExpression(node)) {
    const parent = propertyName(node.expression, ts)
    if (parent && ts.isIdentifier(node.name)) return parent + '.' + node.name.text
  }
  return null
}
function functionValue(node, ts) {
  return node && (ts.isFunctionExpression(node) || ts.isArrowFunction(node))
}
function declarations(file, ts) {
  const entries = []
  for (const statement of file.statements) {
    if (ts.isFunctionDeclaration(statement) && statement.name) {
      entries.push({ name: statement.name.text, node: statement, body: statement.body })
    } else if (ts.isVariableStatement(statement)) {
      const declarations = statement.declarationList.declarations
      // A whole line/range must not silently claim a second variable declaration.
      if (declarations.length !== 1) continue
      const declaration = declarations[0]
      if (ts.isIdentifier(declaration.name) && functionValue(declaration.initializer, ts)) {
        entries.push({ name: declaration.name.text, node: statement, body: declaration.initializer.body })
      }
    } else if (ts.isExpressionStatement(statement) && ts.isBinaryExpression(statement.expression)) {
      const assignment = statement.expression
      if (assignment.operatorToken.kind !== ts.SyntaxKind.EqualsToken || !functionValue(assignment.right, ts)) continue
      const name = propertyName(assignment.left, ts)
      if (name) entries.push({ name, node: statement, body: assignment.right.body })
    }
  }
  return entries
}
function prepare(packet, ts) {
  if (!packet || typeof packet !== 'object' || Array.isArray(packet) ||
      Object.keys(packet).sort().join(',') !== 'path,selectors,source') refuse('invalid packet keys')
  const { source, path, selectors } = packet
  if (typeof source !== 'string' || Buffer.byteLength(source) > MAX_SOURCE_BYTES || source.includes('\0') || Buffer.from(source, 'utf8').toString('utf8') !== source) refuse('invalid source size or content')
  if (source.replaceAll('\r\n', '').includes('\r')) refuse('bare CR line endings unsupported')
  if (/[\u2028\u2029]/.test(source)) refuse('Unicode line/paragraph separators outside LF/CRLF provenance profile')
  if (typeof path !== 'string' || path.length > 1024 || path.startsWith('/') || path.includes(':') || path.includes('\\') ||
      path.split('/').some(part => !part || part.startsWith('.'))) refuse('unsafe relative source path')
  const extension = pathModule.extname(path)
  const kinds = { '.js': ts.ScriptKind.JS, '.cjs': ts.ScriptKind.JS, '.mjs': ts.ScriptKind.JS,
    '.jsx': ts.ScriptKind.JSX, '.ts': ts.ScriptKind.TS, '.tsx': ts.ScriptKind.TSX }
  if (!Object.hasOwn(kinds, extension)) refuse('unsupported source extension')
  if (!Array.isArray(selectors) || selectors.length < 1 || selectors.length > MAX_CARDS ||
      new Set(selectors).size !== selectors.length || selectors.some(value => typeof value !== 'string' ||
      !/^[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*$/.test(value))) refuse('invalid selectors')
  const file = ts.createSourceFile(path, source, ts.ScriptTarget.Latest, true, kinds[extension])
  if (file.parseDiagnostics.length) refuse('source parse diagnostics')
  const candidates = declarations(file, ts)
  const lines = source.match(/[^\n]*\n|[^\n]+$/g) || []
  const selected = []
  const ranges = []
  for (const selector of selectors) {
    const matches = candidates.filter(entry => entry.name === selector)
    if (matches.length !== 1) refuse('declaration missing or ambiguous: ' + selector)
    const entry = matches[0]
    if (!entry.body || !ts.isBlock(entry.body)) refuse('only declarations with block bodies supported: ' + selector)
    const start = entry.node.getStart(file)
    const end = entry.node.end
    const first = file.getLineAndCharacterOfPosition(start)
    const last = file.getLineAndCharacterOfPosition(end - 1)
    if (lines[first.line].slice(0, first.character).trim() ||
        lines[last.line].slice(last.character + 1).trim()) refuse('adjacent same-line source outside selected declaration')
    const quote = lines.slice(first.line, last.line + 1).join('')
    let chunkStart = first.line
    let chunk = ''
    const chunks = []
    for (let line = first.line; line <= last.line; line++) {
      const value = lines[line]
      if (Buffer.byteLength(value) > MAX_QUOTE_BYTES) refuse('source line exceeds quotation budget')
      if (chunk && Buffer.byteLength(chunk + value) > MAX_QUOTE_BYTES) {
        chunks.push({ start_line: chunkStart + 1, end_line: line, quote: chunk, quote_sha256: sha256(chunk) })
        chunkStart = line
        chunk = ''
      }
      chunk += value
    }
    if (chunk) chunks.push({ start_line: chunkStart + 1, end_line: last.line + 1, quote: chunk, quote_sha256: sha256(chunk) })
    if (ranges.length + chunks.length > MAX_CARDS) refuse('selected declarations exceed four-card context budget')
    ranges.push(...chunks.map(chunk => [chunk.start_line, chunk.end_line]))
    selected.push({ selector, start_line: first.line + 1, end_line: last.line + 1,
      quote_sha256: sha256(quote), quote_bytes: Buffer.byteLength(quote),
      complete_ast_declaration: true, chunks })
  }
  return { schema_version: 1, producer: 'javascript-ranges-' + VERSION,
    parser_version: ts.version, source_path: path, source_sha256: sha256(source),
    ranges: { [path]: ranges }, selected, source_executed: false,
    scope: 'Parser declaration spans only; chunks are source ranges, not semantic/type/helper/runtime facts',
    consumer: 'Explicit SectionCommand/ProjectCommand ranges; consumer retains incomplete-unit caveat' }
}

if (require.main === module) {
  try {
    // This path identifies an operator-selected installed parser, never the inspected source.
    const parserPath = require.resolve(process.argv[2] || 'typescript')
    const ts = require(parserPath)
    const result = prepare(JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(fs.readFileSync(0))), ts)
    result.identity = { node: process.version, parser_sha256: sha256(fs.readFileSync(parserPath)),
      producer_sha256: sha256(fs.readFileSync(__filename)) }
    process.stdout.write(JSON.stringify(result) + '\n')
  } catch (error) {
    process.stdout.write(JSON.stringify({ status: 'unsupported', reason: String(error.message) }) + '\n')
    process.exitCode = 1
  }
}
module.exports = { prepare, VERSION }
