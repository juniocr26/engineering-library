import copy
import tempfile
import unittest
from pathlib import Path

from documentation_quality import POLICY, policy_hash, score, sha


class DocumentationQualityTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        path = Path(self.directory.name)/'source.txt'
        path.write_text('LIMIT = 7\n')
        digest = sha(path.read_bytes())
        self.packet = {
            'policy_sha256': policy_hash(), 'scope': 'section', 'source_revision': 'a'*40,
            'artifacts': [{'id': 'en', 'path': str(path), 'sha256': digest}],
            'evidence': [{'id': 'source', 'path': str(path), 'source_sha256': digest,
                          'line_start': 1, 'line_end': 1, 'quote_sha256': digest}],
            'claims': [{'id': 'limit', 'state': 'complete', 'required': True,
                        'critical': False, 'reason': 'LIMIT is 7.', 'evidence': ['source']}],
            'inventory_complete': True,
            'dimensions': {d: {c: {'rating': 'complete', 'reason': 'Reviewed criterion.',
                                   'evidence': ['source']} for c in criteria}
                           for d, criteria in POLICY['criteria'].items()},
        }

    def test_initial_review_is_provisional_without_incremental_evidence(self):
        self.packet['dimensions']['incremental'] = 'not-evaluated'
        result = score(self.packet)
        self.assertIsNone(result['quality'])
        self.assertAlmostEqual(100, result['provisional_quality'])
        self.assertAlmostEqual(90, result['evaluated_weight'])
        self.assertEqual('incomplete', result['classification'])

    def test_critical_shared_error_blocks_publication_without_similarity_gate(self):
        self.packet['claims'][0].update(state='incorrect', critical=True, reason='Source says 7, draft says 8.')
        result = score(self.packet)
        self.assertEqual(['limit'], result['critical_errors'])
        self.assertEqual(0, result['scores']['factual'])
        self.assertEqual('rejected-critical-factual-errors', result['classification'])

    def test_partial_credit_does_not_treat_correct_partial_claim_as_false(self):
        self.packet['claims'][0].update(state='partial', reason='Correct return documented; guard omitted.')
        self.packet['dimensions']['coverage']['contracts_configuration_flows'].update(
            rating='partial', reason='Correct contract with an omitted guard; other rubric areas reviewed separately.')
        result = score(self.packet)
        self.assertEqual(50, result['claim_partial_coverage'])
        self.assertEqual(100, result['factual_claim_accuracy'])
        self.assertAlmostEqual(100 * 2.5 / 3, result['scores']['coverage'])
        self.assertEqual('useful-requires-review', result['classification'])

    def test_unreviewed_claim_inventory_cannot_receive_complete_quality(self):
        self.packet['inventory_complete'] = False
        result = score(self.packet)
        self.assertIsNone(result['quality'])
        self.assertIsNone(result['provisional_quality'])
        self.assertIsNone(result['scores']['factual'])

    def test_pending_judgments_remain_incomplete(self):
        self.packet['claims'][0]['state'] = 'pending'
        self.assertIsNone(score(self.packet)['quality'])

    def test_changed_source_or_artifact_is_rejected(self):
        Path(self.packet['artifacts'][0]['path']).write_text('LIMIT = 8\n')
        with self.assertRaisesRegex(ValueError, 'Artifact changed'):
            score(self.packet)

    def test_evidence_span_is_bound_to_exact_lines(self):
        self.packet['evidence'][0]['quote_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'span hash'):
            score(self.packet)

    def test_positive_ratings_require_real_frozen_evidence(self):
        self.packet['dimensions']['resources']['usefulness_or_justified_absence']['evidence'] = []
        with self.assertRaisesRegex(ValueError, 'require evidence'):
            score(self.packet)

    def test_missing_and_duplicate_claims_cannot_game_the_denominator(self):
        claim = copy.deepcopy(self.packet['claims'][0])
        self.packet['claims'].append(claim)
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            score(self.packet)
        claim.update(id='guard', state='missing', reason='Required guard absent.', evidence=[])
        result = score(self.packet)
        self.assertEqual(50, result['claim_partial_coverage'])
        self.assertEqual(100, result['factual_claim_accuracy'])

    def test_frozen_policy_cannot_be_reweighted_silently(self):
        self.packet['policy_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'policy differs'):
            score(self.packet)

    def test_atomic_credit_exposes_information_hidden_by_strict_groups(self):
        self.packet['claims'][0]['group'] = 'contract'
        missing = copy.deepcopy(self.packet['claims'][0])
        missing.update(id='guard', state='missing', reason='Guard omitted.', evidence=[])
        self.packet['claims'].append(missing)
        result = score(self.packet)
        self.assertEqual(0, result['strict_group_coverage_control'])
        self.assertEqual(50, result['claim_partial_coverage'])
        self.assertEqual(2, result['required_claims'])
        self.assertEqual(1, result['required_groups'])


if __name__ == '__main__':
    unittest.main()
