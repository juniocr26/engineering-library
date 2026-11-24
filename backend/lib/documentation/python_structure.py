"""Return source-layout ranges using Python's parser; never import the source."""
import ast
import json
import re
import sys


def caught_exception_identifiers(node):
    """Written catch references, not resolved exception classes or handler effects."""
    def reference(value):
        if isinstance(value, ast.Name):
            return value.id
        if isinstance(value, ast.Attribute):
            owner = reference(value.value)
            return owner + '.' + value.attr if owner else None
        return None

    names = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.ExceptHandler) or child.type is None:
            continue
        values = child.type.elts if isinstance(child.type, ast.Tuple) else [child.type]
        for value in values:
            name = reference(value)
            if name and len(name) <= 256 and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*', name):
                names.add(name)
    # This optional guard never claims complete exception or runtime coverage.
    return sorted(names) if len(names) <= 32 else []


def direct_return_mapping_identifiers(node):
    """Lexical references in direct literal-map returns, not resolved map semantics."""
    def reference(value):
        parts = []
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
            if len(parts) > 32:
                return None
        if not isinstance(value, ast.Name):
            return None
        parts.append(value.id)
        name = '.'.join(reversed(parts))
        if len(name) <= 256 and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*', name):
            return name
        return None

    names = set()
    for child in node.body:
        if not isinstance(child, ast.Return) or not isinstance(child.value, ast.Dict):
            continue
        mapping = child.value
        if not 1 <= len(mapping.keys) <= 32:
            return []
        for key, value in zip(mapping.keys, mapping.values):
            pair = (reference(key), reference(value))
            if any(name is None for name in pair):
                return []
            names.update(pair)
        if len(names) > 64:
            return []
    # Optional spelling metadata only: no helper execution, pair-direction proof,
    # nested-return ownership, mixed/unpacked-map or unbounded-map coverage.
    return sorted(names)


def ranges(source):
    if '\r' in source.replace('\r\n', ''):
        raise ValueError('bare CR line endings outside LF/CRLF source profile')
    tree = ast.parse(source)
    result = []

    def visit(body, owner=None):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = min([node.lineno] + [d.lineno for d in node.decorator_list])
                result.append({'start': start - 1, 'end': node.end_lineno,
                               'symbol': node.name, 'owner': owner,
                               'caught_exception_identifiers': caught_exception_identifiers(node),
                               'direct_return_mapping_identifiers': direct_return_mapping_identifiers(node)})
            elif isinstance(node, ast.ClassDef):
                visit(node.body, node.name)
    visit(tree.body)
    return result


if __name__ == '__main__':
    print(json.dumps(ranges(sys.stdin.buffer.read().decode('utf-8'))))
