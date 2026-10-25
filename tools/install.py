#!/usr/bin/env python3
"""Offline project or user installer for Secure Vibe Coding.

Refuses to overwrite installed skills unless --update is given, and then only
replaces folders that already hold the same skill."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'skills'
DESTS = {'cursor': '.cursor/skills', 'claude': '.claude/skills', 'codex': '.agents/skills'}
USERS = {'cursor': '.cursor/skills', 'claude': '.claude/skills', 'codex': '.agents/skills'}

def install(agent: str, scope: str, project: Path | None, selection: list[str],
            update: bool = False) -> tuple[int,int]:
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
        if dst.is_symlink():
            print(f'SKIP (symlink, not touched): {dst}')
            skipped += 1
            continue
        if dst.exists():
            if not update:
                print(f'SKIP (already exists; use --update to replace): {dst}')
                skipped += 1
                continue
            if not _is_same_skill(dst, name):
                print(f'SKIP (existing folder is not the {name} skill): {dst}')
                skipped += 1
                continue
            # Keep the previous skill intact as a backup, including user edits.
            suffix = uuid.uuid4().hex
            staging = target / f'.{name}.staging-{suffix}'
            backup = target / f'.{name}.backup-{suffix}'
            shutil.copytree(available[name], staging)
            try:
                dst.rename(backup)
                try:
                    staging.rename(dst)
                except OSError:
                    backup.rename(dst)  # Roll back if replacement fails.
                    raise
            finally:
                if staging.exists():
                    shutil.rmtree(staging)
            print(f'UPDATED: {dst} (previous version backed up at {backup})')
            installed += 1
            continue
        shutil.copytree(available[name], dst)
        print(f'INSTALLED: {dst}')
        installed += 1
    return installed, skipped

def _is_same_skill(folder: Path, name: str) -> bool:
    """True only if folder contains a SKILL.md whose frontmatter name matches."""
    skill_md = folder / 'SKILL.md'
    if not skill_md.is_file():
        return False
    for line in skill_md.read_text(encoding='utf8').splitlines()[1:20]:
        if line.startswith('name:'):
            return line.split(':', 1)[1].strip().strip('"\'') == name
    return False

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', required=True, choices=sorted(DESTS))
    parser.add_argument('--scope', choices=['project','user'], default='project')
    parser.add_argument('--project', type=Path, help='Target application path for project installs')
    parser.add_argument('--skill', action='append', default=[], help='Skill name; repeat to select multiple')
    parser.add_argument('--update', action='store_true', help='Replace previously installed copies of these skills with this version')
    args = parser.parse_args()
    try:
        installed, skipped = install(args.agent, args.scope, args.project, args.skill, args.update)
    except (ValueError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    print(f'Complete: {installed} installed or updated, {skipped} skipped. Inspect installed SKILL.md before use.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
