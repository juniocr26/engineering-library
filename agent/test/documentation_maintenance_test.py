"""Filesystem acceptance: originals, stale source, history and safe refusals."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import documentation_maintenance as maintenance
from documentation_candidates import CandidateRefused, packet_sha
from documentation_workspace import WorkspaceRefused


def sha(data):
    return hashlib.sha256(data).hexdigest()


class DocumentationMaintenanceTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.before, self.current, self.docs = [
            self.root / name for name in ("before", "current", "documents")
        ]
        for directory in (self.before, self.current, self.docs):
            directory.mkdir()
        self.candidate = self.root / "candidate"
        (self.before / "api.py").write_text("def value():\n    return 1\n")
        (self.current / "api.py").write_text("def value():\n    return 2\n")
        for language, claim in (("en", "value returns1."), ("pt-br", "value retorna1.")):
            directory = self.docs / language
            directory.mkdir()
            (directory / "guide.md").write_bytes(
                "# Human title\n[Notes](notes.md)\nHuman café.\r\n".encode()
                + b"<!-- documentation-agent:claim:sample.value:start -->\n"
                + claim.encode() + b"\n"
                + b"<!-- documentation-agent:claim:sample.value:end -->\n"
                + b"Human conclusion.\n"
            )
            (directory / "notes.md").write_text("# Human notes\nUntouched.\n")

    def tearDown(self):
        self.temporary.cleanup()

    def original_state(self):
        return {
            str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mtime_ns)
            for directory in (self.before, self.current, self.docs)
            for path in directory.rglob("*") if path.is_file()
        }

    def spec(self, action="MODIFY"):
        old, current = (self.before / "api.py").read_text(), (self.current / "api.py").read_text()
        proof = None
        if action == "REMOVE":
            proof = {
                "contract_id": "sample.value", "source": "current module RETIRED_CONTRACTS",
                "reason": "retired", "aliases_checked": True, "relocations_checked": True,
            }
        packet = {
            "language": "python", "previous_source": old, "current_source": current,
            "documentation": {"en": "value returns1.", "pt-br": "value retorna1."},
            "source_available": True, "complete_scope": action != "INCONCLUSIVE",
            "positive_retirement_evidence": proof,
            "logical_contract_id": "sample.value", "metadata": {"managed_ownership": True},
        }
        operation = {
            "action": action, "claim_id": "sample.value",
            "previous_file": "api.py", "source_file": "api.py",
            "source_packet": packet, "source_packet_sha256": packet_sha(packet),
            "documents": {
                language: {
                    "path": language + "/guide.md",
                    "expected_block_sha256": sha((claim + "\n").encode()),
                }
                for language, claim in (("en", "value returns1."), ("pt-br", "value retorna1."))
            },
            "replacements": None if action in ("NO-OP", "INCONCLUSIVE", "REMOVE") else {
                "en": "value returns2.\n", "pt-br": "value retorna2.\n",
            },
        }
        return {
            "schema_version": 1, "scope_kind": "owned-synthetic-project",
            "repository": "owned-maintenance-lab",
            "previous_source_root": str(self.before), "source_root": str(self.current),
            "documentation_root": str(self.docs), "candidate_root": str(self.candidate),
            "previous_source_files": {"api.py": sha(old.encode())},
            "source_files": {"api.py": sha(current.encode())},
            "documentation_files": {
                str(path.relative_to(self.docs)): sha(path.read_bytes())
                for path in self.docs.rglob("*.md")
            },
            "operations": [operation],
        }

    def assert_refuses(self, specification):
        before = self.original_state()
        with self.assertRaises((WorkspaceRefused, CandidateRefused, OSError, ValueError)):
            maintenance.build(specification, prepare=True)
        self.assertEqual(before, self.original_state())
        self.assertFalse(self.candidate.exists())

    def test_default_dry_run_writes_nothing(self):
        before = self.original_state()
        report = maintenance.build(self.spec())
        self.assertEqual("VALIDATED_DRY_RUN", report["status"])
        self.assertEqual(2, len(report["changed_documents"]))
        self.assertEqual(before, self.original_state())
        self.assertFalse(self.candidate.exists())

    def test_caller_inventory_edit_cannot_hide_physical_source_drift(self):
        specification = self.spec()
        documents = {str(p): p.read_bytes() for p in self.docs.rglob("*.md")}
        rewrite = maintenance.rewrite_owned
        mutated = False
        def drift(*args, **kwargs):
            nonlocal mutated
            result = rewrite(*args, **kwargs)
            if not mutated:
                source = b"def value():\n    return 3\n"
                (self.current / "api.py").write_bytes(source)
                specification["source_files"]["api.py"] = sha(source)
                mutated = True
            return result
        with patch.object(maintenance, "rewrite_owned", side_effect=drift):
            with self.assertRaisesRegex(WorkspaceRefused, "checksum changed"):
                maintenance.build(specification, prepare=True)
        self.assertFalse(self.candidate.exists())
        self.assertEqual(documents, {str(p): p.read_bytes() for p in self.docs.rglob("*.md")})

    def test_persisted_preconditions_keep_the_original_candidate_root(self):
        specification = self.spec()
        requested_root = specification["candidate_root"]
        rewrite = maintenance.rewrite_owned
        def mutate(*args, **kwargs):
            result = rewrite(*args, **kwargs)
            specification["candidate_root"] = str(self.root / "different-caller-root")
            return result
        with patch.object(maintenance, "rewrite_owned", side_effect=mutate):
            report = maintenance.build(specification, prepare=True)
        self.assertTrue(report["candidate_created"])
        recorded = json.loads((self.candidate / "preconditions.json").read_text())
        self.assertEqual(requested_root, recorded["specification"]["candidate_root"])
        self.assertFalse((self.root / "different-caller-root").exists())

    def test_prepare_requires_a_boolean_before_any_candidate_writes(self):
        for value in ("false", "true", 0, 1, None, []):
            with self.assertRaisesRegex(WorkspaceRefused, "explicit Boolean"):
                maintenance.build(self.spec(), prepare=value)
        self.assertFalse(self.candidate.exists())

    def test_explicit_new_valid_plan_can_use_the_changed_source(self):
        (self.current / "api.py").write_text("def value():\n    return 3\n")
        specification = self.spec()
        specification["operations"][0]["replacements"] = {
            "en": "value returns3.\n", "pt-br": "value retorna3.\n",
        }
        report = maintenance.build(specification, prepare=True)
        self.assertTrue(report["candidate_created"])
        self.assertIn("value returns3.", (self.candidate / "active/en/guide.md").read_text())

    def test_prepare_archives_every_original_and_preserves_unaffected_mtime(self):
        specification, before = self.spec(), self.original_state()
        report = maintenance.build(specification, prepare=True)
        self.assertTrue(report["candidate_created"])
        self.assertTrue(report["candidate_output_readback_verified"])
        self.assertTrue(report["candidate_root_identity_rechecked"])
        self.assertEqual(before, self.original_state())
        history = json.loads((self.candidate / "history-index.json").read_text())
        for name, checksum in specification["documentation_files"].items():
            original = self.docs / name
            self.assertEqual(original.read_bytes(), (self.candidate / history[name]["archive"]).read_bytes())
            self.assertEqual(checksum, sha(original.read_bytes()))
        for language in ("en", "pt-br"):
            candidate = self.candidate / "active" / language / "guide.md"
            self.assertIn("Human café.\r\n".encode(), candidate.read_bytes())
            self.assertTrue(candidate.read_bytes().endswith(b"Human conclusion.\n"))
            note = self.candidate / "active" / language / "notes.md"
            self.assertEqual((self.docs / language / "notes.md").stat().st_mtime_ns, note.stat().st_mtime_ns)
        self.assertTrue((self.candidate / "result.json").is_file())

    def assert_output_tamper_refused(self, mutate, trigger="history-index.json"):
        specification, before = self.spec(), self.original_state()
        write = maintenance.write_new
        triggered = []
        def tamper(fd, name, data, metadata=None):
            write(fd, name, data, metadata)
            if name == trigger:
                mutate()
                triggered.append(name)
        with patch.object(maintenance, "write_new", side_effect=tamper):
            with self.assertRaises((WorkspaceRefused, OSError)):
                maintenance.build(specification, prepare=True)
        self.assertEqual([trigger], triggered)
        self.assertEqual(before, self.original_state())
        self.assertTrue(self.candidate.exists())
        if trigger != "result.json":
            self.assertFalse((self.candidate / "result.json").exists())

    def test_candidate_root_replacement_refuses_without_writing_replacement(self):
        moved = self.root / "preserved-candidate"
        def replace():
            self.candidate.rename(moved)
            self.candidate.mkdir()
            (self.candidate / "human.txt").write_text("keep replacement")
        self.assert_output_tamper_refused(replace)
        self.assertEqual(["human.txt"], os.listdir(self.candidate))
        self.assertEqual("keep replacement", (self.candidate / "human.txt").read_text())
        self.assertTrue((moved / "history-index.json").is_file())
        self.assertFalse((moved / "result.json").exists())

    def test_written_active_bytes_are_read_back_before_success(self):
        path = self.candidate / "active/en/guide.md"
        self.assert_output_tamper_refused(lambda: path.write_text("value returns999.\n"))
        self.assertEqual("value returns999.\n", path.read_text())
        self.assertTrue((self.candidate / "history-index.json").is_file())

    def test_history_copy_corruption_refuses_and_preserves_partial_evidence(self):
        checksum = sha((self.docs / "en/guide.md").read_bytes())
        path = self.candidate / "history" / (checksum + ".bin")
        self.assert_output_tamper_refused(lambda: path.write_bytes(b"corrupted copied history"))
        self.assertEqual(b"corrupted copied history", path.read_bytes())

    def test_unregistered_candidate_artifact_is_preserved_and_refused(self):
        path = self.candidate / "human.txt"
        self.assert_output_tamper_refused(lambda: path.write_text("keep unexpected artifact"))
        self.assertEqual("keep unexpected artifact", path.read_text())

    def test_durable_result_bytes_are_read_back_before_return(self):
        path = self.candidate / "result.json"
        self.assert_output_tamper_refused(lambda: path.write_text('{"tampered":true}\n'), "result.json")
        self.assertEqual({"tampered": True}, json.loads(path.read_text()))

    def test_replaced_active_directory_symlink_is_not_followed(self):
        outside = self.root / "human-outside"
        outside.mkdir()
        sentinel = outside / "human.txt"; sentinel.write_text("keep outside")
        moved = self.root / "preserved-active"
        def replace():
            (self.candidate / "active").rename(moved)
            (self.candidate / "active").symlink_to(outside, target_is_directory=True)
        self.assert_output_tamper_refused(replace)
        self.assertEqual("keep outside", sentinel.read_text())
        self.assertTrue((moved / "en/guide.md").is_file())

    def test_unchanged_active_document_mtime_drift_prevents_preservation_claim(self):
        path = self.candidate / "active/en/notes.md"
        def change_time():
            info = path.stat()
            os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns + 1_000_000_000))
        self.assert_output_tamper_refused(change_time)

    def test_noop_preserves_bytes_mtimes_and_does_not_create_candidate(self):
        (self.current / "api.py").write_bytes((self.before / "api.py").read_bytes())
        specification, before = self.spec("NO-OP"), self.original_state()
        report = maintenance.build(specification, prepare=True)
        self.assertEqual("NO-OP", report["status"])
        self.assertFalse(self.candidate.exists())
        self.assertEqual(before, self.original_state())

    def test_noop_current_inline_claim_cannot_certify_stale_physical_documents(self):
        specification = self.spec("NO-OP")
        operation = specification["operations"][0]
        operation["source_packet"]["documentation"] = {
            "en": "value returns2.", "pt-br": "value retorna2.",
        }
        operation["source_packet_sha256"] = packet_sha(operation["source_packet"])
        self.assert_refuses(specification)

    def test_noop_refuses_unaddressed_documents_without_creating_candidate(self):
        (self.current / "api.py").write_bytes((self.before / "api.py").read_bytes())
        (self.docs / "en/guide.md").write_text("value returns1.\n")
        self.assert_refuses(self.spec("NO-OP"))

    def test_noop_refuses_stale_block_checksum_in_otherwise_valid_specification(self):
        (self.current / "api.py").write_bytes((self.before / "api.py").read_bytes())
        specification = self.spec("NO-OP")
        specification["operations"][0]["documents"]["pt-br"]["expected_block_sha256"] = "0" * 64
        self.assert_refuses(specification)

    def test_inconclusive_is_distinct_from_noop_and_preserves_everything(self):
        specification, before = self.spec("INCONCLUSIVE"), self.original_state()
        report = maintenance.build(specification, prepare=True)
        self.assertEqual("INCONCLUSIVE_PRESERVE_ORIGINALS", report["status"])
        self.assertFalse(self.candidate.exists())
        self.assertEqual(before, self.original_state())

    def test_changed_source_is_refused_without_reverting_owner_edit(self):
        specification = self.spec()
        changed = "def value():\n    return 3\n"
        (self.current / "api.py").write_text(changed)
        self.assert_refuses(specification)
        self.assertEqual(changed, (self.current / "api.py").read_text())

    def test_changed_human_document_is_refused_without_reverting_it(self):
        specification = self.spec()
        path = self.docs / "en/guide.md"
        changed = b"Human new paragraph.\n" + path.read_bytes()
        path.write_bytes(changed)
        self.assert_refuses(specification)
        self.assertEqual(changed, path.read_bytes())

    def test_unregistered_source_prevents_partial_scope_claim(self):
        specification = self.spec()
        (self.current / "relocated.py").write_text("def value():\n    return 1\n")
        self.assert_refuses(specification)

    def test_source_symlink_never_becomes_evidence(self):
        specification = self.spec()
        outside = self.root / "outside.py"
        outside.write_bytes((self.current / "api.py").read_bytes())
        (self.current / "api.py").unlink()
        (self.current / "api.py").symlink_to(outside)
        with self.assertRaises((WorkspaceRefused, OSError)):
            maintenance.build(specification, prepare=True)
        self.assertFalse(self.candidate.exists())
        self.assertEqual(specification["source_files"]["api.py"], sha(outside.read_bytes()))

    def test_root_symlink_is_refused(self):
        specification = self.spec()
        alias = self.root / "source-alias"
        alias.symlink_to(self.current, target_is_directory=True)
        specification["source_root"] = str(alias)
        self.assert_refuses(specification)

    def test_inline_packet_cannot_substitute_different_current_source(self):
        specification = self.spec()
        operation = specification["operations"][0]
        operation["source_packet"]["current_source"] = "def value():\n    return 3\n"
        operation["source_packet_sha256"] = packet_sha(operation["source_packet"])
        self.assert_refuses(specification)

    def test_unowned_claim_and_wrong_language_paths_are_refused(self):
        specification = self.spec()
        operation = specification["operations"][0]
        operation["source_packet"]["metadata"] = {"managed_ownership": False}
        operation["source_packet_sha256"] = packet_sha(operation["source_packet"])
        self.assert_refuses(specification)
        specification = self.spec()
        operation = specification["operations"][0]
        operation["documents"]["en"]["path"] = "pt-br/guide.md"
        self.assert_refuses(specification)

    def test_existing_candidate_is_never_overwritten(self):
        specification = self.spec()
        self.candidate.mkdir()
        sentinel = self.candidate / "human.txt"
        sentinel.write_text("keep")
        with self.assertRaises(WorkspaceRefused):
            maintenance.build(specification, prepare=True)
        self.assertEqual("keep", sentinel.read_text())

    def test_positive_retirement_removes_active_claim_only(self):
        (self.current / "api.py").write_text('RETIRED_CONTRACTS = {"sample.value": "retired"}\n')
        specification, before = self.spec("REMOVE"), self.original_state()
        report = maintenance.build(specification, prepare=True)
        self.assertTrue(report["candidate_created"])
        self.assertEqual(before, self.original_state())
        for language in ("en", "pt-br"):
            active = (self.candidate / "active" / language / "guide.md").read_bytes()
            self.assertNotIn(b"documentation-agent:claim:", active)
            checksum = specification["documentation_files"][language + "/guide.md"]
            self.assertEqual(
                (self.docs / language / "guide.md").read_bytes(),
                (self.candidate / "history" / (checksum + ".bin")).read_bytes(),
            )

    def test_registered_relocated_definition_blocks_retirement(self):
        (self.current / "api.py").write_text('RETIRED_CONTRACTS = {"sample.value": "retired"}\n')
        specification = self.spec("REMOVE")
        relocated = self.current / "moved.py"
        relocated.write_text("def current_value():\n    return 1\n")
        specification["source_files"]["moved.py"] = sha(relocated.read_bytes())
        self.assert_refuses(specification)

    def test_owner_source_change_during_preparation_preserves_partial_history(self):
        specification = self.spec()
        original_write = maintenance.write_new

        def owner_change(fd, name, data, metadata=None):
            original_write(fd, name, data, metadata)
            if name == "preconditions.json":
                (self.current / "api.py").write_text("def value():\n    return 3\n")

        with patch.object(maintenance, "write_new", side_effect=owner_change):
            with self.assertRaises(WorkspaceRefused):
                maintenance.build(specification, prepare=True)
        self.assertTrue(self.candidate.exists())
        self.assertTrue((self.candidate / "history-index.json").exists())
        self.assertFalse((self.candidate / "result.json").exists())
        self.assertIn("return 3", (self.current / "api.py").read_text())
        self.assertIn("value returns1.", (self.docs / "en/guide.md").read_text())

    def test_external_scope_is_not_silently_promoted(self):
        specification = self.spec()
        specification["scope_kind"] = "external-git-project"
        self.assert_refuses(specification)

    def test_regular_specification_cli_keeps_valid_dry_run(self):
        path = self.root / "spec.json"
        path.write_text(json.dumps(self.spec()))
        original = self.original_state()
        result = subprocess.run([sys.executable, str(TOOLS / "documentation_maintenance.py"),
                                 "--spec", str(path)], capture_output=True, text=True, timeout=5)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("VALIDATED_DRY_RUN", json.loads(result.stdout)["status"])
        self.assertEqual(original, self.original_state())
        self.assertFalse(self.candidate.exists())

    def test_fifo_specification_cli_refuses_without_waiting_for_writer(self):
        path = self.root / "spec.fifo"
        os.mkfifo(path)
        result = subprocess.run([sys.executable, str(TOOLS / "documentation_maintenance.py"),
                                 "--spec", str(path), "--prepare"],
                                capture_output=True, text=True, timeout=3)
        self.assertEqual(2, result.returncode)
        self.assertIn("bounded regular file", json.loads(result.stdout)["reason"])
        self.assertFalse(self.candidate.exists())

    def test_specification_symlink_and_symlink_parent_refuse(self):
        real = self.root / "spec.json"
        real.write_text(json.dumps(self.spec()))
        alias = self.root / "alias.json"; alias.symlink_to(real)
        parent = self.root / "alias-directory"; parent.symlink_to(self.root, target_is_directory=True)
        for path in (alias, parent / "spec.json", self.root):
            with self.subTest(path=path), self.assertRaises((WorkspaceRefused, OSError)):
                maintenance.read_specification(path)
        self.assertFalse(self.candidate.exists())

    def test_specification_json_refuses_nonfinite_unicode_depth_and_node_overflow(self):
        path = self.root / "spec.json"
        cases = [b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e9999}',
                 b'{"x":"\\ud800"}', b'{"x":'+b'['*70+b'0'+b']'*70+b'}',
                 json.dumps({"x":[0]*65536}).encode(), b'[]', b'{"x":1,"x":2}']
        for raw in cases:
            path.write_bytes(raw)
            with self.subTest(size=len(raw)), self.assertRaises((WorkspaceRefused, UnicodeError)):
                maintenance.read_specification(path)

    def test_specification_growth_or_path_replacement_is_refused(self):
        path = self.root / "spec.json"
        original_read = maintenance.read
        for replace in (False, True):
            path.write_bytes(b'{}')
            def mutate(*args, **kwargs):
                data = original_read(*args, **kwargs)
                if replace:
                    path.rename(self.root / "preserved-spec.json")
                path.write_bytes(b'{"changed":true}')
                return data
            with patch.object(maintenance, "read", side_effect=mutate):
                with self.assertRaisesRegex(WorkspaceRefused, "changed while reading"):
                    maintenance.read_specification(path)
        self.assertFalse(self.candidate.exists())

    def test_specification_two_megabyte_limit_is_preserved(self):
        path = self.root / "spec.json"
        raw = b'{"padding":"'+b'x'*(2*1024*1024-14)+b'"}'
        self.assertEqual(2*1024*1024, len(raw))
        path.write_bytes(raw)
        self.assertEqual(len(raw)-14, len(maintenance.read_specification(path)["padding"]))
        path.write_bytes(raw+b' ')
        with self.assertRaisesRegex(WorkspaceRefused, "bounded regular file"):
            maintenance.read_specification(path)

    def test_cli_rejects_duplicate_json_keys_without_creating_candidate(self):
        specification = self.spec()
        raw = json.dumps(specification)
        path = self.root / "spec.json"
        path.write_text('{"schema_version": 9,' + raw[1:])
        result = subprocess.run([
            sys.executable, str(TOOLS / "documentation_maintenance.py"),
            "--spec", str(path), "--prepare",
        ], capture_output=True, text=True)
        self.assertEqual(2, result.returncode)
        self.assertEqual("REFUSED_PRESERVE_ORIGINALS", json.loads(result.stdout)["status"])
        self.assertFalse(self.candidate.exists())


if __name__ == "__main__":
    unittest.main()
