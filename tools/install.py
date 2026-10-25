#!/usr/bin/env python3
"""Offline, no-overwrite project or user installer for Secure Vibe Coding."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'skills'
DESTS = {'cursor': '.cursor/skills', 'claude': '.claude/skills', 'codex': '.agents/skills'}
USERS = {'cursor': '.cursor/skills', 'claude': '.claude/skills', 'codex': '.agents/skills'}

def install(agent: str, scope: str, project: Path | None, selection: list[str]) -> tuple[int,int]:
    if scope == 'project':
        if project is None:
            raise ValueError('--project is required for --scope project')
        if not project.is_dir():
            raise ValueError(f'Project directory does not exist: {project}')
        target = project / DESTS[agent]
    else:
        target = Path.home() / USERS[agent]
    # Refuse symlinked path components to prevent unintended writes outside target.
    for node in (target, *target.parents):
        if node.is_symlink():
            raise ValueError(f'Refusing destination through a symlink: {node}')
    available = {p.name: p for p in SOURCE.iterdir() if (p / 'SKILL.md').is_file()}
    names = selection or sorted(available)
    unknown = [n for n in names if n not in available]
    if unknown:
        raise ValueError('Unknown skill(s): ' + ', '.join(unknown))
    target.mkdir(parents=True, exist_ok=True)
    installed, skipped = 0, 0
    for name in names:
        dst = target / name
        if dst.exists() or dst.is_symlink():
            print(f'SKIP (already exists): {dst}')
            skipped += 1
            continue
        shutil.copytree(available[name], dst)
        print(f'INSTALLED: {dst}')
        installed += 1
    return installed, skipped

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', required=True, choices=sorted(DESTS))
    parser.add_argument('--scope', choices=['project','user'], default='project')
    parser.add_argument('--project', type=Path, help='Target application path for project installs')
    parser.add_argument('--skill', action='append', default=[], help='Skill name; repeat to select multiple')
    args = parser.parse_args()
    try:
        installed, skipped = install(args.agent, args.scope, args.project, args.skill)
    except (ValueError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    print(f'Complete: {installed} installed, {skipped} skipped. Inspect installed SKILL.md before use.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
