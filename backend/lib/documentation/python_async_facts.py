"""Bounded Python syntax recorder; never import or execute inspected source."""
import ast
import hashlib
import json
import re
import sys

MAX_SOURCE_BYTES = 1_048_576
MAX_QUOTE_BYTES = 6_144


class Unsupported(ValueError):
    pass


def atom(node):
    if isinstance(node, ast.Name):
        return
    if isinstance(node, ast.Attribute):
        return atom(node.value)
    if isinstance(node, ast.Constant) and (
        node.value is None or type(node.value) in (str, int, bool)
    ):
        return
    raise Unsupported("operand outside bounded subset")


def condition(node):
    if isinstance(node, (ast.Name, ast.Attribute)):
        atom(node)
        return
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        condition(node.operand)
        return
    if (
        isinstance(node, ast.Compare)
        and len(node.ops) == 1
        and len(node.comparators) == 1
        and isinstance(node.ops[0], (ast.Eq, ast.NotEq, ast.Is, ast.IsNot, ast.In, ast.NotIn))
    ):
        atom(node.left)
        atom(node.comparators[0])
        return
    raise Unsupported("condition outside bounded subset")


def callee(node):
    if isinstance(node, ast.Name):
        return
    if isinstance(node, ast.Attribute):
        return callee(node.value)
    raise Unsupported("computed callee outside subset")


def awaited_call(nodes):
    if (
        len(nodes) != 1
        or not isinstance(nodes[0], ast.Expr)
        or not isinstance(nodes[0].value, ast.Await)
        or not isinstance(nodes[0].value.value, ast.Call)
    ):
        raise Unsupported("branch must be sole awaited call expression")
    call = nodes[0].value.value
    callee(call.func)
    for arg in call.args:
        atom(arg.value if isinstance(arg, ast.Starred) else arg)
    for keyword in call.keywords:
        atom(keyword.value)
    return call


def inline(node):
    value = ast.unparse(node)
    if any(char in value for char in "`\r\n\x00") or len(value) > 600:
        raise Unsupported("expression not safe bounded inline code")
    return value


def forwarded_return(function, body):
    """Record a two-statement shape, never resolve names or execute helpers."""
    args = function.args
    if (args.posonlyargs or len(args.args) != 1 or args.kwonlyargs
            or args.defaults or not args.vararg or not args.kwarg):
        raise Unsupported("forwarded return requires one parameter, *args and **kwargs")
    parameter, positional, keywords = args.args[0].arg, args.vararg.arg, args.kwarg.arg
    if len({parameter, positional, keywords}) != 3:
        raise Unsupported("forwarded return parameter names must differ")
    if len(body) != 2 or not isinstance(body[0], ast.Assign) or not isinstance(body[1], ast.Return):
        raise Unsupported("requires sole assignment and awaited return")
    assignment, returned = body
    if (len(assignment.targets) != 1 or not isinstance(assignment.targets[0], ast.Name)
            or assignment.targets[0].id != parameter or not isinstance(assignment.value, ast.Call)
            or not isinstance(returned.value, ast.Await) or not isinstance(returned.value.value, ast.Call)):
        raise Unsupported("requires parameter reassignment then return await call")
    bound, awaited = assignment.value, returned.value.value
    callee(bound.func)
    callee(awaited.func)
    if (len(bound.args) != 2 or not isinstance(bound.args[0], ast.Name)
            or bound.args[0].id != parameter or not isinstance(bound.args[1], ast.Starred)
            or not isinstance(bound.args[1].value, ast.Name) or bound.args[1].value.id != positional
            or len(bound.keywords) != 1 or bound.keywords[0].arg is not None
            or not isinstance(bound.keywords[0].value, ast.Name) or bound.keywords[0].value.id != keywords
            or len(awaited.args) != 1 or not isinstance(awaited.args[0], ast.Name)
            or awaited.args[0].id != parameter or awaited.keywords):
        raise Unsupported("forwarded return argument shape differs")
    return {
        "shape": "local-call-awaited-return",
        "scope": "Syntactic assignment and awaited return; no binding/helper/runtime proof",
        "local_target": parameter,
        "binding_call": inline(bound),
        "binding_callee": inline(bound.func),
        "returned_call": inline(awaited),
        "returned_callee": inline(awaited.func),
    }


def guarded_iteration(function, body):
    """Record one narrow async-generator loop, without resolving exception names."""
    args = function.args
    if (args.posonlyargs or len(args.args) != 1 or args.kwonlyargs
            or args.defaults or args.vararg or args.kwarg):
        raise Unsupported("iteration requires one ordinary parameter")
    if len(body) != 2 or not isinstance(body[0], ast.Assign) or not isinstance(body[1], ast.While):
        raise Unsupported("iteration requires sole local assignment and while loop")
    assignment, loop = body
    if (len(assignment.targets) != 1 or not isinstance(assignment.targets[0], ast.Name)
            or assignment.targets[0].id == args.args[0].arg
            or not isinstance(assignment.value, ast.Call)):
        raise Unsupported("iteration requires distinct assigned local")
    initial = assignment.value
    callee(initial.func)
    if (len(initial.args) != 1 or not isinstance(initial.args[0], ast.Name)
            or initial.args[0].id != args.args[0].arg or initial.keywords):
        raise Unsupported("iteration initializer must receive the sole parameter")
    if (not isinstance(loop.test, ast.Constant) or loop.test.value is not True
            or loop.orelse or len(loop.body) != 1 or not isinstance(loop.body[0], ast.Try)):
        raise Unsupported("iteration requires while True and sole try")
    attempt = loop.body[0]
    if (attempt.orelse or attempt.finalbody or len(attempt.handlers) != 1
            or len(attempt.body) != 1 or not isinstance(attempt.body[0], ast.Expr)
            or not isinstance(attempt.body[0].value, ast.Yield)
            or not isinstance(attempt.body[0].value.value, ast.Await)
            or not isinstance(attempt.body[0].value.value.value, ast.Call)):
        raise Unsupported("iteration requires sole yield await call and one handler")
    yielded = attempt.body[0].value.value.value
    callee(yielded.func)
    local = assignment.targets[0].id
    if (len(yielded.args) != 2 or not all(isinstance(arg, ast.Name) for arg in yielded.args)
            or yielded.args[1].id != local or yielded.keywords):
        raise Unsupported("yielded call requires named helper and assigned local")
    handler = attempt.handlers[0]
    if (not isinstance(handler.type, ast.Name) or handler.name is not None
            or len(handler.body) != 1 or not isinstance(handler.body[0], ast.Break)):
        raise Unsupported("iteration requires one named exception and sole break")
    return {
        "shape": "local-call-guarded-yield-await",
        "scope": "Syntactic async-generator loop; no name/type/helper/runtime proof",
        "local_target": local,
        "initial_call": inline(initial),
        "initial_callee": inline(initial.func),
        "yielded_call": inline(yielded),
        "yielded_callee": inline(yielded.func),
        "exception_name": inline(handler.type),
    }


def record(source, selector):
    if not isinstance(source, str) or len(source.encode()) > MAX_SOURCE_BYTES:
        raise Unsupported("source size/type")
    if '\r' in source.replace('\r\n', ''):
        raise Unsupported("bare CR line endings outside LF/CRLF source profile")
    if not isinstance(selector, str) or not re.fullmatch(
        r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*", selector
    ):
        raise Unsupported("invalid selector")
    try:
        tree = ast.parse(source)
    except (SyntaxError, RecursionError) as error:
        raise Unsupported("source syntax") from error
    matches = []

    def visit(nodes, owner=""):
        for node in nodes:
            if isinstance(node, ast.ClassDef):
                visit(node.body, (owner + "." if owner else "") + node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qualified = (owner + "." if owner else "") + node.name
                if qualified == selector:
                    matches.append(node)

    visit(tree.body)
    if len(matches) != 1:
        raise Unsupported("selected declaration missing or ambiguous")
    function = matches[0]
    if not isinstance(function, ast.AsyncFunctionDef) or function.decorator_list:
        raise Unsupported("requires undecorated async function")
    if getattr(function, 'type_params', []):
        raise Unsupported("generic async declarations outside bounded profile")
    body = list(function.body)
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        body = body[1:]
    if len(body) == 1 and isinstance(body[0], ast.If):
        branch = body[0]
        condition(branch.test)
        true_call = awaited_call(branch.body)
        false_call = awaited_call(branch.orelse)
        details = {
            "shape": "if-else-awaited-dispatch",
            "scope": "Syntactic if/else awaited-call record; no type/helper/runtime proof",
            "condition": inline(branch.test),
            "truthy_callee": inline(true_call.func),
            "truthy_await": inline(true_call),
            "falsy_callee": inline(false_call.func),
            "falsy_await": inline(false_call),
        }
    elif "." not in selector and len(body) == 2 and isinstance(body[1], ast.While):
        details = guarded_iteration(function, body)
    elif "." not in selector:
        details = forwarded_return(function, body)
    else:
        raise Unsupported("requires sole if/else body or module-level forwarded return")
    lines = re.findall(r'[^\n]*\n|[^\n]+$', source)
    quote = "".join(lines[function.lineno - 1:function.end_lineno])
    if len(quote.encode()) > MAX_QUOTE_BYTES:
        raise Unsupported("quote byte budget")
    declaration = "async def " + function.name + "(" + inline(function.args) + ")"
    if function.returns is not None:
        declaration += " -> " + inline(function.returns)
    if len(declaration) > 600:
        raise Unsupported("declaration exceeds inline budget")
    return {
        "declaration": declaration,
        "kind": "source-derived",
        "qualified_symbol": selector,
        "line": function.lineno,
        "end_line": function.end_lineno,
        "quote": quote,
        "quote_sha256": hashlib.sha256(quote.encode()).hexdigest(),
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "source_executed": False,
        **details,
    }


def render(ir, language):
    if language not in ("en", "pt-br"):
        raise Unsupported("unsupported language")
    if ir["shape"] == "local-call-guarded-yield-await":
        if language == "en":
            return (
                f"`{ir['qualified_symbol']}` has declaration `{ir['declaration']}`. "
                f"Before the loop, the body assigns `{ir['initial_call']}` to local `{ir['local_target']}`. "
                f"Inside `while True`, the try body executes `yield await {ir['yielded_call']}`. "
                "If the awaited expression completes normally, its result is yielded, not returned as a final value. "
                f"The sole handler is `except {ir['exception_name']}` and its sole statement is `break`; "
                "this handler contains no raise. There is no loop else, try else or finally. "
                "These are source-derived syntax facts; names, exception matching, helper behavior, "
                "thread scheduling and successful runtime completion are not verified."
            )
        return (
            f"`{ir['qualified_symbol']}` tem declaração `{ir['declaration']}`. "
            f"Antes do laço, o corpo atribui `{ir['initial_call']}` à variável local `{ir['local_target']}`. "
            f"Dentro de `while True`, o corpo do try executa `yield await {ir['yielded_call']}`. "
            "Se a expressão aguardada termina normalmente, seu resultado é emitido com yield, não retornado como valor final. "
            f"Há um tratador `except {ir['exception_name']}` cujo corpo contém apenas `break`; "
            "esse tratador não contém raise. Não há else do laço, else do try nem finally. "
            "São fatos sintáticos derivados da fonte; nomes, correspondência de exceções, comportamento dos auxiliares, "
            "escalonamento de threads e conclusão bem-sucedida em execução não foram verificados."
        )
    if ir["shape"] == "local-call-awaited-return":
        if language == "en":
            return (
                f"`{ir['qualified_symbol']}` has declaration `{ir['declaration']}`. "
                f"The body assigns the result of `{ir['binding_call']}` to local `{ir['local_target']}`, "
                f"then executes `return await {ir['returned_call']}`. "
                "If that awaited expression completes normally, its result is returned by this body. "
                "There is no try/except in the body. Annotations are recorded syntax, not evaluated types. "
                "These are source-derived syntax facts; name bindings, argument-binding behavior of helpers, "
                "thread scheduling and successful runtime completion are not verified."
            )
        return (
            f"`{ir['qualified_symbol']}` tem declaração `{ir['declaration']}`. "
            f"O corpo atribui o resultado de `{ir['binding_call']}` à variável local `{ir['local_target']}`, "
            f"depois executa `return await {ir['returned_call']}`. "
            "Se essa expressão aguardada termina normalmente, seu resultado é retornado por este corpo. "
            "Não há try/except no corpo. Anotações são sintaxe registrada, não tipos avaliados. "
            "São fatos sintáticos derivados da fonte; vínculos de nomes, comportamento de associação de argumentos "
            "dos auxiliares, escalonamento de threads e conclusão bem-sucedida em execução não foram verificados."
        )
    if language == "en":
        return (
            f"`{ir['qualified_symbol']}` has declaration `{ir['declaration']}` and contains one if/else dispatch. "
            f"If `{ir['condition']}` is truthy, the source awaits `{ir['truthy_await']}`; "
            f"if it is falsy, the source awaits `{ir['falsy_await']}`. "
            "The body has no explicit return statement or try/except. Declaration annotations "
            "and defaults are recorded syntax, not runtime validation or evaluated values. "
            "These are source-derived syntax facts; called operations, dynamic dispatch, "
            "normal completion and runtime behavior are not verified."
        )
    return (
        f"`{ir['qualified_symbol']}` tem declaração `{ir['declaration']}` e contém um despacho if/else. "
        f"Se `{ir['condition']}` tem valor lógico verdadeiro, o código aguarda `{ir['truthy_await']}`; "
        f"se tem valor lógico falso, o código aguarda `{ir['falsy_await']}`. "
        "O corpo não contém return explícito nem try/except. Anotações e valores padrão "
        "da declaração são sintaxe registrada, não validação em execução nem valores avaliados. "
        "São fatos sintáticos derivados da fonte; operações chamadas, despacho dinâmico, "
        "conclusão normal e comportamento em execução não foram verificados."
    )


def main():
    try:
        packet = json.load(sys.stdin)
        if not isinstance(packet, dict) or set(packet) != {"source", "selector"}:
            raise Unsupported("invalid source-analysis packet")
        ir = record(packet["source"], packet["selector"])
        print(json.dumps({
            "ir": ir,
            "explanations": {language: render(ir, language) for language in ("en", "pt-br")},
            "expression_format": "AST-normalized expressions; quote bytes remain verbatim",
        }, ensure_ascii=False))
        return 0
    except (Unsupported, ValueError, TypeError, KeyError, RecursionError) as error:
        print(json.dumps({"status": "unsupported", "reason": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
