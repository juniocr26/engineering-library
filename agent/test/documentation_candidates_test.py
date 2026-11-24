"""Preservation and source-boundary controls for isolated managed candidates."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from documentation_candidates import (
    CandidateRefused, packet_sha, rewrite_owned, sha,
)
import documentation_candidates as candidates


class DocumentationCandidatesTest(unittest.TestCase):
    def packet(self, action="MODIFY"):
        before = "def value():\n    return 1\n"
        current = "def value():\n    return 2\n"
        docs = {"en": "value returns1.", "pt-br": "value retorna1."}
        proof = None
        if action == "ADD":
            before, current, docs = "pass\n", before, {"en": "", "pt-br": ""}
        if action == "NO-OP":
            current = before
        if action == "REMOVE":
            current = 'RETIRED_CONTRACTS = {"sample.value": "retired"}\n'
            proof = {
                "contract_id": "sample.value", "source": "current module RETIRED_CONTRACTS",
                "reason": "retired", "aliases_checked": True, "relocations_checked": True,
            }
        return {
            "id": "owned-control", "family": "owned-development", "language": "python",
            "previous_source": before, "current_source": current, "documentation": docs,
            "complete_scope": True, "source_available": True,
            "positive_retirement_evidence": proof, "logical_contract_id": "sample.value",
            "metadata": {"managed_ownership": True},
        }

    def document(self, language="en", eol=b"\n"):
        body = ("value returns1." if language == "en" else "value retorna1.").encode() + eol
        before = b"Human introduction: unchanged.\r\n\r\n"
        start = b"<!-- documentation-agent:claim:sample.value:start -->" + eol
        end = b"<!-- documentation-agent:claim:sample.value:end -->" + eol
        tail = "Human conclusion: café, ação.\n".encode()
        return before + start + body + end + tail, before + start, body, end + tail

    def operation(self, document, body, action="MODIFY"):
        packet = self.packet(action)
        return {
            "action": action, "claim_id": "sample.value", "source_packet": packet,
            "source_packet_sha256": packet_sha(packet),
            "expected_file_sha256": sha(document),
            "expected_block_sha256": sha(body) if body is not None else None,
            "replacements": (
                None if action in ("REMOVE", "NO-OP", "INCONCLUSIVE") else {
                    "en": "value returns" + ("1" if action == "ADD" else "2") + ".\n",
                    "pt-br": "value retorna" + ("1" if action == "ADD" else "2") + ".\n",
                }
            ),
        }

    def test_modify_preserves_every_outside_byte_in_both_languages(self):
        for language in ("en", "pt-br"):
            for eol in (b"\n", b"\r\n"):
                document, prefix, body, suffix = self.document(language, eol)
                operation = self.operation(document, body)
                before = copy.deepcopy(operation)
                result, evidence = rewrite_owned(document, language, [operation])
                self.assertEqual(prefix + operation["replacements"][language].encode() + suffix, result)
                self.assertEqual(operation, before)
                self.assertTrue(evidence["history_required"])
                self.assertEqual(0, evidence["original_files_written"])
                self.assertFalse(evidence["owner_approved"])

    def test_remove_needs_positive_retirement_and_retains_original_input(self):
        document, _, body, _ = self.document()
        operation = self.operation(document, body, "REMOVE")
        result, evidence = rewrite_owned(document, "en", [operation])
        self.assertEqual(
            b"Human introduction: unchanged.\r\n\r\n" + "Human conclusion: café, ação.\n".encode(),
            result,
        )
        self.assertTrue(evidence["history_required"])
        operation["source_packet"]["positive_retirement_evidence"] = None
        operation["source_packet_sha256"] = packet_sha(operation["source_packet"])
        with self.assertRaises(CandidateRefused):
            rewrite_owned(document, "en", [operation])

    def test_add_uses_unique_explicit_anchor_and_keeps_it(self):
        anchor = b"<!-- documentation-agent:anchor:sample.value -->\n"
        document = b"Human preface.\n" + anchor + b"Human ending.\n"
        operation = self.operation(document, None, "ADD")
        result, evidence = rewrite_owned(document, "en", [operation])
        self.assertTrue(result.startswith(b"Human preface.\n"))
        self.assertTrue(result.endswith(anchor + b"Human ending.\n"))
        self.assertIn(b"value returns1.\n", result)
        self.assertTrue(evidence["changed"])

    def test_add_without_anchor_or_into_existing_block_refuses(self):
        document, _, body, _ = self.document()
        with self.assertRaises(CandidateRefused):
            rewrite_owned(document, "en", [self.operation(document, None, "ADD")])
        document = b"Human document without an anchor.\n"
        with self.assertRaises(CandidateRefused):
            rewrite_owned(document, "en", [self.operation(document, None, "ADD")])

    def test_noop_preserves_identical_bytes_and_needs_no_history(self):
        document, _, body, _ = self.document()
        result, evidence = rewrite_owned(document, "en", [self.operation(document, body, "NO-OP")])
        self.assertEqual(document, result)
        self.assertFalse(evidence["history_required"])
        self.assertFalse(evidence["changed"])

    def test_noop_refuses_current_inline_claim_over_outdated_physical_body(self):
        for language in ("en", "pt-br"):
            document, _, body, _ = self.document(language)
            operation = self.operation(document, body, "NO-OP")
            operation["source_packet"]["current_source"] = "def value():\n    return 2\n"
            operation["source_packet"]["documentation"] = {
                "en": "value returns2.", "pt-br": "value retorna2.",
            }
            operation["source_packet_sha256"] = packet_sha(operation["source_packet"])
            with self.assertRaisesRegex(CandidateRefused, "different documentation"):
                rewrite_owned(document, language, [operation])

    def test_noop_requires_exact_physical_block_checksum(self):
        document, _, body, _ = self.document()
        for checksum in (None, "0" * 64):
            operation = self.operation(document, body, "NO-OP")
            operation["expected_block_sha256"] = checksum
            with self.assertRaisesRegex(CandidateRefused, "body changed"):
                rewrite_owned(document, "en", [operation])

    def test_noop_cannot_certify_unaddressed_or_absent_document_claim(self):
        for document in (b"value returns1.\n", b"Human content with no such claim.\n"):
            operation = self.operation(document, None, "NO-OP")
            with self.assertRaisesRegex(CandidateRefused, "addressed claim block"):
                rewrite_owned(document, "en", [operation])

    def test_inconclusive_preserves_without_certifying_physical_claim(self):
        document = b"Human content with no addressed claim.\n"
        operation = self.operation(document, None, "NO-OP")
        operation["source_packet"]["complete_scope"] = False
        operation["source_packet_sha256"] = packet_sha(operation["source_packet"])
        operation["action"] = "INCONCLUSIVE"
        candidate, evidence = rewrite_owned(document, "en", [operation])
        self.assertEqual(document, candidate)
        self.assertEqual("INCONCLUSIVE", evidence["operations"][0]["action"])
        self.assertFalse(evidence["history_required"])

    def test_stale_file_or_owned_body_refuses(self):
        document, _, body, _ = self.document()
        for key in ("expected_file_sha256", "expected_block_sha256"):
            operation = self.operation(document, body)
            operation[key] = "0" * 64
            with self.assertRaises(CandidateRefused):
                rewrite_owned(document, "en", [operation])

    def test_source_packet_change_and_action_mismatch_refuse(self):
        document, _, body, _ = self.document()
        operation = self.operation(document, body)
        operation["source_packet"]["current_source"] = "def value():\n    return 1\n"
        with self.assertRaises(CandidateRefused):
            rewrite_owned(document, "en", [operation])
        operation["source_packet_sha256"] = packet_sha(operation["source_packet"])
        with self.assertRaises(CandidateRefused):
            rewrite_owned(document, "en", [operation])

    def test_unowned_human_claim_cannot_be_adopted_from_markers(self):
        document, _, body, _ = self.document()
        for metadata in ({"managed_ownership": False}, {"managed_ownership": True, "human_authored": True}):
            operation = self.operation(document, body)
            operation["source_packet"]["metadata"] = metadata
            operation["source_packet_sha256"] = packet_sha(operation["source_packet"])
            with self.assertRaises(CandidateRefused):
                rewrite_owned(document, "en", [operation])

    def test_nested_duplicate_and_unmatched_markers_refuse(self):
        document, _, body, _ = self.document()
        operation = self.operation(document, body)
        for invalid in (
            document + document,
            document.replace(b":end -->", b":start -->"),
            document.replace(b":sample.value:end", b":other:end"),
        ):
            operation["expected_file_sha256"] = sha(invalid)
            with self.assertRaises(CandidateRefused):
                rewrite_owned(invalid, "en", [operation])

    def test_unsupported_or_disagreeing_replacements_are_not_applied(self):
        document, _, body, _ = self.document()
        for replacement in ("value returns3.\n", "value does not return2.\n", "<!-- documentation-agent:claim:evil:start -->\n"):
            operation = self.operation(document, body)
            operation["replacements"]["en"] = replacement
            with self.assertRaises(CandidateRefused):
                rewrite_owned(document, "en", [operation])

    def test_duplicate_operations_refuse_before_candidate_result(self):
        document, _, body, _ = self.document()
        operation = self.operation(document, body)
        with self.assertRaises(CandidateRefused):
            rewrite_owned(document, "en", [operation, copy.deepcopy(operation)])

    def test_caller_replacement_change_after_validation_cannot_enter_candidate(self):
        document, _, body, _ = self.document()
        operation = self.operation(document, body)
        validate = candidates.validate_operation
        def mutate_after_validation(argument):
            recommendation = validate(argument)
            operation["replacements"]["en"] = "value returns999.\n"
            return recommendation
        with patch.object(candidates, "validate_operation", side_effect=mutate_after_validation):
            candidate, _ = rewrite_owned(document, "en", [operation])
        self.assertIn(b"value returns2.\n", candidate)
        self.assertNotIn(b"999", candidate)
        with self.assertRaises(CandidateRefused):
            rewrite_owned(document, "en", [operation])

    def test_caller_action_change_cannot_remove_a_nonretired_claim(self):
        document, _, body, _ = self.document()
        operation = self.operation(document, body)
        validate = candidates.validate_operation
        def mutate_after_validation(argument):
            recommendation = validate(argument)
            operation["action"] = "REMOVE"
            return recommendation
        with patch.object(candidates, "validate_operation", side_effect=mutate_after_validation):
            candidate, evidence = rewrite_owned(document, "en", [operation])
        self.assertIn(b"documentation-agent:claim:sample.value:start", candidate)
        self.assertIn(b"value returns2.\n", candidate)
        self.assertEqual("MODIFY", evidence["operations"][0]["action"])

    def test_new_explicit_valid_operation_can_describe_another_current_value(self):
        document, _, body, _ = self.document()
        operation = self.operation(document, body)
        operation["source_packet"]["current_source"] = "def value():\n    return 3\n"
        operation["source_packet_sha256"] = packet_sha(operation["source_packet"])
        operation["replacements"] = {"en": "value returns3.\n", "pt-br": "value retorna3.\n"}
        candidate, _ = rewrite_owned(document, "en", [operation])
        self.assertIn(b"value returns3.\n", candidate)


if __name__ == "__main__":
    unittest.main()
