"""Bounded module declaration facts, not execution or a general doc planner."""
import ast
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "agent/tools"))
import documentation_retrieval as retrieval

VERSION = "0.0.4-research"
MAX_SOURCE = 65536
MAX_NODES = 16384
MAX_QUOTE = 6144
OWN_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
RETRIEVAL_SHA = hashlib.sha256(Path(retrieval.__file__).read_bytes()).hexdigest()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class ObservationRefused(ValueError):
    pass


def literal_or_expression(node):
    if node is None:
        return {"kind": "required"}
    text = ast.unparse(node)
    if len(text.encode()) > 512:
        return {"kind": "unresolved-expression", "ast_sha256": sha(ast.dump(node, include_attributes=False).encode())}
    if isinstance(node, ast.Name):
        return {"kind": "written-name", "name": node.id, "runtime_binding_verified": False}
    try:
        value = ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        return {"kind": "unresolved-expression", "text": text}
    if type(value) not in (str, int, float, bool, type(None)) or isinstance(value, float) and not math.isfinite(value):
        return {"kind": "unresolved-expression", "text": text}
    if len(json.dumps(value, ensure_ascii=False).encode()) > 2048:
        return {"kind": "unresolved-expression", "text": text}
    return {"kind": "literal", "type": type(value).__name__, "value": value}


def signature(node):
    args = node.args
    positional = args.posonlyargs + args.args
    defaults = {arg.arg: {"kind": "required"} for arg in positional}
    defaults.update({arg.arg: literal_or_expression(value)
                     for arg,value in zip(positional[-len(args.defaults):], args.defaults)}
                    if args.defaults else {})
    defaults.update({arg.arg: literal_or_expression(value) for arg,value in zip(args.kwonlyargs,args.kw_defaults)})
    parameters = [*positional, *args.kwonlyargs]
    if len({arg.arg for arg in parameters}) != len(parameters):
        raise ObservationRefused("duplicate parameter identity")
    return {"positional_only": [arg.arg for arg in args.posonlyargs],
            "positional_or_keyword": [arg.arg for arg in args.args],
            "keyword_only": [arg.arg for arg in args.kwonlyargs],
            "vararg": args.vararg.arg if args.vararg else None,
            "kwarg": args.kwarg.arg if args.kwarg else None,
            "defaults": defaults,
            "annotations": {arg.arg: ast.unparse(arg.annotation) if arg.annotation else None for arg in parameters},
            "return_annotation": ast.unparse(node.returns) if node.returns else None,
            "annotation_or_default_executed": False}


def without_docstring(body):
    body = list(body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body.pop(0)
    return body


def module_bindings(module):
    names = set()
    dynamic = []
    class BindingVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            names.add(node.name)
            arguments = [*node.args.posonlyargs,*node.args.args,*node.args.kwonlyargs] + ([node.args.vararg] if node.args.vararg else []) + ([node.args.kwarg] if node.args.kwarg else [])
            for value in [*node.decorator_list, *node.args.defaults,
                          *(v for v in node.args.kw_defaults if v is not None),
                          *(a.annotation for a in arguments if a.annotation is not None),
                          *([node.returns] if node.returns is not None else [])]:
                self.visit(value)
        visit_AsyncFunctionDef = visit_FunctionDef
        def visit_ClassDef(self, node):
            names.add(node.name)
            if any(isinstance(child, (ast.Global,ast.Nonlocal)) for child in ast.walk(node)):
                dynamic.append({"line":node.lineno,"callee":"class-global-or-nonlocal-scope"})
            for value in [*node.decorator_list,*node.bases,*(v.value for v in node.keywords)]:
                self.visit(value)
        def visit_Name(self, node):
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                names.add(node.id)
        def visit_Import(self, node):
            names.update(v.asname or v.name.split(".")[0] for v in node.names)
        def visit_ImportFrom(self, node):
            names.update(v.asname or v.name for v in node.names)
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id in {"exec", "eval", "globals", "locals", "setattr", "delattr"}:
                dynamic.append({"line": node.lineno, "callee": node.func.id})
            self.generic_visit(node)
        def visit_ExceptHandler(self, node):
            if node.name:
                names.add(node.name)
            self.generic_visit(node)
        def visit_MatchAs(self, node):
            if node.name:
                names.add(node.name)
            self.generic_visit(node)
        def visit_MatchStar(self, node):
            if node.name:
                names.add(node.name)
        def visit_MatchMapping(self, node):
            if node.rest:
                names.add(node.rest)
            self.generic_visit(node)
    visitor = BindingVisitor()
    for node in module.body:
        visitor.visit(node)
    return names, dynamic


def return_shape(node):
    body = without_docstring(node.body)
    if len(body) != 1 or not isinstance(body[0], ast.Return):
        return {"kind": "outside-direct-return-profile"}
    value = body[0].value
    if isinstance(value, ast.Tuple) and all(isinstance(item, ast.Name) for item in value.elts):
        return {"kind": "tuple-of-written-names", "elements": [item.id for item in value.elts]}
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
        return {"kind": "written-return-call", "callee": value.func.id,
                "args": [ast.unparse(arg) for arg in value.args],
                "keywords": [{"name": kw.arg,"value":ast.unparse(kw.value)} for kw in value.keywords],
                "expression": ast.unparse(value)}
    return {"kind": "other-written-return", "expression": ast.unparse(value) if value else None}


def nested_returned_class(node):
    body = without_docstring(node.body)
    if not body or not isinstance(body[-1], ast.Return):
        return None
    value = body[-1].value
    if not isinstance(value, ast.Call) or not isinstance(value.func, ast.Name) or value.args or value.keywords:
        return None
    classes = [child for child in body if isinstance(child, ast.ClassDef) and child.name == value.func.id]
    if len(classes) != 1 or classes[0].decorator_list:
        return None
    cls = classes[0]
    class_counts = {}
    for statement in body:
        bound, dynamic = module_bindings(ast.Module(body=[statement], type_ignores=[]))
        if dynamic:
            return None
        for name in bound:
            class_counts[name] = class_counts.get(name,0)+1
    if class_counts.get(cls.name) != 1:
        return None
    method_counts = {}
    for statement in cls.body:
        bound, dynamic = module_bindings(ast.Module(body=[statement], type_ignores=[]))
        if dynamic:
            return None
        for name in bound:
            method_counts[name] = method_counts.get(name,0)+1
    methods = {}
    for child in cls.body:
        if isinstance(child, ast.FunctionDef) and not child.decorator_list:
            if child.name in methods or method_counts.get(child.name) != 1:
                return None
            methods[child.name] = {"first_line":child.lineno,"last_line":child.end_lineno,
                                   "signature":signature(child),"return":return_shape(child)}
    if any(isinstance(child, ast.Attribute) and isinstance(child.ctx,(ast.Store,ast.Del)) and isinstance(child.value,ast.Name) and child.value.id == cls.name and child.attr in methods for statement in body for child in ast.walk(statement)):
        return None
    return {"kind":"written-local-class-constructor-return","class_name":cls.name,
            "class_first_line":cls.lineno,"class_last_line":cls.end_lineno,
            "unconditional_direct_methods":methods,"written_constructor_call_not_direct_class_name_return":True,
            "runtime_class_identity_verified":False}


def observe(card, selector):
    result = {"version":VERSION,"status":"INCONCLUSIVE","source_executed":False,
              "runtime_bindings_verified":False,"owner_approved":False,
              "publication_authorized":False,"training_gold":False,"model_calls":0,"writes":0}
    try:
        card = dict(card) if type(card) is dict else card
        if sha(Path(__file__).read_bytes()) != OWN_SHA or sha(Path(retrieval.__file__).read_bytes()) != RETRIEVAL_SHA:
            raise ObservationRefused("loaded observer or retrieval implementation changed; reload required")
        if type(card) is not dict or set(card)!={"path","revision","source","sha256"}:
            raise ObservationRefused("closed source card required")
        if any(type(value) is not str for value in card.values()):
            raise ObservationRefused("source card values must be strings")
        if len(card["path"].encode()) > 1024:
            raise ObservationRefused("source path identity exceeds bound")
        retrieval.relative_path(card["path"])
        if not card["path"].endswith(".py"):
            raise ObservationRefused("Python source path required")
        if not card["revision"] or len(card["revision"].encode())>256:
            raise ObservationRefused("bounded revision identity required")
        if type(selector) is not str or len(selector)>128 or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*",selector):
            raise ObservationRefused("explicit top-level callable selector required")
        raw = card["source"].encode()
        if len(raw)>MAX_SOURCE or b"\0"in raw or sha(raw)!=card["sha256"]:
            raise ObservationRefused("source bytes or identity invalid")
        module = ast.parse(card["source"],type_comments=True)
        if sum(1 for _ in ast.walk(module))>MAX_NODES:
            raise ObservationRefused("module AST bound exceeded")
        bindings,dynamic = module_bindings(module)
        if dynamic or "*"in bindings:
            raise ObservationRefused("dynamic or wildcard module namespace requires review")
        selected = [node for node in module.body if isinstance(node,ast.FunctionDef) and node.name==selector]
        result["source_card"]={key:value for key,value in card.items() if key!="source"}
        result["selector"]=selector
        if not selected and selector not in bindings:
            result.update(status="NO_WRITTEN_MODULE_BINDING",reason="No written binding in the complete supplied module; this is never retirement evidence.")
            return result
        if len(selected)!=1:
            raise ObservationRefused("unique unconditional top-level declaration not established")
        node=selected[0]
        if getattr(node,"type_params",[]):
            raise ObservationRefused("generic type parameter scope requires separate profile")
        if node.decorator_list:
            raise ObservationRefused("decorated public contract requires separate evidence")
        unit=retrieval.python_unit(card["source"],selector)
        if len(unit["quote"].encode())>MAX_QUOTE:
            raise ObservationRefused("complete callable quote exceeds bound")
        nested_functions={child.name:{"signature":signature(child),
                                      "direct_body_return_calls":[ast.unparse(n.value)for n in child.body if isinstance(n,ast.Return) and isinstance(n.value,ast.Call)]}
                          for child in node.body if isinstance(child,ast.FunctionDef)}
        result.update(status="WRITTEN_CALLABLE_FACTS",signature=signature(node),
                      direct_return=return_shape(node),returned_local_class=nested_returned_class(node),
                      direct_nested_functions=nested_functions,
                      direct_statement_calls=[ast.unparse(n.value)for n in node.body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)],
                      module_written_binding_names=sorted(bindings),evidence=unit,
                      limitations=["Written signature, return and local-class declarations only; imports/defaults/annotations are not executed.",
                                   "Operator-supplied full source and revision, not authenticated origin or current filesystem proof.",
                                   "No arbitrary prose entailment, runtime values, inherited methods or helper binding guarantee.",
                                   "Missing declarations never authorize REMOVE. Whole-unit quotation bounds are preserved."])
    except (ValueError,TypeError,KeyError,UnicodeError,RecursionError,SyntaxError,retrieval.RetrievalRefused)as error:
        result["reason"]=str(error)
    if len(json.dumps(result,ensure_ascii=False).encode()) > 65536:
        return {"version":VERSION,"status":"INCONCLUSIVE","reason":"observer response exceeds bound","source_executed":False,"runtime_bindings_verified":False,"model_calls":0,"writes":0,"owner_approved":False,"training_gold":False}
    return result
