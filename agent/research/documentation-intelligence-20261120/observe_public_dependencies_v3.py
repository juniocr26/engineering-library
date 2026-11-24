"""Compare written local dependency closures; never infer runtime equivalence."""
import ast
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def index(raw):
    tree = ast.parse(raw)
    functions = {}
    imports = {}
    module_bindings = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in functions:
                raise ValueError("ambiguous module function identity")
            functions[node.name] = node
        elif isinstance(node, ast.ImportFrom):
            for name in node.names:
                imports[name.asname or name.name] = {"module": node.module, "symbol": name.name, "level": node.level}
        elif isinstance(node, ast.Import):
            for name in node.names:
                imports[name.asname or name.name.split(".")[0]] = {"module": name.name}
        elif isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            module_bindings.append({"line": node.lineno, "kind": type(node).__name__, "syntax": ast.unparse(node)[:500]})
    return functions, imports, module_bindings


def observe(raw, symbol):
    functions, imports, bindings = index(raw)
    selected, pending, unresolved = {}, [symbol], set()
    while pending:
        name = pending.pop()
        if name in selected:
            continue
        node = functions.get(name)
        if node is None:
            unresolved.add(name)
            continue
        # Deliberately include parameter/global collisions and nested names as
        # possible references. Overapproximation is recorded, not resolved away.
        called_names = {n.func.id for n in ast.walk(node)
                        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        default_names = {n.id for default in [*node.args.defaults, *(d for d in node.args.kw_defaults if d is not None)] for n in ast.walk(default) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        local_candidates = sorted((called_names | default_names) & functions.keys())
        external = sorted(called_names - functions.keys())
        selected[name] = {
            "first_line": node.lineno, "last_line": node.end_lineno,
            "normalized_ast_sha256": sha(ast.dump(node, include_attributes=False).encode()),
            "possible_module_function_dependencies": local_candidates,
            "written_default_name_references": sorted(default_names),
            "written_parameter_calls_unresolved": sorted(called_names & {a.arg for a in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]}),
            "possible_callee_parameter_shadowing": sorted(called_names & functions.keys() & {a.arg for a in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]}),
            "other_written_call_names_unresolved": external,
            "signature": ast.unparse(node.args),
        }
        unresolved.update(external)
        pending.extend(local_candidates)
        if len(selected) > 64:
            raise ValueError("dependency closure exceeds bounded registry")
    return {"source_sha256": sha(raw), "selected_symbol": symbol, "units": selected,
            "imports": imports, "module_assignments": bindings,
            "unresolved_written_calls": sorted(unresolved),
            "runtime_name_binding_verified": False,
            "limitations": ["Call-name graph is a conservative syntactic candidate graph; lexical shadowing and dynamic binding are unresolved.",
                            "Stable normalized AST does not prove stable helper runtime behavior.",
                            "Attribute calls and external imports have no runtime resolution.",
                            "Module assignments are retained as evidence, not silently ignored."]}


def run():
    oracle = json.loads((HERE / "public-lifecycle-oracle-v1.json").read_text())
    rows = []
    for case in oracle["cases"]:
        versions = []
        for tag in ("24.0.0", "25.0.0"):
            span = case["source_spans"][tag]
            raw = (ROOT / span["path"]).read_bytes()
            if sha(raw) != span["sha256"]:
                raise ValueError("public source changed")
            versions.append(observe(raw, span["selector"]))
        before, after = versions
        names = before["units"].keys() | after["units"].keys()
        changed = [name for name in sorted(names) if name in before["units"] and name in after["units"] and
                   before["units"][name]["normalized_ast_sha256"] != after["units"][name]["normalized_ast_sha256"]]
        membership = {"added_to_closure": sorted(after["units"].keys() - before["units"].keys()), "removed_from_closure": sorted(before["units"].keys() - after["units"].keys())}
        rows.append({"id": case["id"], "versions": versions,
                     "changed_written_closure_units": changed,
                     "closure_membership_delta_not_source_retirement": membership,
                     "same_written_closure": not changed and not any(membership.values()) and bool(after["units"]),
                     "correct_documentation_action_established": False,
                     "source_executed": False})
    with (HERE / "public-dependency-observations-v3.json").open("x") as stream:
        stream.write(json.dumps({"at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                "classification": "POST_EVALUATION_DEVELOPMENT_OBSERVATION_NOT_HOLDOUT_SCORE",
                                "rows": rows, "model_calls": 0}, ensure_ascii=False, indent=2) + "\n")
    print([(r["id"], r["changed_written_closure_units"]) for r in rows])


if __name__ == "__main__":
    run()
