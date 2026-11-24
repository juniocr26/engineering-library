"""Opt-in operator-bound JavaScript AST observer; never selected by packet data.

The caller supplies a trusted executable argument vector and a verified runtime
identity. No shell, automatic container discovery or source execution is used.
The default lifecycle command does not enable this observer.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

from documentation_lifecycle import MAX_SOURCE, Unsupported


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class JavaScriptObserver:
    def __init__(self, command, *, parser_sha256, parser_version, node_version, timeout=20):
        if not isinstance(command, (list, tuple)) or not command or not all(
            isinstance(item, str) and item and "\x00" not in item for item in command
        ):
            raise ValueError("trusted operator command must be an argument vector")
        if not re.fullmatch(r"[0-9a-f]{64}", parser_sha256):
            raise ValueError("verified parser checksum required")
        if type(timeout) not in (int, float) or not 0 < timeout <= 60:
            raise ValueError("observer deadline must be at most 60 seconds")
        self.command = tuple(command)
        self.parser_sha256 = parser_sha256
        self.parser_version = parser_version
        self.node_version = node_version
        self.timeout = timeout
        self.producer_sha256 = sha(Path(__file__).with_name("javascript_contract_facts.cjs").read_bytes())

    def __call__(self, source):
        if not isinstance(source, str) or "\x00" in source or len(source.encode()) > MAX_SOURCE:
            raise Unsupported("invalid or oversized JavaScript source")
        result = subprocess.run(
            self.command, input=json.dumps({"source": source, "source_path": "selected.js"}).encode(),
            capture_output=True, timeout=self.timeout, shell=False,
        )
        if result.returncode or len(result.stdout) > 256 * 1024:
            raise Unsupported("JavaScript observer refused or exceeded output bound")
        try:
            packet = json.loads(result.stdout)
        except (ValueError, UnicodeError) as error:
            raise Unsupported("invalid observer JSON") from error
        self.validate(packet, source)
        return packet

    def validate(self, packet, source):
        raw = source.encode()
        expected = {
            "version": "0.1.0", "code_sha256": self.producer_sha256,
            "parser_sha256": self.parser_sha256, "parser_version": self.parser_version,
            "node_version": self.node_version,
        }
        fields = {"profile", "source_sha256", "source_bytes", "source_path", "functions", "registries", "syntax_only", "source_executed", "runtime_bindings_verified", "limitations", "producer"}
        if not isinstance(packet, dict) or set(packet) != fields or packet.get("producer") != expected:
            raise Unsupported("JavaScript producer/runtime identity mismatch")
        if (
            packet.get("profile") != "javascript-bounded-written-field-map-v1"
            or packet.get("source_sha256") != sha(raw)
            or packet.get("source_bytes") != len(raw)
            or type(packet.get("source_bytes")) is not int
            or packet.get("source_path") != "selected.js"
            or packet.get("syntax_only") is not True
            or packet.get("source_executed") is not False
            or packet.get("runtime_bindings_verified") is not False
            or packet.get("registries") != {}
        ):
            raise Unsupported("JavaScript source provenance mismatch")
        functions = packet.get("functions")
        if not isinstance(functions, dict) or len(functions) > 16:
            raise Unsupported("invalid JavaScript contract inventory")
        for selector, unit in functions.items():
            if not isinstance(unit, dict) or not re.fullmatch(
                r"[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)?", selector
            ):
                raise Unsupported("invalid lexical selector")
            kind = "lexical-instance-method" if "." in selector else "exported-function"
            if unit.get("declaration_kind") != kind:
                raise Unsupported("declaration kind differs from lexical selector")
            start, end = unit.get("quote_byte_start"), unit.get("quote_byte_end")
            quote = unit.get("quote")
            if (
                type(start) is not int or type(end) is not int
                or not 0 <= start < end <= len(raw) or end - start > 6144
                or not isinstance(quote, str) or raw[start:end] != quote.encode()
                or unit.get("quote_sha256") != sha(quote.encode())
                or unit.get("lexical_selector") != selector
                or unit.get("receiver_binding_verified") is not False
            ):
                raise Unsupported("JavaScript quote/ownership mismatch")
            fact = unit.get("fact")
            if not isinstance(fact, dict) or not isinstance(fact.get("behavior"), dict):
                raise Unsupported("invalid JavaScript fact shape")
            signature = fact.get("signature")
            if not isinstance(signature, dict) or set(signature) != {"posonly", "positional", "keyword_only", "vararg", "kwarg", "defaults", "keyword_defaults"}:
                raise Unsupported("invalid JavaScript signature")
            positional = signature["positional"]
            if not isinstance(positional, list) or len(positional) != 1 or not isinstance(positional[0], str) or not re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", positional[0]):
                raise Unsupported("invalid positional input")
            if any(signature[key] != [] for key in ("posonly", "keyword_only", "defaults", "keyword_defaults")) or signature["vararg"] is not None or signature["kwarg"] is not None:
                raise Unsupported("unsupported JavaScript signature")
            behavior = fact["behavior"]
            mapping = behavior.get("mapping")
            if behavior.get("kind") != "written-object-field-map" or not isinstance(mapping, dict) or not 1 <= len(mapping) <= 8:
                raise Unsupported("invalid written mapping")
            for output, value in mapping.items():
                if not isinstance(output, str) or not re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", output) or output == "__proto__":
                    raise Unsupported("invalid output property")
                if not isinstance(value, dict) or set(value) != {"parameter_index", "property"} or type(value["parameter_index"]) is not int or value["parameter_index"] != 0:
                    raise Unsupported("invalid input parameter identity")
                if not isinstance(value["property"], str) or not re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", value["property"]):
                    raise Unsupported("invalid input property")
