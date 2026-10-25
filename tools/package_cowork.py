#!/usr/bin/env python3
"""Build one ZIP archive per skill for Claude custom-skill upload."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'skills'
DIST = ROOT / 'dist'

def package() -> list[Path]:
    DIST.mkdir(exist_ok=True)
    out = []
    for skill in sorted(SKILLS.iterdir()):
        if not skill.is_dir() or not (skill / 'SKILL.md').is_file():
            continue
        archive = DIST / f'{skill.name}.zip'
        with ZipFile(archive,'w',ZIP_DEFLATED) as z:
            for path in sorted(skill.rglob('*')):
                if path.is_file():
                    z.write(path, arcname=Path(skill.name) / path.relative_to(skill))
        out.append(archive)
        print('BUILT:', archive)
    return out

if __name__ == '__main__':
    package()
