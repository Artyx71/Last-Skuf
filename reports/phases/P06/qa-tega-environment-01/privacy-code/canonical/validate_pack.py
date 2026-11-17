#!/usr/bin/env python3
"""Offline integrity checker, safe to run before unpacked package is shared."""
import pathlib, json, hashlib, sys
r=pathlib.Path(__file__).resolve().parents[1]
manifest=json.loads((r/'assets/references/manifest.json').read_text('utf-8'))
errors=[]
for item in manifest:
 p=r/item['path']
 if not p.exists(): errors.append('Missing '+str(p)); continue
 digest=hashlib.sha256(p.read_bytes()).hexdigest()
 if digest!=item['sha256']: errors.append('Hash mismatch '+str(p))
for required in ['AGENTS.md','prompts/CODEX_MASTER_PROMPT.md','agents/LEAD_REVIEWER.md','specs/GAMEPLAY_SPEC.md','specs/STORY_SPEC.md','specs/AUDIO_SPEC.md','specs/DIALOGUE_SPEC.md','docs/ART_BIBLE.md','docs/TECH_ARCHITECTURE.md','automation/REVIEW_LOOP.md']:
 if not (r/required).is_file(): errors.append('Missing '+required)
print(f'References: {len(manifest)}, errors: {len(errors)}')
for e in errors: print('FAIL:',e)
sys.exit(bool(errors))
