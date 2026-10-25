import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from validate_skills import validate
from install import install
from package_cowork import package
from zipfile import ZipFile

class ToolkitTests(unittest.TestCase):
    def test_valid_skills(self):
        self.assertEqual(validate(ROOT), [])

    def test_installer_is_non_overwriting(self):
        with tempfile.TemporaryDirectory() as path:
            project = Path(path)
            first = install('cursor','project',project,['vibe-security-check'])
            second = install('cursor','project',project,['vibe-security-check'])
            self.assertEqual(first,(1,0))
            self.assertEqual(second,(0,1))
            self.assertTrue((project/'.cursor/skills/vibe-security-check/SKILL.md').is_file())

    def test_zip_has_one_skill_root(self):
        for archive in package():
            with ZipFile(archive) as z:
                self.assertIn(f'{archive.stem}/SKILL.md', z.namelist())
                self.assertEqual(sum(n.endswith('/SKILL.md') for n in z.namelist()), 1)

if __name__ == '__main__':
    unittest.main()
