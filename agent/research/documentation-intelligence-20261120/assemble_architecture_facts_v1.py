"""Bounded syntax facts for the preserved owned example; no source execution."""
import ast
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "agent/research/documentation-intelligence-20261119/owned-adapter/source"
FILES = ("domain.py", "client.py", "adapter.py", "mapping.py", "service.py")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def expression(node):
    return ast.unparse(node) if node is not None else None


def extract(sources):
    if set(sources) != set(FILES):
        raise ValueError("exact owned module registry required")
    result = {"files": {}, "units": {}, "limitations": [
        "Syntax facts do not execute annotations, imports, protocols or inspected source.",
        "An import maps to a frozen local module only under the declared owned registry; runtime sys.path is unverified.",
        "A self attribute or annotation does not prove a concrete runtime receiver type.",
        "A passed timeout does not prove an enforced deadline; client retries and I/O remain unknown.",
    ]}
    for filename, raw in sorted(sources.items()):
        if not isinstance(raw, bytes) or len(raw) > 16384:
            raise ValueError("owned source byte bound")
        text = raw.decode("utf-8")
        tree = ast.parse(text)
        imports = {}
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                if node.level or any(n.name == "*" for n in node.names):
                    raise ValueError("unsupported import")
                for name in node.names:
                    local = name.asname or name.name
                    if local in imports:
                        raise ValueError("duplicate import identity")
                    module_path = node.module.replace(".", "/") + ".py"
                    imports[local] = {"module": node.module, "symbol": name.name,
                                      "local_registry_path": module_path if module_path in sources else None}
        result["files"][filename] = {"sha256": sha(raw), "bytes": len(raw), "imports": imports}
        functions = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                functions.append((node.name, node))
            elif isinstance(node, ast.ClassDef):
                functions.extend((node.name + "." + child.name, child)
                                 for child in node.body if isinstance(child, ast.FunctionDef))
        for name, node in functions:
            identity = filename + ":" + name
            if identity in result["units"]:
                raise ValueError("duplicate declaration identity")
            lines = text.splitlines(keepends=True)
            quote = "".join(lines[node.lineno-1:node.end_lineno])
            calls = []
            for call in ast.walk(node):
                if isinstance(call, ast.Call):
                    calls.append({"callee_expression": expression(call.func),
                                  "arguments": [expression(a) for a in call.args],
                                  "keywords": {a.arg: expression(a.value) for a in call.keywords},
                                  "physical_line": call.lineno})
            assignments = []
            for child in ast.walk(node):
                if isinstance(child, ast.Assign):
                    assignments.append({"targets": [expression(t) for t in child.targets],
                                        "value": expression(child.value), "physical_line": child.lineno})
            handlers = [{"type_expression": expression(n.type), "binding": n.name,
                         "raises": [{"exception_expression": expression(r.exc),
                                     "cause_expression": expression(r.cause)}
                                    for r in ast.walk(n) if isinstance(r, ast.Raise)],
                         "physical_line": n.lineno}
                        for n in ast.walk(node) if isinstance(n, ast.ExceptHandler)]
            positional = node.args.posonlyargs + node.args.args
            defaults = dict(zip([a.arg for a in positional[-len(node.args.defaults):]],
                                [expression(d) for d in node.args.defaults])) if node.args.defaults else {}
            defaults.update({a.arg: expression(d) for a,d in zip(node.args.kwonlyargs, node.args.kw_defaults)
                             if d is not None})
            result["units"][identity] = {
                "file": filename, "selector": name, "source_sha256": sha(raw),
                "first_line": node.lineno, "last_line": node.end_lineno,
                "quote": quote, "quote_sha256": sha(quote.encode()),
                "declared_parameters": [a.arg for a in positional + node.args.kwonlyargs],
                "declared_annotations": {a.arg: expression(a.annotation) for a in positional + node.args.kwonlyargs},
                "declared_defaults": defaults, "calls": calls, "assignments": assignments,
                "handlers": handlers,
                "top_level_statement_kinds": [type(n).__name__ for n in node.body],
                "source_executed": False, "runtime_receiver_identity_verified": False,
            }
    return result


def run():
    sources = {name: (SOURCE / name).read_bytes() for name in FILES}
    pack = extract(sources)
    pack.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                status="EXPERIMENTAL_SYNTAX_FACT_PACK_NOT_RUNTIME_GRAPH",
                family="owned-wallet-adapter-v1", training_gold=False, owner_approved=False)
    out = HERE / "architecture-facts-v1.json"
    with out.open("x") as stream:
        stream.write(json.dumps(pack, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"units": len(pack["units"]), "files": len(pack["files"]), "model_calls": 0}))


if __name__ == "__main__":
    run()
