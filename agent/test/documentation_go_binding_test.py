import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from documentation_go_binding import GoBindingObserver, POSITIVE, closed_json, sha
from documentation_lifecycle import Unsupported


class GoBindingConsumerTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.binary = Path(self.temporary.name) / "operator-executable"
        self.binary.write_bytes(b"operator-pinned-native-binary-fixture")
        self.binary_hash = sha(self.binary.read_bytes())
        self.observer = GoBindingObserver(
            self.binary, binary_sha256=self.binary_hash, go_version="go1.27.4"
        )
        self.source = "// ação 🧪\npackage p\nfunc Value() int { return max(1,2) }\n"
        self.quote = "func Value() int { return max(1,2) }"
        self.source_hash = sha(self.source.encode())
        self.request = {
            "profile": {"goos": "darwin", "goarch": "arm64", "build_tags": []},
            "module": {"source": "module example.test/owned\n\ngo 1.26.0\n", "sha256": "not-used-by-mocked-producer"},
            "package_import_path": "example.test/owned/p", "file": "selected.go",
            "function": "Value", "builtin": "max",
            "packages": [{"import_path": "example.test/owned/p", "kind": "module",
                          "files": [{"name": "selected.go", "source": self.source, "sha256": self.source_hash}]}],
        }
        self.raw = json.dumps(self.request, ensure_ascii=False, separators=(",", ":")).encode()
        start = self.source.encode().index(self.quote.encode())
        self.packet = {
            "producer": {"version": "0.1.0", "go_version": "go1.27.4", "binary_sha256": self.binary_hash},
            "input_sha256": sha(self.raw), "status": POSITIVE, "source_executed": False,
            "owner_approved": False, "runtime_bindings_verified": False, "type_checked": False,
            "publication_authorized": False, "conditional_on_supplied_complete_census": True,
            "build_profile": self.request["profile"], "profile": "go-build-filtered-predeclared-binding-v1",
            "version": "0.1.0", "function": "Value", "builtin": "max",
            "quote": self.quote, "source_sha256": self.source_hash, "quote_sha256": sha(self.quote.encode()),
            "quote_byte_start": start, "quote_byte_end": start + len(self.quote.encode()),
            "first_line": 3, "last_line": 3, "proof_fingerprint": "a"*64,
            "package_censuses": {"example.test/owned/p": {
                "active_files": ["selected.go"], "source_set_sha256": sha(("selected.go:"+self.source_hash).encode())
            }},
        }

    def validate(self, packet):
        self.observer.validate(packet, self.request, self.raw)

    def test_positive_response_preserves_conditional_source_only_scope(self):
        self.validate(self.packet)

    def test_cross_language_unicode_quote_offsets_use_bytes(self):
        packet = copy.deepcopy(self.packet)
        packet["quote_byte_start"] = self.source.index(self.quote)
        with self.assertRaises(Unsupported):
            self.validate(packet)

    def test_wrong_input_producer_or_profile_refused(self):
        for key, value in [
            ("input_sha256", "0"*64), ("producer", {}), ("build_profile", {}),
            ("function", "Other"), ("builtin", "min"), ("profile", "unbounded"),
        ]:
            with self.subTest(key=key):
                packet = copy.deepcopy(self.packet)
                packet[key] = value
                with self.assertRaises(Unsupported):
                    self.validate(packet)

    def test_source_quote_and_lines_cannot_drift(self):
        for key, value in [
            ("source_sha256", "0"*64), ("quote_sha256", "0"*64),
            ("quote", self.quote.replace("2", "3")), ("first_line", 2),
            ("last_line", 4), ("quote_byte_end", True),
        ]:
            with self.subTest(key=key):
                packet = copy.deepcopy(self.packet)
                packet[key] = value
                with self.assertRaises(Unsupported):
                    self.validate(packet)

    def test_dependency_census_mismatch_or_inactive_selected_source_refused(self):
        for field, value in [("source_set_sha256", "0"*64), ("active_files", [])]:
            packet = copy.deepcopy(self.packet)
            packet["package_censuses"]["example.test/owned/p"][field] = value
            with self.assertRaises(Unsupported):
                self.validate(packet)

    def test_claiming_execution_type_check_or_owner_approval_refused(self):
        for field in ["source_executed", "owner_approved", "type_checked",
                      "runtime_bindings_verified", "publication_authorized"]:
            packet = copy.deepcopy(self.packet)
            packet[field] = True
            with self.assertRaises(Unsupported):
                self.validate(packet)

    def test_inconclusive_does_not_require_or_invent_a_quote(self):
        packet = {key: self.packet[key] for key in [
            "producer", "input_sha256", "source_executed", "owner_approved",
            "runtime_bindings_verified", "type_checked", "publication_authorized",
            "conditional_on_supplied_complete_census", "build_profile",
        ]}
        packet["status"] = "INCONCLUSIVE"
        self.validate(packet)
        self.assertNotIn("quote", packet)

    def test_refusal_exit_code_is_not_success(self):
        packet = {key: self.packet[key] for key in ["producer","input_sha256","source_executed","owner_approved"]}
        packet["status"] = "REFUSED"
        self.observer.validate(packet, self.request, self.raw, 2)
        with self.assertRaises(Unsupported):
            self.validate(packet)

    def test_changed_binary_refused_before_launch(self):
        self.binary.write_bytes(b"changed")
        with patch("documentation_go_binding.subprocess.run") as run:
            with self.assertRaises(Unsupported):
                self.observer(self.request)
            run.assert_not_called()

    def test_symlink_executable_refused(self):
        link = self.binary.with_name("link")
        link.symlink_to(self.binary)
        with self.assertRaises(OSError):
            GoBindingObserver(link, binary_sha256=self.binary_hash, go_version="go1.27.4")

    def test_deadline_is_a_refusal_without_retry(self):
        with patch("documentation_go_binding.subprocess.run", side_effect=subprocess.TimeoutExpired("native", 1)) as run:
            with self.assertRaises(Unsupported):
                self.observer(self.request)
            self.assertEqual(run.call_count, 1)
            self.assertFalse(run.call_args.kwargs["shell"])
            self.assertEqual(run.call_args.args[0], [str(self.binary)])
            self.assertEqual(run.call_args.kwargs["env"]["GOPROXY"], "off")

    def test_response_duplicate_fields_and_oversize_refused(self):
        with self.assertRaises(ValueError):
            closed_json(b'{"status":"REFUSED","status":"SUCCESS"}')
        with patch("documentation_go_binding.subprocess.run", return_value=subprocess.CompletedProcess([], 0, b" "*1048577, b"")):
            with self.assertRaises(Unsupported):
                self.observer(self.request)

    def test_request_cannot_select_shell_command_or_ill_formed_unicode(self):
        with self.assertRaises(ValueError):
            GoBindingObserver("relative-native", binary_sha256=self.binary_hash, go_version="go1.27.4")
        with patch("documentation_go_binding.subprocess.run") as run:
            with self.assertRaises(Unsupported):
                self.observer({"source": "\ud800"})
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
