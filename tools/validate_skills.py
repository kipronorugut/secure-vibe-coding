#!/usr/bin/env python3
"""Check portable Agent Skills syntax with only the Python standard library."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
# Relative paths a SKILL.md points to inside its own folder, e.g. `references/foo.md`
LOCAL_REF = re.compile(r'`((?:references|scripts|assets)/[A-Za-z0-9._/-]+)`')


def skill_dirs(root: Path = ROOT) -> list[Path]:
    base = root / 'skills'
    return sorted(p for p in base.iterdir() if p.is_dir()) if base.exists() else []


def validate(root: Path = ROOT) -> list[str]:
    errors = []
    dirs = skill_dirs(root)
    if not dirs:
        errors.append('No skills found')
    for folder in dirs:
        f = folder / 'SKILL.md'
        if not f.is_file():
            errors.append(f'{folder.name}: SKILL.md missing')
            continue
        content = f.read_text(encoding='utf8')
        match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not match:
            errors.append(f'{folder.name}: YAML frontmatter missing')
            continue
        front = match.group(1)
        info = {}
        for line in front.splitlines():
            if line and not line.startswith((' ', '\t')) and ':' in line:
                k, v = line.split(':', 1)
                info[k.strip()] = v.strip().strip('"\'')
        name = info.get('name', '')
        desc = info.get('description', '')
        if not NAME.fullmatch(name) or len(name) > 64 or name != folder.name:
            errors.append(f'{folder.name}: invalid/mismatched name')
        if not (1 <= len(desc) <= 1024):
            errors.append(f'{folder.name}: description missing or too long')
        if len(content) < 500:
            errors.append(f'{folder.name}: instructions too short for meaningful workflow')
        # Every bundled file the instructions point to must exist.
        for ref in sorted(set(LOCAL_REF.findall(content))):
            if not (folder / ref).is_file():
                errors.append(f'{folder.name}: referenced file missing: {ref}')
        # Helper scripts must declare an interpreter.
        scripts = folder / 'scripts'
        if scripts.is_dir():
            for script in sorted(scripts.iterdir()):
                if script.suffix == '.sh' and not script.read_text(encoding='utf8').startswith('#!'):
                    errors.append(f'{folder.name}: {script.name} missing shebang')
    return errors


if __name__ == '__main__':
    errs = validate()
    if errs:
        for err in errs:
            print('FAIL:', err, file=sys.stderr)
        raise SystemExit(1)
    print(f'PASS: {len(skill_dirs())} portable skill definitions validated')
