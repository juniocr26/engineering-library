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
        self.write('docs/index.md', '[EN](projects/library/docs/en/index.md) [PT](projects/library/docs/pt-BR/index.md) [Intro](projects/library/README.md) [Intro PT](projects/library/README.pt-BR.md)')
        for lang in ('en', 'pt-BR'):
            prefix = f'docs/projects/library/docs/{lang}'
            self.write(f'{prefix}/index.md', '[FAQ](faq/index.md) [ENV](env/index.md)')
            self.write(f'{prefix}/faq/index.md', '# FAQ\n\n### Q001 — Example\n\n**Answer:** Detailed answer.\n\n**Follow-up:** Detail.')
            self.write(f'{prefix}/env/index.md', '# ENV\n\n`EXAMPLE_PORT`\n\nOptional\n\nEmpty falls back.')
            filename = 'README.md' if lang == 'en' else 'README.pt-BR.md'
            self.write(f'docs/projects/library/{filename}', f'[Index](docs/{lang}/index.md)')
        self.write('docs/catalog-provenance.json', json.dumps({'projects': {'library': {'imports': [], 'relocated_interviews': []}}}))
        spec = importlib.util.spec_from_file_location('catalog_under_test', SOURCE / 'docs/validation/check_catalog.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.module.__file__ = str(self.library / 'docs/validation/check_catalog.py')

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
        (self.library / 'docs/projects/library/docs/en/env/index.md').unlink()
        self.assertIn('missing-env-reference', self.run_catalog()[1])

    def test_intermediate_faq_is_rejected(self):
        self.write('docs/projects/library/docs/en/faq/index.md', '[Study](study.md)')
        self.write('docs/projects/library/docs/en/faq/study.md', '# Questions\n\n**Answer:** Detail.')
        errors = self.run_catalog()[1]
        self.assertIn('faq-without-answers', errors)
        self.assertIn('duplicate-or-nested-faq', errors)

    def test_root_language_directory_is_rejected(self):
        (self.library / 'docs/en').mkdir()
        self.assertIn('forbidden-root-language-directory', self.run_catalog()[1])

    def test_root_readme_broken_link_is_reported(self):
        self.write('README.md', '[Broken](absent.md)')
        self.assertIn('missing-target', self.run_catalog()[1])

    def test_env_variable_language_mismatch(self):
        self.write('docs/projects/library/docs/pt-BR/env/index.md', '# ENV\n\n`OTHER_PORT`\n\nOptional\n\nEmpty falls back.')
        self.assertIn('env-variable-parity', self.run_catalog()[1])


if __name__ == '__main__':
    unittest.main()
