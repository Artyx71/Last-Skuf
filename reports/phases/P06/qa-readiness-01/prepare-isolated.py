"""Reproduce a ROOT-only readiness fixture. Never modifies production WORK."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[4];WORK=ROOT/'.autopilot/worktrees/P06'
p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve()
assert out.parent==ROOT/'reports/phases/P06' and not out.exists(),'Use a fresh ROOT reports directory'
out.mkdir(parents=True);dest=out/'isolated-project/game'
files={str(f.relative_to(WORK)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((WORK/'game').rglob('*')) if f.is_file() and '.godot' not in f.relative_to(WORK/'game').parts}
(out/'project-source-before.json').write_text(json.dumps(files,indent=2)+'\n');shutil.copytree(WORK/'game',dest,symlinks=False)
assert all(hashlib.sha256((out/'isolated-project'/rel).read_bytes()).hexdigest()==h for rel,h in files.items())
for name in ['run-isolated.py','qa_readiness_adversarial.gd']:shutil.copyfile(Path(__file__).parent/name,out/name)
shutil.copyfile(out/'qa_readiness_adversarial.gd',dest/'tests/qa_readiness_adversarial.gd')
(out/'copy-validation.json').write_text(json.dumps({'game_source_files':len(files),'all_source_files_byte_exact':True,'production_game_opened_by_engine':False},indent=2)+'\n')
print('Prepared ROOT-only copy. Run copied run-isolated.py readiness character_readiness_test.gd, then adversarial qa_readiness_adversarial.gd sequentially.')
