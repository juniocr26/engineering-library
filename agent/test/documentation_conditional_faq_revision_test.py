"""Closed conditional FAQ revision acceptance: helper changes and safe refusal."""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import documentation_conditional_faq_revision as revision
import documentation_python_dependencies as dependencies
import documentation_closed_faq as renderer


class ConditionalFaqRevisionTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.old, self.new = self.root / "old", self.root / "new"
        for root, value in [(self.old, 1), (self.new, 2)]:
            root.mkdir()
            (root / "entry.py").write_text("from helper import value\ndef result():\n    return value()\n")
            (root / "helper.py").write_text(f"def value():\n    return {value}\n")
        self.before, self.after = self.observer(self.old, "previous"), self.observer(self.new, "current")
        self.pair = self.pair_for(1)
        self.original = {str(p):p.read_bytes() for root in [self.old,self.new] for p in root.glob('*.py')}

    def tearDown(self):
        self.temporary.cleanup()

    def observer(self, root, label):
        registry = {"revision": label, "modules": {p.stem:{"path":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}for p in root.glob('*.py')}}
        return dependencies.ClosedDependencyObserver(root, registry)

    def pair_for(self, value):
        qualified = "entry.result"
        return {"en":{"question":f"What integer does `{qualified}` return under the registered closed profile?","answer":f"Under the registered closed source profile, `{qualified}` returns `{value}`. Runtime name bindings are unverified."},
                "pt-br":{"question":f"Qual valor inteiro `{qualified}` retorna sob o perfil fechado registrado?","answer":f"Sob o perfil fechado de fontes registrado, `{qualified}` retorna `{value}`. A resolução dos nomes em execução não foi verificada."}}

    def call(self, **changes):
        kwargs = dict(existing_pair=self.pair, expected_pair_sha256=revision.digest(self.pair),
                      question_registered=True, complete_inventory=True,
                      managed_ownership=True, human_authored=False)
        kwargs.update(changes)
        return revision.plan_revision(self.before, self.after, "sample.result", "entry", "result", **kwargs)

    def assert_refusal(self, result):
        self.assertEqual("INCONCLUSIVE", result["action"], result)
        self.assertFalse(result["changed"])
        self.assertIsNone(result["history"])
        self.assertNotIn("source_observations", result)
        self.assertEqual(0, result["original_files_written"])
        self.assertFalse(result["publication_authorized"])

    def test_only_helper_change_modifies_exact_conditional_pair(self):
        result = self.call()
        self.assertEqual("MODIFY", result["action"], result)
        self.assertEqual(self.pair_for(2), result["candidate_pair"])
        self.assertEqual(self.pair_for(1), result["history"])
        self.assertTrue(result["source_value_changed"])
        self.assertTrue(result["source_evidence_changed"])
        self.assertEqual(self.original, {str(p):p.read_bytes()for root in [self.old,self.new]for p in root.glob('*.py')})
        self.assertFalse(result["runtime_bindings_verified"])
        self.assertEqual(0, result["model_calls"])

    def test_unchanged_value_and_changed_helper_keep_exact_pair(self):
        (self.new / "helper.py").write_text("def value():\n    # changed ordinary comment\n    return 1\n")
        self.after = self.observer(self.new, "current")
        result = self.call()
        self.assertEqual("NO-OP", result["action"], result)
        self.assertFalse(result["changed"])
        self.assertFalse(result["source_value_changed"])
        self.assertTrue(result["source_evidence_changed"])
        self.assertEqual(self.pair, result["candidate_pair"])

    def test_already_current_pair_is_noop(self):
        self.pair = self.pair_for(2)
        result = self.call()
        self.assertEqual("NO-OP", result["action"], result)
        self.assertIsNone(result["history"])

    def test_missing_registered_question_adds_without_requiring_new_feature(self):
        result = self.call(existing_pair=None, expected_pair_sha256=None, question_registered=False)
        self.assertEqual("ADD", result["action"], result)
        self.assertEqual(self.pair_for(2), result["candidate_pair"])
        self.assertIsNone(result["history"])
        self.assertIsNone(result["before_pair_sha256"])

    def test_identical_source_snapshots_keep_pair(self):
        self.after = self.before
        result = self.call()
        self.assertEqual("NO-OP", result["action"], result)
        self.assertFalse(result["source_evidence_changed"])

    def test_source_disappearance_never_recommends_remove(self):
        (self.new / "helper.py").write_text("def another():\n    return 2\n")
        self.after = self.observer(self.new, "current")
        self.assert_refusal(self.call())

    def test_missing_helper_file_or_stale_digest_preserves_pair(self):
        (self.new / "helper.py").write_text("def value():\n    return 3\n")
        self.assert_refusal(self.call())
        (self.new / "helper.py").unlink()
        self.assert_refusal(self.call())

    def test_conditional_ambiguous_helper_is_unknown(self):
        (self.new / "helper.py").write_text("if enabled:\n    def value():\n        return 2\n")
        self.after = self.observer(self.new, "current")
        self.assert_refusal(self.call())

    def test_unrelated_or_asymmetric_existing_answer_is_not_overwritten(self):
        for lang in ["en", "pt-br"]:
            pair = self.pair_for(1); pair[lang]["answer"] = "Human custom answer."
            self.assert_refusal(self.call(existing_pair=pair, expected_pair_sha256=revision.digest(pair)))

    def test_missing_runtime_caveat_is_not_silently_adopted(self):
        pair = self.pair_for(1);pair['en']['answer']=pair['en']['answer'].split(' Runtime')[0]
        self.assert_refusal(self.call(existing_pair=pair, expected_pair_sha256=revision.digest(pair)))

    def test_inventory_ownership_and_hash_failures_refuse(self):
        for kwargs in [dict(complete_inventory=False),dict(complete_inventory=1),dict(managed_ownership=False),dict(managed_ownership=1),dict(human_authored=True),dict(human_authored=0),dict(question_registered="true"),dict(question_registered=False),dict(expected_pair_sha256="0"*64)]:
            with self.subTest(kwargs=kwargs):self.assert_refusal(self.call(**kwargs))

    def test_missing_pair_cannot_claim_existing_hash_or_registered_question(self):
        self.assert_refusal(self.call(existing_pair=None, question_registered=False))
        self.assert_refusal(self.call(existing_pair=None, expected_pair_sha256=None, question_registered=True))

    def test_untrusted_observer_or_persisted_json_fact_refuses(self):
        for fake in [{"value":2}, object()]:
            self.after = fake
            self.assert_refusal(self.call())

    def test_caller_pair_mutation_cannot_change_history_or_plan(self):
        original = renderer.prepare_closed_return_pair
        def mutate(*args, **kwargs):
            result = original(*args, **kwargs)
            self.pair['en']['answer'] = "Caller changed this after entry."
            return result
        with patch.object(renderer, "prepare_closed_return_pair", side_effect=mutate):
            result = self.call()
        self.assertEqual("MODIFY", result['action'], result)
        self.assertEqual(self.pair_for(1), result['history'])
        self.assertEqual(revision.digest(self.pair_for(1)), result['before_pair_sha256'])

    def test_previous_physical_drift_after_observation_withholds_candidate(self):
        original = renderer.prepare_closed_return_pair
        def mutate(observer, *args, **kwargs):
            result = original(observer, *args, **kwargs)
            if observer is self.after:
                (self.old/'helper.py').write_text('def value():\n    return 99\n')
            return result
        with patch.object(renderer, "prepare_closed_return_pair", side_effect=mutate):
            self.assert_refusal(self.call())

    def test_observer_configuration_drift_withholds_candidate(self):
        original = renderer.prepare_closed_return_pair
        def mutate(observer, *args, **kwargs):
            result = original(observer, *args, **kwargs)
            if observer is self.after:self.before.registry['revision']='caller-rebound'
            return result
        with patch.object(renderer, "prepare_closed_return_pair", side_effect=mutate):
            self.assert_refusal(self.call())

    def test_deadline_prevents_delivery(self):
        with patch.object(revision.time, "monotonic", side_effect=[0,9]):
            result = self.call()
        self.assert_refusal(result)

    def test_loaded_implementation_drift_refuses(self):
        original = revision.implementation
        with patch.object(revision, 'implementation', side_effect=[original(), {'changed':True}]):
            self.assert_refusal(self.call())

    def test_pair_schema_unicode_and_byte_bounds_refuse(self):
        cases=[{}, {'en':{'question':'q','answer':'a'}}, self.pair_for(1), self.pair_for(1), self.pair_for(1)]
        cases[2]['en']['answer']='x'*17000;cases[3]['en']['answer']='\ud800';cases[4]['en']['answer']='bad\0value'
        for pair in cases:
            with self.subTest(kind=str(pair)[:80]):
                result=self.call(existing_pair=pair,expected_pair_sha256='0'*64)
                self.assert_refusal(result)

    def test_invalid_question_identity_preserves_pair(self):
        result=revision.plan_revision(self.before,self.after,'../bad','entry','result',existing_pair=self.pair,expected_pair_sha256=revision.digest(self.pair),question_registered=True,complete_inventory=True,managed_ownership=True,human_authored=False)
        self.assert_refusal(result)


if __name__ == "__main__":
    unittest.main()
