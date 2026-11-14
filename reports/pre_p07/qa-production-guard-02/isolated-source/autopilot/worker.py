#!/usr/bin/env python3
"""One bounded subprocess; inherits controller flock, persists a completion receipt."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def atomic(path, data):
    path=Path(path); temp=path.with_suffix('.tmp')
    with temp.open('w') as stream:
        json.dump(data,stream,indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    os.replace(temp,path)


def identity(pid):
    try:
        text=Path(f'/proc/{pid}/stat').read_text()
        return {'pid':pid,'start_ticks':text.rsplit(')',1)[1].split()[19],
                'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
    except (OSError,IndexError):
        return {'pid':pid,'start_ticks':None,'boot_id':None}


def main():
    job=json.loads(Path(sys.argv[1]).read_text()); lock_fd=int(sys.argv[2]); stopped=False
    def stop(_sig,_frame):
        nonlocal stopped
        stopped=True
    signal.signal(signal.SIGTERM,stop); signal.signal(signal.SIGINT,stop)
    start=time.monotonic(); code=125; child=None
    with Path(job['log']).open('wb') as log:
        try:
            child=subprocess.Popen(job['argv'],cwd=job['cwd'],stdin=subprocess.PIPE if job.get('stdin') else subprocess.DEVNULL,
                stdout=log,stderr=subprocess.STDOUT,start_new_session=True,pass_fds=(lock_fd,))
            atomic(job['started'],{'worker':identity(os.getpid()),'child':identity(child.pid),'operation':job['id']})
            if job.get('stdin'):
                child.stdin.write(job['stdin'].encode()); child.stdin.close()
            while child.poll() is None:
                if stopped or time.monotonic()-start>job['timeout']:
                    os.killpg(child.pid,signal.SIGTERM)
                    try: child.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid,signal.SIGKILL); child.wait()
                    code=130 if stopped else 124
                    break
                time.sleep(.1)
            else: code=child.returncode
        except OSError as exc:
            log.write(f'WORKER ERROR: {exc}\n'.encode())
        finally:
            if child and child.poll() is None:
                os.killpg(child.pid,signal.SIGKILL); child.wait()
    atomic(job['receipt'],{'operation':job['id'],'argv_sha256':job['argv_sha256'],'exit_code':code,
        'log_sha256':hashlib.sha256(Path(job['log']).read_bytes()).hexdigest(),'seconds':round(time.monotonic()-start,3)})
    return code

if __name__=='__main__':
    sys.exit(main())
