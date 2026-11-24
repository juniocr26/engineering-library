#!/usr/bin/env python3
"""Closed static import/call profile; inspected Python is never executed."""
import ast
import copy
import hashlib
import json
import keyword
import os
from pathlib import Path
import re
import subprocess
import sys

from documentation_workspace import directory, read, same_root, WorkspaceRefused

VERSION = "0.1.2"
MAX_FILE = 65536
MAX_TOTAL = 262144
MAX_QUOTES = 24576
MAX_ALIASES = 64
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,63}\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")
OWN_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
WORKSPACE_SHA = hashlib.sha256(Path(__file__).with_name("documentation_workspace.py").read_bytes()).hexdigest()


class DependencyRefused(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise DependencyRefused("duplicate JSON field")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(DependencyRefused("nonfinite JSON")))


def identifier(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value) or value.startswith("__") or keyword.iskeyword(value):
        raise DependencyRefused("unsupported identifier")
    return value


def strip_docstring(body):
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and type(body[0].value.value) is str:
        return body[1:]
    return body


def literal(node):
    sign = 1
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        sign, node = -1, node.operand
    if isinstance(node, ast.Constant) and type(node.value) is int and abs(node.value) <= 2**53 - 1:
        return sign * node.value
    return None


def analyze_sources(sources, entry_module, entry_symbol):
    """Pure bounded syntax analysis on already-read UTF-8 strings."""
    if not isinstance(sources, dict) or not 1 <= len(sources) <= 16:
        raise DependencyRefused("module registry bound")
    modules, quotes, imports = {}, {}, []
    total, aliases, import_quote_bytes = 0, 0, 0
    for name, source in sorted(sources.items()):
        identifier(name)
        if not isinstance(source, str):
            raise DependencyRefused("source must be UTF-8 text")
        raw = source.encode("utf-8"); total += len(raw)
        if not 0 < len(raw) <= MAX_FILE or total > MAX_TOTAL:
            raise DependencyRefused("source byte bound")
        tree = ast.parse(source)
        if sum(1 for _ in ast.walk(tree)) > 4096:
            raise DependencyRefused("AST node bound")
        lines = re.findall(rb"[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+$", raw)
        source_sha = sha(raw)
        def physical_quote(node):
            quoted = b"".join(lines[node.lineno-1:node.end_lineno])
            if not 0 < len(quoted) <= 6144:
                raise DependencyRefused("complete statement quote bound")
            return {"module": name, "path": name + ".py", "source_sha256": source_sha,
                    "first_line": node.lineno, "last_line": node.end_lineno,
                    "quote": quoted.decode("utf-8"), "quote_sha256": sha(quoted)}
        bindings = {}
        for node in strip_docstring(tree.body):
            if isinstance(node, ast.ImportFrom):
                if node.level or node.module not in sources:
                    raise DependencyRefused("relative, external or missing module import")
                aliases += len(node.names)
                if aliases > MAX_ALIASES:
                    raise DependencyRefused("registered import alias bound")
                import_bindings = []
                for alias in node.names:
                    target, local = identifier(alias.name), identifier(alias.asname or alias.name)
                    if local in bindings:
                        raise DependencyRefused("duplicate module binding")
                    bindings[local] = ("import", node.module, target)
                    import_bindings.append({"local_symbol": local, "target_module": node.module,
                                            "target_symbol": target})
                unit = physical_quote(node)
                import_quote_bytes += len(unit["quote"].encode())
                if import_quote_bytes > MAX_QUOTES:
                    raise DependencyRefused("registered import quote budget")
                imports.append({**unit, "bindings": import_bindings})
            elif isinstance(node, ast.FunctionDef):
                identifier(node.name)
                args = node.args
                if node.decorator_list or node.returns or getattr(node, "type_params", []) or args.posonlyargs or args.args or args.kwonlyargs or args.vararg or args.kwarg or args.defaults or args.kw_defaults:
                    raise DependencyRefused("function must have no decorators, annotations, type parameters or arguments")
                body = strip_docstring(node.body)
                if len(body) != 1 or not isinstance(body[0], ast.Return):
                    raise DependencyRefused("unsupported function body")
                value = body[0].value
                integer = literal(value)
                if integer is not None:
                    binding = ("literal", integer)
                elif isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and not value.args and not value.keywords:
                    binding = ("call", identifier(value.func.id))
                else:
                    raise DependencyRefused("unsupported return expression")
                if node.name in bindings:
                    raise DependencyRefused("duplicate module binding")
                bindings[node.name] = binding
                quotes[(name, node.name)] = {**physical_quote(node), "symbol": node.name}
            else:
                raise DependencyRefused("unsupported top-level statement")
        modules[name] = bindings
    # Reject module import cycles independently of callable alias cycles.
    checked_modules = set()
    def check_imports(module, active=()):
        if module in active:
            raise DependencyRefused("module import cycle")
        if module in checked_modules:
            return
        for binding in modules[module].values():
            if binding[0] == "import":
                check_imports(binding[1], active + (module,))
        checked_modules.add(module)
    for module in modules:
        check_imports(module)
    # Validate every declared import even when the entry path never reaches it.
    def resolve(module, symbol, seen=()):
        key = (module, symbol)
        if key in seen or len(seen) >= 16:
            raise DependencyRefused("cyclic or excessive imported binding chain")
        binding = modules.get(module, {}).get(symbol)
        if binding is None:
            raise DependencyRefused("missing function binding")
        if binding[0] == "import":
            return resolve(binding[1], binding[2], seen + (key,))
        return key, binding
    for module, bindings in modules.items():
        for symbol in bindings:
            resolved, binding = resolve(module, symbol)
            if binding[0] == "call":
                resolve(resolved[0], binding[1])
    path, edges = [], []
    def visit(module, symbol):
        key, binding = resolve(module, symbol)
        if key in path or len(path) >= 8:
            raise DependencyRefused("call cycle or depth bound")
        path.append(key)
        if binding[0] == "literal":
            value = binding[1]
        else:
            target, _ = resolve(key[0], binding[1])
            edges.append({"from_module": key[0], "from_symbol": key[1],
                          "to_module": target[0], "to_symbol": target[1],
                          "call_name": binding[1]})
            value = visit(key[0], binding[1])
        return value
    value = visit(identifier(entry_module), identifier(entry_symbol))
    total_quote_bytes = import_quote_bytes + sum(len(quotes[key]["quote"].encode()) for key in path)
    if total_quote_bytes > MAX_QUOTES:
        raise DependencyRefused("combined import/function quote budget")
    return {"status": "STATIC_INTEGER_RETURN_UNDER_CLOSED_PROFILE", "value": value,
            "entry_module": entry_module, "entry_symbol": entry_symbol,
            "imports": imports, "total_quote_bytes": total_quote_bytes,
            "contract_key": sha(canonical({"profile": VERSION, "integer_return": value})),
            "edges": edges, "functions": [quotes[key] for key in path],
            "limitations": ["Conditional on operator-supplied flat module and runtime binding assumptions.",
                            "No import hooks, sys.modules, monkeypatching or actual execution are verified.",
                            "All registered files participate in the evidence key; it is conservative, not a minimal dependency cache."]}


def validate_observation(observed, sources, entry_module, entry_symbol):
    """Validate the trusted producer envelope and quotes without parent AST parsing."""
    if not isinstance(observed, dict) or set(observed) != {"status", "value", "contract_key", "edges", "functions", "limitations", "entry_module", "entry_symbol", "imports", "total_quote_bytes"}:
        raise DependencyRefused("invalid worker result fields")
    if observed["entry_module"] != entry_module or observed["entry_symbol"] != entry_symbol or entry_module not in sources:
        raise DependencyRefused("worker entry identity differs from request")
    identifier(entry_module); identifier(entry_symbol)
    if observed["status"] != "STATIC_INTEGER_RETURN_UNDER_CLOSED_PROFILE" or type(observed["value"]) is not int or abs(observed["value"]) > 2**53-1:
        raise DependencyRefused("invalid worker result value")
    if observed["contract_key"] != sha(canonical({"profile": VERSION, "integer_return": observed["value"]})):
        raise DependencyRefused("invalid worker contract key")
    functions, edges = observed["functions"], observed["edges"]
    if not isinstance(functions, list) or not 1 <= len(functions) <= 8 or not isinstance(edges, list) or len(edges) != len(functions)-1:
        raise DependencyRefused("invalid worker graph bounds")
    shared = {"module", "path", "source_sha256", "first_line", "last_line", "quote", "quote_sha256"}
    def physical(unit):
        module = identifier(unit["module"])
        if module not in sources:
            raise DependencyRefused("unknown quote module")
        source = sources[module].encode()
        if unit["path"] != module + ".py" or unit["source_sha256"] != sha(source):
            raise DependencyRefused("statement source identity differs")
        first, last = unit["first_line"], unit["last_line"]
        lines = re.findall(rb"[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+$", source)
        if type(first) is not int or type(last) is not int or not 1 <= first <= last <= len(lines):
            raise DependencyRefused("invalid quote lines")
        raw = b"".join(lines[first-1:last])
        if not 0 < len(raw) <= 6144 or not isinstance(unit["quote"], str) or unit["quote"].encode() != raw or unit["quote_sha256"] != sha(raw):
            raise DependencyRefused("quote differs from physical source")
        return len(raw)
    keys, quote_bytes = [], 0
    for function in functions:
        if not isinstance(function, dict) or set(function) != shared | {"symbol"}:
            raise DependencyRefused("invalid function evidence fields")
        module, symbol = identifier(function["module"]), identifier(function["symbol"])
        quote_bytes += physical(function)
        keys.append((module, symbol))
    if len(set(keys)) != len(keys):
        raise DependencyRefused("repeated graph function")
    imports = observed["imports"]
    if not isinstance(imports, list) or len(imports) > MAX_ALIASES:
        raise DependencyRefused("import evidence bound")
    alias_keys = set()
    for unit in imports:
        if not isinstance(unit, dict) or set(unit) != shared | {"bindings"}:
            raise DependencyRefused("invalid import evidence fields")
        quote_bytes += physical(unit)
        if not isinstance(unit["bindings"], list) or not unit["bindings"]:
            raise DependencyRefused("invalid import binding list")
        for binding in unit["bindings"]:
            if not isinstance(binding, dict) or set(binding) != {"local_symbol", "target_module", "target_symbol"}:
                raise DependencyRefused("invalid import binding fields")
            local = identifier(binding["local_symbol"])
            target = identifier(binding["target_module"]); identifier(binding["target_symbol"])
            key = unit["module"], local
            if target not in sources or key in alias_keys or key in keys:
                raise DependencyRefused("unknown or duplicate imported binding")
            alias_keys.add(key)
            if len(alias_keys) > MAX_ALIASES:
                raise DependencyRefused("registered import alias bound")
    if type(observed["total_quote_bytes"]) is not int or observed["total_quote_bytes"] != quote_bytes or quote_bytes > MAX_QUOTES:
        raise DependencyRefused("combined quote byte accounting differs")
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict) or set(edge) != {"from_module", "from_symbol", "to_module", "to_symbol", "call_name"}:
            raise DependencyRefused("invalid graph edge fields")
        identifier(edge["call_name"])
        if (edge["from_module"], edge["from_symbol"]) != keys[index] or (edge["to_module"], edge["to_symbol"]) != keys[index+1]:
            raise DependencyRefused("graph edge differs from function path")
    if not isinstance(observed["limitations"], list) or not observed["limitations"] or not all(isinstance(item, str) for item in observed["limitations"]):
        raise DependencyRefused("invalid worker limitations")


class ClosedDependencyObserver:
    """Explicit operator registry; immutable per instance, no persistent cache."""
    def __init__(self, root, registry, timeout=3):
        if not isinstance(registry, dict) or set(registry) != {"revision", "modules"}:
            raise DependencyRefused("closed registry fields required")
        if not isinstance(registry["revision"], str) or not 1 <= len(registry["revision"]) <= 160:
            raise DependencyRefused("revision bound")
        if not isinstance(registry["modules"], dict) or not 1 <= len(registry["modules"]) <= 16:
            raise DependencyRefused("module registry bound")
        for name, entry in registry["modules"].items():
            identifier(name)
            if not isinstance(entry, dict) or set(entry) != {"path", "sha256"} or entry["path"] != name + ".py" or not isinstance(entry["sha256"], str) or not HASH.fullmatch(entry["sha256"]):
                raise DependencyRefused("invalid flat module identity")
        if type(timeout) not in (int, float) or not 0 < timeout <= 3:
            raise DependencyRefused("timeout bound")
        self.root, self.registry, self.timeout = Path(root), copy.deepcopy(registry), timeout
        self._registry_bytes = canonical(self.registry)
        self._root_config = str(self.root)
        self._timeout_config = timeout
        with directory(self.root) as fd:
            info = os.fstat(fd)
            self.root_identity = info.st_dev, info.st_ino
        self._root_identity_config = self.root_identity

    def configuration(self):
        if (canonical(self.registry) != self._registry_bytes
                or str(self.root) != self._root_config
                or type(self.timeout) not in (int, float)
                or self.timeout != self._timeout_config
                or self.root_identity != self._root_identity_config):
            raise DependencyRefused("operator-frozen configuration changed; construct a reviewed new observer")
        # Operation-local data is decoded from the initial immutable bytes,
        # never from a public mapping that another caller can mutate in flight.
        return strict_json(self._registry_bytes)

    def observe(self, entry_module, entry_symbol):
        result = {"version": VERSION, "status": "INCONCLUSIVE", "source_executed": False,
                  "runtime_bindings_verified": False, "owner_approved": False}
        try:
            identifier(entry_module); identifier(entry_symbol)
            registry = self.configuration()
            root, root_identity, timeout = self._root_config, self._root_identity_config, self._timeout_config
            if sha(Path(__file__).read_bytes()) != OWN_SHA or sha(Path(__file__).with_name("documentation_workspace.py").read_bytes()) != WORKSPACE_SHA:
                raise DependencyRefused("loaded implementation changed; operator reload required")
            sources, metadata = {}, {}
            with directory(root) as fd:
                info = os.fstat(fd)
                if (info.st_dev, info.st_ino) != root_identity:
                    raise DependencyRefused("registered root identity changed")
                for name, entry in sorted(registry["modules"].items()):
                    raw, meta = read(fd, entry["path"], MAX_FILE)
                    if meta["sha256"] != entry["sha256"]:
                        raise DependencyRefused("source hash differs")
                    sources[name] = raw.decode("utf-8"); metadata[name] = meta
                if sum(len(source.encode()) for source in sources.values()) > MAX_TOTAL:
                    raise DependencyRefused("total source byte bound")
                packet = {"sources": sources, "entry_module": entry_module, "entry_symbol": entry_symbol}
                worker = subprocess.run([sys.executable, str(Path(__file__).resolve()), "_worker"],
                    input=canonical(packet), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    timeout=timeout, check=False)
                if len(worker.stdout) > 131072:
                    raise DependencyRefused("worker exceeded response bound")
                if worker.returncode:
                    detail = worker.stderr.decode("utf-8", errors="replace").strip()[:512]
                    raise DependencyRefused("worker refused: " + detail)
                observed = strict_json(worker.stdout)
                validate_observation(observed, sources, entry_module, entry_symbol)
                for name, entry in sorted(registry["modules"].items()):
                    _, current = read(fd, entry["path"], MAX_FILE)
                    if current["sha256"] != metadata[name]["sha256"]:
                        raise DependencyRefused("source changed during observation")
                if not same_root(root, fd):
                    raise DependencyRefused("source root changed during observation")
                if sha(Path(__file__).read_bytes()) != OWN_SHA or sha(Path(__file__).with_name("documentation_workspace.py").read_bytes()) != WORKSPACE_SHA:
                    raise DependencyRefused("implementation changed during observation")
                self.configuration()
            identity = {"registry": registry, "entry_module": entry_module,
                        "entry_symbol": entry_symbol, "profile": VERSION,
                        "extractor_sha256": OWN_SHA, "workspace_sha256": WORKSPACE_SHA}
            result.update(observed, revision=registry["revision"], evidence_key=sha(canonical(identity)),
                          source_registry_sha256=sha(canonical(registry)),
                          registered_sources=[{"module": name, **entry} for name, entry in sorted(registry["modules"].items())],
                          extractor_sha256=OWN_SHA, workspace_sha256=WORKSPACE_SHA)
        except (DependencyRefused, WorkspaceRefused, OSError, UnicodeError, ValueError, TypeError,
                SyntaxError, RecursionError, subprocess.TimeoutExpired) as error:
            result.update(status="INCONCLUSIVE", reason=str(error))
        return result


if __name__ == "__main__":
    if sys.argv[1:] != ["_worker"]:
        raise SystemExit(2)
    try:
        raw = sys.stdin.buffer.read(MAX_TOTAL * 2 + 1)
        if len(raw) > MAX_TOTAL * 2:
            raise DependencyRefused("worker input bound")
        packet = strict_json(raw)
        if not isinstance(packet, dict) or set(packet) != {"sources", "entry_module", "entry_symbol"}:
            raise DependencyRefused("invalid worker fields")
        output = analyze_sources(packet["sources"], packet["entry_module"], packet["entry_symbol"])
        sys.stdout.buffer.write(canonical(output))
    except (ValueError, SyntaxError, UnicodeError, RecursionError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2)
