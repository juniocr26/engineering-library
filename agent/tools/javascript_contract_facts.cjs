'use strict'
// Closed written field-mapping facts; inspected application source is never loaded.
const fs = require('node:fs')
const crypto = require('node:crypto')
const VERSION = '0.1.0'
const MAX_SOURCE = 65536
const MAX_QUOTE = 6144
const namePattern = /^[A-Za-z_$][A-Za-z0-9_$]*$/
const forbiddenBindings = new Set(['eval', 'arguments'])
const sha = value => crypto.createHash('sha256').update(value).digest('hex')
const refuse = reason => { throw new Error(reason) }

function parseContracts(source, ts, sourcePath = 'selected.js') {
  if (typeof source !== 'string' || source.includes('\0') ||
      Buffer.byteLength(source) > MAX_SOURCE ||
      Buffer.from(source, 'utf8').toString('utf8') !== source) refuse('invalid bounded UTF-8 source')
  if (typeof sourcePath !== 'string' || !/^[A-Za-z0-9_./-]+\.js$/.test(sourcePath) ||
      sourcePath.startsWith('/') || sourcePath.split('/').includes('..')) refuse('invalid source path')
  const file = ts.createSourceFile(sourcePath, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS)
  if (file.parseDiagnostics.length) refuse('JavaScript syntax diagnostic')
  const functions = Object.create(null)
  const topNames = new Set()
  const allowedExport = node => {
    const modifiers = node.modifiers || []
    return modifiers.some(value => value.kind === ts.SyntaxKind.ExportKeyword) &&
      modifiers.every(value => value.kind === ts.SyntaxKind.ExportKeyword)
  }
  function record(fn, selector, declarationKind) {
    if (!namePattern.test(selector.split('.').at(-1)) || functions[selector]) refuse('ambiguous declaration')
    if (!fn.body || !ts.isBlock(fn.body) || fn.asteriskToken || fn.type ||
        (fn.typeParameters && fn.typeParameters.length) || fn.parameters.length !== 1) refuse('unsupported callable shape')
    const parameter = fn.parameters[0]
    if (!ts.isIdentifier(parameter.name) || !namePattern.test(parameter.name.text) || forbiddenBindings.has(parameter.name.text) ||
        parameter.initializer || parameter.dotDotDotToken || parameter.questionToken ||
        parameter.type || (parameter.modifiers && parameter.modifiers.length)) refuse('unsupported parameter')
    if (fn.body.statements.length !== 1 || !ts.isReturnStatement(fn.body.statements[0])) refuse('unsupported body')
    const expression = fn.body.statements[0].expression
    if (!expression || !ts.isObjectLiteralExpression(expression) ||
        expression.properties.length < 1 || expression.properties.length > 8) refuse('unsupported returned object')
    const mapping = Object.create(null)
    for (const property of expression.properties) {
      if (!ts.isPropertyAssignment(property) || !ts.isIdentifier(property.name) ||
          !namePattern.test(property.name.text) || property.name.text === '__proto__' ||
          Object.hasOwn(mapping, property.name.text)) refuse('unsupported or duplicate output property')
      const value = property.initializer
      if (!ts.isPropertyAccessExpression(value) || value.questionDotToken ||
          !ts.isIdentifier(value.expression) || value.expression.text !== parameter.name.text ||
          !ts.isIdentifier(value.name) || !namePattern.test(value.name.text)) refuse('unsupported input property')
      mapping[property.name.text] = { parameter_index: 0, property: value.name.text }
    }
    const start = fn.getStart(file)
    const end = fn.end
    const quote = source.slice(start, end)
    if (Buffer.byteLength(quote) > MAX_QUOTE) refuse('complete callable exceeds quote bound')
    const first = file.getLineAndCharacterOfPosition(start)
    const last = file.getLineAndCharacterOfPosition(end - 1)
    functions[selector] = {
      lexical_selector: selector, declaration_kind: declarationKind,
      fact: {
        signature: {
          posonly: [], positional: [parameter.name.text], keyword_only: [],
          vararg: null, kwarg: null, defaults: [], keyword_defaults: []
        },
        behavior: { kind: 'written-object-field-map', mapping }
      },
      first_line: first.line + 1, last_line: last.line + 1,
      first_column_utf16: first.character,
      quote, quote_sha256: sha(Buffer.from(quote)),
      quote_byte_start: Buffer.byteLength(source.slice(0, start)),
      quote_byte_end: Buffer.byteLength(source.slice(0, end)),
      receiver_binding_verified: false
    }
  }
  for (const statement of file.statements) {
    if (ts.isExportDeclaration(statement) && !statement.moduleSpecifier &&
        statement.exportClause && ts.isNamedExports(statement.exportClause) &&
        statement.exportClause.elements.length === 0) continue
    if (ts.isExpressionStatement(statement) && ts.isStringLiteral(statement.expression) &&
        statement.expression.text === 'use strict') continue
    if (!statement.name || !ts.isIdentifier(statement.name) ||
        !namePattern.test(statement.name.text) || forbiddenBindings.has(statement.name.text) || topNames.has(statement.name.text) ||
        !allowedExport(statement)) refuse('unsupported or duplicate module declaration')
    topNames.add(statement.name.text)
    if (ts.isFunctionDeclaration(statement)) {
      record(statement, statement.name.text, 'exported-function')
    } else if (ts.isClassDeclaration(statement)) {
      if ((statement.heritageClauses && statement.heritageClauses.length) ||
          (statement.typeParameters && statement.typeParameters.length) ||
          !statement.members.length || statement.members.length > 16) refuse('unsupported class context')
      for (const member of statement.members) {
        if (!ts.isMethodDeclaration(member) || !member.name ||
            !ts.isIdentifier(member.name) || (member.modifiers && member.modifiers.length)) refuse('unsupported class member')
        record(member, statement.name.text + '.' + member.name.text, 'lexical-instance-method')
      }
    } else refuse('unsupported module statement')
    if (Object.keys(functions).length > 16) refuse('contract count exceeds bound')
  }
  return {
    profile: 'javascript-bounded-written-field-map-v1',
    source_sha256: sha(Buffer.from(source)), source_bytes: Buffer.byteLength(source),
    source_path: sourcePath, functions, registries: {},
    syntax_only: true, source_executed: false, runtime_bindings_verified: false,
    limitations: [
      'Exact written object-field mapping, not type/import/build or runtime verification.',
      'Property getters, values, exceptions and effects remain unverified.',
      'A lexical instance-method selector is not a static invocation or runtime binding.'
    ]
  }
}

module.exports = { parseContracts, VERSION }
if (require.main === module) {
  try {
    const raw = fs.readFileSync(0)
    if (raw.length > 131072) refuse('request exceeds bound')
    const request = JSON.parse(raw.toString('utf8'))
    if (!request || typeof request !== 'object' || Array.isArray(request) ||
        Object.keys(request).some(key => !['source', 'source_path'].includes(key))) refuse('invalid request schema')
    const parserPath = require.resolve(process.argv[2] || 'typescript')
    const ts = require(parserPath)
    const result = parseContracts(request.source, ts, request.source_path ?? 'selected.js')
    result.producer = {
      version: VERSION, code_sha256: sha(fs.readFileSync(__filename)),
      parser_sha256: sha(fs.readFileSync(parserPath)),
      parser_version: ts.version, node_version: process.version
    }
    process.stdout.write(JSON.stringify(result) + '\n')
  } catch (error) {
    process.stdout.write(JSON.stringify({
      status: 'REFUSED', profile: 'javascript-bounded-written-field-map-v1',
      reason: error.message, source_executed: false, runtime_bindings_verified: false
    }) + '\n')
    process.exitCode = 2
  }
}
