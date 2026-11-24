"""Bounded written Python revision signals; never a documentation decision."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import documentation_retrieval as retrieval

VERSION = "0.1.1"
MAX_SOURCE = 65536
MAX_NODES = 8192
MAX_SELECTORS = 8
MAX_QUOTES = 24576
MAX_RESPONSE = 131072
OWN_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
RETRIEVAL_SHA = retrieval.LOADED_IMPLEMENTATION_SHA256


class RevisionRefused(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def implementation():
    own = sha(Path(__file__).read_bytes())
    other = sha(Path(retrieval.__file__).read_bytes())
    workspace = sha(Path(retrieval.__file__).with_name("documentation_workspace.py").read_bytes())
    if own != OWN_SHA or other != RETRIEVAL_SHA or workspace != retrieval.LOADED_WORKSPACE_SHA256:
        raise RevisionRefused("loaded implementation changed; explicit operator reload required")
    return {"version": VERSION, "implementation_sha256": own,
            "retrieval_sha256": other, "workspace_sha256": workspace, "python_version": sys.version}


def validate_card(card):
    if type(card) is not dict or set(card) != {"revision", "path", "source", "sha256"}:
        raise RevisionRefused("strict source card required")
    if not all(type(value) is str for value in card.values()):
        raise RevisionRefused("source card values must be strings")
    retrieval.relative_path(card["path"])
    if not 1 <= len(card["revision"].encode()) <= 256:
        raise RevisionRefused("bounded explicit revision identity required")
    raw = card["source"].encode()
    if len(raw) > MAX_SOURCE or b"\0" in raw or sha(raw) != card["sha256"]:
        raise RevisionRefused("source exceeds bound or differs from source card hash")


def inspect_source(source, selectors):
    module = ast.parse(source, type_comments=True)
    nodes = list(ast.walk(module))
    if len(nodes) > MAX_NODES:
        raise RevisionRefused("AST node bound exceeded")
    result = {"module_ast_sha256": sha(ast.dump(module, include_attributes=False).encode()),
              "ast_nodes": len(nodes), "selectors": []}
    for selector in selectors:
        try:
            unit = retrieval.python_unit(source, selector)
        except (retrieval.RetrievalRefused, ValueError, SyntaxError) as error:
            result["selectors"].append({"selector": selector,
                "status": "DECLARATION_NOT_ESTABLISHED", "reason": str(error)})
            continue
        matching = [node for node in nodes
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name == selector.rsplit(".", 1)[-1]
                    and min([node.lineno] + [item.lineno for item in node.decorator_list]) == unit["first_line"]
                    and node.end_lineno == unit["last_line"]]
        if len(matching) != 1:
            raise RevisionRefused("selected physical declaration has ambiguous AST identity")
        # Use the original module AST. Dedenting a method quotation can alter
        # multiline string values and must not redefine the normalized node.
        fingerprint = sha(ast.dump(matching[0], include_attributes=False).encode())
        result["selectors"].append({"selector": selector, "status": "DECLARATION_ESTABLISHED",
                                    "declaration_ast_sha256": fingerprint, "evidence": unit})
    return result


def worker_observation(packet):
    previous, current = [inspect_source(packet[cut]["source"], packet["selectors"])
                         for cut in ("previous", "current")]
    quote_bytes = sum(len(row.get("evidence", {}).get("quote", "").encode())
                      for cut in (previous, current) for row in cut["selectors"])
    if quote_bytes > MAX_QUOTES:
        raise RevisionRefused("combined physical quotation bound exceeded")
    same_module = previous["module_ast_sha256"] == current["module_ast_sha256"]
    observations = []
    for before, after in zip(previous["selectors"], current["selectors"]):
        known = before["status"] == after["status"] == "DECLARATION_ESTABLISHED"
        same = known and before["declaration_ast_sha256"] == after["declaration_ast_sha256"]
        signal = ("IDENTICAL_WRITTEN_DECLARATION_AST" if same else
                  "DIFFERENT_WRITTEN_DECLARATION_AST" if known else "DECLARATION_COMPARISON_UNESTABLISHED")
        observations.append({"selector": before["selector"], "signal": signal,
            "enclosing_module_changed": not same_module,
            "unchanged_selection_requires_dependency_review": bool(same and not same_module),
            "previous": before, "current": after})
    return {"module_signal": "IDENTICAL_WRITTEN_MODULE_AST" if same_module else "DIFFERENT_WRITTEN_MODULE_AST",
            "previous_module_ast_sha256": previous["module_ast_sha256"],
            "current_module_ast_sha256": current["module_ast_sha256"],
            "quote_bytes": quote_bytes, "observations": observations}


def observe_revision(previous, current, selectors):
    """Compare supplied immutable strings, not current filesystem/runtime state."""
    result = {"version": VERSION, "status": "INCONCLUSIVE", "documentation_action": None,
              "source_executed": False, "runtime_bindings_verified": False,
              "owner_approved": False, "publication_authorized": False,
              "training_gold": False, "model_calls": 0, "writes": 0}
    try:
        identity = implementation()
        # Keep operation-local containers; source strings themselves are immutable.
        previous = dict(previous) if type(previous) is dict else previous
        current = dict(current) if type(current) is dict else current
        selectors = list(selectors) if type(selectors) is list else selectors
        validate_card(previous); validate_card(current)
        if (type(selectors) is not list or not 1 <= len(selectors) <= MAX_SELECTORS
                or not all(type(value) is str and retrieval.SELECTOR.fullmatch(value) for value in selectors)
                or len(set(selectors)) != len(selectors)):
            raise RevisionRefused("one to eight unique lexical selectors required")
        # The transport freezes caller dictionaries before subprocess execution.
        encoded = canonical({"previous": previous, "current": current, "selectors": selectors})
        packet = json.loads(encoded)
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--worker"],
                                   input=encoded, capture_output=True, timeout=3)
        if completed.returncode or len(completed.stdout) > MAX_RESPONSE:
            raise RevisionRefused("worker failed or exceeded its response bound")
        observed = retrieval.strict_json(completed.stdout)
        if type(observed) is not dict or set(observed) != {"status", "result"} or observed["status"] != "OBSERVED":
            raise RevisionRefused("worker did not establish bounded structural observations")
        body = observed["result"]
        expected = {"module_signal", "previous_module_ast_sha256", "current_module_ast_sha256",
                    "quote_bytes", "observations"}
        if type(body) is not dict or set(body) != expected or type(body["observations"]) is not list or len(body["observations"]) != len(selectors):
            raise RevisionRefused("worker result schema differs")
        if body["module_signal"] not in ("IDENTICAL_WRITTEN_MODULE_AST", "DIFFERENT_WRITTEN_MODULE_AST"):
            raise RevisionRefused("unknown module signal")
        for key in ("previous_module_ast_sha256", "current_module_ast_sha256"):
            if type(body[key]) is not str or not retrieval.HASH.fullmatch(body[key]):
                raise RevisionRefused("invalid normalized module digest")
        same_module = body["previous_module_ast_sha256"] == body["current_module_ast_sha256"]
        if same_module != (body["module_signal"] == "IDENTICAL_WRITTEN_MODULE_AST"):
            raise RevisionRefused("inconsistent normalized module identity")
        total = 0
        for selector, row in zip(selectors, body["observations"]):
            if type(row) is not dict or set(row) != {"selector", "signal", "enclosing_module_changed", "unchanged_selection_requires_dependency_review", "previous", "current"} or row["selector"] != selector:
                raise RevisionRefused("invalid selector observation")
            established = []
            for cut in ("previous", "current"):
                item = row[cut]
                if type(item) is not dict or item.get("selector") != selector:
                    raise RevisionRefused("worker selector identity differs")
                if item.get("status") == "DECLARATION_ESTABLISHED":
                    if set(item) != {"selector", "status", "declaration_ast_sha256", "evidence"} or not retrieval.HASH.fullmatch(item["declaration_ast_sha256"]):
                        raise RevisionRefused("invalid declaration identity")
                    retrieval.validate_unit(item["evidence"], packet[cut]["source"].encode(), selector, "python")
                    total += len(item["evidence"]["quote"].encode()); established.append(True)
                elif item.get("status") == "DECLARATION_NOT_ESTABLISHED":
                    if set(item) != {"selector", "status", "reason"} or type(item["reason"]) is not str:
                        raise RevisionRefused("invalid unknown declaration")
                    established.append(False)
                else:
                    raise RevisionRefused("unknown declaration status")
            known = all(established)
            same = known and row["previous"]["declaration_ast_sha256"] == row["current"]["declaration_ast_sha256"]
            expected_signal = ("IDENTICAL_WRITTEN_DECLARATION_AST" if same else
                               "DIFFERENT_WRITTEN_DECLARATION_AST" if known else "DECLARATION_COMPARISON_UNESTABLISHED")
            if (row["signal"] != expected_signal or type(row["enclosing_module_changed"]) is not bool
                    or row["enclosing_module_changed"] != (not same_module)
                    or type(row["unchanged_selection_requires_dependency_review"]) is not bool
                    or row["unchanged_selection_requires_dependency_review"] != bool(same and not same_module)):
                raise RevisionRefused("inconsistent declaration signal")
        if type(body["quote_bytes"]) is not int or body["quote_bytes"] != total or total > MAX_QUOTES:
            raise RevisionRefused("invalid quotation accounting")
        if implementation() != identity:
            raise RevisionRefused("implementation changed during observation")
        result.update(status="STRUCTURAL_REVISION_OBSERVATIONS", implementation=identity,
                      source_cards={cut: {key: value for key, value in packet[cut].items() if key != "source"}
                                    for cut in ("previous", "current")},
                      observations=body, evidence_key=sha(encoded + canonical(identity)),
                      limitations=["Written AST equality is not runtime behavior, dependency completeness or permission to skip a document review.",
                                   "Source cards are operator-supplied snapshots, not proof of current filesystem state or authenticated repository origin.",
                                   "Missing or ambiguous selection is never retirement evidence. No documentation action is chosen."])
    except (RevisionRefused, retrieval.RetrievalRefused, ValueError, TypeError, OSError,
            UnicodeError, RecursionError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        result["reason"] = str(error)
    return result


def worker():
    try:
        raw = sys.stdin.buffer.read(300000)
        if len(raw) >= 300000:
            raise RevisionRefused("worker packet bound exceeded")
        packet = retrieval.strict_json(raw)
        if type(packet) is not dict or set(packet) != {"previous", "current", "selectors"}:
            raise RevisionRefused("invalid worker packet")
        validate_card(packet["previous"]); validate_card(packet["current"])
        selectors = packet["selectors"]
        if type(selectors) is not list or not 1 <= len(selectors) <= MAX_SELECTORS or not all(type(s) is str and retrieval.SELECTOR.fullmatch(s) for s in selectors) or len(set(selectors)) != len(selectors):
            raise RevisionRefused("invalid worker selectors")
        encoded = canonical({"status": "OBSERVED", "result": worker_observation(packet)})
        if len(encoded) > MAX_RESPONSE:
            raise RevisionRefused("worker response bound exceeded")
        sys.stdout.buffer.write(encoded)
    except (RevisionRefused, retrieval.RetrievalRefused, ValueError, TypeError,
            SyntaxError, RecursionError, UnicodeError) as error:
        sys.stdout.buffer.write(canonical({"status": "INCONCLUSIVE", "reason": str(error)}))


if __name__ == "__main__":
    if sys.argv[1:] != ["--worker"]:
        raise SystemExit("Memory API only; worker accepts supplied source text, not file paths.")
    worker()
