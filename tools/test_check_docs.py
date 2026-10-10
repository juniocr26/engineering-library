"""Isolated documentation-validator tests: fixtures only, no applications/services."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('check_docs', Path(__file__).with_name('check_docs.py'))
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class DocumentationValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'demo'
        (self.repo / '.git').mkdir(parents=True)
        self.config = {'repositories': ['demo']}
        for lang, readme in [('en', 'README.md'), ('pt-BR', 'README.pt-BR.md')]:
            self.write(readme, f'# Demo\n\n[Index](docs/{lang}/index.md)\n')
            self.write(f'docs/{lang}/index.md', '# Index\n\n[Guide](guides/start.md)\n[Checklist](operations/completion-checklist.md)\n')
            self.write(f'docs/{lang}/guides/start.md', '# Start\n\n## Repeated\n\n## Repeated\n\n[Local](#repeated-1)\n')
            self.write(f'docs/{lang}/operations/completion-checklist.md', '# Checklist\n')

    def write(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def result(self):
        return checker.validate(self.root, self.config)

    def codes(self):
        return {f['code'] for f in self.result()['findings']}

    def test_valid_tree_is_read_only(self):
        before = {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(self.result()['errors'], 0)
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_missing_repository_and_language_counterpart(self):
        self.config['repositories'].append('absent')
        (self.repo / 'docs/pt-BR/guides/start.md').unlink()
        self.assertTrue({'repository-missing', 'counterpart-missing'} <= self.codes())

    def test_broken_file_anchor_and_reference(self):
        self.write('docs/en/guides/start.md', '# Start\n\n[Missing](missing.md)\n[Anchor](#nope)\n[Ref][undefined]\n')
        self.assertTrue({'link-missing', 'anchor-missing', 'reference-missing'} <= self.codes())

    def test_reference_percent_encoded_path_and_unicode_duplicate_heading(self):
        for lang in checker.LANGS:
            self.write(f'docs/{lang}/guides/space name.md', '# Ação\n\n## Ação\n')
            self.write(f'docs/{lang}/guides/start.md', '# Start\n\n[Ref][ok]\n\n[ok]: <space%20name.md#a%C3%A7%C3%A3o-1>\n')
        self.assertEqual(self.result()['errors'], 0)

    def test_unreachable_and_invalid_category(self):
        for lang in checker.LANGS:
            self.write(f'docs/{lang}/stray.md', '# Stray\n')
        self.assertTrue({'index-unreachable', 'category-invalid'} <= self.codes())

    def test_restricted_links_are_not_read_even_with_dotdot(self):
        restricted = self.write('.env', 'MUST NEVER READ')
        self.write('docs/en/guides/start.md', '# Start\n\n[Env](../../../.env)\n[Escape](../../../.env/../README.md)\n[Outside](../../../../../outside.md)\n')
        original = Path.read_text
        def guarded(path, *args, **kwargs):
            if path == restricted:
                raise AssertionError('Restricted file read')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', guarded):
            result = self.result()
        blocked = [f for f in result['findings'] if f['code'] == 'link-blocked']
        self.assertEqual(len(blocked), 3)
        self.assertTrue(all('not read' in f['detail'] for f in blocked))

    def test_symlink_target_and_directory_never_followed(self):
        outside = self.root.parent / ('docs-outside-' + self.root.name)
        outside.mkdir()
        self.addCleanup(lambda: outside.rmdir())
        file = outside / 'secret.md'
        file.write_text('DO NOT READ')
        self.addCleanup(file.unlink)
        (self.repo / 'docs/en/guides/linked.md').symlink_to(file)
        (self.repo / 'docs/en/linked-folder').symlink_to(outside, target_is_directory=True)
        self.write('docs/en/guides/start.md', '# Start\n\n[Linked](linked.md)\n')
        self.assertTrue({'document-unsafe', 'directory-excluded', 'link-blocked'} <= self.codes())

    def test_source_link_gets_metadata_only(self):
        source = self.write('app.py', 'DO NOT READ')
        self.write('docs/en/guides/start.md', '# Start\n\n[Source](../../../app.py)\n')
        original = Path.read_text
        def guarded(path, *args, **kwargs):
            if path == source:
                raise AssertionError('Application source read')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', guarded):
            self.assertEqual(self.result()['errors'], 0)

    def test_unreadable_utf8_is_finding_not_crash(self):
        (self.repo / 'docs/en/guides/start.md').write_bytes(b'\xff')
        self.assertIn('document-unreadable', self.codes())

    def test_permission_error_is_finding(self):
        target = self.repo / 'docs/en/guides/start.md'
        original = Path.read_text
        def guarded(path, *args, **kwargs):
            if path == target:
                raise PermissionError('test only')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', guarded):
            self.assertIn('document-unreadable', self.codes())

    def test_questions_require_alignment_numbering_answers_followups(self):
        for lang in checker.LANGS:
            self.write(f'docs/{lang}/interviews/demo.md', '### Q001 — Test\n\n**Answer:** Text. Follow-up: reason.\n')
            index = self.repo / f'docs/{lang}/index.md'
            index.write_text(index.read_text() + '[Interview](interviews/demo.md)\n')
        self.assertEqual(self.result()['errors'], 0)
        self.write('docs/pt-BR/interviews/demo.md', '### Q002 — Test\n\nNo answer.\n')
        self.assertTrue({'question-numbering', 'question-language-mismatch', 'question-answer-missing', 'question-followup-missing'} <= self.codes())

    def test_historical_language_exception_requires_reason(self):
        self.write('docs/en/guides/archive.md', '# Archive\n')
        self.config['exceptions'] = {'demo': ['docs/en/guides/archive.md']}
        self.assertIn('counterpart-missing', self.codes())
        self.config['exception_reasons'] = {'demo/docs/en/guides/archive.md': 'Historical artifact'}
        self.assertIn('counterpart-exception', self.codes())
        self.assertNotIn('counterpart-missing', self.codes())

    def test_obsolete_name_and_private_key_marker_are_not_echoed(self):
        self.write('docs/en/guides/start.md', '# Start\n\ntecnical-interview/docs/en\n-----BEGIN PRIVATE KEY-----\nsecret-body\n')
        report = self.result()
        self.assertTrue({'obsolete-library-name', 'private-key-marker'} <= {f['code'] for f in report['findings']})
        self.assertNotIn('secret-body', json.dumps(report))

    def test_fences_and_inline_code_are_not_links(self):
        self.write('docs/en/guides/start.md', '# Start\n\n```md\n[Fake](missing.md)\n## Hidden\n```\n\n`[Fake](missing.md)`\n')
        self.assertNotIn('link-missing', self.codes())
        self.assertNotIn('hidden', checker.anchors((self.repo / 'docs/en/guides/start.md').read_text()))

    def test_empty_unknown_category_and_retained_number_gap(self):
        (self.repo / 'docs/en/misc').mkdir()
        self.write('docs/en/interviews/demo.md', '## 1 First\n\n## 3 Third\n')
        self.assertTrue({'category-empty', 'category-invalid', 'legacy-numbering-invalid'} <= self.codes())

    def test_linked_workspace_is_rejected(self):
        link = self.root.parent / ('workspace-link-' + self.root.name)
        link.symlink_to(self.root, target_is_directory=True)
        self.addCleanup(link.unlink)
        report = checker.validate(link, self.config)
        self.assertEqual(report['findings'][0]['code'], 'workspace-unsafe')

    def test_cli_json_and_nonzero_on_errors(self):
        tools = self.repo / 'tools'
        tools.mkdir()
        config = tools / 'docs_manifest.json'
        config.write_text(json.dumps(self.config))
        command = [sys.executable, '-B', str(Path(checker.__file__)), '--workspace', str(self.root), '--config', str(config)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['errors'], 0)
        self.write('docs/en/guides/start.md', '# Start\n[Broken](missing.md)\n')
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertGreater(json.loads(result.stdout)['errors'], 0)

    def test_cli_rejects_unsafe_config_without_read(self):
        restricted = self.write('.env', 'secret')
        command = [sys.executable, '-B', str(Path(checker.__file__)), '--workspace', str(self.root), '--config', str(restricted)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['findings'][0]['code'], 'config-unsafe')


if __name__ == '__main__':
    unittest.main()
