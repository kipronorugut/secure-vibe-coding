import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from validate_skills import validate, skill_dirs
from install import install
from package_cowork import package
from zipfile import ZipFile

INVENTORY = ROOT / 'skills' / 'cve-to-pr-remediation' / 'scripts' / 'inventory.sh'


class ToolkitTests(unittest.TestCase):
    def test_valid_skills(self):
        self.assertEqual(validate(ROOT), [])

    def test_seven_skills_including_remediation(self):
        skills = sorted(p.name for p in (ROOT / 'skills').iterdir() if (p / 'SKILL.md').is_file())
        self.assertEqual(len(skills), 7)
        self.assertIn('cve-to-pr-remediation', skills)
        self.assertIn('supabase-firebase-hardening', skills)
        remediation = (ROOT / 'skills/cve-to-pr-remediation/SKILL.md').read_text(encoding='utf8')
        for requirement in ('G1 — Version evidence', 'G6 — Deployed-state verification',
                            'UNVERIFIED ADVISORY', 'explicit approval',
                            'Compromised release', 'scripts/inventory.sh', 'references/advisories.md'):
            self.assertIn(requirement, remediation)

    def test_validator_flags_missing_reference(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            skill = root / 'skills' / 'demo-skill'
            skill.mkdir(parents=True)
            body = 'x' * 600
            (skill / 'SKILL.md').write_text(
                '---\nname: demo-skill\ndescription: Demo.\n---\n'
                f'See `references/missing.md`.\n{body}\n', encoding='utf8')
            errors = validate(root)
            self.assertTrue(any('referenced file missing' in e for e in errors), errors)

    def test_installer_is_non_overwriting(self):
        with tempfile.TemporaryDirectory() as path:
            project = Path(path)
            first = install('cursor', 'project', project, ['vibe-security-check'])
            second = install('cursor', 'project', project, ['vibe-security-check'])
            self.assertEqual(first, (1, 0))
            self.assertEqual(second, (0, 1))
            self.assertTrue((project / '.cursor/skills/vibe-security-check/SKILL.md').is_file())

    def test_installer_update_replaces_same_skill_only(self):
        with tempfile.TemporaryDirectory() as path:
            project = Path(path)
            install('codex', 'project', project, ['secrets-hygiene'])
            installed = project / '.agents/skills/secrets-hygiene'
            (installed / 'stale.txt').write_text('old', encoding='utf8')
            self.assertEqual(install('codex', 'project', project, ['secrets-hygiene'], update=True), (1, 0))
            self.assertFalse((installed / 'stale.txt').exists())
            self.assertTrue((installed / 'references/client-and-tool-exposure.md').is_file())
            # A same-named folder that is not this skill is left alone.
            other = project / '.agents/skills/cve-to-pr-remediation'
            other.mkdir(parents=True)
            (other / 'notes.txt').write_text('mine', encoding='utf8')
            self.assertEqual(install('codex', 'project', project, ['cve-to-pr-remediation'], update=True), (0, 1))
            self.assertTrue((other / 'notes.txt').exists())

    def test_zip_has_one_skill_root(self):
        for archive in package():
            with ZipFile(archive) as z:
                self.assertIn(f'{archive.stem}/SKILL.md', z.namelist())
                self.assertEqual(sum(n.endswith('/SKILL.md') for n in z.namelist()), 1)


@unittest.skipUnless(shutil.which('bash'), 'bash not available')
class InventoryScriptTests(unittest.TestCase):
    """Offline checks of the read-only cve-to-pr-remediation inventory helper on synthetic fixtures."""

    def run_inventory(self, files: dict[str, str]) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as path:
            project = Path(path)
            for rel, text in files.items():
                target = project / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding='utf8')
            result = subprocess.run(['bash', str(INVENTORY), str(project)],
                                    capture_output=True, text=True, timeout=120)
            return result.returncode, result.stdout

    def project_lines(self, output: str, tag: str) -> list[str]:
        # Only findings about fixture files, not the machine running the tests.
        return [l for l in output.splitlines() if f'[{tag}]' in l and './' in l]

    def test_flags_vulnerable_and_compromised_pins(self):
        code, out = self.run_inventory({
            'Dockerfile': 'FROM node:24.22.0-alpine\n',
            'web/Dockerfile': 'FROM php:8.4.20-apache\n',
            '.nvmrc': '20\n',
            'requirements.txt': 'litellm==1.107.0\nbrotli==1.1.0\n',
            'api/client.js': 'new https.Agent({ rejectUnauthorized: false });\n',
        })
        self.assertEqual(code, 1)
        vulnerable = '\n'.join(self.project_lines(out, 'VULNERABLE'))
        self.assertIn('Node 24.22.0', vulnerable)
        self.assertIn('PHP 8.4.20', vulnerable)
        self.assertIn('brotli 1.1.0', vulnerable)
        self.assertTrue(self.project_lines(out, 'EOL'))
        self.assertTrue(self.project_lines(out, 'COMPROMISED'))
        self.assertIn('[DISABLED-TLS]', out)

    def test_fixed_versions_are_not_flagged(self):
        _, out = self.run_inventory({
            'Dockerfile': 'FROM node:24.22.1-alpine\n',
            'requirements.txt': 'litellm==1.106.2\nbrotli==1.2.1\n',
        })
        for tag in ('VULNERABLE', 'COMPROMISED', 'EOL'):
            self.assertEqual(self.project_lines(out, tag), [], out)


if __name__ == '__main__':
    unittest.main()
