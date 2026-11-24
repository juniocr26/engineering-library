"""Regression checks for the project-first catalog contract."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.library = Path(self.temp.name) / 'library'
        (self.library / '.git').mkdir(parents=True)
        (self.library / 'tools').mkdir()
        shutil.copyfile(SOURCE / 'tools/check_docs.py', self.library / 'tools/check_docs.py')
        self.write('README.md', '[Catalog](docs/index.md)')
        self.write('README.pt-BR.md', '[Catálogo](docs/index.md)')
        self.write('docs/index.md', '[EN](engineering-library/en/index.md) [PT](engineering-library/pt-br/index.md)')
        for lang in ('en', 'pt-br'):
            prefix = f'docs/engineering-library/{lang}'
            self.write(f'{prefix}/index.md', '[README](README.md) [FAQ](faq/index.md) [ENV](env/index.md)')
            self.write(f'{prefix}/faq/index.md', '[Study](study.md)')
            self.write(f'{prefix}/faq/study.md', '# Questions\n\n### Q001 — Example\n\n**Answer:** Detailed answer.\n\n**Follow-up:** Detail.')
            self.write(f'{prefix}/env/index.md', '# ENV\n\n`EXAMPLE_PORT`\n\nOptional\n\nEmpty falls back.')
            self.write(f'docs/engineering-library/{lang}/bio.md', '---\nid: library\nname: Library\n---\n\nPurpose.\n')
            filename = 'README.md' if lang == 'en' else 'README.pt-BR.md'
            self.write(f'docs/engineering-library/{lang}/README.md', '[Index](index.md)')
        self.write('docs/engineering-library/en/operations/catalog-provenance.json', json.dumps({'projects': {'engineering-library': {'imports': [], 'relocated_interviews': []}}}))
        spec = importlib.util.spec_from_file_location('catalog_under_test', SOURCE / 'tools/check_catalog.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.module.__file__ = str(self.library / 'tools/check_catalog.py')
        self.module.MANIFEST_RELATIVE = 'docs/engineering-library/en/operations/catalog-provenance.json'

    def write(self, relative, body):
        path = self.library / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)

    def run_catalog(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = self.module.main()
        report = json.loads(output.getvalue())
        return status, [finding[0] for finding in report['errors']]

    def test_valid_catalog(self):
        self.assertEqual(self.run_catalog(), (False, []))

    def test_missing_env_is_rejected(self):
        (self.library / 'docs/engineering-library/en/env/index.md').unlink()
        self.assertIn('missing-env-reference', self.run_catalog()[1])

    def test_unknown_root_directory_is_rejected(self):
        (self.library / 'docs/other').mkdir()
        self.assertIn('project-collection-inventory-mismatch', self.run_catalog()[1])

    def test_root_readme_broken_link_is_reported(self):
        self.write('README.md', '[Broken](absent.md)')
        self.assertIn('missing-target', self.run_catalog()[1])

    def test_env_variable_language_mismatch(self):
        self.write('docs/engineering-library/pt-br/env/index.md', '# ENV\n\n`OTHER_PORT`\n\nOptional\n\nEmpty falls back.')
        self.assertIn('env-variable-parity', self.run_catalog()[1])


if __name__ == '__main__':
    unittest.main()
