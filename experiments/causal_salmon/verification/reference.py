"""Run a public-only analysis through macOS kernel file/network sandbox."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import numpy as np
from .materials import extract_report


def run_reference(public, description):
    source = Path(__file__).resolve().parent
    site = Path(np.__file__).resolve().parents[1]
    executable = Path(sys.executable).resolve()
    probe = source.parent/'planning.md'
    with tempfile.TemporaryDirectory(prefix='salmon-independent-public-') as tmp:
        work = Path(tmp).resolve()
        runtime, inputs = work/'runtime', work/'public'
        runtime.mkdir(); inputs.mkdir()
        shutil.copyfile(source/'reference_exec.py', runtime/'analyze.py')
        shutil.copyfile(source/'statistics.py', runtime/'statistics_public.py')
        (inputs/'data.csv').write_bytes(public)
        (inputs/'STUDY_DESCRIPTION.md').write_bytes(description)
        whitelist = ['/System','/usr','/Library',str(executable.parents[1]),str(site),str(runtime)]
        literals = [str(inputs/'data.csv'),str(inputs/'STUDY_DESCRIPTION.md'),'/dev/null','/private/var/db/dyld','/']
        profile = '(version 1)\n(allow default)\n(deny network*)\n(deny file-read*)\n(deny file-write*)\n'+''.join('(allow file-read* (subpath '+json.dumps(p)+'))\n' for p in whitelist)+''.join('(allow file-read* (literal '+json.dumps(p)+'))\n' for p in literals)
        environment = {'PATH':'/usr/bin:/bin','HOME':str(work),'TMPDIR':str(work),'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','VECLIB_MAXIMUM_THREADS':'1','LC_ALL':'C'}
        command = ['/usr/bin/sandbox-exec','-p',profile,str(executable),'-I','-S',str(runtime/'analyze.py'),str(inputs),str(runtime),str(site),str(probe)]
        completed = subprocess.run(command,cwd=inputs,env=environment,capture_output=True,text=True,timeout=60)
        if completed.returncode:
            raise RuntimeError(f'Public sandbox failed ({completed.returncode}): {completed.stderr}')
        output = json.loads(completed.stdout)
        report,error = extract_report(output['report'])
        boundary = all(output['probes'].values())
        good_numeric = output['analysis_status']=='ok'
        if output['method']=='insufficient_information':
            correct = bool(report and 'cannot determine the effect' in report and 'descriptive only' in report)
        else:
            correct = bool(report and 'We adopt its estimate' in report and 'comparable' in report and good_numeric)
        output.update(correct=correct,format_valid=error is None,input_boundary_passed=boundary,sandbox_profile=profile,executable_sha256=hashlib.sha256((runtime/'analyze.py').read_bytes()).hexdigest(),statistics_sha256=hashlib.sha256((runtime/'statistics_public.py').read_bytes()).hexdigest())
        return output
