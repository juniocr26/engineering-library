"""H74 owned literal-function identity experiment; no source execution or removal action."""
import ast
import copy
import hashlib
import json
from pathlib import PurePosixPath


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def declarations(filemap):
    result = []
    for path, source in filemap.items():
        posix = PurePosixPath(path)
        if posix.is_absolute() or ".." in posix.parts or not path.endswith(".py"):
            raise ValueError("unsupported path")
        for node in ast.parse(source).body:
            if not isinstance(node, ast.FunctionDef) or node.decorator_list or node.returns or node.type_params:
                raise ValueError("unsupported declaration or module statement")
            args = node.args
            if args.posonlyargs or args.args or args.kwonlyargs or args.vararg or args.kwarg or args.defaults:
                raise ValueError("unsupported function signature")
            if len(node.body) != 1 or not isinstance(node.body[0], ast.Return):
                raise ValueError("unsupported body")
            value = node.body[0].value
            if not isinstance(value, ast.Constant) or type(value.value) is not int:
                raise ValueError("unsupported return")
            normalized = copy.deepcopy(node)
            normalized.name = "_identity_"
            result.append((path, node.name, ast.dump(node, include_attributes=False), ast.dump(normalized, include_attributes=False)))
    return result


def observe(packet, trusted):
    if trusted.get("complete_acquisition") is not True:
        return "INCONCLUSIVE"
    for phase in ("before", "after"):
        if digest(packet[phase]) != trusted[phase + "_digest"]:
            return "INCONCLUSIVE"
    try:
        before, after = declarations(packet["before"]), declarations(packet["after"])
        path, name = packet["selector"].rsplit(":", 1)
        selected = [r for r in before if r[:2] == (path, name)]
        if len(selected) != 1:
            return "INCONCLUSIVE"
        target = selected[0]
        exact = [r for r in after if r[2] == target[2]]
        renamed = [r for r in after if r[3] == target[3]]
        if len(exact) > 1 or len(renamed) > 1:
            return "INCONCLUSIVE"
        if exact:
            return "UNCHANGED_IDENTITY" if exact[0][:2] == target[:2] else "CONTINUING_IDENTITY"
        if renamed:
            return "POSSIBLE_RENAMED_CONTINUITY"
        retirement = trusted.get("retirement")
        if retirement and retirement.get("selector") == packet["selector"] and retirement.get("reason"):
            return "DECLARED_RETIREMENT_CORROBORATED"
        return "ABSENCE_NOT_RETIREMENT"
    except (SyntaxError, ValueError, TypeError, KeyError, AttributeError):
        return "INCONCLUSIVE"
