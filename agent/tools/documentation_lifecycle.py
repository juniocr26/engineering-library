#!/usr/bin/env python3
"""Experimental read-only recommendations from bounded, explicit source packets.

This is a source/claim protocol for isolated development, not a general semantic
analyzer, owner approval engine or replacement for the Ruby documentation writer.
"""
import argparse
import ast
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

VERSION = "0.3.6"
ACTIONS = ("ADD", "MODIFY", "REMOVE", "NO-OP", "INCONCLUSIVE")
MAX_PACKET = 256 * 1024
MAX_SOURCE = 64 * 1024
TOP_KEYS = {
    "id", "family", "language", "previous_source", "current_source",
    "documentation", "complete_scope", "source_available",
    "positive_retirement_evidence", "logical_contract_id", "metadata",
}
META_KEYS = {
    "renamed_to", "previous_path", "current_path", "document_kind",
    "conflicting_history", "human_authored", "managed_ownership",
    "admitted_contract_question",
    "selector",
}


class Unsupported(ValueError):
    """Missing proof is a refusal, not a reason to force a documentation edit."""


def read_packet(path):
    """Admit one stable bounded regular file; never block opening a FIFO."""
    if not all(hasattr(os, name) for name in ("O_NOFOLLOW", "O_NONBLOCK")):
        raise Unsupported("safe packet file admission unavailable on this platform")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_PACKET:
            raise Unsupported("packet must be a bounded regular file")
        chunks, size = [], 0
        while True:
            chunk = os.read(descriptor, min(65536, MAX_PACKET + 1 - size))
            if not chunk:
                break
            chunks.append(chunk); size += len(chunk)
            if size > MAX_PACKET:
                raise Unsupported("packet grew beyond byte bound")
        after = os.fstat(descriptor)
        fields = lambda value: (value.st_dev, value.st_ino, value.st_size,
                                value.st_mtime_ns, value.st_ctime_ns)
        if fields(before) != fields(after) or size != after.st_size:
            raise Unsupported("packet changed while reading")
        named = os.stat(path, follow_symlinks=False)
        if not stat.S_ISREG(named.st_mode) or fields(named) != fields(after):
            raise Unsupported("packet path changed while reading")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def parse_packet_json(raw):
    """Reject lexical ambiguity before constructing a typed decision packet."""
    if not isinstance(raw, bytes) or len(raw) > MAX_PACKET:
        raise Unsupported("bounded UTF-8 packet bytes required")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise Unsupported("duplicate JSON field: " + repr(key[:80]))
            result[key] = value
        return result
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(Unsupported("nonfinite JSON value")))
    if not isinstance(value, dict):
        raise Unsupported("JSON object packet required")
    pending, count = [(value, 0)], 0
    while pending:
        item, depth = pending.pop(); count += 1
        if depth > 64 or count > 8192:
            raise Unsupported("JSON structure bound exceeded")
        if isinstance(item, str):
            item.encode("utf-8")  # Refuse unpaired surrogate code points.
        elif isinstance(item, float) and not math.isfinite(item):
            raise Unsupported("nonfinite decoded JSON number")
        elif isinstance(item, dict):
            pending.extend((entry, depth+1) for pair in item.items() for entry in pair)
        elif isinstance(item, list):
            pending.extend((entry, depth+1) for entry in item)
    return value


def digest(data):
    return hashlib.sha256(data).hexdigest()


def declared_source_path(value):
    """Validate a canonical operator-declared repository-relative identity.

    This does not read the path or prove that it exists in a Git revision.
    """
    if not isinstance(value, str) or not value or len(value) > 1024:
        raise Unsupported("missing or invalid declared source path")
    parts = value.split("/")
    if any(part in ("", ".", "..") or not re.fullmatch(r"[A-Za-z0-9_.-]+", part)
           for part in parts):
        raise Unsupported("source path must be a canonical repository-relative identity")
    return value


def literal(node):
    if not isinstance(node, (ast.Constant, ast.UnaryOp)):
        raise Unsupported("literal value not supplied")
    value = ast.literal_eval(node)
    if type(value) not in (str, int, float, bool, type(None)):
        raise Unsupported("unsupported literal type")
    if isinstance(value, float) and not math.isfinite(value):
        raise Unsupported("nonfinite literal")
    if len(json.dumps(value, ensure_ascii=False).encode()) > 2048:
        raise Unsupported("literal exceeds bound")
    return {"type": type(value).__name__, "value": value}


def function_fact(node):
    if not isinstance(node, ast.FunctionDef) or node.decorator_list or getattr(node, "type_params", []):
        raise Unsupported("async/decorated function requires separate evidence")
    args = node.args
    all_args = [*args.posonlyargs, *args.args, *args.kwonlyargs]
    annotated_args = all_args + ([args.vararg] if args.vararg else []) + ([args.kwarg] if args.kwarg else [])
    parameter_names = [arg.arg for arg in annotated_args]
    if len(parameter_names) != len(set(parameter_names)):
        raise Unsupported("duplicate parameter ownership")
    if node.returns or any(arg.annotation for arg in annotated_args):
        raise Unsupported("annotation contract outside first profile")
    signature = {
        "posonly": [arg.arg for arg in args.posonlyargs],
        "positional": [arg.arg for arg in args.args],
        "keyword_only": [arg.arg for arg in args.kwonlyargs],
        "vararg": args.vararg.arg if args.vararg else None,
        "kwarg": args.kwarg.arg if args.kwarg else None,
        "defaults": [literal(value) for value in args.defaults],
        "keyword_defaults": [
            None if value is None else literal(value)
            for value in args.kw_defaults
        ],
    }
    body = list(node.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(
        body[0].value, ast.Constant
    ) and isinstance(body[0].value.value, str):
        body = body[1:]
    parameters = {arg.arg for arg in all_args}
    if len(body) == 1 and isinstance(body[0], ast.Return):
        value = body[0].value
        if isinstance(value, ast.Name) and value.id in parameters:
            behavior = {"kind": "parameter-return", "name": value.id}
        else:
            behavior = {"kind": "literal-return", "literal": literal(value)}
    elif (
        len(body) == 2 and isinstance(body[0], ast.Assign)
        and len(body[0].targets) == 1
        and isinstance(body[0].targets[0], ast.Name)
        and isinstance(body[1], ast.Return)
        and isinstance(body[1].value, ast.Name)
        and body[0].targets[0].id == body[1].value.id
    ):
        behavior = {
            "kind": "literal-return", "literal": literal(body[0].value),
        }
    elif len(body) == 1 and isinstance(body[0], ast.Raise):
        # Written expression only: no exception constructor/binding execution.
        if body[0].exc is None or body[0].cause is not None:
            raise Unsupported("unsupported raise form")
        behavior = {
            "kind": "written-raise",
            "expression": ast.dump(body[0].exc, include_attributes=False),
        }
    else:
        raise Unsupported("function body outside admitted literal/return profile")
    return {"signature": signature, "behavior": behavior}


def observe_python(text):
    if not isinstance(text, str) or "\x00" in text:
        raise Unsupported("missing or invalid source text")
    raw = text.encode("utf-8")
    if len(raw) > MAX_SOURCE:
        raise Unsupported("source exceeds bound")
    module = ast.parse(text)
    functions, registries = {}, {}
    lines = re.findall(r"[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+$", text)
    for node in module.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in functions or node.name in registries:
                raise Unsupported("duplicate function ownership")
            quote = "".join(lines[node.lineno - 1:node.end_lineno])
            if len(quote.encode()) > 6144:
                raise Unsupported("complete Python callable exceeds quote bound")
            functions[node.name] = {
                "fact": function_fact(node),
                "first_line": node.lineno, "last_line": node.end_lineno,
                "quote": quote, "quote_sha256": digest(quote.encode()),
            }
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if not isinstance(target, ast.Name) or target.id not in {
                "RETIRED_CONTRACTS", "CONTRACT_ALIASES", "OPTIONS",
            }:
                raise Unsupported("unreviewed module binding")
            if target.id in registries or target.id in functions or not isinstance(node.value, ast.Dict):
                raise Unsupported("duplicate or dynamic registry")
            keys = [literal(key)["value"] for key in node.value.keys]
            values = [literal(value)["value"] for value in node.value.values]
            if any(not isinstance(key, str) for key in keys) or len(set(keys)) != len(keys):
                raise Unsupported("non-string or duplicate registry keys")
            registries[target.id] = dict(zip(keys, values))
        elif isinstance(node, ast.Pass):
            continue
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        else:
            raise Unsupported("conditional/imported/dynamic module scope")
    return {
        "profile": "python-bounded-written-contract-v1",
        "source_sha256": digest(raw), "source_bytes": len(raw),
        "functions": functions, "registries": registries,
        "source_executed": False, "runtime_bindings_verified": False,
    }


def observe_go(text):
    """Admit one parser-verified written integer-return layout, not Go bindings."""
    if not isinstance(text, str) or "\x00" in text or len(text.encode()) > MAX_SOURCE:
        raise Unsupported("missing, invalid or oversized Go source")
    match = re.fullmatch(
        r"\s*package\s+([A-Za-z_]\w*)\s*;?\s+"
        r"func\s+([A-Za-z_]\w*)\s*\(\s*\)\s+int\s*\{([^{}]*)\}\s*",
        text,
    )
    if not match or match[2] in ("int", "init", "_"):
        raise Unsupported("Go module outside closed written-literal layout")
    name, body = match[2], match[3]
    direct = re.fullmatch(r"\s*return\s+(-?(?:0|[1-9][0-9]*))\s*;?\s*", body)
    local = re.fullmatch(
        r"\s*([A-Za-z_]\w*)\s*:=\s*(-?(?:0|[1-9][0-9]*))"
        r"\s*(?:;|\n)\s*return\s+([A-Za-z_]\w*)\s*;?\s*", body,
    )
    if direct:
        value = int(direct[1])
    elif local and local[1] == local[3] and local[1] != "_":
        value = int(local[2])
    else:
        raise Unsupported("Go return/dependency outside admitted layout")
    if not -(2 ** 31) <= value < 2 ** 31:
        raise Unsupported("Go literal exceeds conservative integer bound")
    request = json.dumps({"source": text, "path": "selected.go", "selectors": [name]}).encode()
    producer = Path(__file__).with_name("go_source_ast.py")
    result = subprocess.run(
        [sys.executable, str(producer)], input=request,
        capture_output=True, timeout=20,
    )
    if result.returncode:
        raise Unsupported("verified Go producer refused selected source")
    packet = json.loads(result.stdout)
    if (
        packet.get("source_sha256") != digest(text.encode())
        or packet.get("syntax_only") is not True
        or packet.get("source_executed") is not False
        or len(packet.get("units", [])) != 1
    ):
        raise Unsupported("Go producer provenance mismatch")
    unit = packet["units"][0]
    if unit.get("selector") != name or unit.get("declaration_kind") != "function":
        raise Unsupported("Go declaration identity mismatch")
    return {
        "profile": "go-bounded-written-integer-return-v1",
        "source_sha256": packet["source_sha256"], "source_bytes": len(text.encode()),
        "functions": {name: {
            "fact": {
                "signature": {"posonly": [], "positional": [], "keyword_only": [],
                              "vararg": None, "kwarg": None, "defaults": [],
                              "keyword_defaults": []},
                "behavior": {"kind": "literal-return",
                             "literal": {"type": "int", "value": value}},
            },
            "first_line": unit["start_line"], "last_line": unit["end_line"],
            "quote": unit["quote"], "quote_sha256": digest(unit["quote"].encode()),
        }},
        "registries": {}, "producer": packet["producer"],
        "source_executed": False, "runtime_bindings_verified": False,
        "scope_limit": "One complete declared fixture file; no package/build/type or runtime binding proof.",
    }


def claim(text, language):
    """Closed fixture claim grammar; arbitrary prose never becomes trusted facts."""
    if not isinstance(text, str):
        raise Unsupported("invalid documentation text")
    symbol = r"([A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)?)"
    mapping_pattern = symbol + (
        r" copies ([A-Za-z_$][A-Za-z0-9_$]*) into ([A-Za-z_$][A-Za-z0-9_$]*)\."
        if language == "en" else
        r" copia ([A-Za-z_$][A-Za-z0-9_$]*) para ([A-Za-z_$][A-Za-z0-9_$]*)\."
    )
    match = re.fullmatch(mapping_pattern, text)
    if match:
        return {"kind": "field-map", "symbol": match[1], "input": match[2], "output": match[3]}
    pattern = r"([A-Za-z_]\w*) " + (
        r"returns\s*(-?\d+)\." if language == "en" else r"retorna\s*(-?\d+)\."
    )
    match = re.fullmatch(pattern, text)
    if match:
        return {"kind": "return", "symbol": match[1], "value": int(match[2])}
    if language == "en":
        match = re.fullmatch(r"FAQ: Does ([A-Za-z_]\w*) return\s*(-?\d+)\? Yes\.", text)
    else:
        match = re.fullmatch(r"FAQ: ([A-Za-z_]\w*) retorna\s*(-?\d+)\? Sim\.", text)
    if match:
        return {"kind": "return", "symbol": match[1], "value": int(match[2])}
    # A visible delimiter keeps trailing digits in a parameter identifier from
    # being silently consumed as part of the numeric default.
    pattern = (
        r"([A-Za-z_]\w*) uses default ([A-Za-z_]\w*)\s*=\s*(-?\d+)\."
        if language == "en" else
        r"([A-Za-z_]\w*) usa ([A-Za-z_]\w*)\s*=\s*(-?\d+) como padrão\."
    )
    match = re.fullmatch(pattern, text)
    if match:
        return {"kind": "default", "symbol": match[1], "parameter": match[2], "value": int(match[3])}
    pattern = (
        r"([A-Za-z_]\w*) uses default ([A-Za-z_]\w*?)(-?\d+)\."
        if language == "en" else
        r"([A-Za-z_]\w*) usa ([A-Za-z_]\w*?)(-?\d+) como padrão\."
    )
    match = re.fullmatch(pattern, text)
    if match:
        return {"kind": "default", "symbol": match[1], "parameter": match[2],
                "value": int(match[3]), "legacy_concatenation": match[2] + match[3]}
    pattern = (
        r"See ([a-zA-Z0-9_./-]+) for ([A-Za-z_]\w*)\."
        if language == "en" else
        r"Consulte ([a-zA-Z0-9_./-]+) para ([A-Za-z_]\w*)\."
    )
    match = re.fullmatch(pattern, text)
    if match:
        return {"kind": "source-link", "path": match[1], "symbol": match[2]}
    raise Unsupported("documentation needs an explicit claim mapping or human review")


def decision(packet, *, observers=None):
    output = {
        "profile": "bounded-documentation-lifecycle-v2", "version": VERSION,
        "action": "INCONCLUSIVE", "technical_recommendation": True,
        "owner_approved": False, "publication_authorized": False,
        "training_gold": False, "source_executed": False,
        "writes": 0, "model_calls": 0, "evidence": {},
        "limitations": [
            "Closed Python/Go development source/claim protocol, not arbitrary prose comprehension.",
            "Scope and paths are fixture-declared; no Git tree or repository-wide completeness proof.",
            "A recommendation does not authorize applying a change to human content.",
        ],
    }

    def finish(action, reason):
        output.update(action=action, reason=reason)
        metadata = packet.get("metadata", {}) if isinstance(packet, dict) else {}
        if not isinstance(metadata, dict):
            metadata = {}
        output["candidate_application"] = (
            "HUMAN_ALIGNMENT_REQUIRED"
            if metadata.get("human_authored") or metadata.get("managed_ownership") is False
            else "ISOLATED_REVIEW_CANDIDATE_ONLY"
        )
        return output

    try:
        if not isinstance(packet, dict) or set(packet) - TOP_KEYS:
            raise Unsupported("invalid or unknown packet fields")
        packet = copy.deepcopy(packet)
        observers = dict(observers) if isinstance(observers, dict) else observers
        if len(json.dumps(packet, ensure_ascii=False, allow_nan=False).encode()) > MAX_PACKET:
            raise Unsupported("packet exceeds byte bound")
        metadata = packet.get("metadata")
        if not isinstance(metadata, dict) or set(metadata) - META_KEYS:
            raise Unsupported("unknown metadata fields")
        if packet.get("source_available") is not True:
            raise Unsupported("current source unavailable")
        if packet.get("complete_scope") is not True:
            raise Unsupported("incomplete declared source scope")
        if metadata.get("conflicting_history"):
            raise Unsupported("conflicting documentation authority")
        providers = {"python": observe_python, "go": observe_go}
        # Optional call-site configuration is trusted operator code, never packet data.
        if observers is not None:
            if not isinstance(observers, dict) or set(observers) - {"javascript"} or not all(callable(value) for value in observers.values()):
                raise Unsupported("invalid operator observer configuration")
            providers.update(observers)
        provider = providers.get(packet.get("language"))
        if provider is None:
            raise Unsupported("language outside first admitted provider")
        previous = provider(packet.get("previous_source"))
        current = provider(packet.get("current_source"))
        output["evidence"] = {"previous": previous, "current": current}
        documentation = packet.get("documentation")
        if not isinstance(documentation, dict) or set(documentation) != {"en", "pt-br"}:
            raise Unsupported("missing paired documentation")
        if not all(isinstance(value, str) for value in documentation.values()):
            raise Unsupported("invalid bilingual documentation")
        contract_id = packet.get("logical_contract_id")
        if not isinstance(contract_id, str) or not re.fullmatch(r"[a-z][a-z0-9_.-]{0,95}", contract_id):
            raise Unsupported("invalid logical contract identity")
        name = metadata.get("selector", contract_id.rsplit(".", 1)[-1])
        if not documentation["en"] and not documentation["pt-br"]:
            before = previous["functions"].get(name)
            after = current["functions"].get(name)
            if after and not before:
                return finish("ADD", "Positive current definition and complete declared previous/document scope without a claim.")
            raise Unsupported("new documentation need not established")
        if not documentation["en"] or not documentation["pt-br"]:
            raise Unsupported("one language is missing")
        en, pt = claim(documentation["en"], "en"), claim(documentation["pt-br"], "pt-br")
        if en != pt:
            raise Unsupported("bilingual claims disagree")
        if "selector" in metadata and metadata["selector"] != en["symbol"]:
            raise Unsupported("claim differs from explicit source selector")
        name = en["symbol"]
        before = previous["functions"].get(name)
        after = current["functions"].get(name)
        output["evidence"]["selected_symbol"] = name
        if not after:
            target = metadata.get("renamed_to")
            aliases = current["registries"].get("CONTRACT_ALIASES", {})
            if target and aliases.get(name) == target and target in current["functions"] and before:
                return finish("MODIFY", "Explicit identity-preserving alias and current definition; rename is not retirement.")
            retirement = packet.get("positive_retirement_evidence")
            recorded = current["registries"].get("RETIRED_CONTRACTS", {}).get(contract_id)
            required = {"contract_id", "source", "reason", "aliases_checked", "relocations_checked"}
            if (
                before and isinstance(retirement, dict) and set(retirement) == required
                and retirement["contract_id"] == contract_id
                and retirement["source"] == "current module RETIRED_CONTRACTS"
                and retirement["reason"] == recorded and isinstance(recorded, str) and recorded
                and retirement["aliases_checked"] is True
                and retirement["relocations_checked"] is True
                and name not in aliases
            ):
                return finish("REMOVE", "Positive frozen retirement declaration and complete declared scope; preserve old bytes and migration history.")
            raise Unsupported("absence is not positive retirement evidence")
        if en["symbol"] != name:
            raise Unsupported("claim symbol differs from logical contract")
        if en["kind"] == "source-link":
            current_path = declared_source_path(metadata.get("current_path"))
            previous_path = metadata.get("previous_path")
            if previous_path is not None:
                previous_path = declared_source_path(previous_path)
            if en["path"] == current_path:
                return finish("NO-OP", "Both source references already match the explicit fixture-declared current identity; preserve bytes/mtime.")
            if previous_path and en["path"] == previous_path and previous_path != current_path:
                return finish("MODIFY", "Explicit fixture-declared source relocation affects this exact reference.")
            raise Unsupported("source link target not established")
        fact = after["fact"]
        if en["kind"] == "return":
            behavior = fact["behavior"]
            matches = (
                behavior["kind"] == "literal-return"
                and behavior["literal"]["type"] == "int"
                and behavior["literal"]["value"] == en["value"]
            )
        elif en["kind"] == "field-map":
            behavior = fact["behavior"]
            matches = (
                behavior["kind"] == "written-object-field-map"
                and behavior["mapping"].get(en["output"]) == {
                    "parameter_index": 0, "property": en["input"],
                }
            )
        else:
            signature = fact["signature"]
            names = signature["posonly"] + signature["positional"]
            default_names = names[len(names) - len(signature["defaults"]):] if signature["defaults"] else []
            defaults = dict(zip(default_names, signature["defaults"]))
            defaults.update({
                name: value for name, value in zip(signature["keyword_only"], signature["keyword_defaults"])
                if value is not None
            })
            parameter_names = names + signature["keyword_only"]
            if "legacy_concatenation" in en:
                token = en["legacy_concatenation"]
                interpretations = [
                    name for name in parameter_names
                    if token.startswith(name) and re.fullmatch(r"-?\d+", token[len(name):])
                ]
                if len(interpretations) > 1:
                    raise Unsupported("ambiguous legacy default token; use an explicit parameter = value delimiter")
            if en["parameter"] not in parameter_names:
                raise Unsupported("documented parameter identity is not established")
            value = defaults.get(en["parameter"])
            # A positively declared parameter without a default is required.
            # That contradicts an optional-default claim; an absent parameter
            # remains inconclusive instead of being guessed or renamed.
            matches = value is not None and value["type"] == "int" and value["value"] == en["value"]
        return finish(
            "NO-OP" if matches else "MODIFY",
            "Current admitted fact already matches both documented claims; preserve bytes/mtime."
            if matches else
            "Current admitted written fact contradicts the exact bilingual claim; change only its managed candidate.",
        )
    except (
        Unsupported, SyntaxError, ValueError, TypeError, KeyError, RecursionError,
        UnicodeError, OSError, subprocess.SubprocessError,
    ) as error:
        return finish("INCONCLUSIVE", str(error))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        raw = read_packet(args.input)
        packet = parse_packet_json(raw)
    except (Unsupported, OSError, UnicodeError, ValueError, RecursionError) as error:
        parser.error("packet admission refused: " + str(error))
    result = decision(packet)
    result["input_sha256"] = digest(raw)
    data = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        # Explicit new artifact only; default operation is read-only stdout.
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(data)
    else:
        print(data, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
