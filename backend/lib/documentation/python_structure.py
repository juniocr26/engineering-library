"""Return source-layout ranges using Python's parser; never import the source."""
import ast
import json
import sys


def ranges(source):
    tree = ast.parse(source)
    result = []

    def visit(body, owner=None):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = min([node.lineno] + [d.lineno for d in node.decorator_list])
                result.append({'start': start - 1, 'end': node.end_lineno,
                               'symbol': node.name, 'owner': owner})
            elif isinstance(node, ast.ClassDef):
                visit(node.body, node.name)
    visit(tree.body)
    return result


if __name__ == '__main__':
    print(json.dumps(ranges(sys.stdin.read())))
