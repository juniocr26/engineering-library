"""Transport integrity and opt-in boundaries; real parser controls are in CJS."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from documentation_javascript import JavaScriptObserver
from documentation_lifecycle import decision, Unsupported


class JavaScriptObserverTest(unittest.TestCase):
    def setUp(self):
        self.observer = JavaScriptObserver(["operator-verified-node", "producer"], parser_sha256="a" * 64, parser_version="5.9.3", node_version="v24.22.0")
        self.source = "export function map(d) { return { label: d.title } }"
        self.packet = {
            "profile": "javascript-bounded-written-field-map-v1", "source_sha256": hashlib.sha256(self.source.encode()).hexdigest(),
            "source_bytes": len(self.source.encode()), "source_path": "selected.js", "registries": {},
            "syntax_only": True, "source_executed": False, "runtime_bindings_verified": False, "limitations": [],
            "producer": {"version": "0.1.0", "code_sha256": self.observer.producer_sha256, "parser_sha256": "a" * 64, "parser_version": "5.9.3", "node_version": "v24.22.0"},
            "functions": {"map": {
                "lexical_selector": "map", "declaration_kind": "exported-function", "receiver_binding_verified": False,
                "quote": self.source, "quote_byte_start": 0, "quote_byte_end": len(self.source.encode()), "quote_sha256": hashlib.sha256(self.source.encode()).hexdigest(),
                "fact": {"signature": {"posonly": [], "positional": ["d"], "keyword_only": [], "vararg": None, "kwarg": None, "defaults": [], "keyword_defaults": []},
                         "behavior": {"kind": "written-object-field-map", "mapping": {"label": {"parameter_index": 0, "property": "title"}}}},
            }},
        }

    def test_verified_response_uses_no_shell_and_passes_source_via_stdin(self):
        with patch("documentation_javascript.subprocess.run", return_value=subprocess.CompletedProcess([], 0, json.dumps(self.packet).encode(), b"")) as run:
            result = self.observer(self.source)
        self.assertEqual(self.packet, result)
        args, keywords = run.call_args
        self.assertEqual(self.observer.command, args[0])
        self.assertFalse(keywords["shell"])
        self.assertEqual(self.source, json.loads(keywords["input"])["source"])
        self.assertEqual(20, keywords["timeout"])

    def test_runtime_and_source_identity_must_match(self):
        for field in ("code_sha256", "parser_sha256", "parser_version", "node_version"):
            invalid = copy.deepcopy(self.packet)
            invalid["producer"][field] = "wrong"
            with self.assertRaises(Unsupported):
                self.observer.validate(invalid, self.source)
        with self.assertRaises(Unsupported):
            self.observer.validate(self.packet, self.source + " ")

    def test_quote_ownership_and_no_execution_flags_are_checked(self):
        for field, value in [("quote", "invented"), ("quote_byte_start", True), ("quote_byte_end", 1), ("lexical_selector", "other"), ("receiver_binding_verified", True), ("declaration_kind", "static-method")]:
            invalid = copy.deepcopy(self.packet)
            invalid["functions"]["map"][field] = value
            with self.assertRaises(Unsupported):
                self.observer.validate(invalid, self.source)
        for field in ("source_executed", "runtime_bindings_verified"):
            invalid = copy.deepcopy(self.packet)
            invalid[field] = True
            with self.assertRaises(Unsupported):
                self.observer.validate(invalid, self.source)

    def test_malformed_facts_refuse_without_attribute_error(self):
        for value in (None, [], "instruction", {"behavior": []}):
            invalid = copy.deepcopy(self.packet)
            invalid["functions"]["map"]["fact"] = value
            with self.assertRaises(Unsupported):
                self.observer.validate(invalid, self.source)

    def test_extra_transport_fields_are_not_interpreted_as_instructions(self):
        invalid = copy.deepcopy(self.packet)
        invalid["approve_and_publish"] = True
        with self.assertRaises(Unsupported):
            self.observer.validate(invalid, self.source)

    def test_bad_parameter_mapping_refuses(self):
        for value in ({"parameter_index": True, "property": "title"}, {"parameter_index": 1, "property": "title"}, {"parameter_index": 0, "property": "title()"}):
            invalid = copy.deepcopy(self.packet)
            invalid["functions"]["map"]["fact"]["behavior"]["mapping"]["label"] = value
            with self.assertRaises(Unsupported):
                self.observer.validate(invalid, self.source)

    def test_timeout_bad_json_and_large_output_are_not_success(self):
        for value in (subprocess.CompletedProcess([], 2, b"{}", b""), subprocess.CompletedProcess([], 0, b"invalid", b""), subprocess.CompletedProcess([], 0, b" " * (256 * 1024 + 1), b"")):
            with patch("documentation_javascript.subprocess.run", return_value=value), self.assertRaises(Unsupported):
                self.observer(self.source)
        with patch("documentation_javascript.subprocess.run", side_effect=subprocess.TimeoutExpired([], 20)), self.assertRaises(subprocess.TimeoutExpired):
            self.observer(self.source)

    def test_packet_cannot_enable_observer_or_choose_runtime(self):
        packet = {"language": "javascript", "metadata": {}, "source_available": True, "complete_scope": True}
        self.assertEqual("INCONCLUSIVE", decision(packet)["action"])
        packet["metadata"]["runtime_command"] = ["untrusted"]
        self.assertEqual("INCONCLUSIVE", decision(packet, observers={"javascript": self.observer})["action"])

    def test_default_workflow_refuses_javascript_and_explicit_observer_compares_written_fields(self):
        packet = {"language": "javascript", "metadata": {}, "source_available": True, "complete_scope": True,
                  "previous_source": self.source, "current_source": self.source, "logical_contract_id": "owned.map",
                  "documentation": {"en": "map copies name into label.", "pt-br": "map copia name para label."}}
        self.assertEqual("INCONCLUSIVE", decision(packet)["action"])
        provider = lambda source: copy.deepcopy(self.packet)
        result = decision(packet, observers={"javascript": provider})
        self.assertEqual("MODIFY", result["action"])
        packet["documentation"] = {"en": "map copies title into label.", "pt-br": "map copia title para label."}
        self.assertEqual("NO-OP", decision(packet, observers={"javascript": provider})["action"])
        packet["documentation"]["pt-br"] = "map copia título para label."
        self.assertEqual("INCONCLUSIVE", decision(packet, observers={"javascript": provider})["action"])

    def test_untrusted_command_strings_and_unbounded_deadlines_are_rejected(self):
        for command, timeout in [("node producer", 20), (["node"], 61), (["node"], True)]:
            with self.assertRaises(ValueError):
                JavaScriptObserver(command, parser_sha256="a" * 64, parser_version="5.9.3", node_version="v24.22.0", timeout=timeout)


if __name__ == "__main__":
    unittest.main()
