import tempfile
import unittest
from pathlib import Path
from check_catalog import project_directories


class ProjectInventoryTest(unittest.TestCase):
    def test_shared_assets_and_recovery_are_excluded_but_unknown_projects_are_visible(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ['img', '.docs-state', '.evaluations', 'known-project', 'unexpected-project']:
                (root / name).mkdir()
            (root / 'index.md').write_text('# Catalog\n')
            self.assertEqual({'known-project', 'unexpected-project'}, project_directories(root))

    def test_symlink_is_not_a_catalog_project(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'actual-project').mkdir()
            (root / 'alias-project').symlink_to(root / 'actual-project', target_is_directory=True)
            self.assertEqual({'actual-project'}, project_directories(root))
