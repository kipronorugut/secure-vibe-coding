#!/usr/bin/env python3
"""Check portable Agent Skills syntax with only the Python standard library."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

def validate(root: Path = ROOT) -> list[str]:
    errors = []
    dirs = sorted((root / 'skills').iterdir()) if (root / 'skills').exists() else []
    if not dirs:
        errors.append('No skills found')
    for folder in dirs:
        if not folder.is_dir():
            continue
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
        name = info.get('name','')
        desc = info.get('description','')
        if not NAME.fullmatch(name) or len(name)>64 or name!=folder.name:
            errors.append(f'{folder.name}: invalid/mismatched name')
        if not (1<=len(desc)<=1024):
            errors.append(f'{folder.name}: description missing or too long')
        if len(content) < 500:
            errors.append(f'{folder.name}: instructions too short for meaningful workflow')
    return errors

if __name__ == '__main__':
    errs = validate()
    if errs:
        for err in errs: print('FAIL:', err, file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS: {sum(p.is_dir() and (p / 'SKILL.md').is_file() for p in (ROOT / 'skills').iterdir())} portable skill definitions validated")
