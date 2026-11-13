#!/usr/bin/env python3
"""Unpack a pinned ImageIO-maintained FFmpeg wheel into .tools; no pip/system/sudo."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
LOCK={'publisher':'imageio-ffmpeg maintainers, PyPI0.6.0',
 'url':'https://files.pythonhosted.org/packages/a0/2d/43c8522a2038e9d0e7dbdf3a61195ecc31ca576fb1527a528c877e87d973/imageio_ffmpeg-0.6.0-py3-none-manylinux2014_x86_64.whl',
 'sha256':'c7e46fcec401dd990405049d2e2f475e2b397779df2519b544b8aab515195282',
 'metadata':'https://pypi.org/project/imageio-ffmpeg/0.6.0/','scope':'build/test tool only, not exported game media'}

def main():
 if platform.system()!='Linux' or platform.machine() not in ['x86_64','AMD64']:
  raise SystemExit('Pinned media tool supports Linuxx86_64; unsupported platform is BLOCKED')
 dest=ROOT/'.tools/ci-media';dest.mkdir(parents=True,exist_ok=True)
 archive=dest/'imageio_ffmpeg.whl'
 if not archive.exists():urllib.request.urlretrieve(LOCK['url'],archive)
 if hashlib.sha256(archive.read_bytes()).hexdigest()!=LOCK['sha256']:
  raise SystemExit('FFmpeg wheel checksum mismatch; refusing execution')
 bindir=dest/'bin';bindir.mkdir(exist_ok=True)
 with zipfile.ZipFile(archive) as package:
  binaries=[n for n in package.namelist() if n.startswith('imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-')]
  if len(binaries)!=1:raise SystemExit('Unexpected wheel binary inventory')
  executable=bindir/'ffmpeg';executable.write_bytes(package.read(binaries[0]));executable.chmod(0o755)
  for name in package.namelist():
   if 'LICENSE' in name.upper() or 'COPYING' in name.upper():
    (dest/Path(name).name).write_bytes(package.read(name))
 version=subprocess.check_output([str(executable),'-version'],text=True).splitlines()[0]
 (dest/'provenance.json').write_text(json.dumps({**LOCK,'binary_sha256':hashlib.sha256(executable.read_bytes()).hexdigest(),'version':version},indent=2)+'\n')
 if os.environ.get('GITHUB_PATH'):
  with open(os.environ['GITHUB_PATH'],'a') as stream:stream.write(str(bindir)+'\n')
 print(version);print('Verified user-local media tool:',bindir)

if __name__=='__main__':main()
