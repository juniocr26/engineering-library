"""Conservative C/C++/Java/PHP/Rust/Go definition ranges, not semantic analysis.

Only definitions beginning on their own line are supported. One-parameter C++
class-template method definitions and ordinary C# methods have bounded lexical
support. Other templates, properties, text blocks and ambiguous names require
a different selection. This is not compiler or semantic validation.
"""
import bisect
import json
import re
import sys


def mask_literals(source, rust=False, go=False):
    masked = list(source)

    def erase(start, finish):
        for offset in range(start, finish):
            if masked[offset] not in '\r\n':
                masked[offset] = ' '

    index = 0
    while index < len(source):
        if source.startswith('//', index):
            finish = source.find('\n', index)
            finish = len(source) if finish < 0 else finish
        elif source.startswith('/*', index):
            finish = source.find('*/', index + 2)
            if finish < 0:
                raise ValueError('Unclosed comment')
            finish += 2
        elif go and source[index] == '`':
            finish = source.find('`', index + 1)
            if finish < 0:
                raise ValueError('Unclosed Go raw string')
            finish += 1
        elif rust and (raw := re.match(r'r(#+)?"', source[index:])):
            ending = '"' + (raw[1] or '')
            finish = source.find(ending, index + raw.end())
            if finish < 0:
                raise ValueError('Unclosed Rust raw string')
            finish += len(ending)
        elif source.startswith('R"', index):
            opening = source.find('(', index + 2, index + 20)
            if opening < 0:
                raise ValueError('Unsupported raw string')
            delimiter = source[index + 2:opening]
            ending = ')' + delimiter + '"'
            finish = source.find(ending, opening + 1)
            if finish < 0:
                raise ValueError('Unclosed raw string')
            finish += len(ending)
        elif source.startswith('"""', index):
            raise ValueError('Java text blocks are unsupported')
        elif source[index] in "\"'":
            if rust and source[index] == "'":
                lifetime = re.match(r"'[A-Za-z_]\w*", source[index:])
                if lifetime and source[index + lifetime.end():index + lifetime.end() + 1] != "'":
                    index += lifetime.end()
                    continue
            if source[index] == "'" and index > 0 and source[index - 1].isdigit():
                index += 1  # C++ numeric separator.
                continue
            quote = source[index]
            finish = index + 1
            while finish < len(source):
                if source[finish] == '\\':
                    finish += 2
                elif source[finish] == quote:
                    finish += 1
                    break
                else:
                    finish += 1
            else:
                raise ValueError('Unclosed literal')
        else:
            index += 1
            continue
        erase(index, finish)
        index = finish
    return ''.join(masked)


def ranges(source, rust=False, go=False):
    masked = mask_literals(source, rust=rust, go=go)
    package = re.search(r'(?m)^[ \t]*package[ \t]+([A-Za-z_]\w*)\b', masked) if go else None
    if go and not package:
        raise ValueError('Go unit selection requires a package declaration')
    breaks = [match.start() for match in re.finditer('\n', source)]
    lines = source.splitlines(keepends=True)
    pairs, stack = {}, []
    for index, char in enumerate(masked):
        if char == '{':
            stack.append(index)
        elif char == '}' and stack:
            pairs[stack.pop()] = index
    scopes = []
    scope_pattern = r'\b(namespace|class|struct|interface)\s+([A-Za-z_]\w*)\s*(?:(?:\:|extends\b|implements\b)[^;{}]+)?\{'
    for match in re.finditer(scope_pattern, masked):
        opening = match.end() - 1
        if opening in pairs:
            scopes.append((opening, pairs[opening], match[1], match[2]))
    if rust:
        for match in re.finditer(r'\bimpl\s+([A-Za-z_]\w*)\s*\{', masked):
            opening = match.end() - 1
            if opening in pairs:
                scopes.append((opening, pairs[opening], 'impl', match[1]))
    definition = re.compile(r'(?m)^[ \t]*(?P<prefix>[A-Za-z_][\w:<>,*&\[\] \t]*?)[ \t]+(?P<name>(?:[A-Za-z_]\w*(?:<[A-Za-z_]\w*>)?::)*[A-Za-z_]\w*)[ \t]*\(')
    forbidden = {'return', 'throw', 'new', 'delete', 'typedef', 'using', 'namespace', 'class', 'struct', 'enum', 'interface', 'record', 'import', 'package', 'case'}
    result = []
    for match in definition.finditer(masked):
        if go and match['prefix'].strip() != 'func':
            continue  # Receiver methods and generic declarations are unsupported.
        if forbidden.intersection(match['prefix'].split()) or match['name'] in {'if', 'for', 'while', 'switch', 'catch', 'synchronized'}:
            continue
        cursor = match.end()
        depth = 1
        while cursor < len(masked) and depth:
            depth += (masked[cursor] == '(') - (masked[cursor] == ')')
            cursor += 1
        if depth:
            continue
        tail = re.search(r'[;={]', masked[cursor:cursor + 2000])
        if not tail or tail[0] != '{':
            continue
        opening = cursor + tail.start()
        if go and re.search(r'\b(?:struct|interface|func)\b', masked[cursor:opening]):
            continue  # Do not confuse an anonymous return type with the body.
        if re.search(r'\brequires\b', masked[cursor:opening]):
            continue  # A requires-expression brace is not the function body.
        finish = pairs.get(opening)
        if finish is None:
            continue
        line_finish = masked.find('\n', finish)
        line_finish = len(masked) if line_finish < 0 else line_finish
        if masked[finish + 1:line_finish].strip() not in {'', ';'}:
            continue  # Do not include a second declaration from the same line.
        start_line = bisect.bisect_left(breaks, match.start())
        end_line = bisect.bisect_left(breaks, finish) + 1
        body = ''.join(lines[start_line:end_line])
        # A preprocessor branch can make lexical brace pairing differ from the
        # compiled definition. Reject instead of claiming a complete method.
        if re.search(r'(?m)^\s*#', body):
            continue
        previous_boundary = max(masked.rfind(';', 0, match.start()), masked.rfind('}', 0, match.start()), masked.rfind('{', 0, match.start()))
        preceding = masked[previous_boundary + 1:match.start()]
        template = re.search(r'\btemplate\b', preceding)
        if template:
            # Support only a complete, single class/typename parameter preceding
            # an explicitly qualified class-template method. No free templates,
            # specializations, constraints or nested template expressions.
            declaration = preceding[template.start():]
            parameter = re.fullmatch(r'template\s*<\s*(?:class|typename)\s+([A-Za-z_]\w*)\s*>\s*', declaration)
            if not parameter or '<' not in match['name'] or ('<' + parameter[1] + '>') not in match['name']:
                continue
            template_start = previous_boundary + 1 + template.start()
            start_line = bisect.bisect_left(breaks, template_start)
        elif '<' in match['name']:
            continue

        while start_line and lines[start_line - 1].lstrip().startswith('@'):
            start_line -= 1
        enclosing = sorted((scope for scope in scopes if scope[0] < match.start() < scope[1]), key=lambda item: item[0])
        names = [scope[3] for scope in enclosing]
        canonical_name = re.sub(r'<[A-Za-z_]\w*>', '', match['name'])
        explicit = canonical_name.split('::')
        symbol = explicit[-1]
        owner = explicit[-2] if len(explicit) > 1 else next((scope[3] for scope in reversed(enclosing) if scope[2] != 'namespace'), None)
        qualified = canonical_name if len(explicit) > 1 else '::'.join([*names, symbol])
        if go:
            owner = package[1]
            qualified = owner + '.' + symbol
        aliases = {symbol, qualified}
        if owner:
            aliases.update({owner + '.' + symbol, owner + '::' + symbol})
        result.append({'start': start_line, 'end': end_line, 'symbol': symbol,
                       'owner': owner, 'qualified': qualified, 'aliases': sorted(aliases)})
    return result


if __name__ == '__main__':
    print(json.dumps(ranges(sys.stdin.read(), rust='--rust' in sys.argv[1:], go='--go' in sys.argv[1:])))
