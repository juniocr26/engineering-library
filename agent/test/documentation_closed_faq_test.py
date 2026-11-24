import hashlib
from pathlib import Path
import re
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from documentation_closed_faq import prepare_closed_return_pair, ClosedFaqRefused
from documentation_python_dependencies import ClosedDependencyObserver


class ClosedFaqTests(unittest.TestCase):
    def observer(self, sources):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        root = Path(temporary.name).resolve(); modules = {}
        for name, source in sources.items():
            raw = source.encode(); (root / (name + ".py")).write_bytes(raw)
            modules[name] = {"path": name + ".py", "sha256": hashlib.sha256(raw).hexdigest()}
        return root, ClosedDependencyObserver(root, {"revision": "owned-faq-source-cut", "modules": modules})

    def prepare(self, observer):
        return prepare_closed_return_pair(observer, "fixture.integer-return", "entry", "value")

    def test_cross_file_answer_preserves_requested_entry_value_and_uncertainty(self):
        root, observer = self.observer({"entry": "from leaf import answer as value\n", "leaf": "def answer(): return 9\n"})
        result = self.prepare(observer)
        self.assertEqual(result["status"], "PREPARED_CONDITIONAL_FAQ_PAIR")
        pair = result["faq_pair"]
        for language in ("en", "pt-br"):
            self.assertEqual(re.findall(r"`([^`]+)`", pair[language]["question"]), ["entry.value"])
            self.assertEqual(re.findall(r"`([^`]+)`", pair[language]["answer"]), ["entry.value", "9"])
            self.assertNotIn("leaf.answer", pair[language]["question"])
        self.assertIn("unverified", pair["en"]["answer"])
        self.assertIn("não foi verificada", pair["pt-br"]["answer"])
        self.assertEqual(result["model_calls"], 0)
        self.assertEqual(result["writes"], 0)
        self.assertFalse(result["publication_authorized"])
        self.assertEqual(result["source_observation"]["entry_module"], "entry")
        self.assertEqual(len(result["source_observation"]["imports"]), 1)

    def test_helper_change_changes_answer_but_formatting_preserves_pair(self):
        entry = "from leaf import answer\ndef value(): return answer()\n"
        results = []
        for leaf in ["def answer(): return 2\n", "# reformatted\ndef answer():\n    return 2\n", "def answer(): return 9\n"]:
            _, observer = self.observer({"entry": entry, "leaf": leaf});results.append(self.prepare(observer))
        self.assertEqual(results[0]["faq_pair"], results[1]["faq_pair"])
        self.assertEqual(results[0]["pair_sha256"], results[1]["pair_sha256"])
        self.assertNotEqual(results[0]["evidence_key"], results[1]["evidence_key"])
        self.assertNotEqual(results[0]["pair_sha256"], results[2]["pair_sha256"])
        self.assertEqual(results[2]["source_observation"]["value"], 9)

    def test_private_helper_and_negative_integer_preserve_bilingual_symbols(self):
        _, observer = self.observer({"entry": "from _leaf import _answer\ndef value(): return _answer()\n", "_leaf": "def _answer(): return -7\n"})
        result = self.prepare(observer)
        for language in ("en", "pt-br"):
            self.assertEqual(re.findall(r"`([^`]+)`", result["faq_pair"][language]["answer"]), ["entry.value", "-7"])

    def test_missing_dynamic_or_stale_source_produces_no_answer(self):
        for sources in [{"entry": "from absent import answer\ndef value(): return answer()\n"},
                        {"entry": "def value(): return 1 + 2\n"}]:
            _, observer = self.observer(sources); result = self.prepare(observer)
            self.assertEqual(result["status"], "INCONCLUSIVE")
            self.assertIsNone(result["faq_pair"])
        root, observer = self.observer({"entry": "def value(): return 2\n"})
        (root / "entry.py").write_text("def value(): return 9\n")
        self.assertIsNone(self.prepare(observer)["faq_pair"])

    def test_mutated_registry_does_not_turn_json_or_unregistered_value_into_answer(self):
        root, observer = self.observer({"entry": "def value(): return 2\n"})
        (root / "other.py").write_text("def value(): return 999\n")
        observer.registry["modules"]["entry"] = {"path": "other.py", "sha256": hashlib.sha256((root / "other.py").read_bytes()).hexdigest()}
        result = self.prepare(observer)
        self.assertEqual(result["status"], "INCONCLUSIVE")
        self.assertIsNone(result["faq_pair"])
        with self.assertRaises(ClosedFaqRefused):
            self.prepare({"status": "STATIC_INTEGER_RETURN_UNDER_CLOSED_PROFILE", "value": 999})

    def test_explicit_stable_question_identity_and_source_preservation(self):
        root, observer = self.observer({"entry": "def value(): return 2\n"})
        path = root / "entry.py"; before = (path.read_bytes(), path.stat().st_ino, path.stat().st_mtime_ns, path.stat().st_ctime_ns)
        for question_id in ["", "<script>", "id with spaces", ["not-a-string"]]:
            with self.subTest(question_id=question_id), self.assertRaises(ClosedFaqRefused):
                prepare_closed_return_pair(observer, question_id, "entry", "value")
        result = self.prepare(observer)
        self.assertEqual(result["question_id"], "fixture.integer-return")
        self.assertEqual(before, (path.read_bytes(), path.stat().st_ino, path.stat().st_mtime_ns, path.stat().st_ctime_ns))
        self.assertEqual(sorted(path.name for path in root.iterdir()), ["entry.py"])


if __name__ == "__main__":unittest.main()
