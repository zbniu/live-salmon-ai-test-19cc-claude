"""macOS public-input whitelist; only standalone reference code is staged."""
import functools
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from src.evaluation.extract import extract_report

ROOT=Path(__file__).resolve().parents[2]
_PROBE=None


@functools.lru_cache
def runtime():
    source=ROOT/'src/calibration/public_reference.py'
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    staging=Path(tempfile.gettempdir())/'causal-salmon-reference-main'/digest
    staging.mkdir(parents=True,exist_ok=True)
    target=staging/'reference.py'
    if not target.exists():
        shutil.copyfile(source,target)
        target.chmod(0o444)
    if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
        raise RuntimeError('Staged public executable changed')
    return target


def profile(public_dir):
    public_dir=Path(public_dir).resolve()
    reference_path=runtime().resolve()
    literal=lambda p:'(literal '+json.dumps(str(p))+')'
    subpath=lambda p:'(subpath '+json.dumps(str(p))+')'
    roots=['/System','/usr/lib','/usr/share/zoneinfo',str(Path(sys.base_prefix)/'lib'),str(Path(sys.prefix)/'lib')]
    paths=[literal('/'),literal('/dev/null'),literal('/dev/urandom'),literal(Path(sys.executable).resolve()),literal(Path(sys.prefix)/'pyvenv.cfg'),literal(reference_path),literal(public_dir/'data.csv'),literal(public_dir/'STUDY_DESCRIPTION.md')]+[subpath(p) for p in roots]
    return '(version 1)\n(deny default)\n(allow process*)\n(allow sysctl-read)\n(allow mach-lookup)\n(allow file-read-metadata)\n(allow file-read* '+' '.join(paths)+')\n(deny network*)\n'


def launch(public_dir,args):
    policy=profile(public_dir)
    environment={'PATH':'/usr/bin:/bin','LANG':'en_US.UTF-8','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','VECLIB_MAXIMUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
    command=['/usr/bin/sandbox-exec','-p',policy,sys.executable,'-I','-B',str(runtime()),*args]
    p=subprocess.run(command,cwd=public_dir,env=environment,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
    if p.returncode:
        raise RuntimeError(f'Public reference failed (retained by caller): {p.stderr}')
    return json.loads(p.stdout),policy


def preflight(public_dir):
    return launch(public_dir,['--probe',str(ROOT)])[0]


def reference(public_dir):
    global _PROBE
    source=Path(public_dir)
    if set(p.name for p in source.iterdir() if p.is_file()) != {'data.csv','STUDY_DESCRIPTION.md'}:
        raise RuntimeError('Reference input directory must initially contain exactly two files')
    with tempfile.TemporaryDirectory(prefix='causal-salmon-public-') as temporary:
        staging=Path(temporary).resolve()
        for name in ('data.csv','STUDY_DESCRIPTION.md'):
            shutil.copyfile(source/name,staging/name)
            (staging/name).chmod(0o444)
        if _PROBE is None:
            _PROBE=preflight(staging)
        if not all(_PROBE.values()):
            raise RuntimeError('Public-only sandbox preflight failed: '+str(_PROBE))
        output,policy=launch(staging,[str(staging/'data.csv'),str(staging/'STUDY_DESCRIPTION.md')])
        extraction=extract_report(output['report'])
        output['format_valid']=extraction['status']=='ok'
        output['input_boundary_passed']=all(_PROBE.values())
        audit={'data_inputs':output['accessed_inputs'],'input_hashes':output['input_hashes'],'canonical_retained_inputs':[str((source/n).resolve()) for n in ('data.csv','STUDY_DESCRIPTION.md')],'runtime_executable':str(runtime()),'runtime_sha256':hashlib.sha256(runtime().read_bytes()).hexdigest(),'sandbox_policy':policy,'sandbox_policy_sha256':hashlib.sha256(policy.encode()).hexdigest(),'probe':_PROBE,'network':'denied','environment_keys':['PATH','LANG','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','PYTHONDONTWRITEBYTECODE'],'staged_inputs_removed_after_analysis':True}
    return output,audit
