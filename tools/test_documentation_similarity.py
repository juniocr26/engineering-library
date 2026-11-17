import copy
import json
from pathlib import Path
import tempfile
import unittest
from documentation_similarity import PROTOCOL,sha,score,normalize

class ComparisonAcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.packet={'protocol_sha256':sha(json.dumps(PROTOCOL,sort_keys=True).encode()),'scope':'component','source_revision':'source-1','reference_revision':'reference-1','candidate_revision':'candidate-1','feedback_assisted':False,
                     'artifacts':{},'claims':[{'id':'C1','reference':'supported','candidate':'supported','equivalent':True,'bilingual':True,'evidence':['E1']}],
                     'required_topics':['contract'],'covered_topics':['contract'],'required_sections':['behavior'],'mapped_sections':['behavior'],'inventory_complete':True,'leakage_check':'passed','critical_errors':[]}
        source=Path(self.tmp.name)/'source.cpp';source.write_text('float ease(float t) { return t*t; }\n')
        self.packet['evidence']=[{'id':'E1','path':str(source),'source_sha256':sha(source.read_bytes()),'line_start':1,'line_end':1,'quote_sha256':sha(source.read_bytes())}]
        for side in ['reference','candidate']:
            self.packet['artifacts'][side]={}
            for lang in ['en','pt-br']:
                p=Path(self.tmp.name)/f'{side}-{lang}.md'
                p.write_text(' '.join(f'word{n}' for n in range(60)))
                self.packet['artifacts'][side][lang]={'path':str(p),'sha256':sha(p.read_bytes())}
    def test_full_review_with_frozen_matching_artifacts(self):
        result=score(self.packet)
        self.assertEqual(100,result['composite']);self.assertEqual('accepted',result['acceptance']);self.assertEqual('component',result['scope'])
    def test_shared_critical_error_is_rejected_even_with_identical_text(self):
        c=self.packet['claims'][0];c['reference']='unsupported';c['candidate']='unsupported';self.packet['critical_errors']=['invented persistence guarantee']
        result=score(self.packet)
        self.assertEqual(100,result['scores']['textual']);self.assertIsNone(result['scores']['semantic']);self.assertEqual('rejected',result['acceptance']);self.assertEqual(100,result['unsupported_claim_rate'])
    def test_missing_review_cannot_become_perfect(self):
        self.packet['inventory_complete']=False
        result=score(self.packet)
        self.assertIsNone(result['composite']);self.assertEqual('incomplete',result['acceptance'])
    def test_covered_component_does_not_fill_missing_project_topics(self):
        self.packet['scope']='project';self.packet['required_topics']=[f'module{n}' for n in range(20)];self.packet['covered_topics']=['module0']
        result=score(self.packet)
        self.assertEqual(5,result['scores']['coverage']);self.assertLess(result['composite'],95)
    def test_supported_extra_claim_is_not_a_semantic_penalty(self):
        self.packet['claims'].append({'id':'C2','reference':'absent','candidate':'supported','equivalent':None,'bilingual':True,'evidence':['E1']})
        self.assertEqual(100,score(self.packet)['scores']['semantic'])
    def test_frozen_artifact_tampering_is_detected(self):
        Path(self.packet['artifacts']['candidate']['en']['path']).write_text('changed')
        with self.assertRaises(ValueError):score(self.packet)
    def test_unreviewed_translation_prevents_composite(self):
        self.packet['claims'][0]['bilingual']=None
        self.assertIsNone(score(self.packet)['composite'])
    def test_duplicate_topics_cannot_inflate_denominator(self):
        self.packet['required_topics']=['contract','contract']
        with self.assertRaises(ValueError):score(self.packet)
    def test_source_quotes_cannot_inflate_textual_similarity(self):
        self.assertEqual(normalize('A concrete fact.\n\n    return x * x;\n'),normalize('A concrete fact.'))
        self.assertEqual([],normalize('```cpp\nreturn x;\n```\n\n    return y;\n'))
    def test_code_only_artifacts_produce_incomplete_textual_score(self):
        for side in self.packet['artifacts'].values():
            for spec in side.values():
                path=Path(spec['path']);path.write_text('    return x;\n');spec['sha256']=sha(path.read_bytes())
        result=score(self.packet)
        self.assertIsNone(result['scores']['textual']);self.assertIsNone(result['composite'])
    def test_invalid_citation_cannot_pass_factual_gate(self):
        self.packet['evidence'][0]['line_end']=99
        with self.assertRaises(ValueError):score(self.packet)
    def test_owner_acceptance_is_preserved_separately(self):
        self.packet['owner_acceptance']='approved as useful';self.packet['critical_errors']=['wrong responsibility']
        result=score(self.packet)
        self.assertEqual('approved as useful',result['owner_acceptance']);self.assertEqual('rejected',result['acceptance'])

if __name__=='__main__':unittest.main()
