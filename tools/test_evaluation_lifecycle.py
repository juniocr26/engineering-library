import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('lifecycle', Path(__file__).with_name('evaluation_lifecycle.py'))
lifecycle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lifecycle)


class EvaluationRecoveryTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.docs = self.base / 'project/docs'
        self.docs.mkdir(parents=True)
        (self.docs / 'manual.md').write_bytes(b'Owner original\r\n')
        (self.docs / 'manual.md').chmod(0o640)
        self.session = self.base / 'private/session'
        self.before = lifecycle.inventory(self.docs)

    def experiment(self):
        lifecycle.capture(self.session, [self.docs])
        (self.docs / 'manual.md').write_text('Experimental replacement')
        (self.docs / 'img').mkdir()
        (self.docs / 'img/new.webp').write_bytes(b'synthetic image fixture')
        lifecycle.seal(self.session)

    def test_restore_preserves_bytes_modes_media_and_is_idempotent(self):
        (self.docs / 'original.webp').write_bytes(b'original media bytes')
        before = lifecycle.inventory(self.docs)
        self.experiment()
        lifecycle.restore(self.session)
        self.assertEqual(before, lifecycle.inventory(self.docs))
        lifecycle.restore(self.session)
        self.assertEqual(before, lifecycle.inventory(self.docs))
        self.assertEqual((self.session / 'originals/0/original.webp').read_bytes(), b'original media bytes')

    def test_human_edit_aborts_entire_set_before_writes(self):
        self.experiment()
        (self.docs / 'img/new.webp').write_bytes(b'new owner edit')
        before = lifecycle.inventory(self.docs)
        with self.assertRaisesRegex(ValueError, 'Ownership conflict'):
            lifecycle.restore(self.session)
        self.assertEqual(before, lifecycle.inventory(self.docs))

    def test_interrupted_restore_can_resume(self):
        self.experiment()
        original = lifecycle.atomic
        calls = []
        def interrupt(path, data, mode=0o600):
            original(path, data, mode)
            if path == self.docs / 'manual.md' and not calls:
                calls.append(path)
                raise OSError('interrupted after original rename')
        with patch.object(lifecycle, 'atomic', interrupt):
            with self.assertRaisesRegex(OSError, 'interrupted'):
                lifecycle.restore(self.session)
        lifecycle.restore(self.session)
        self.assertEqual(self.before, lifecycle.inventory(self.docs))

    def test_corrupt_backup_aborts_before_writes(self):
        self.experiment()
        (self.session / 'originals/0/manual.md').write_bytes(b'corrupt')
        before = lifecycle.inventory(self.docs)
        with self.assertRaisesRegex(ValueError, 'Corrupt recovery'):
            lifecycle.restore(self.session)
        self.assertEqual(before, lifecycle.inventory(self.docs))

    def test_unsealed_run_cannot_delete_unclassified_files(self):
        lifecycle.capture(self.session, [self.docs])
        (self.docs / 'new.md').write_text('unclassified')
        with self.assertRaisesRegex(ValueError, 'Seal ownership'):
            lifecycle.restore(self.session)
        self.assertTrue((self.docs / 'new.md').exists())

    def test_missing_tree_restored_to_missing_without_deleting_repository(self):
        missing = self.docs.parent / 'docs_codex'
        lifecycle.capture(self.session, [missing])
        missing.mkdir()
        (missing / 'reference.md').write_text('temporary')
        lifecycle.seal(self.session)
        lifecycle.restore(self.session)
        self.assertFalse(missing.exists())
        self.assertTrue(self.docs.is_dir())

    def test_symlinks_and_existing_recovery_directory_are_rejected(self):
        lifecycle.capture(self.session, [self.docs])
        with self.assertRaises(FileExistsError):
            lifecycle.capture(self.session, [self.docs])
        (self.docs / 'link').symlink_to(self.base)
        with self.assertRaisesRegex(ValueError, 'Symlink rejected'):
            lifecycle.seal(self.session)


if __name__ == '__main__':
    unittest.main()
