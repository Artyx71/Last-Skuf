#!/usr/bin/env python3
"""Controller handoff only. Commits local authorized files; never pushes or changes gates.

The executor cannot run this successfully because the shared gitdir is read-only.
Controller must first perform privacy inspection and verify its branch ownership.
"""
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[3]
manifest=json.loads((Path(__file__).parent/'staging_manifest.json').read_text())
branch=subprocess.run(['git','branch','--show-current'],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
if branch!=manifest['branch']:raise SystemExit('Refusing to commit outside assigned phase branch')
if subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode:raise SystemExit('Existing staged changes require controller inspection')
for group in manifest['groups']:
 paths=group['paths']
 if not paths:continue
 for p in paths:
  path=Path(p)
  if path.is_absolute() or '..' in path.parts or any(part in {'references','.tools','.git','.autopilot','private','build'} for part in path.parts):raise SystemExit('Unsafe staging path: '+p)
  if (ROOT/path).stat().st_size>100_000_000:raise SystemExit('Oversize file: '+p)
 subprocess.run(['git','add','--',*paths],cwd=ROOT,check=True)
 subprocess.run(['python3','tools/check_privacy.py'],cwd=ROOT,check=True)
 subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True)
 subprocess.run(['git','commit','-m',group['message']],cwd=ROOT,check=True)
print('Local source/evidence commits complete. Independent exact-SHA Lead and CI remain required. No push/merge performed.')
