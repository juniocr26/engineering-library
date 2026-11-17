"""Synthetic setup checks; actual container-path integration is recorded separately."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('mounts', Path(__file__).with_name('prepare_docs_mounts.py'))
mounts = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mounts)


class DocumentationMountSetupTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.parent = self.root / 'siblings'
        self.library = self.project(self.parent, 'library')
        (self.library / 'docs').mkdir()
        (self.library / 'agent').mkdir()

    def project(self, root, name):
        p = root / name
        (p / '.git').mkdir(parents=True)
        return p

    def test_container_paths_generate_host_relative_narrow_mounts(self):
        p = self.project(self.parent, 'sample')
        (p / 'app.py').write_text('OWNER_SENTINEL = True')
        extra = self.root / 'extra'
        second = self.project(extra, 'another')
        out = self.root / 'output'
        result = mounts.prepare(self.library, out, bindings={self.parent: '..', extra: '../../Other Collection'})
        self.assertEqual(result['projects'], 2)
        volumes = json.loads((out / 'mounts.json').read_text())['services']['backend']['volumes']
        self.assertEqual(next(v for v in volumes if v['target'] == '/sources')['source'], '..')
        self.assertTrue(next(v for v in volumes if v['target'] == '/sources')['read_only'])
        self.assertEqual(next(v for v in volumes if v['target'] == '/project-docs/another')['source'], '../../Other Collection/another/docs')
        self.assertTrue((p / 'docs').is_dir() and (second / 'docs').is_dir())
        self.assertEqual((p / 'app.py').read_text(), 'OWNER_SENTINEL = True')
        config = json.loads((out / 'projects.json').read_text())['projects']
        self.assertNotIn('library', [v['slug'] for v in config])
        self.assertEqual(len([v for v in volumes if not v['read_only']]), 3)  # library + two docs destinations

    def test_existing_documentation_is_preserved_and_symlink_destination_rejected(self):
        p = self.project(self.parent, 'sample')
        (p / 'docs').mkdir();f = p / 'docs/manual.md';f.write_text('Human documentation')
        mounts.prepare(self.library, self.root / 'output')
        self.assertEqual(f.read_text(), 'Human documentation')
        q = self.project(self.parent, 'linked')
        (q / 'docs').symlink_to(p / 'docs', target_is_directory=True)
        with self.assertRaises(ValueError):
            mounts.prepare(self.library, self.root / 'other-output')
        self.assertEqual(f.read_text(), 'Human documentation')

    def test_duplicate_project_slugs_rejected_before_destination_creation(self):
        p = self.project(self.parent, 'sample')
        extra = self.root / 'extra';self.project(extra, 'sample')
        with self.assertRaises(ValueError):
            mounts.prepare(self.library, self.root / 'output', bindings={self.parent: '..', extra: '../../Other'})
        self.assertFalse((p / 'docs').exists())

    def test_missing_collection_does_not_create_or_delete_sources(self):
        with self.assertRaises(FileNotFoundError):
            mounts.prepare(self.library, self.root / 'output', bindings={self.root / 'missing': '..'})
        self.assertFalse((self.root / 'missing').exists())

    def test_temporary_catalog_projects_are_not_prepared_as_permanent_sources(self):
        permanent = self.project(self.parent, 'permanent')
        temporary = self.project(self.parent, 'temporary')
        (temporary / 'upstream.md').write_text('OWNER_SENTINEL')
        (self.library / 'docs/.catalog-policy.json').write_text(json.dumps({'schema': 1, 'temporary_projects': ['temporary']}))
        result = mounts.prepare(self.library, self.root / 'output')
        config = json.loads((self.root / 'output/projects.json').read_text())['projects']
        self.assertEqual(result['projects'], 1)
        self.assertEqual([project['slug'] for project in config], ['permanent'])
        self.assertTrue((permanent / 'docs').is_dir())
        self.assertFalse((temporary / 'docs').exists())
        self.assertEqual((temporary / 'upstream.md').read_text(), 'OWNER_SENTINEL')

    def test_invalid_or_symlink_policy_fails_before_creating_destinations(self):
        project = self.project(self.parent, 'sample')
        policy = self.library / 'docs/.catalog-policy.json'
        for data in ({'schema': True, 'temporary_projects': []}, {'schema': 1, 'temporary_projects': ['../unsafe']}, {'schema': 1, 'temporary_projects': ['sample', 'sample']}):
            policy.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                mounts.prepare(self.library, self.root / 'output')
            self.assertFalse((project / 'docs').exists())
            self.assertFalse((self.root / 'output').exists())
        policy.unlink()
        policy.symlink_to(self.root / 'missing-policy')
        with self.assertRaises(ValueError):
            mounts.prepare(self.library, self.root / 'output')
        self.assertFalse((project / 'docs').exists())


if __name__ == '__main__':
    unittest.main()
